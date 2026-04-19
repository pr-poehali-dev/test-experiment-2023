import json
import os
import urllib.request
import urllib.error
from datetime import datetime, timezone


def handler(event: dict, context) -> dict:
    """Health check внешнего мониторинг-сервера из MONITORING_URL. Требует ADMIN_TOKEN."""

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

    token = os.environ.get('ADMIN_TOKEN', '')
    auth = (event.get('headers') or {}).get('X-Authorization', '')
    if not token or auth != f'Bearer {token}':
        return {
            'statusCode': 401,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Unauthorized'}),
        }

    monitoring_url = os.environ.get('MONITORING_URL', '')
    if not monitoring_url:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'MONITORING_URL not set'}),
        }

    cookie = os.environ.get('HEALTH_CHECK_COOKIE', '')
    req = urllib.request.Request(monitoring_url)
    if cookie:
        req.add_header('Cookie', cookie)

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            status = resp.status
            body = resp.read(1000).decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read(1000).decode('utf-8', errors='replace')
    except Exception as e:
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'ok': False, 'error': str(e)}),
        }

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'ok': status < 400, 'status': status, 'body': body, 'timestamp': datetime.now(timezone.utc).isoformat()}),
    }