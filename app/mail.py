"""Module for sending messages via email."""

from email.message import EmailMessage
from os import environ, path

import jinja2

from . import config, const, paths

_TEMPLATE_DIR = path.join(paths.TEMPLATES, 'mail')
_JINJA_ENV = jinja2.Environment(
    loader = jinja2.FileSystemLoader(_TEMPLATE_DIR),
)


def _send(message: EmailMessage):
    """Reads host and account info for an SMTP server from
    environmental variables and uses them to send an email."""
    import smtplib

    HOST = environ.get(const.env.MAILSERVER)
    PORT = environ.get(const.env.MAILPORT, 587)
    USERNAME = environ.get(const.env.MAILUSER, '')
    PASSWORD = environ.get(const.env.MAILPASSWORD, '')
    with smtplib.SMTP(HOST, PORT) as server:
        server.ehlo()

        server.starttls()
        server.ehlo()

        if USERNAME or PASSWORD:
            server.login(USERNAME, PASSWORD)
        
        server.send_message(message)

def send_confirmation(recipient: str, data: dict = {}, config: dict = config.fetch(), filelist: list[str] = []):
    """Sends an acknowledgement of a form submission via email."""
    msg = EmailMessage()
    mailconfig = config[const.conf.keys.FORM][const.conf.keys.CONFIRM_MAIL]

    template = _JINJA_ENV.get_template('confirmation.j2')
    content = template.render(
        data = data,
        keys = const.conf.keys,
        cert = config[const.conf.keys.CERT],
        contact = config[const.conf.keys.CONTACT],
        filelist = filelist,
    )

    msg.set_content(content)
    msg['From'] = mailconfig[const.conf.keys.FROM]
    msg['To'] = recipient
    if mailconfig[const.conf.keys.CC]:
        msg['CC'] = mailconfig[const.conf.keys.CC]
    msg['Subject'] = const.form.MAIL_SUBJECT

    _send(msg)

def available() -> bool:
    """Confirms whether settings allow sending emails."""
    return bool(environ.get(const.env.MAILSERVER))
