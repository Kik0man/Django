from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from mailing.models import Mailing, MailingAttempt


class Command(BaseCommand):
    help = 'Отправить рассылку по ID'

    def add_arguments(self, parser):
        parser.add_argument('mailing_id', type=int, help='ID рассылки')

    def handle(self, *args, **options):
        mailing_id = options['mailing_id']
        try:
            mailing = Mailing.objects.get(pk=mailing_id)
        except Mailing.DoesNotExist:
            self.stderr.write(self.style.ERROR(f'Рассылка с ID {mailing_id} не найдена.'))
            return

        if not mailing.can_send():
            self.stdout.write(self.style.WARNING('Рассылка не может быть отправлена (неверный статус или время).'))
            return

        success_count = 0
        fail_count = 0
        for recipient in mailing.recipients.all():
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                )
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='success',
                    server_response='OK'
                )
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f'Отправлено: {recipient.email}'))
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status='failed',
                    server_response=str(e)
                )
                fail_count += 1
                self.stderr.write(self.style.ERROR(f'Ошибка отправки {recipient.email}: {e}'))

        self.stdout.write(self.style.SUCCESS(
            f'Рассылка завершена. Успешно: {success_count}, ошибок: {fail_count}.'
        ))