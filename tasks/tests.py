from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from tasks.models import Task
from employees.models import Employee


class TaskModelTest(TestCase):
    """Тесты для модели Task"""

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="developer",
            email="ivan@example.com"
        )
        self.task = Task.objects.create(
            title="Тестовая задача",
            description="Описание тестовой задачи",
            assignee=self.employee,
            deadline=timezone.now().date() + timedelta(days=7),
            status="new",
            priority=2
        )

    def test_task_creation(self):
        """Тест создания задачи"""
        self.assertEqual(self.task.title, "Тестовая задача")
        self.assertEqual(self.task.status, "new")
        self.assertEqual(self.task.assignee, self.employee)

    def test_task_str(self):
        """Тест строкового представления задачи"""
        self.assertEqual(str(self.task), "Тестовая задача")

    def test_task_with_parent(self):
        """Тест создания задачи с родительской задачей"""
        parent_task = Task.objects.create(
            title="Родительская задача",
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )
        self.task.parent_task = parent_task
        self.task.save()
        self.assertEqual(self.task.parent_task, parent_task)


class TaskAPITest(APITestCase):
    """Базовые тесты API для задач"""

    def setUp(self):
        self.client = APIClient()
        self.employee = Employee.objects.create(
            full_name="Сотрудник",
            position="developer",
            email="employee@example.com"
        )
        self.task_data = {
            "title": "Новая задача",
            "description": "Описание",
            "assignee": self.employee.id,
            "deadline": (timezone.now().date() + timedelta(days=7)).isoformat(),
            "status": "new",
            "priority": 2
        }

    def test_create_task(self):
        """Тест создания задачи через API"""
        response = self.client.post('/api/tasks/', self.task_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

    def test_create_task_with_past_deadline(self):
        """Тест создания задачи с прошедшим сроком (должно быть ошибкой)"""
        invalid_data = self.task_data.copy()
        invalid_data["deadline"] = (timezone.now().date() - timedelta(days=1)).isoformat()
        response = self.client.post('/api/tasks/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_important_tasks_endpoint(self):
        """Базовый тест эндпоинта важных задач"""
        # Создаем родительскую задачу
        parent_task = Task.objects.create(
            title="Родительская задача",
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )

        # Создаем дочернюю задачу в работе
        Task.objects.create(
            title="Дочерняя задача",
            parent_task=parent_task,
            assignee=self.employee,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )

        response = self.client.get('/api/tasks/important/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task'], "Родительская задача")
        self.assertIn(self.employee.full_name, response.data[0]['recommended_employees'])

    def test_important_tasks_recommendations(self):
        """Тест рекомендаций сотрудников для важных задач"""
        # Удаляем сотрудника из setUp, чтобы он не мешал
        Employee.objects.all().delete()

        # Создаем новых сотрудников
        emp_busy = Employee.objects.create(
            full_name="Занятый Сотрудник",
            position="developer",
            email="busy@example.com"
        )
        emp_free = Employee.objects.create(
            full_name="Свободный Сотрудник",
            position="developer",
            email="free@example.com"
        )

        # Создаем задачи для занятого сотрудника (3 задачи)
        for i in range(3):
            Task.objects.create(
                title=f"Задача {i}",
                assignee=emp_busy,
                deadline=timezone.now().date() + timedelta(days=7),
                status="in_progress"
            )

        # Создаем родительскую задачу (не в работе)
        parent = Task.objects.create(
            title="Важная родительская",
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )

        # Создаем дочернюю задачу в работе, зависящую от родительской
        Task.objects.create(
            title="Дочерняя",
            parent_task=parent,
            assignee=emp_busy,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )

        response = self.client.get('/api/tasks/important/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task'], "Важная родительская")

        # Проверяем рекомендации
        recommendations = response.data[0]['recommended_employees']

        # Должен рекомендовать свободного сотрудника
        self.assertIn("Свободный Сотрудник", recommendations)

        # Не должен рекомендовать занятого
        self.assertNotIn("Занятый Сотрудник", recommendations)


class ImportantTasksExtendedTest(APITestCase):
    """Расширенные тесты для эндпоинта важных задач"""

    def setUp(self):
        self.client = APIClient()

        # Создаем сотрудников
        self.emp_busy = Employee.objects.create(
            full_name="Занятый Сотрудник",
            position="developer",
            email="busy@example.com"
        )
        self.emp_free = Employee.objects.create(
            full_name="Свободный Сотрудник",
            position="developer",
            email="free@example.com"
        )
        self.emp_moderate = Employee.objects.create(
            full_name="Умеренно Занятый",
            position="developer",
            email="moderate@example.com"
        )

        # Загружаем занятого сотрудника (3 задачи)
        for i in range(3):
            Task.objects.create(
                title=f"Активная задача {i}",
                assignee=self.emp_busy,
                deadline=timezone.now().date() + timedelta(days=7),
                status="in_progress"
            )

        # Загружаем умеренно занятого (2 задачи)
        for i in range(2):
            Task.objects.create(
                title=f"Задача {i}",
                assignee=self.emp_moderate,
                deadline=timezone.now().date() + timedelta(days=7),
                status="in_progress"
            )

    def test_important_task_with_parent_assignee_not_overloaded(self):
        """Тест: исполнитель родительской задачи не перегружен (<= least_busy + 2)"""
        # Создаем родительскую задачу (не в работе) с исполнителем
        parent = Task.objects.create(
            title="Родительская задача",
            assignee=self.emp_moderate,  # У этого сотрудника 2 задачи
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )

        # Создаем дочернюю задачу в работе
        Task.objects.create(
            title="Дочерняя задача",
            parent_task=parent,
            assignee=self.emp_busy,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )

        response = self.client.get('/api/tasks/important/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        # Проверяем рекомендации
        recommendations = response.data[0]['recommended_employees']

        # Должен рекомендовать свободного сотрудника
        self.assertIn(self.emp_free.full_name, recommendations)

        # Рекомендаций не больше 2
        self.assertLessEqual(len(recommendations), 2)

    def test_important_task_with_parent_assignee_overloaded(self):
        """Тест: исполнитель родительской задачи перегружен (> least_busy + 2)"""
        # Создаем родительскую задачу (не в работе) с перегруженным исполнителем
        parent = Task.objects.create(
            title="Родительская задача",
            assignee=self.emp_busy,  # У этого сотрудника 3 задачи
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )

        # Создаем дочернюю задачу в работе
        Task.objects.create(
            title="Дочерняя задача",
            parent_task=parent,
            assignee=self.emp_moderate,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )

        response = self.client.get('/api/tasks/important/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        recommendations = response.data[0]['recommended_employees']

        # Не должен рекомендовать перегруженного исполнителя
        self.assertNotIn(self.emp_busy.full_name, recommendations)
        # Должен рекомендовать свободного
        self.assertIn(self.emp_free.full_name, recommendations)

    def test_important_task_no_recommendations(self):
        """Тест: нет подходящих сотрудников"""
        # Делаем всех сотрудников неактивными
        Employee.objects.all().update(is_active=False)

        # Создаем родительскую задачу
        parent = Task.objects.create(
            title="Родительская задача",
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )

        # Создаем дочернюю задачу в работе
        Task.objects.create(
            title="Дочерняя задача",
            parent_task=parent,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )

        response = self.client.get('/api/tasks/important/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        # Должен вернуть пустой список рекомендаций
        self.assertEqual(len(response.data[0]['recommended_employees']), 0)

    def test_important_task_filtering(self):
        """Тест: правильная фильтрация задач"""
        # Создаем задачи, которые НЕ должны попасть в важные
        Task.objects.create(
            title="Обычная задача",
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"  # Нет дочерних в работе
        )

        Task.objects.create(
            title="Задача в работе",
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"  # Уже в работе
        )

        # Создаем важную задачу
        parent = Task.objects.create(
            title="Важная задача",
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )

        Task.objects.create(
            title="Дочерняя в работе",
            parent_task=parent,
            assignee=self.emp_free,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )

        response = self.client.get('/api/tasks/important/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task'], "Важная задача")

    def test_important_task_deadline_format(self):
        """Тест: проверка формата даты в ответе"""
        deadline = timezone.now().date() + timedelta(days=10)

        parent = Task.objects.create(
            title="Задача с дедлайном",
            deadline=deadline,
            status="new"
        )

        Task.objects.create(
            title="Дочерняя",
            parent_task=parent,
            assignee=self.emp_free,
            deadline=deadline + timedelta(days=5),
            status="in_progress"
        )

        response = self.client.get('/api/tasks/important/')
        self.assertEqual(response.status_code, 200)

        # Преобразуем дату в строку для сравнения
        response_deadline = str(response.data[0]['deadline'])
        expected_date = deadline.isoformat()
        self.assertEqual(response_deadline, expected_date)

    def test_important_task_multiple_children(self):
        """Тест: несколько дочерних задач от одной родительской"""
        parent = Task.objects.create(
            title="Родительская",
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )

        # Создаем две дочерние задачи в работе
        Task.objects.create(
            title="Дочерняя 1",
            parent_task=parent,
            assignee=self.emp_free,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )

        Task.objects.create(
            title="Дочерняя 2",
            parent_task=parent,
            assignee=self.emp_free,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )

        response = self.client.get('/api/tasks/important/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)  # Родительская должна быть только один раз
        self.assertEqual(response.data[0]['task'], "Родительская")
