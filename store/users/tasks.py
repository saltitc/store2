import uuid
from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils.timezone import now

from users.models import EmailVerification

User = get_user_model()


@shared_task
def send_email_verification(user_id):
    user = User.objects.get(id=user_id)
    expiration = now() + timedelta(hours=48)
    record = EmailVerification.objects.create(code=uuid.uuid4(), user=user, expiration=expiration)
    record.send_verification_email()
