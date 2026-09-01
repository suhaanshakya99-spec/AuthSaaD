from celery import Celery, Task
from core.config import settings
from brevo import Brevo
from brevo.transactional_emails import (SendTransacEmailRequestSender, SendTransacEmailRequestToItem)
from typing import cast
import httpx


celery = Celery(namespace="celery_app",
                 broker=settings.BROKER_URL,
                 backend=settings.BACKEND_URL)

@celery.task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def _sending_verification_mail(verification_token:str, receiver_email:str):
    api = settings.BREVO_API
    sender = settings.SENDER_EMAIL

    client = Brevo(api_key=api)

    result = client.transactional_emails.send_transac_email(
        subject="Verification Email",
        sender=SendTransacEmailRequestSender(name="AuthSaas", email=sender),
        to=[SendTransacEmailRequestToItem(email=receiver_email)],
        html_content=f"""
        <html>
            <body>
                <h2>Verify your email</h2>

                <p>
                    Thanks for signing up!
                    Click the button below to verify your email.
                </p>

                <a href="{verification_token}">
                    Verify Email
                </a>

                <p>This link expires in 30 minutes.</p>
            </body>
        </html>
        """
    )
    return result.message_id

sending_verification_mail = cast(Task, _sending_verification_mail)



@celery.task(autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def _send_user_verificationmail(receiver_email:str, verification_token:str):

    api = settings.BREVO_API
    sender = settings.SENDER_EMAIL

    brevo = Brevo(api_key=api)

    response = brevo.transactional_emails.send_transac_email(
        sender= SendTransacEmailRequestSender(name="Auth", email=sender),
        subject="Verification",
        to=[SendTransacEmailRequestToItem(email=receiver_email)],
        html_content=f"""
                <html>
                    <body>
                        <h2>Verify your email</h2>
        
                        <p>
                            Thanks for signing up!
                            Click the button below to verify your email.
                        </p>
        
                        <a href="{verification_token}">
                            Verify Email
                        </a>
        
                        <p>This link expires in 30 minutes.</p>
                    </body>
                </html>
                """
    )

    return response.message_id


send_user_verificationmail = cast(Task, _send_user_verificationmail)