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
    cur = conn.cursor()

    tables = {}
    for table in TABLES:
        cur.execute(f'SELECT count(*), max(created_at) FROM {SCHEMA}.{table}')
        count, last_updated = cur.fetchone()
        tables[table] = {
            'count': count,
            'last_updated': last_updated.isoformat() if last_updated else None,
        }

    cur.execute('SELECT pg_database_size(current_database())')
    db_size = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'tables': tables, 'db_size_bytes': db_size}),
    }
