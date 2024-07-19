import pytest
import json
from model_bakery import baker
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from students.models import Course, Student



# def test_example():
#     assert False, "Just test example"



@pytest.fixture
def api_client():
    return APIClient()



@pytest.fixture
def student_factory():
    def create_student(**kwargs):
        return baker.make(Student, **kwargs)
    return create_student


@pytest.fixture
def course_factory():
    def create_course(**kwargs):
        return baker.make(Course, **kwargs)
    return create_course



#проверка получения первого курса (retrieve-логика):

@pytest.mark.django_db
def test_retrieve_course(api_client, course_factory):
     # Создаем курс через фабрику
    course = course_factory()
    # Строим URL для получения курса
    url = reverse('courses-detail', kwargs={'pk': course.pk})
    # Делаем запрос к API
    response = api_client.get(url)
    # Проверяем, что код ответа равен 200
    assert response.status_code == status.HTTP_200_OK
    # Проверяем, что полученный курс совпадает с созданным
    assert response.data['id'] == course.id
   
    assert response.data['name'] == course.name

    assert set(response.data.keys()) == {'id', 'name', 'students'}

#проверка получения списка курсов (list-логика):
    
@pytest.mark.django_db
def test_list_courses(api_client, course_factory):

    # Arrange
    courses = course_factory(_quantity=10)

    # # Act
    url = reverse('courses-list')
    response = api_client.get(url)  


    #accert
    assert response.status_code == 200

    assert len(response.data) == 10

    for course_data in response.data:
        assert {'id', 'name', 'students'} == set(course_data.keys())



#проверка фильтрации списка курсов по id
        
@pytest.mark.django_db
def test_filter_courses_by_id(api_client, course_factory):

     # Arrange
    courses = course_factory(_quantity=10)

    # Выбираем произвольный курс из списка для фильтрации
    filter_course_id = courses[2].id


    # Act
    url = reverse('courses-list') + f'?id={filter_course_id}'
    response = api_client.get(url)


    # Assert
    assert response.status_code == 200

    # Проверяем, что в ответе есть только один курс с заданным id
    assert len(response.data) == 1

    # Проверяем, что id этого курса совпадает с заданным id
    assert response.data[0]['id'] == filter_course_id


#проверка фильтрации списка курсов по name
    
@pytest.mark.django_db
def test_filter_courses_by_name(api_client, course_factory):

     # Arrange
    courses = course_factory(_quantity=10)

    # Выбираем произвольный курс из списка для фильтрации
    filter_course_name = courses[2].name


    # Act
    url = reverse('courses-list') + f'?name={filter_course_name}'
    response = api_client.get(url)


    # Assert
    assert response.status_code == 200

    # Проверяем, что в ответе есть только один курс с заданным id
    assert len(response.data) == 1

    # Проверяем, что name этого курса совпадает с заданным name
    assert response.data[0]['name'] == filter_course_name


#тест успешного создания курса
@pytest.mark.django_db
def test_create_course(api_client):

    #Arrange
    course_data = {'name':'name', 'students':'students'}

     # Act
    url = reverse('courses-list')
    response = api_client.post(url, data=json.dumps(course_data), content_type='application/json')
    
    #Accert
    assert response.status_code == status.HTTP_201_CREATED


    assert Course.objects.filter(name=course_data['name']).exists()



#тест успешного обновления курса
    
@pytest.mark.django_db
def test_create_course(api_client, course_factory):
    #arrange

    course = course_factory()

     # Создаем студента для курса
    student = Student.objects.create(name="Test Student")

     # Обновляем данные курса
    updated_course_data = {"name": "Updated Course Name", "students": [student.id]}

    #Act
    url = reverse('courses-detail', kwargs={'pk': course.pk})
    response = api_client.put(url, data=json.dumps(updated_course_data),  content_type='application/json')

     # Assert
    assert response.status_code == status.HTTP_200_OK
    # Перезагрузите экземпляр объекта курса из базы данных, чтобы увидеть обновленные значения

# Перезагружаем экземпляр объекта курса из базы данных, чтобы увидеть обновленные значения
    course.refresh_from_db()
    assert course.name == updated_course_data['name']

   # Получаем список студентов из базы данных для данного курса
    actual_students_names = list(course.students.values_list('name', flat=True))

    # Проверяем, что список студентов не пустой
    assert course.students.exists()


      # Проверяем, что полученные имена студентов совпадают с ожидаемыми именами
    assert actual_students_names == [student.name]




#тест успешного удаления курса.
@pytest.mark.django_db
def test_delete_course(api_client, course_factory):
     # Создаем курс с помощью фабрики
    course = course_factory()

     # Отправляем запрос на удаление курса
    url = reverse('courses-detail', kwargs={'pk': course.pk})
    response = api_client.delete(url)

     # Проверяем успешность запроса
    assert response.status_code == status.HTTP_204_NO_CONTENT

     
    # Проверяем, что курс действительно удален из базы данных
    assert not Course.objects.filter(pk=course.pk).exists()


