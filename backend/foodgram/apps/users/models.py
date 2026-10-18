from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import CheckConstraint, F, Q, UniqueConstraint


EMAIL_MAX_LENGTH = 254
NAME_MAX_LENGTH = 150


class User(AbstractUser):
    email = models.EmailField(max_length=EMAIL_MAX_LENGTH, unique=True)
    username = models.CharField(
        max_length=NAME_MAX_LENGTH,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+\Z',
                message='Имя пользователя содержит недопустимые символы.',
            )
        ],
    )
    first_name = models.CharField(max_length=NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscriptions'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='subscribers'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

        constraints = (
            UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_author'
            ),
            CheckConstraint(
                condition=~Q(user=F('author')),
                name='prevent_self_subscription'
            ),
        )

    def __str__(self):
        return f'{self.user} подписан/а на {self.author}'
