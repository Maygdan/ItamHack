from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, time
from django.utils import timezone

class LoginCode(models.Model):
    code = models.CharField(max_length=8, unique=True)
    telegram_id = models.CharField(max_length=50)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

class UserProfile(models.Model):
    LEVEL_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Продолжающий'),
        ('experienced', 'Опытный'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_telegram_user = models.BooleanField(default=False)

    # Данные для Telegram пользователей
    telegram_id = models.CharField(max_length=50, blank=True, null=True)

    # Профильные данные
    display_name = models.CharField(max_length=100, blank=True, verbose_name='Отображаемое имя')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, verbose_name='О себе')
    skills = models.TextField(blank=True, verbose_name='Стек технологий')
    experience_months = models.IntegerField(default=0, verbose_name='Опыт в месяцах')
    level = models.CharField(
        max_length=20,
        choices=LEVEL_CHOICES,
        default='beginner',
        verbose_name='Уровень'
    )
    hackathons_participated = models.IntegerField(default=0, verbose_name='Количество участий в хакатонах')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return f'Профиль {self.user.username}'

    def get_experience_years(self):
        """Возвращает опыт в годах и месяцах"""
        years = self.experience_months // 12
        months = self.experience_months % 12
        return years, months

    def update_level(self):
        """Обновляет уровень на основе количества участий в хакатонах"""
        if self.hackathons_participated >= 10:
            self.level = 'experienced'
        elif self.hackathons_participated >= 5:
            self.level = 'intermediate'
        else:
            self.level = 'beginner'
        self.save()

class Hackathon(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Легкий'),
        ('medium', 'Средний'),
        ('hard', 'Сложный'),
    ]

    CATEGORY_CHOICES = [
        ('it', 'IT'),
        ('robotics', 'Робототехника'),
        ('design', 'Дизайн'),
        ('other', 'Другое'),
    ]

    name = models.CharField(max_length=200, verbose_name='Название')
    start_date = models.DateField(verbose_name='Дата начала')
    start_time = models.TimeField(default=time(10, 0), verbose_name='Время начала')
    end_date = models.DateField(verbose_name='Дата окончания')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='it',
        verbose_name='Категория'
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='medium',
        verbose_name='Сложность'
    )
    max_teams = models.IntegerField(default=10, verbose_name='Максимальное количество команд')
    registered_teams = models.IntegerField(default=0, verbose_name='Количество зарегистрированных команд')
    required_roles = models.JSONField(
        default=list,
        verbose_name='Требуемые роли',
        help_text='Список требуемых ролей, например: ["frontender", "backender", "designer"]'
    )

    class Meta:
        verbose_name = 'Хакатон'
        verbose_name_plural = 'Хакатоны'
        ordering = ['start_date']

    def __str__(self):
        return self.name
