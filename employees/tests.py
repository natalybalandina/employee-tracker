from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from employees.models import Employee
from tasks.models import Task


class EmployeeModelTest(TestCase):
    """Тесты для модели Employee"""

    def setUp(self):
        self.employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="developer",
            email="ivan@example.com",
            phone="+1234567890"
        )

    def test_employee_creation(self):
        """Тест создания сотрудника"""
        self.assertEqual(self.employee.full_name, "Иван Иванов")
        self.assertEqual(self.employee.position, "developer")
        self.assertEqual(self.employee.email, "ivan@example.com")
        self.assertTrue(self.employee.is_active)

    def test_employee_str(self):
        """Тест строкового представления"""
        self.assertEqual(str(self.employee), "Иван Иванов")

    def test_get_active_tasks_count(self):
        """Тест подсчета активных задач"""
        # Создаем задачи с разными статусами
        Task.objects.create(
            title="Активная задача 1",
            assignee=self.employee,
            deadline=timezone.now().date() + timedelta(days=7),
            status="in_progress"
        )
        Task.objects.create(
            title="Активная задача 2",
            assignee=self.employee,
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )
        Task.objects.create(
            title="Завершенная задача",
            assignee=self.employee,
            deadline=timezone.now().date() + timedelta(days=7),
            status="completed"
        )

        self.assertEqual(self.employee.get_active_tasks_count(), 2)

    def test_employee_without_tasks(self):
        """Тест сотрудника без задач"""
        self.assertEqual(self.employee.get_active_tasks_count(), 0)


class EmployeeAPITest(APITestCase):
    """Тесты API для сотрудников"""

    def setUp(self):
        self.client = APIClient()
        self.employee_data = {
            "full_name": "Петр Петров",
            "position": "manager",
            "email": "petr@example.com",
            "phone": "+9876543210"
        }
        self.employee = Employee.objects.create(**self.employee_data)

    def test_create_employee(self):
        """Тест создания сотрудника через API"""
        new_employee = {
            "full_name": "Новый Сотрудник",
            "position": "developer",
            "email": "new@example.com",
            "phone": "+1111111111"
        }
        response = self.client.post('/api/employees/', new_employee, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)
        self.assertEqual(Employee.objects.get(email="new@example.com").full_name, "Новый Сотрудник")

    def test_get_employees_list(self):
        """Тест получения списка сотрудников"""
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_employee_detail(self):
        """Тест получения конкретного сотрудника"""
        response = self.client.get(f'/api/employees/{self.employee.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], self.employee.full_name)

    def test_update_employee(self):
        """Тест обновления сотрудника"""
        updated_data = {
            "full_name": "Петр Петров Обновленный",
            "position": "senior_manager",
            "email": "petr_updated@example.com",  # Новый уникальный email
            "phone": "+9999999999"
        }
        response = self.client.put(
            f'/api/employees/{self.employee.id}/',
            updated_data,
            format='json'
        )

        # Если получаем 400, выведем ошибки для отладки
        if response.status_code == 400:
            print("\nОшибки валидации:", response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.full_name, "Петр Петров Обновленный")
        self.assertEqual(self.employee.position, "senior_manager")
        self.assertEqual(self.employee.email, "petr_updated@example.com")


def test_update_employee_with_same_email(self):
    """Тест обновления сотрудника с тем же email (должно работать)"""
    updated_data = {
        "full_name": "Петр Петров Обновленный",
        "position": "senior_manager",
        "email": "petr@example.com",  # Тот же email
        "phone": "+9999999999"
    }
    response = self.client.put(
        f'/api/employees/{self.employee.id}/',
        updated_data,
        format='json'
    )


# Если получаем 400, выведем ошибки для отладки
    if response.status_code == 400:
        print("\nОшибки валидации:", response.data)

    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.employee.refresh_from_db()
    self.assertEqual(self.employee.full_name, "Петр Петров Обновленный")
    self.assertEqual(self.employee.email, "petr@example.com")  # Email не изменился


def test_update_employee_with_existing_email(self):
    """Тест обновления с email, который уже занят другим сотрудником (должно быть ошибкой)"""
    # Создаем другого сотрудника
    other_employee = Employee.objects.create(
        full_name="Другой Сотрудник",
        position="developer",
        email="other@example.com",
        phone="+1111111111"
    )

    # Пытаемся обновить первого сотрудника, используя email второго
    updated_data = {
        "full_name": "Петр Петров",
        "position": "manager",
        "email": "other@example.com",  # Email другого сотрудника
        "phone": "+9876543210"
    }
    response = self.client.put(
        f'/api/employees/{self.employee.id}/',
        updated_data,
        format='json'
    )
    self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


def test_partial_update_employee(self):
    """Тест частичного обновления сотрудника"""
    response = self.client.patch(
        f'/api/employees/{self.employee.id}/',
        {'phone': '+7777777777'},
        format='json'
    )
    self.assertEqual(response.status_code, status.HTTP_200_OK)
    self.employee.refresh_from_db()
    self.assertEqual(self.employee.phone, '+7777777777')


def test_delete_employee(self):
    """Тест удаления сотрудника"""
    response = self.client.delete(f'/api/employees/{self.employee.id}/')
    self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
    self.assertEqual(Employee.objects.count(), 0)


def test_filter_employees_by_active(self):
    """Тест фильтрации сотрудников по статусу"""
    # Создаем неактивного сотрудника
    Employee.objects.create(
        full_name="Неактивный",
        position="tester",
        email="inactive@example.com",
        is_active=False
    )

    # Фильтр по активным
    response = self.client.get('/api/employees/?is_active=true')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['full_name'], "Петр Петров")

    # Фильтр по неактивным
    response = self.client.get('/api/employees/?is_active=false')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 1)
    self.assertEqual(response.data[0]['full_name'], "Неактивный")

    # Без фильтра - все сотрудники
    response = self.client.get('/api/employees/')
    self.assertEqual(response.status_code, 200)
    self.assertEqual(len(response.data), 2)


class EmployeeBusyEndpointTest(APITestCase):
    """Тесты для эндпоинта занятых сотрудников"""

    def setUp(self):
        self.client = APIClient()

        # Создаем сотрудников
        self.emp1 = Employee.objects.create(
            full_name="Активный 1",
            position="developer",
            email="active1@example.com"
        )
        self.emp2 = Employee.objects.create(
            full_name="Активный 2",
            position="developer",
            email="active2@example.com"
        )
        self.emp3 = Employee.objects.create(
            full_name="Неактивный",
            position="manager",
            email="inactive@example.com",
            is_active=False
        )

        # Создаем задачи с разными статусами
        # Для emp1 - 3 активных задачи
        for i in range(3):
            Task.objects.create(
                title=f"Задача {i} для emp1",
                assignee=self.emp1,
                deadline=timezone.now().date() + timedelta(days=7),
                status="in_progress"
            )

        # Для emp2 - 1 активная задача
        Task.objects.create(
            title="Задача для emp2",
            assignee=self.emp2,
            deadline=timezone.now().date() + timedelta(days=7),
            status="new"
        )

        # Для emp1 еще одна завершенная задача (не активная)
        Task.objects.create(
            title="Завершенная задача",
            assignee=self.emp1,
            deadline=timezone.now().date() + timedelta(days=7),
            status="completed"
        )

    def test_busy_endpoint_ordering(self):
        """Тест сортировки сотрудников по загруженности"""
        response = self.client.get('/api/employees/busy/')
        self.assertEqual(response.status_code, 200)

        # Должны быть только активные сотрудники
        self.assertEqual(len(response.data), 2)

        # Первый должен быть emp1 (3 задачи), второй emp2 (1 задача)
        self.assertEqual(response.data[0]['full_name'], "Активный 1")
        self.assertEqual(response.data[0]['active_tasks_count'], 3)
        self.assertEqual(response.data[1]['full_name'], "Активный 2")
        self.assertEqual(response.data[1]['active_tasks_count'], 1)

    def test_busy_endpoint_with_no_active_employees(self):
        """Тест когда нет активных сотрудников"""
        Employee.objects.all().update(is_active=False)

        response = self.client.get('/api/employees/busy/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)

    def test_busy_endpoint_with_no_tasks(self):
        """Тест когда у сотрудников нет задач"""
        Employee.objects.all().delete()
        emp = Employee.objects.create(
            full_name="Новый",
            position="developer",
            email="new@example.com"
        )

        response = self.client.get('/api/employees/busy/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['active_tasks_count'], 0)


class EmployeeValidationTest(APITestCase):
    """Тесты валидации данных сотрудников"""

    def setUp(self):
        self.client = APIClient()
        self.valid_data = {
            "full_name": "Тестовый Сотрудник",
            "position": "developer",
            "email": "test@example.com",
            "phone": "+1234567890"
        }

    def test_create_employee_without_required_fields(self):
        """Тест создания без обязательных полей"""
        # Без full_name
        invalid_data = self.valid_data.copy()
        del invalid_data['full_name']
        response = self.client.post('/api/employees/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Без email
        invalid_data = self.valid_data.copy()
        del invalid_data['email']
        response = self.client.post('/api/employees/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_with_duplicate_email(self):
        """Тест создания с дублирующимся email"""
        # Создаем первого сотрудника
        self.client.post('/api/employees/', self.valid_data, format='json')

        # Пытаемся создать второго с тем же email
        duplicate_data = self.valid_data.copy()
        duplicate_data['full_name'] = "Другой Сотрудник"
        response = self.client.post('/api/employees/', duplicate_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_with_invalid_email(self):
        """Тест создания с невалидным email"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = "not-an-email"
        response = self.client.post('/api/employees/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_with_long_phone(self):
        """Тест создания с длинным номером телефона (должно быть ошибкой)"""
        invalid_data = self.valid_data.copy()
        # Создаем телефон длиннее 20 символов (ограничение модели)
        invalid_data['phone'] = "+" + "1" * 25  # 26 символов
        response = self.client.post('/api/employees/', invalid_data, format='json')
        # Ожидаем ошибку валидации, так как поле phone имеет max_length=20
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_employee_with_valid_phone(self):
        """Тест создания с корректным номером телефона"""
        valid_data = self.valid_data.copy()
        valid_data['phone'] = "+" + "1" * 15  # 16 символов (меньше 20)
        response = self.client.post('/api/employees/', valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
