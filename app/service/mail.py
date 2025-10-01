from fastapi import Request
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate

from app.config import (
    SMTP_LOGIN,
    SMTP_PORT,
    SMTP_EMAIL,
    SMTP_SERVER,
    SMTP_ENABLED,
    SMTP_PASSWORD,
)

from app.exception.database import RecordNotFound
import app.service.user as user_service

from app.template.init import jinja
from app.model.user import User, UserPasswordResetToken
from app.model.report import Report, ReportExtended
from app.exception.service import (
    SMTPCredentialsNotSet,
    SendingEmailFailed,
    Unauthorized,
)


def notify_user_created(new_user: User, request: Request, current_user: User) -> bool:

    if not current_user.can_send_emails:
        raise Unauthorized(msg="You cannot send e-mails")

    username = new_user.username
    email = new_user.email

    subject = f"Hello {username}, welcome to BAT App!"

    context = {
        "username": username,
        "website_url": request.base_url,
        "url_for": request.url_for,
    }

    template = jinja.env.get_template("email/new-user.html")
    content = template.render(context)

    try:
        send_html_email(recipient_email=email, subject=subject, html_message=content)
        return True
    except Exception as e:
        # NotImplemented
        raise e

    return False


def send_password_reset(token_object: UserPasswordResetToken, request: Request) -> bool:

    subject = "Set you new password"

    context = {"token_object": token_object, "url_for": request.url_for}

    print("again stuck on template?")
    template = jinja.env.get_template("email/set-password.html")
    print("no we got stuck on render:")
    content = template.render(context)

    print("sending mail?")
    send_html_email(
        recipient_email=token_object.email, subject=subject, html_message=content
    )

    return True


def notify_report_published(
    report: ReportExtended, request: Request, current_user: User
) -> bool:

    if not current_user.can_send_emails:
        raise Unauthorized(msg="You cannot send e-mails")

    if type(report.assessment_owner) == str:
        report_owner = user_service.get_by_username(
            username=report.assessment_owner, current_user=current_user
        )
    else:
        raise RecordNotFound(msg="Report owner seems not to exist. Maybe deleted user?")

    context = {
        "username": report_owner.username,
        "report_name": report.report_name,
        "website_url": request.base_url,
    }

    template = jinja.env.get_template("email/report-published.html")
    content = template.render(context)

    context = {
        "username": report_owner.username,
        "report_name": report.report_name,
        "website_url": request.base_url,
    }

    send_html_email(
        recipient_email=report_owner.email,
        subject="New report is now accessible.",
        html_message=content,
    )

    send_html_email(
        recipient_email=current_user.email,
        subject="COPY: New report is now accessible.",
        html_message=content,
    )

    return False


def send_html_email(recipient_email: str, subject: str, html_message: str) -> bool:
    """
    Sends an HTML-encoded email through SMTP using predefined constants.

    Parameters:
    - recipient_email: The email address of the recipient.
    - subject: The subject of the email.
    - html_message: The HTML content of the email.

    Returns:
    - True if the email was sent successfully, False otherwise.
    """

    if not SMTP_ENABLED:
        raise SMTPCredentialsNotSet(
            msg="SMTP credentials are not set. You need to notify user manually."
        )

    try:
        # Create the MIMEMultipart message object
        msg = MIMEMultipart()
        msg["From"] = f"BAT App <{SMTP_EMAIL}>"
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)

        # Attach the HTML message to the email
        msg.attach(MIMEText(html_message, "html"))

        # Connect to the SMTP server using SSL
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)  # Log in to the SMTP server
            server.sendmail(
                SMTP_EMAIL, recipient_email, msg.as_string()
            )  # Send the email

        return True

    except Exception as e:
        print(f"Failed to send email: {e}")
        raise SendingEmailFailed(msg=str(e))
