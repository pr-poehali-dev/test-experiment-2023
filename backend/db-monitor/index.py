import json
import os
import psycopg2

SCHEMA = 't_p53092451_test_experiment_2023'
TABLES = ('members', 'spots', 'trips')


def handler(event: dict, context) -> dict:
    """Мониторинг: счётчики строк, last_updated и размер БД. Требует ADMIN_TOKEN."""

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '86400',
            },
            'body': '',
        }

    auth = (event.get('headers') or {}).get('X-Authorization', '')
    token = os.environ.get('ADMIN_TOKEN', '')
    if not token or auth != f'Bearer {token}':
        return {
            'statusCode': 401,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Unauthorized'}),
        }

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    dsn_params = conn.get_dsn_parameters()
    connection_info = {
        'host': conn.info.host,
        'port': conn.info.port,
        'dbname': conn.info.dbname,
        'user': conn.info.user,
        'ssl_in_use': conn.info.ssl_in_use,
        'server_version': conn.info.server_version,
        'dsn_parameters': {k: v for k, v in dsn_params.items() if k != 'password'},
    }
    cur = conn.cursor()

    cur.execute("""
        SELECT relname, seq_scan, idx_scan, n_live_tup,
               n_dead_tup, last_autovacuum, last_autoanalyze
        FROM pg_stat_user_tables
        WHERE schemaname = %s AND relname = ANY(%s)
    """, (SCHEMA, list(TABLES)))
    stat_rows = {row[0]: row for row in cur.fetchall()}

    tables = {}
    for table in TABLES:
        cur.execute(f'SELECT count(*), max(created_at) FROM {SCHEMA}.{table}')
        count, last_updated = cur.fetchone()

        cur.execute('SELECT pg_total_relation_size(%s)', (f'{SCHEMA}.{table}',))
        size_bytes = cur.fetchone()[0]

        stat = stat_rows.get(table)
        tables[table] = {
            'count': count,
            'last_updated': last_updated.isoformat() if last_updated else None,
            'size_bytes': size_bytes,
            'seq_scan': stat[1] if stat else None,
            'idx_scan': stat[2] if stat else None,
            'n_live_tup': stat[3] if stat else None,
            'n_dead_tup': stat[4] if stat else None,
            'last_autovacuum': stat[5].isoformat() if stat and stat[5] else None,
            'last_autoanalyze': stat[6].isoformat() if stat and stat[6] else None,
        }

    cur.execute('SELECT current_database()')
    db_name = cur.fetchone()[0]

    cur.execute('SELECT current_user')
    db_user = cur.fetchone()[0]

    cur.execute('SELECT pg_database_size(%s)', (db_name,))
    db_size = cur.fetchone()[0]

    cur.execute("""
        SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin
        FROM pg_catalog.pg_roles WHERE rolname = current_user
    """)
    row = cur.fetchone()
    user_privileges = {
        'rolname': row[0], 'rolsuper': row[1],
        'rolcreaterole': row[2], 'rolcreatedb': row[3], 'rolcanlogin': row[4],
    } if row else {}

    cur.execute("SELECT extname, extversion FROM pg_extension ORDER BY extname")
    extensions = [{'name': r[0], 'version': r[1]} for r in cur.fetchall()]

    cur.execute("""
        SELECT nspname FROM pg_catalog.pg_namespace
        WHERE nspname NOT LIKE 'pg_%' AND nspname != 'information_schema'
        ORDER BY nspname LIMIT 20
    """)
    accessible_schemas = [r[0] for r in cur.fetchall()]

    user_privileges['extensions'] = extensions
    user_privileges['accessible_schemas'] = accessible_schemas

    cur.execute("""
        SELECT schemaname, count(*) AS table_count,
               sum(pg_total_relation_size(relid)) AS total_size
        FROM pg_stat_user_tables
        GROUP BY schemaname
        ORDER BY total_size DESC
        LIMIT 10
    """)
    schema_stats = [
        {'schemaname': r[0], 'table_count': r[1], 'total_size': int(r[2]) if r[2] else 0}
        for r in cur.fetchall()
    ]

    diagnostics = {}
    try:
        cur.execute("SELECT count(*) FROM pg_catalog.pg_namespace")
        diagnostics['namespace_count'] = cur.fetchone()[0]
    except Exception:
        diagnostics['namespace_count'] = None

    try:
        cur.execute("SELECT setting FROM pg_catalog.pg_settings WHERE name = %s", ("password_encryption",))
        row = cur.fetchone()
        diagnostics['password_encryption'] = row[0] if row else None
    except Exception:
        diagnostics['password_encryption'] = None

    cur.close()
    conn.close()

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'db_name': db_name, 'db_user': db_user, 'connection_info': connection_info, 'user_privileges': user_privileges, 'schema_stats': schema_stats, 'diagnostics': diagnostics, 'tables': tables, 'db_size_bytes': db_size}),
    }