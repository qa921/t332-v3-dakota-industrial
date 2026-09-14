import os, re
import psycopg
from psycopg import sql
SCHEMA=os.environ.get('DATABASE_SCHEMA','t332_v1')
if not re.fullmatch(r't332_v[1-5]',SCHEMA):
    raise ValueError('Invalid isolated schema')
def initialise():
    with psycopg.connect(os.environ['DATABASE_URL']) as c:
        c.execute('CREATE EXTENSION IF NOT EXISTS postgis')
        c.execute(sql.SQL('CREATE SCHEMA IF NOT EXISTS {}').format(sql.Identifier(SCHEMA)))
        c.execute(sql.SQL('CREATE TABLE IF NOT EXISTS {}.properties (parcel_id text PRIMARY KEY, payload jsonb NOT NULL, source_url text NOT NULL, saved_at timestamptz DEFAULT now())').format(sql.Identifier(SCHEMA)))
def save_property(parcel_id,payload,source_url):
    from psycopg.types.json import Jsonb
    with psycopg.connect(os.environ['DATABASE_URL']) as c:
        c.execute(sql.SQL('INSERT INTO {}.properties(parcel_id,payload,source_url) VALUES (%s,%s,%s) ON CONFLICT (parcel_id) DO UPDATE SET payload=EXCLUDED.payload,source_url=EXCLUDED.source_url,saved_at=now()').format(sql.Identifier(SCHEMA)),(parcel_id,Jsonb(payload),source_url))
