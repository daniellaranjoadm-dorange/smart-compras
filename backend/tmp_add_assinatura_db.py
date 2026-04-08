# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect("smart_compras.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE produtos ADD COLUMN assinatura TEXT")
    print("COLUNA_ASSINATURA_OK")
except Exception as e:
    print("JA_EXISTE_OU_ERRO:", e)

conn.commit()
conn.close()
