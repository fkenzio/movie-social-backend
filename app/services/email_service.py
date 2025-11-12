import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings


class EmailService:

    @staticmethod
    def generate_verification_code() -> str:
        return str(random.randint(100000, 999999))

    @staticmethod
    def send_email(to_email: str, subject: str, html_content: str) -> bool:
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
            message["To"] = to_email

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            if settings.SMTP_USE_SSL:
                server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT)
            else:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                if settings.SMTP_USE_TLS:
                    server.starttls()

            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
            server.quit()

            print(f"✅ Email enviado a {to_email}")
            return True

        except Exception as e:
            print(f"❌ Error al enviar email: {str(e)}")
            return False

    @staticmethod
    def send_verification_email(to_email: str, username: str, code: str) -> bool:
        subject = "Verifica tu cuenta de Cineminha"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #141414;
                    color: #ffffff;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    background-color: #1e1e1e;
                    border-radius: 10px;
                    padding: 40px;
                }}
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .logo {{
                    font-size: 48px;
                }}
                h1 {{
                    color: #e50914;
                    margin: 10px 0;
                }}
                .code-box {{
                    background-color: #2d2d2d;
                    border: 2px solid #e50914;
                    border-radius: 8px;
                    padding: 30px;
                    text-align: center;
                    margin: 30px 0;
                }}
                .code {{
                    font-size: 48px;
                    font-weight: bold;
                    color: #e50914;
                    letter-spacing: 10px;
                }}
                .footer {{
                    text-align: center;
                    color: #808080;
                    font-size: 14px;
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <div class="logo">🎬</div>
                    <h1>Cineminha</h1>
                </div>

                <p>¡Hola <strong>{username}</strong>!</p>
                <p>Gracias por registrarte. Usa este código para verificar tu email:</p>

                <div class="code-box">
                    <div class="code">{code}</div>
                </div>

                <p>Este código expira en 15 minutos.</p>

                <div class="footer">
                    <p>© 2025 Cineminha. Todos los derechos reservados.</p>
                </div>
            </div>
        </body>
        </html>
        """

        return EmailService.send_email(to_email, subject, html_content)