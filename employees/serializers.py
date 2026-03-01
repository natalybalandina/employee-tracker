from rest_framework import serializers
from rest_framework import serializers
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    active_tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position', 'email', 'phone',
                  'hire_date', 'is_active', 'active_tasks_count']
        read_only_fields = ['hire_date']

    def validate_email(self, value):
        """Проверка уникальности email при создании и обновлении"""
        if self.instance:
            # При обновлении исключаем текущий экземпляр из проверки
            if Employee.objects.filter(email=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Сотрудник с таким email уже существует.")
        else:
            # При создании проверяем уникальность
            if Employee.objects.filter(email=value).exists():
                raise serializers.ValidationError("Сотрудник с таким email уже существует.")
        return value
