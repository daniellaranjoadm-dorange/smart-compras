from sqlalchemy import create_engine, text

DATABASE_URL = "COLE_AQUI_SUA_DATABASE_URL"

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

with engine.begin() as conn:
    conn.execute(text("""
        ALTER TABLE usuarios
        ADD COLUMN IF NOT EXISTS senha_hash TEXT;
    """))
    print("OK 1/2: coluna senha_hash garantida.")

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'usuarios'
        ORDER BY ordinal_position;
    """))
    cols = [row[0] for row in result]
    print("OK 2/2: colunas atuais =", cols)
