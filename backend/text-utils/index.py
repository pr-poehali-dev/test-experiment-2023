import json
import os
import psycopg2


def handler(event: dict, context) -> dict:
    """Анализ текста: length, octet_length, кодировка. Требует ADMIN_TOKEN."""

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

    text = (event.get('queryStringParameters') or {}).get('text', '')
    if not text:
        return {
            'statusCode': 400,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Параметр text обязателен'}),
        }

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
        cur.execute(
            "SELECT length(%s::text), octet_length(%s::text)",
            (text, text)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        conn.close()
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Ошибка выполнения запроса', 'stage': 'query', 'exception': type(e).__name__}),
        }

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({
            'text': text,
            'length': row[0],
            'octet_length': row[1],
        }, ensure_ascii=False),
    }