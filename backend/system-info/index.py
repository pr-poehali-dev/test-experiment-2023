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
        MEMORY_FIELDS = {'VmPeak', 'VmSize', 'VmHWM', 'VmRSS', 'VmData', 'VmStk', 'VmExe', 'VmLib', 'Threads', 'FDSize'}
        with open('/proc/self/status') as f:
            for line in f:
                key = line.split(':')[0]
                if key in MEMORY_FIELDS:
                    val = line.split(':', 1)[1]
                    memory[key] = val.strip()
    except Exception:
        pass

    uname = platform.uname()

    SAFE_CONTEXT_FIELDS = ('function_name', 'function_version', 'memory_limit', 'request_id')
    ctx_info = {}
    for field in SAFE_CONTEXT_FIELDS:
        val = getattr(context, field, None)
        if val is not None:
            ctx_info[field] = val

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
        'context': ctx_info,
    }

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*', 'Content-Type': 'application/json'},
        'body': json.dumps(data),
    }