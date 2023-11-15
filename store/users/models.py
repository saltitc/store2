from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.core.validators import RegexValidator
from django.db import models
from django.urls import reverse
from django.utils.timezone import now


class User(AbstractUser):
    MALE = "M"
    FEMALE = "F"

    GENDER_CHOICES = [
        (MALE, "Мужской"),
        (FEMALE, "Женский"),
    ]

    phone = models.CharField(
        max_length=15,
        null=True,
        verbose_name="Телефон",
        validators=[
            RegexValidator(
                regex=r"\b\+?[7,8](\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2})\b",
                message="Неверный формат номера телефона.",
            )
        ],
    )
    image = models.ImageField(upload_to="users_images", null=True, blank=True)
    gender = models.CharField(max_length=2, verbose_name="Пол", choices=GENDER_CHOICES, default=MALE)
    is_verified_email = models.BooleanField(default=False)
    email = models.EmailField(
        unique=True,
        verbose_name="Эл. почта",
        error_messages={
            "unique": "Аккаунт с данной электронной почтой уже существует.",
        },
    )

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f"Подтверждение почты для пользователя {self.user.email}"

    def send_verification_email(self):
        # generates a verification link
        link = reverse(
            "users:email_verification",
            kwargs={"email": self.user.email, "code": self.code},
        )
        verification_link = f"{settings.DOMAIN_NAME}{link}"

        subject = f"Подтверждение учетной записи для {self.user.username}"
        message = f"Для подтверждения учетной записи для {self.user.email} перейдите по ссылке {verification_link}"
        # send email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return now() >= self.expiration
