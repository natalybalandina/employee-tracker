from django.db import models

class Employee(models.Model):
    POSITION_CHOICES = [
        ('developer', 'Разработчик'),
        ('designer', 'Дизайнер'),
        ('manager', 'Менеджер'),
        ('senior_manager', 'Старший менеджер'),
        ('analyst', 'Аналитик'),
        ('tester', 'Тестировщик'),
    ]

    full_name = models.CharField('ФИО', max_length=255)
    position = models.CharField('Должность', max_length=50, choices=POSITION_CHOICES)
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=20, blank=True)
    hire_date = models.DateField('Дата найма', auto_now_add=True)
    is_active = models.BooleanField('Активен', default=True)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['full_name']

    def __str__(self):
        return self.full_name

    def get_active_tasks_count(self):
        return self.tasks.filter(status__in=['new', 'in_progress']).count()
