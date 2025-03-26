import pytest
import CONST as C
import datetime
import json
from django.urls import reverse_lazy

from authentication.models import User
from api.models import Project


@pytest.fixture
def user_data():
    return {
        'username': C.username,
        'password1': C.password,
        'password2': C.password,
        'birthday': C.birthday,
        'can_be_contacted': C.can_be_contacted,
        'can_data_be_shared': C.can_data_be_shared,
    }


def birthday_formated(birthday=C.birthday):
    return birthday.strftime('%Y-%m-%d')


def token_obtain():
    tokens = C.client.post(
        f"{C.user_url}login/",
        {
            'username': C.username,
            'password': C.password,
        }
    )
    return tokens.json()['access']


def format_datetime(value):
    return (value + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.%f+01:00')


def get_project_list(projects):
    return [
        {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'date_created': format_datetime(project.date_created),
            'author': {
                'id': project.author.id,
                'username': project.author.username
            },
            'project_type': project.project_type
        } for project in projects
    ]


@pytest.mark.django_db
def test_project_add(user_data):
    user_response = C.client.post(C.user_url, user_data)
    assert user_response.status_code == 201
    project_response = C.client.post(
        f'{C.api_url}project/',
        data={
            'title': 'test',
            'description': 'test',
            'project_type': 'Android'
        },
    )
    assert project_response.status_code == 401
    project_response = C.client.post(
        f'{C.api_url}project/',
        data={
            'title': 'test',
            'description': 'test',
            'project_type': 'Android'
        },
        headers={'Authorization': f'Bearer {token_obtain()}'}
    )
    assert project_response.status_code == 201


@pytest.mark.django_db
def test_project_update(user_data):
    test_project_add(user_data)
    url = reverse_lazy('project-list')
    token = token_obtain()
    response = C.client.get(url, headers={'Authorization': f'Bearer {token}'})
    project_id = response.json()['results'][0]['id']
    response_update = C.client.patch(
        f'{C.api_url}project/{project_id}/',
        data=json.dumps({'description': 'changement de description'}),
        headers={
            'content-type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    )
    assert response.status_code == 200
    expected_response = {
        'id': response.json()['results'][0]['id'],
        'title': response.json()['results'][0]['title'],
        'description': 'changement de description',
        'author': response.json()['results'][0]['author'],
        'project_type': response.json()['results'][0]['project_type'],
        'date_created': response.json()['results'][0]['date_created'],
    }
    assert response_update.json() == expected_response


@pytest.mark.django_db
def test_project_list(user_data):
    user_response = C.client.post(C.user_url, user_data)
    user = User.objects.get(pk=user_response.json()['id'])
    projects = []
    projects.append(
        Project.objects.create(
            title='Projet 1',
            description='Description du projet 1',
            author=user,
            project_type="front-end",
        )
    )
    projects.append(
        Project.objects.create(
            title='Projet 2',
            description='Description du projet 2',
            author=user,
            project_type="back-end",
        )
    )
    projects.append(
        Project.objects.create(
            title='Projet 3',
            description='Description du projet 3',
            author=user,
            project_type="iOS",
        )
    )
    projects.append(
        Project.objects.create(
            title='Projet 4',
            description='Description du projet 4',
            author=user,
            project_type="Android",
        )
    )
    url = reverse_lazy('project-list')
    response = C.client.get(url)
    assert response.status_code == 401
    response = C.client.get(url, headers={'Authorization': f'Bearer {token_obtain()}'})
    assert response.status_code == 200
    assert response.json()['results'] == get_project_list(projects)


@pytest.mark.django_db
def test_project_detail(user_data):
    user_response = C.client.post(C.user_url, user_data)
    user = User.objects.get(pk=user_response.json()['id'])
    projects = []
    projects.append(
        Project.objects.create(
            title='Projet 1',
            description='Description du projet 1',
            author=user,
            project_type="front-end",
        )
    )
    response = C.client.get(f'{C.api_url}project/1/', headers={'Authorization': f'Bearer {token_obtain()}'})
    assert response.status_code == 200
    expected_response = {
        'id': response.json()['id'],
        'title': response.json()['title'],
        'description': response.json()['description'],
        'author': response.json()['author'],
        'project_type': response.json()['project_type'],
        'date_created': response.json()['date_created'],
        'issues': [],
        'contributors': [],
    }
    assert response.json() == expected_response
