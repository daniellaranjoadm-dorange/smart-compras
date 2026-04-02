from sqlalchemy import create_engine, text

DATABASE_URL = "SUA_DATABASE_URL"

engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    conn.execute(text("""
        ALTER TABLE usuarios
        ADD COLUMN IF NOT EXISTS senha_hash TEXT;
    """))
    print("OK: coluna senha_hash garantida com sucesso.")
