import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import random
import string
from app.config import settings
import logging

logger = logging.getLogger(__name__)

# Configurar Brevo
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = settings.BREVO_API_KEY


class EmailService:
    @staticmethod
    def generate_verification_code() -> str:
        """Generar código de verificación de 6 dígitos"""
        return ''.join(random.choices(string.digits, k=6))

    @staticmethod
    def send_verification_email(email: str, code: str) -> bool:
        """Enviar email de verificación usando Brevo"""
        try:
            if not settings.BREVO_API_KEY:
                logger.warning("BREVO_API_KEY not configured. Email not sent.")
                logger.info(f"Verification code for {email}: {code}")
                return False

            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": email}],
                sender={"email": settings.EMAIL_FROM, "name": settings.EMAIL_FROM_NAME},
                subject="Código de verificación - Cineminha",
                html_content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            margin: 0;
                            padding: 20px;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                            background-color: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }}
                        .code {{
                            font-size: 36px;
                            font-weight: bold;
                            color: #4F46E5;
                            letter-spacing: 8px;
                            text-align: center;
                            padding: 20px;
                            background-color: #f8f9fa;
                            border-radius: 8px;
                            margin: 20px 0;
                        }}
                        h2 {{
                            color: #333;
                        }}
                        p {{
                            color: #666;
                            line-height: 1.6;
                        }}
                        .footer {{
                            margin-top: 30px;
                            padding-top: 20px;
                            border-top: 1px solid #eee;
                            color: #999;
                            font-size: 12px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>🎬 Verifica tu cuenta en Cineminha</h2>
                        <p>¡Gracias por registrarte! Para completar tu registro, usa el siguiente código de verificación:</p>
                        <div class="code">{code}</div>
                        <p><strong>Este código expirará en 10 minutos.</strong></p>
                        <p>Si no solicitaste este código, puedes ignorar este mensaje de forma segura.</p>
                        <div class="footer">
                            <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            )

            api_response = api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Verification email sent to {email}. Message ID: {api_response.message_id}")
            return True

        except ApiException as e:
            logger.error(f"Brevo API error: {e}")
            logger.info(f"Verification code for {email}: {code}")
            return False
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            logger.info(f"Verification code for {email}: {code}")
            return False

    @staticmethod
    def send_password_reset_email(email: str, code: str) -> bool:
        """Enviar email de recuperación de contraseña usando Brevo"""
        try:
            if not settings.BREVO_API_KEY:
                logger.warning("BREVO_API_KEY not configured. Email not sent.")
                logger.info(f"Password reset code for {email}: {code}")
                return False

            api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
                sib_api_v3_sdk.ApiClient(configuration)
            )

            send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
                to=[{"email": email}],
                sender={"email": settings.EMAIL_FROM, "name": settings.EMAIL_FROM_NAME},
                subject="Recuperación de contraseña - Cineminha",
                html_content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            margin: 0;
                            padding: 20px;
                        }}
                        .container {{
                            max-width: 600px;
                            margin: 0 auto;
                            background-color: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                        }}
                        .code {{
                            font-size: 36px;
                            font-weight: bold;
                            color: #DC2626;
                            letter-spacing: 8px;
                            text-align: center;
                            padding: 20px;
                            background-color: #fef2f2;
                            border-radius: 8px;
                            margin: 20px 0;
                        }}
                        h2 {{
                            color: #333;
                        }}
                        p {{
                            color: #666;
                            line-height: 1.6;
                        }}
                        .warning {{
                            background-color: #fef3c7;
                            padding: 15px;
                            border-radius: 5px;
                            border-left: 4px solid #f59e0b;
                            margin: 20px 0;
                        }}
                        .footer {{
                            margin-top: 30px;
                            padding-top: 20px;
                            border-top: 1px solid #eee;
                            color: #999;
                            font-size: 12px;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h2>🔐 Recuperación de contraseña</h2>
                        <p>Recibimos una solicitud para restablecer tu contraseña. Usa el siguiente código:</p>
                        <div class="code">{code}</div>
                        <p><strong>Este código expirará en 10 minutos.</strong></p>
                        <div class="warning">
                            <p><strong>⚠️ Importante:</strong> Si no solicitaste este código, tu cuenta podría estar en riesgo. Considera cambiar tu contraseña inmediatamente.</p>
                        </div>
                        <div class="footer">
                            <p>Este es un correo automático, por favor no respondas a este mensaje.</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            )

            api_response = api_instance.send_transac_email(send_smtp_email)
            logger.info(f"Password reset email sent to {email}. Message ID: {api_response.message_id}")
            return True

        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            logger.info(f"Password reset code for {email}: {code}")
            return False