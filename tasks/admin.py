from django.contrib import admin
from .models import Task

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'assignee', 'status', 'priority', 'deadline']
    list_filter = ['status', 'priority']
    search_fields = ['title', 'description']
    list_editable = ['status', 'priority']
    raw_id_fields = ['assignee', 'parent_task']
    date_hierarchy = 'deadline'