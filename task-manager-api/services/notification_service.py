import logging
import smtplib

from config.settings import Settings
from utils.helpers import utcnow

logger = logging.getLogger(__name__)


class NotificationService:
    """Envio de e-mails; as credenciais SMTP vêm da configuração (variáveis de ambiente)."""

    def __init__(self, settings=Settings):
        self.notifications = []
        self.email_host = settings.SMTP_HOST
        self.email_port = settings.SMTP_PORT
        self.email_user = settings.SMTP_USER
        self.email_password = settings.SMTP_PASSWORD

    def send_email(self, to, subject, body):
        if not self.email_host:
            logger.warning('SMTP não configurado; e-mail para %s não enviado', to)
            return False
        try:
            with smtplib.SMTP(self.email_host, self.email_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.sendmail(self.email_user, to, f'Subject: {subject}\n\n{body}')
            logger.info('Email enviado para %s', to)
            return True
        except Exception as exc:
            logger.error('Erro ao enviar email: %s', exc)
            return False

    def notify_task_assigned(self, user, task):
        subject = f'Nova task atribuída: {task.title}'
        body = (
            f"Olá {user.name},\n\nA task '{task.title}' foi atribuída a você.\n\n"
            f'Prioridade: {task.priority}\nStatus: {task.status}'
        )
        self.send_email(user.email, subject, body)
        self.notifications.append({
            'type': 'task_assigned',
            'user_id': user.id,
            'task_id': task.id,
            'timestamp': utcnow(),
        })

    def notify_task_overdue(self, user, task):
        subject = f'Task atrasada: {task.title}'
        body = f"Olá {user.name},\n\nA task '{task.title}' está atrasada!\n\nData limite: {task.due_date}"
        self.send_email(user.email, subject, body)

    def get_notifications(self, user_id):
        return [n for n in self.notifications if n['user_id'] == user_id]
