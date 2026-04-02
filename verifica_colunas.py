from sqlalchemy import create_engine, text

DATABASE_URL = "SUA_DATABASE_URL"

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'usuarios'
        ORDER BY ordinal_position;
    """))
    cols = [row[0] for row in result]
    print("COLUNAS:", cols)
