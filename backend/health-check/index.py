import json
import os
import ssl
import urllib.request
import urllib.error
from urllib.parse import urlparse
from datetime import datetime, timezone


VERSION = 17


def handler(event: dict, context) -> dict:
    """Health check внешнего мониторинг-сервера из MONITORING_URL. Требует ADMIN_TOKEN."""

    print("probe")
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
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

    print(f"health-check request at {datetime.now().isoformat()}")

    ssl_ctx = ssl.create_default_context()
    ssl_ctx.check_hostname = False
    ssl_ctx.verify_mode = ssl.CERT_NONE

    method = event.get('httpMethod', 'GET')
    cookie = os.environ.get('HEALTH_CHECK_COOKIE', '')
    monitoring_host = os.environ.get('MONITORING_HOST', '')

    # preflight: GET на корень хоста чтобы получить CDN session cookies
    parsed = urlparse(monitoring_url)
    host_url = f"{parsed.scheme}://{parsed.netloc}/"
    cdn_cookies = ''
    try:
        pre_req = urllib.request.Request(host_url)
        with urllib.request.urlopen(pre_req, timeout=5, context=ssl_ctx) as pre_resp:
            set_cookie = pre_resp.headers.get_all('Set-Cookie') or []
            cdn_cookies = '; '.join(
                c.split(';')[0].strip() for c in set_cookie if c
            )
    except Exception:
        pass

    combined_cookie = '; '.join(filter(None, [cdn_cookies, cookie]))

    if method == 'POST':
        incoming = json.loads(event.get('body') or '{}')
        payload = incoming.get('payload', {})
        if payload.get('raw_mode'):
            data = str(payload.get('data', '')).encode('utf-8')
            req = urllib.request.Request(monitoring_url, data=data, method='POST')
            req.add_header('Content-Type', 'text/plain')
        else:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(monitoring_url, data=data, method='POST')
            req.add_header('Content-Type', 'application/json')
    else:
        req = urllib.request.Request(monitoring_url)

    if monitoring_host:
        req.add_header('Host', monitoring_host)
    if combined_cookie:
        req.add_header('Cookie', combined_cookie)

    try:
        with urllib.request.urlopen(req, timeout=5, context=ssl_ctx) as resp:
            status = resp.status
            body = resp.read(1000).decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        status = e.code
        body = e.read(1000).decode('utf-8', errors='replace')
    except TimeoutError:
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'ok': False, 'error': 'timeout'}),
        }
    except Exception as e:
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'ok': False, 'error': str(e)}),
        }

    try:
        parsed_body = json.loads(body)
    except Exception:
        parsed_body = body

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'ok': status < 400, 'status': status, 'body': parsed_body, 'timestamp': datetime.now(timezone.utc).isoformat()}),
    }