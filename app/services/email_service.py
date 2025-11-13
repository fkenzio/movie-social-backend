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
        """Enviar email de verificación con código"""
        subject = "Verifica tu cuenta de Cineminha"

        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{
                        font-family: 'Arial', 'Helvetica', sans-serif;
                        background-color: #0a0a0a;
                        color: #ffffff;
                        margin: 0;
                        padding: 0;
                        -webkit-font-smoothing: antialiased;
                    }}
                    .email-wrapper {{
                        background-color: #0a0a0a;
                        padding: 40px 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                        border-radius: 16px;
                        padding: 40px;
                        box-shadow: 0 8px 32px rgba(229, 9, 20, 0.15);
                        border: 1px solid rgba(229, 9, 20, 0.2);
                    }}
                    .header {{
                        text-align: center;
                        margin-bottom: 40px;
                    }}
                    .logo {{
                        font-size: 64px;
                        margin-bottom: 16px;
                        display: block;
                    }}
                    h1 {{
                        color: #e50914;
                        margin: 0 0 16px 0;
                        font-size: 28px;
                        font-weight: bold;
                    }}
                    .subtitle {{
                        color: #ffffff;
                        font-size: 18px;
                        margin: 0 0 8px 0;
                    }}
                    .message {{
                        color: #e0e0e0;
                        font-size: 16px;
                        line-height: 1.6;
                        margin: 24px 0;
                    }}
                    .message strong {{
                        color: #ffffff;
                        font-weight: bold;
                    }}
                    .code-box {{
                        background: linear-gradient(135deg, #1f1f1f 0%, #141414 100%);
                        border: 3px solid #e50914;
                        border-radius: 12px;
                        padding: 32px;
                        text-align: center;
                        margin: 32px 0;
                        box-shadow: 0 4px 24px rgba(229, 9, 20, 0.3);
                    }}
                    .code-label {{
                        color: #b0b0b0;
                        font-size: 14px;
                        text-transform: uppercase;
                        letter-spacing: 2px;
                        margin-bottom: 16px;
                        display: block;
                    }}
                    .code {{
                        font-size: 56px;
                        font-weight: bold;
                        color: #e50914;
                        letter-spacing: 12px;
                        font-family: 'Courier New', monospace;
                        display: block;
                        text-shadow: 0 0 20px rgba(229, 9, 20, 0.5);
                    }}
                    .warning {{
                        background-color: rgba(229, 9, 20, 0.1);
                        border-left: 4px solid #e50914;
                        padding: 16px;
                        margin: 24px 0;
                        border-radius: 4px;
                    }}
                    .warning-text {{
                        color: #ffffff;
                        font-size: 14px;
                        margin: 0;
                    }}
                    .footer {{
                        text-align: center;
                        color: #808080;
                        font-size: 13px;
                        margin-top: 40px;
                        padding-top: 24px;
                        border-top: 1px solid #333333;
                    }}
                    .footer a {{
                        color: #e50914;
                        text-decoration: none;
                    }}
                    .button {{
                        display: inline-block;
                        background-color: #e50914;
                        color: #ffffff !important;
                        text-decoration: none;
                        padding: 14px 32px;
                        border-radius: 6px;
                        font-weight: bold;
                        font-size: 16px;
                        margin: 24px 0;
                        box-shadow: 0 4px 16px rgba(229, 9, 20, 0.3);
                    }}
                </style>
            </head>
            <body>
                <div class="email-wrapper">
                    <div class="container">
                        <div class="header">
                            <span class="logo">🎬</span>
                            <h1>Cineminha</h1>
                            <p class="subtitle">Verifica tu cuenta</p>
                        </div>

                        <p class="message">
                            ¡Hola <strong>{username}</strong>! 👋
                        </p>

                        <p class="message">
                            Gracias por unirte a <strong>Cineminha</strong>, tu nueva comunidad de cinéfilos. 
                            Para completar tu registro y empezar a disfrutar de todas las funciones, 
                            por favor verifica tu email usando el siguiente código:
                        </p>

                        <div class="code-box">
                            <span class="code-label">Tu código de verificación</span>
                            <span class="code">{code}</span>
                        </div>

                        <div class="warning">
                            <p class="warning-text">
                                ⏱️ Este código es válido por <strong>15 minutos</strong> y solo puede usarse una vez.
                            </p>
                        </div>

                        <p class="message">
                            Si no creaste esta cuenta, puedes ignorar este email de forma segura.
                        </p>

                        <div class="footer">
                            <p>© 2025 Cineminha. Todos los derechos reservados.</p>
                            <p>
                                ¿Problemas? Contáctanos en 
                                <a href="mailto:support@cineminha.com">support@cineminha.com</a>
                            </p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
        """

        return EmailService.send_email(to_email, subject, html_content)