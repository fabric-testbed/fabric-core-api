import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from swagger_server.api_logger import consoleLogger
from swagger_server.database.models.people import FabricPeople
from swagger_server.database.models.projects import FabricProjects
from swagger_server.database.models.sshkeys import FabricSshKeys

SMTP_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER'),
    'smtp_port': os.getenv('SMTP_PORT'),
    'smtp_user': os.getenv('SMTP_USER'),
    'smtp_password': os.getenv('SMTP_PASSWORD'),
    'from_email': os.getenv('SMTP_FROM_EMAIL'),
    'reply_to_email': os.getenv('SMTP_REPLY_TO_EMAIL'),
}

"""
Email Template
- {0} = project_info: project_name (project_uuid)
- {1} = people_info: people_name (people_uuid)
- {2} = sshkey_info: sshkey_name (sshkey_uuid)
"""
EMAIL_TEMPLATES = {
    'project_create': {
        'subject': '[FABRIC] Project Created - {0}',
        'body': '{1} has created project: {0}',
    },
    'project_retire': {
        'subject': '[FABRIC] Project Retired - {0}',
        'body': '{1} has retired project: {0}',
    },
    'project_add_member': {
        'subject': '[FABRIC] Project Add Member - {0}',
        'body': '{1} has added you as a member of project: {0}',
    },
    'project_remove_member': {
        'subject': '[FABRIC] Project Remove Member - {0}',
        'body': '{1} has removed you as a member of project: {0}',
    },
    'project_add_owner': {
        'subject': '[FABRIC] Project Add Owner - {0}',
        'body': '{1} has added you as a owner of project: {0}',
    },
    'project_remove_owner': {
        'subject': '[FABRIC] Project Remove Owner - {0}',
        'body': '{1} has removed you as a owner of project: {0}',
    },
    'project_add_tokenholder': {
        'subject': '[FABRIC] Project Add Token Holder - {0}',
        'body': '{1} has added you as a token holder of project: {0}',
    },
    'project_remove_tokenholder': {
        'subject': '[FABRIC] Project Remove Token Holder - {0}',
        'body': '{1} has removed you as a token holder of project: {0}',
    },
    'people_sshkey_expiry_30_day': {
        'subject': '[FABRIC] SSH Key Expiry 30 days notice - {2}',
        'body': '{1} has alerted you to SSH key expiry in 30 days: {2}',
    },
    'people_sshkey_expiry_7_day': {
        'subject': '[FABRIC] SSH Key Expiry 7 days notice - {0}',
        'body': '{1} has alerted you to SSH key expiry in 7 days: {0}',
    },
    'people_sshkey_expiry_1_day': {
        'subject': '[FABRIC] SSH Key Expiry 1 day notice - {0}',
        'body': '{1} has alerted you to SSH key expiry in 1 day: {0}',
    },
}


def core_api_send_email(*, smtp_config: dict, to_email: str, subject: str, body: str):
    """
    Send Email to a user
    :param smtp_config: SMTP config parameters
    :param to_email:    User's email
    :param subject:     Email subject
    :param body         Email body

    :@raise Exception in case of error
    """
    # Create the message container
    msg = MIMEMultipart()
    msg['From'] = smtp_config.get("from_email")
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.add_header('Reply-To', smtp_config.get("reply_to_email"))

    # Attach the message body
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Establish an SMTP connection and send the email
        server = smtplib.SMTP(smtp_config.get("smtp_server"), smtp_config.get("smtp_port"))
        server.connect(smtp_config.get("smtp_server"), smtp_config.get("smtp_port"))
        server.starttls()  # Upgrade to TLS
        server.login(smtp_config.get("smtp_user"), smtp_config.get("smtp_password"))
        server.sendmail(smtp_config.get("from_email"), to_email, msg.as_string())
    except Exception as e:
        consoleLogger.error('core_api_send_email', e)
    finally:
        server.quit()


def send_fabric_email(email_type: str = None, *args, **kwargs):
    email_type = email_type.lower() if email_type else None
    if email_type not in EMAIL_TEMPLATES:
        consoleLogger.error("Invalid email type")
    else:
        to_email = kwargs.get('to_email')
        people_uuid = kwargs.get('people_uuid', None)
        sshkey_uuid = kwargs.get('sshkey_uuid', None)
        project_uuid = kwargs.get('project_uuid', None)
        people_info = None
        if people_uuid:
            if people_uuid == os.getenv('SERVICE_ACCOUNT_UUID'):
                people_info = 'FABRIC Service Account (' + os.getenv('SERVICE_ACCOUNT_UUID') + ')'
            else:
                people_info = FabricPeople.query.filter_by(uuid=people_uuid).first().display_name + ' ({})'.format(
                    people_uuid)
        sshkey_info = None
        if sshkey_uuid:
            sshkey_info = FabricSshKeys.query.filter_by(uuid=sshkey_uuid).first().fabric_key_type + ' ({})'.format(
                sshkey_uuid)
        project_info = None
        if project_uuid:
            project_info = FabricProjects.query.filter_by(uuid=project_uuid).first().name + ' ({})'.format(project_uuid)

        subject = EMAIL_TEMPLATES[email_type]['subject'].format(project_info, people_info, sshkey_info)
        body = EMAIL_TEMPLATES[email_type]['body'].format(project_info, people_info, sshkey_info)

        try:
            core_api_send_email(smtp_config=SMTP_CONFIG, to_email=to_email, subject=subject, body=body)
            consoleLogger.info("Email type: {0}, sent to {1}".format(email_type, to_email))
        except smtplib.SMTPAuthenticationError as e:
            print(e.smtp_code)
            print(e.smtp_error)
