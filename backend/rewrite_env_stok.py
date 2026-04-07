from pathlib import Path

content = """STOK_AUTH_BEARER="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJ2aXBjb21tZXJjZSIsImF1ZCI6ImFwaS1hZG1pbiIsInN1YiI6IjZiYzQ4NjdlLWRjYTktMTFlOS04NzQyLTAyMGQ3OTM1OWNhMCIsInZpcGNvbW1lcmNlQ2xpZW50ZUlkIjpudWxsLCJpYXQiOjE3NjIxOTI4NTgsInZlciI6MSwiY2xpZW50IjpudWxsLCJvcGVyYXRvciI6bnVsbCwib3JnIjoiMTMwIn0.Mf5lbWYbRdbsx-1lpMceO5K-PBZU2Akwy4zMFjqp9Ai2jhLGBiSZO8i5IzE5rql3FiHjzJanSH6CUwNBBZAW4Q"
STOK_SESSAO_ID="e9d6291aa45027cb4a940e78a54b01f5"
STOK_ORGANIZATION_ID="130"
STOK_DOMAIN_KEY="stokonline.com.br"
"""

Path(".env.stok").write_text(content, encoding="utf-8")
print("OK: .env.stok regravado sem BOM")
