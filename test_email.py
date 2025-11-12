from dotenv import load_dotenv
load_dotenv()

from app.services.email_service import EmailService

# Probar envío de email
print("Probando envío de email...")
result = EmailService.send_verification_email(
    to_email="victorjoseruizsoto4@gmail.com",
    username="TestUser",
    code="123456"
)

if result:
    print("✅ Email enviado correctamente")
else:
    print("❌ Error al enviar email")