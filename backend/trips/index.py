import json
import os
import psycopg2
from datetime import date

SCHEMA = 't_p53092451_test_experiment_2023'


def handler(event: dict, context) -> dict:
    """Возвращает список предстоящих выездов с информацией о водоёме."""

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

    region = (event.get('queryStringParameters') or {}).get('region', '').strip()

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
        if region:
            cur.execute("""
                SELECT
                    t.id, t.title, t.date, t.participants_count, t.organizer, t.status,
                    s.name AS spot_name, s.region, s.fish_types, s.difficulty
                FROM {schema}.trips t
                LEFT JOIN {schema}.spots s ON t.spot_id = s.id
                WHERE t.status = 'planned'
                  AND s.region ILIKE '%%' || %s || '%%'
                ORDER BY t.date ASC
                LIMIT 10
            """.format(schema=SCHEMA), (region,))
        else:
            cur.execute("""
                SELECT
                    t.id, t.title, t.date, t.participants_count, t.organizer, t.status,
                    s.name AS spot_name, s.region, s.fish_types, s.difficulty
                FROM {schema}.trips t
                LEFT JOIN {schema}.spots s ON t.spot_id = s.id
                WHERE t.status = 'planned'
                ORDER BY t.date ASC
                LIMIT 10
            """.format(schema=SCHEMA))

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

    trips = []
    for row in rows:
        trips.append({
            'id': row[0],
            'title': row[1],
            'date': row[2].isoformat() if isinstance(row[2], date) else str(row[2]),
            'participants_count': row[3],
            'organizer': row[4],
            'status': row[5],
            'spot_name': row[6],
            'region': row[7],
            'fish_types': row[8],
            'difficulty': row[9],
        })

    return {
        'statusCode': 200,
        'headers': {'Access-Control-Allow-Origin': '*'},
        'body': json.dumps({'trips': trips}, ensure_ascii=False),
    }
