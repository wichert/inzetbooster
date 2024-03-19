from email.message import EmailMessage
from email.utils import make_msgid, formataddr
import smtplib


class Mailer:
    server: smtplib.SMTP
    from_address: str
    from_name: str | None

    def __init__(
        self,
        *,
        smtp_server: str,
        from_address: str,
        smtp_use_ssl: bool = False,
        smtp_port: int = 0,
        smtp_user: str | None = None,
        smtp_password: str | None = None,
        from_name: str | None = None,
    ):
        self.from_address = from_address
        self.from_name = from_name
        if smtp_use_ssl:
            self.smtp = smtplib.SMTP_SSL(host=smtp_server, port=smtp_port, timeout=5)
        else:
            self.smtp = smtplib.SMTP(host=smtp_server, port=smtp_port, timeout=5)
        if smtp_user and smtp_password:
            self.smtp.login(smtp_user, smtp_password)

    def send(self, to_addr: str, to_name: str, subject: str, html: str) -> str:
        message = EmailMessage()
        message["From"] = formataddr((self.from_name, self.from_address))
        message["To"] = formataddr((to_name, to_addr))
        message["Subject"] = subject
        msg_id = make_msgid()
        message["Message-Id"] = msg_id
        message.set_content(html, subtype="html")
        self.smtp.send_message(message, from_addr=self.from_address, to_addrs=[to_addr])
        return msg_id
