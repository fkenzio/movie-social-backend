# test_env.py
from dotenv import load_dotenv
import os

load_dotenv()

print("DATABASE_URL:", os.getenv("DATABASE_URL"))
print("SECRET_KEY:", os.getenv("SECRET_KEY"))
print("SMTP_HOST:", os.getenv("SMTP_HOST"))
print("SMTP_USER:", os.getenv("SMTP_USER"))

if os.getenv("DATABASE_URL"):
    print("\n✅ .env se está leyendo correctamente")
else:
    print("\n❌ .env NO se está leyendo")