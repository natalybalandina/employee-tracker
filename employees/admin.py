from django.contrib import admin
from employees.models import Employee

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'position', 'email', 'is_active', 'hire_date']
    list_filter = ['position', 'is_active']
    search_fields = ['full_name', 'email']
    list_editable = ['is_active']