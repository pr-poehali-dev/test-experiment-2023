import json
import os
import psycopg2

SCHEMA = 't_p53092451_test_experiment_2023'
ALLOWED_TABLES = {'members', 'spots', 'trips'}
ALLOWED_COLUMNS = {
    'members': {'id', 'name', 'role', 'joined_year', 'location', 'favorite_fish', 'trips_count', 'created_at'},
    'spots':   {'id', 'name', 'region', 'fish_types', 'difficulty', 'created_at'},
    'trips':   {'id', 'title', 'spot_id', 'date', 'participants_count', 'organizer', 'status', 'created_at'},
}


def handler(event: dict, context) -> dict:
    """Отладочный эндпоинт: принимает имя таблицы, возвращает её содержимое. Требует ADMIN_TOKEN."""

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

    try:
        limit = min(int(params.get('limit') or 100), 500)
        offset = max(int(params.get('offset') or 0), 0)
    except ValueError:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'limit и offset должны быть числами'}),
        }

    order_by = (params.get('order_by') or 'id').strip().lower()
    if order_by not in ALLOWED_COLUMNS[table]:
        order_by = 'id'

    where_clause = ''
    where_values = []
    where_raw = (params.get('where') or '').strip()
    if where_raw and '=' in where_raw:
        col, _, val = where_raw.partition('=')
        col = col.strip().lower()
        if col in ALLOWED_COLUMNS[table]:
            where_clause = f'WHERE {col} = %s'
            where_values = [val.strip()]

    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
    except Exception:
        return {
            'statusCode': 503,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'База данных недоступна', 'stage': 'connection'}),
        }

    try:
        cur = conn.cursor()
        query = f'SELECT * FROM {SCHEMA}.{table} {where_clause} ORDER BY {order_by} LIMIT %s OFFSET %s'
        cur.execute(query, where_values + [limit, offset])
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception:
        conn.close()
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Ошибка выполнения запроса', 'stage': 'query'}),
        }

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
