import json
import os
import redis


def _auth(event: dict) -> bool:
    token = os.environ.get('ADMIN_TOKEN', '')
    auth = (event.get('headers') or {}).get('X-Authorization', '')
    return bool(token) and auth == f'Bearer {token}'


def _redis() -> redis.Redis:
    return redis.Redis.from_url(os.environ['REDIS_URL'], decode_responses=True)


def handler(event: dict, context) -> dict:
    """Кэш-менеджер: POST сохраняет {key, value, ttl?}, GET возвращает все ключи. Требует ADMIN_TOKEN."""

    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization',
                'Access-Control-Max-Age': '86400',
            },
            'body': '',
        }

    if not _auth(event):
        return {
            'statusCode': 401,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Unauthorized'}),
        }

    method = event.get('httpMethod', 'GET')
    r = _redis()

    if method == 'POST':
        body = json.loads(event.get('body') or '{}')
        key = body.get('key')
        value = body.get('value')
        ttl = body.get('ttl')

        if not key:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'key is required'}),
            }

        serialized = json.dumps(value)
        if ttl:
            r.setex(key, int(ttl), serialized)
        else:
            r.set(key, serialized)

        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'ok': True, 'key': key, 'ttl': ttl}),
        }

    if method == 'DELETE':
        body = json.loads(event.get('body') or '{}')
        key = body.get('key')
        if not key:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'key is required'}),
            }
        deleted = r.delete(key)
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'ok': True, 'deleted': deleted}),
        }

    keys = r.keys('*')
    result = {}
    for key in keys:
        raw = r.get(key)
        ttl = r.ttl(key)
        try:
            result[key] = {'value': json.loads(raw), 'ttl': ttl if ttl >= 0 else None}
        except Exception:
            result[key] = {'value': raw, 'ttl': ttl if ttl >= 0 else None}

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'keys': result, 'count': len(result)}),
    }
