from pathlib import Path

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkYW5pZWwubGFyYW5qb0BlY292aXguY29tIiwiZXhwIjoxNzc1MTU2OTExfQ.E4NnpQzv4HQbGEj2reGXKJYiAW776JjMLcO2BS73328"
Path(".smart_token").write_text(token, encoding="utf-8")

print("OK: .smart_token regravado sem BOM")
