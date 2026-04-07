from dotenv import dotenv_values

env = dotenv_values(".env.stok")
print(env)
print("AUTH:", repr(env.get("STOK_AUTH_BEARER")))
print("SESSAO:", repr(env.get("STOK_SESSAO_ID")))
