from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from tasks.models import Task
from employees.models import Employee
from tasks.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.all()

        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)

        assignee = self.request.query_params.get('assignee', None)
        if assignee:
            queryset = queryset.filter(assignee_id=assignee)

        return queryset.select_related('assignee', 'parent_task')

    @action(detail=False, methods=['get'])
    def important(self, request):
        """Важные задачи: не в работе, но от которых зависят задачи в работе"""
        # Задачи в работе, у которых есть родитель
        tasks_in_progress = Task.objects.filter(
            status='in_progress',
            parent_task__isnull=False
        ).values_list('parent_task_id', flat=True)

        # Важные задачи
        important_tasks = Task.objects.filter(
            Q(status='new') | Q(status='on_hold'),
            id__in=tasks_in_progress
        ).select_related('parent_task')

        result = []
        for task in important_tasks:
            # Наименее загруженный сотрудник
            least_busy = Employee.objects.filter(is_active=True).annotate(
                active_tasks=Count(
                    'tasks',
                    filter=Q(tasks__status__in=['new', 'in_progress'])
                )
            ).order_by('active_tasks').first()

            recommended = []
            if task.parent_task and task.parent_task.assignee:
                parent_assignee = task.parent_task.assignee
                if parent_assignee.is_active:
                    parent_tasks = parent_assignee.tasks.filter(
                        status__in=['new', 'in_progress']
                    ).count()

                    least_busy_count = least_busy.active_tasks if least_busy else 0
                    if parent_tasks <= least_busy_count + 2:
                        recommended.append(parent_assignee.full_name)

            if least_busy and least_busy.full_name not in recommended:
                recommended.append(least_busy.full_name)

            result.append({
                'task': task.title,
                'deadline': task.deadline,
                'recommended_employees': recommended[:2]
            })

        return Response(result)