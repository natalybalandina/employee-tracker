from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from employees.models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        queryset = Employee.objects.all()
        is_active = self.request.query_params.get('is_active', None)

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        return queryset

    @action(detail=False, methods=['get'])
    def busy(self, request):
        """Список сотрудников, отсортированный по количеству активных задач"""
        employees = Employee.objects.filter(is_active=True).annotate(
            active_tasks_count=Count(
                'tasks',
                filter=Q(tasks__status__in=['new', 'in_progress'])
            )
        ).order_by('-active_tasks_count')

        serializer = self.get_serializer(employees, many=True)
        return Response(serializer.data)
