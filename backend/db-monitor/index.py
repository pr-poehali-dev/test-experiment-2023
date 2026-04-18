import json
import os
import psycopg2

SCHEMA = 't_p53092451_test_experiment_2023'


def handler(event: dict, context) -> dict:
    """Мониторинг: возвращает количество строк в таблицах members, spots, trips. Требует ADMIN_TOKEN."""

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

    counts = {}
    for table in ('members', 'spots', 'trips'):
        cur.execute(f'SELECT count(*) FROM {SCHEMA}.{table}')
        counts[table] = cur.fetchone()[0]

    cur.close()
    conn.close()

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'counts': counts}),
    }