import pytest
import CONST as C
import datetime
from django.core.exceptions import ValidationError
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


def token_obtain(user):
    tokens = C.client.post(
        f"{C.user_url}login/",
        {
            'username': user['username'],
            'password': C.password,
        }
    )
    return tokens.json()['access']


def format_datetime(value):
    return (value + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.%f+01:00')


@pytest.mark.django_db
def contributor_add_to_project(user_data):
    user1_response = C.client.post(C.user_url, user_data)
    data = user_data.copy()
    data['username'] = 'user2'
    user2_response = C.client.post(C.user_url, data)
    user1 = User.objects.get(pk=user1_response.json()['id'])
    user2 = User.objects.get(pk=user2_response.json()['id'])
    project_response = C.client.post(
        f'{C.api_url}project/',
        data={
            'title': 'test',
            'description': 'test',
            'project_type': 'Android'
        },
        headers={'Authorization': f'Bearer {token_obtain(user1_response.json())}'}
    )
    project = Project.objects.get(pk=project_response.json()['id'])
    assert project.author == user1
    assert project.author != user2
    with pytest.raises(ValidationError, match="L'auteur du projet ne peut pas être ajouté aux contributeurs"):
        C.client.post(
            f'{C.api_url}contributor/',
            data={
                'user': user1.id,
                'project': project.id
            },
            headers={'Authorization': f'Bearer {token_obtain(user1_response.json())}'}
        )

    response = C.client.post(
        f'{C.api_url}contributor/',
        data={
            'user': user2.id,
            'project': project.id
        },
        headers={'Authorization': f'Bearer {token_obtain(user1_response.json())}'}
    )
    assert response.status_code == 201
    expected_response = {
        'user':
        {
            'id': user2.id,
            'username': user2.username
        },
        'project':
        {
            'id': project.id,
            'author':
            {
                'id': user1.id,
                'username': user1.username
            },
            'title': project.title,
            'description': project.description,
            'project_type': project.project_type,
            'date_created': format_datetime(project.date_created)
        }
    }
    assert response.json() == expected_response


@pytest.mark.django_db
def test_contributor_in_project(user_data):
    contributor_add_to_project(user_data)
    project_response = C.client.get(
        f'{C.api_url}project/1/',
        headers={'Authorization': f'Bearer {token_obtain(user_data)}'}
    )
    assert project_response.status_code == 200
    expected_response = [
        {
            'id': 2,
            'username': 'user2'
        }
    ]
    assert project_response.json()['contributors'] == expected_response


@pytest.mark.django_db
def test_contributor_delete(user_data):
    contributor_add_to_project(user_data)
    delete_response = C.client.delete(
        f'{C.user_url}2/',
        headers={'Authorization': f'Bearer {token_obtain(user_data)}'}
        )
    assert delete_response.status_code == 204
    project_response = C.client.get(
        f'{C.api_url}project/1/',
        headers={'Authorization': f'Bearer {token_obtain(user_data)}'}
    )
    assert project_response.status_code == 200
    expected_response = []
    assert project_response.json()['contributors'] == expected_response


@pytest.mark.django_db
def test_contributor_change(user_data):
    contributor_add_to_project(user_data)
    data = user_data.copy()
    data['username'] = 'user3'
    user3_response = C.client.post(C.user_url, data)
    user3 = User.objects.get(pk=user3_response.json()['id'])
    project = Project.objects.get(pk=1)
    C.client.post(
        f'{C.api_url}contributor/',
        data={
            'user': user3.id,
            'project': project.id
        },
        headers={'Authorization': f'Bearer {token_obtain(user3_response.json())}'}
    )
    delete_response = C.client.delete(
        f'{C.user_url}2/',
        headers={'Authorization': f'Bearer {token_obtain(user_data)}'}
        )
    assert delete_response.status_code == 204
    project_response = C.client.get(
        f'{C.api_url}project/1/',
        headers={'Authorization': f'Bearer {token_obtain(user_data)}'}
    )
    assert project_response.status_code == 200
    expected_response = [
        {
            'id': user3.id,
            'username': user3.username
        }
    ]
    assert project_response.json()['contributors'] == expected_response
