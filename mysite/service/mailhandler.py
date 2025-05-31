import os
from flask import Flask
from flask_mail import Mail, Message

from service.databasehandler import DatabaseHandler

class MailHandler:
    """
    Handles mail operations for the property listings.
    """
    def __init__(self, app: Flask, db_handler: DatabaseHandler):
        self.app = app,
        self.db_handler = db_handler

    def send_email_in_background(
            self,
            token_id: int,
            recipient: str,
            subject: str,
            html_body: str
    ) -> None:
        """
        Send an email in a background thread and update the database with status

        Args:
            token_id: Database ID of the verification token
            recipient: Email address of the recipient
            subject: Email subject line
            html_body: HTML content of the email
        """

        mail = self.__update_config()
        # Create application context since this runs in a separate thread
        with self.app.app_context():
            try:
                # Create the email message
                msg: Message = Message(
                    subject=subject,
                    recipients=[recipient],
                    html=html_body
                )

                # Send the email
                mail.send(msg)

                # Update status in database (success)
                self.db_handler.update_email_status(token_id=token_id, status="sent")

            except Exception as e:
                # Update status in database (failure)
                self.db_handler.update_email_status(
                    token_id=token_id,
                    status="failed",
                    error_message=str(e)
                )
                print(f"Email sending failed: {e}")

    def __update_config(self) -> Mail:
        # Flask-Mail configuration
        self.app.config.update(
            MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.sendgrid.net'),
            MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
            MAIL_USE_TLS=True,
            MAIL_USERNAME=os.environ.get('MAIL_USERNAME', 'apikey'),  # SendGrid uses 'apikey' as username
            MAIL_PASSWORD=os.environ.get('SENDGRID_API_KEY', ''),
            MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@yourdomain.com')
        )

        return Mail(self.app)


