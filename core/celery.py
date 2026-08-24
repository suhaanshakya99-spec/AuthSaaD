from celery import Celery, Task
from core.config import settings
import resend
from typing import cast


celery = Celery(namespace="app",
                 broker=settings.BROKER_URL,
                 backend=settings.BACKEND_URL)


@celery.task(autoretry_for=(Exception,),
             retry_backoff=True,
             max_retries=3)
def _sending_verification_mail(receiver_mail:str, verification_url:str):

    api = settings.RESEND_API
    sender_mail = settings.SENDER_EMAIL

    resend.api_key = api

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verify your email</title>
    </head>

    <body style="margin:0; padding:0; background:#f5f7fb; font-family:Arial,sans-serif; color:#1f2937;">
    <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 20px;">
        <tr>
        <td align="center">

            <table width="100%" cellpadding="0" cellspacing="0"
                style="max-width:600px; background:#ffffff; border-radius:12px; padding:40px;">

            <tr>
                <td align="center">
                <h1 style="margin:0 0 20px; font-size:28px; color:#111827;">
                    Verify your email
                </h1>

                <p style="font-size:16px; line-height:1.6; color:#4b5563;">
                    Thanks for signing up! Please verify your email address
                    by clicking the button below.
                </p>

                <table cellpadding="0" cellspacing="0" style="margin:30px auto;">
                    <tr>
                    <td style="background:#2563eb; border-radius:8px;">
                        <a href="{verification_url}"
                        style="display:inline-block; padding:14px 28px;
                                color:#ffffff; text-decoration:none;
                                font-size:16px; font-weight:bold;">
                        Verify Email
                        </a>
                    </td>
                    </tr>
                </table>

                <p style="font-size:14px; line-height:1.6; color:#6b7280;">
                    This verification link will expire in 15 minutes.
                </p>

                <p style="font-size:14px; line-height:1.6; color:#6b7280;">
                    If you didn't create an account, you can safely ignore this email.
                </p>

                <hr style="border:0; border-top:1px solid #e5e7eb; margin:30px 0;">

                <p style="font-size:12px; color:#9ca3af;">
                    © 2026 Your App. All rights reserved.
                </p>

                </td>
            </tr>

            </table>

        </td>
        </tr>
    </table>
    </body>
    </html>
    """


    params:resend.Emails.SendParams= {"from":sender_mail,
              "to":[receiver_mail],
              "subject":"Auth System Email Verification",
              "html":html}

    resend.Emails.send(params=params)
    print("Sending Verification Mail.")

#letting python know data type is Task
sending_verification_mail = cast(Task, _sending_verification_mail)