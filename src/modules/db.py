import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, TIMESTAMP

# テーブル定義
metadata = sa.MetaData()
tbl = sa.Table(
    'users', metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), unique=True),
    Column("password", String(120), unique=True),
)

async def get_user(conn, user, password):
    query = sa.select([ tbl.c.id, tbl.c.name, tbl.c.password ]).select_from(tbl).where(tbl.c.name == user)
    user = await (await conn.execute(query)).first()
    return user
