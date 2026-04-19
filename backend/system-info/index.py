import json
import sys
import os
import platform
from datetime import datetime, timezone


def handler(event: dict, context) -> dict:
    """Возвращает системную информацию: время, версию Python, рабочую директорию, hostname, память, ОС."""
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Methods': 'GET, OPTIONS', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400'}, 'body': ''}

    hostname = None
    try:
        with open('/etc/hostname') as f:
            hostname = f.read().strip()
    except Exception:
        pass

    memory = {}
    try:
        with open('/proc/self/status') as f:
            for line in f:
                if line.startswith('VmRSS:') or line.startswith('VmSize:'):
                    key, val = line.split(':', 1)
                    memory[key.strip()] = val.strip()
    except Exception:
        pass

    uname = platform.uname()

    data = {
        'time': datetime.now(timezone.utc).isoformat(),
        'python_version': sys.version,
        'cwd': os.getcwd(),
        'hostname': hostname,
        'memory': memory,
        'os': {
            'system': uname.system,
            'release': uname.release,
            'machine': uname.machine,
        },
    }

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
        'body': json.dumps(data),
    }
