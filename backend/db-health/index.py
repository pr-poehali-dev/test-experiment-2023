import json
import os
import time
import datetime
import psycopg2


def handler(event: dict, context) -> dict:
    """Проверяет доступность базы данных и возвращает версию PostgreSQL."""
    ts = datetime.datetime.utcnow().isoformat() + 'Z'
    ip = (event.get('requestContext') or {}).get('identity', {}).get('sourceIp', 'unknown')
    print(f"[db-health] {ts} ip={ip}")

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400',
            },
            'body': ''
        }

    try:
        t0 = time.monotonic()
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        cur = conn.cursor()
        cur.execute('SELECT version()')
        version = cur.fetchone()[0]
        latency_ms = round((time.monotonic() - t0) * 1000, 1)
        cur.close()
        conn.close()
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': {'status': 'ok', 'version': version, 'latency_ms': latency_ms},
        }
    except Exception:
        return {
            'statusCode': 503,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': {'status': 'error', 'message': 'База данных недоступна'},
        }