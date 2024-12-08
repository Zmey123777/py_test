import pytest
from rest_framework.test import APIClient
from model_bakery import baker

from students.models import Course, Student


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(**kwargs):
        return baker.make(Course, **kwargs)
    return factory


@pytest.fixture
def student_factory():
    def factory(**kwargs):
        return baker.make(Student, **kwargs)
    return factory


@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
    # Создаем курс
    course = course_factory(name="Test Course")

    # Делаем GET-запрос на конкретный курс
    url = f"/api/v1/courses/{course.id}/"
    response = api_client.get(url)

    assert response.status_code == 200, "Ожидается код ответа 200 при получении курса"
    data = response.json()
    # Проверяем, что вернулся корректный курс
    assert data["id"] == course.id
    assert data["name"] == "Test Course"


@pytest.mark.django_db
def test_list_courses(api_client, course_factory):
    # Создаем несколько курсов
    course_factory(name="Course 1")
    course_factory(name="Course 2")

    # Получаем список курсов
    url = "/api/v1/courses/"
    response = api_client.get(url)

    assert response.status_code == 200, "Ожидается код ответа 200 при получении списка"
    data = response.json()

    # Проверяем, что вернулись все созданные курсы
    course_names = [c["name"] for c in data]
    assert "Course 1" in course_names
    assert "Course 2" in course_names


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):
    # Создаём 3 курса
    c1 = course_factory(name="Filtered Course 1")
    c2 = course_factory(name="Filtered Course 2")
    c3 = course_factory(name="Filtered Course 3")

    # Фильтруем по ID (например, по id c2)
    url = f"/api/v1/courses/?id={c2.id}"
    response = api_client.get(url)

    assert response.status_code == 200, "Ожидается код ответа 200 при фильтрации по ID"
    data = response.json()

    # Должен вернуться только курс с c2.id
    assert len(data) == 1
    assert data[0]["id"] == c2.id


@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):
    # Создаем курсы
    course_factory(name="DjangoBasics")
    course_factory(name="PythonAdvanced")

    # Предполагаем точный фильтр по имени
    url = "/api/v1/courses/?name=DjangoBasics"
    response = api_client.get(url)

    assert response.status_code == 200, "Ожидается код ответа 200 при фильтрации по имени"
    data = response.json()

    # Должен вернуться только курс "DjangoBasics"
    assert len(data) == 1
    assert data[0]["name"] == "DjangoBasics"


@pytest.mark.django_db
def test_create_course(api_client):
    # Создаем курс через POST запрос
    url = "/api/v1/courses/"
    payload = {
        "name": "NewCourse"
    }
    response = api_client.post(url, payload, format='json')

    assert response.status_code == 201, "Ожидается код ответа 201 при создании курса"
    data = response.json()
    assert data["name"] == "NewCourse"
    assert "id" in data
    # Проверяем, что курс создан в БД
    assert Course.objects.filter(id=data["id"]).exists()


@pytest.mark.django_db
def test_update_course(api_client, course_factory):
    # Создаем курс через фабрику
    course = course_factory(name="OldName")

    # Обновляем курс через PATCH
    url = f"/api/v1/courses/{course.id}/"
    payload = {
        "name": "UpdatedName"
    }
    response = api_client.patch(url, payload, format='json')

    assert response.status_code == 200, "Ожидается код ответа 200 при обновлении курса"
    data = response.json()
    assert data["name"] == "UpdatedName"

    # Проверяем обновление в БД
    course.refresh_from_db()
    assert course.name == "UpdatedName"


@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
    # Создаем курс
    course = course_factory(name="ToBeDeleted")
    url = f"/api/v1/courses/{course.id}/"

    # Удаляем курс
    response = api_client.delete(url)

    assert response.status_code == 204, "Ожидается код ответа 204 при удалении курса"
    # Проверяем, что курс удален из базы
    assert not Course.objects.filter(id=course.id).exists()