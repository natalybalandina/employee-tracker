from rest_framework import serializers
from tasks.models import Task
from employees.serializers import EmployeeSerializer


class TaskSerializer(serializers.ModelSerializer):
    assignee_detail = EmployeeSerializer(source='assignee', read_only=True)
    parent_task_title = serializers.CharField(source='parent_task.title', read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'parent_task', 'parent_task_title',
                  'assignee', 'assignee_detail', 'deadline', 'status',
                  'priority', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def validate_deadline(self, value):
        from django.utils import timezone
        if value < timezone.now().date():
            raise serializers.ValidationError("Срок выполнения не может быть в прошлом")
        return value
