import json
import os
import psycopg2


SCHEMA = 't_p53092451_test_experiment_2023'
ALLOWED_TABLES = {'members', 'spots', 'trips'}


def handler(event: dict, context) -> dict:
    """Отладочный эндпоинт: принимает имя таблицы, возвращает её содержимое."""

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400',
            },
            'body': '',
        }

    params = event.get('queryStringParameters') or {}
    table = (params.get('table') or '').strip().lower()

    if not table:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Параметр table обязателен', 'allowed': list(ALLOWED_TABLES)}),
        }

    if table not in ALLOWED_TABLES:
        return {
            'statusCode': 403,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f'Таблица "{table}" не разрешена', 'allowed': list(ALLOWED_TABLES)}),
        }

    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    cur = conn.cursor()

    cur.execute(f'SELECT * FROM {SCHEMA}.{table} LIMIT 100')
    columns = [desc[0] for desc in cur.description]
    rows = cur.fetchall()

    cur.close()
    conn.close()

    data = []
    for row in rows:
        record = {}
        for col, val in zip(columns, row):
            record[col] = str(val) if hasattr(val, 'isoformat') else val
        data.append(record)

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'table': table, 'count': len(data), 'rows': data}, ensure_ascii=False),
    }
