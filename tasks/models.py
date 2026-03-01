from django.db import models
from employees.models import Employee

class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('on_hold', 'Отложена'),
    ]

    PRIORITY_CHOICES = [
        (1, 'Низкий'),
        (2, 'Средний'),
        (3, 'Высокий'),
    ]

    title = models.CharField('Наименование', max_length=255)
    description = models.TextField('Описание', blank=True)
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Родительская задача',
        related_name='subtasks'
    )
    assignee = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Исполнитель',
        related_name='tasks'
    )
    deadline = models.DateField('Срок выполнения')
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    priority = models.IntegerField('Приоритет', choices=PRIORITY_CHOICES, default=1)

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-priority', 'deadline']

    def __str__(self):
        return self.title