import pytest
import CONST as C
import datetime
import json
from authentication.models import User
from api.models import Project
from django.core.exceptions import ValidationError


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
def test_issue(user_data):
    user1_response = C.client.post(C.user_url, user_data)
    user1 = User.objects.get(pk=user1_response.json()['id'])
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
    response = C.client.post(
        f'{C.api_url}issue/',
        data={
            'project': project.id,
            'title': 'test',
            'description': 'test',
            'status': 'To-Do',
            'priority': 'LOW',
            'tag': 'BUG',
        },
        headers={'Authorization': f'Bearer {token_obtain(user1_response.json())}'}
    )
    assert response.status_code == 201
    expected_value = {
        'id': 1,
        'author': {
            'id': user1.id,
            'username': user1.username
        },
        'project': {
            'id': project.id,
            'title': project.title,
            'description': project.description,
            'project_type': project.project_type,
            'date_created': format_datetime(project.date_created),
            'author': {
                'id': project.author.id,
                'username': project.author.username,
            }
        },
        'title': 'test',
        'description': 'test',
        'status': 'To-Do',
        'priority': 'LOW',
        'tag': 'BUG',
        'assigned_user': {
            'id': user1.id,
            'username': user1.username,
        },
        'date_created': response.json()['date_created'],
    }
    assert response.json() == expected_value

    response = C.client.patch(
        f'{C.api_url}issue/1/',
        json.dumps(
            {
                'title': 'Meilleur titre',
            },
        ),
        headers={
            'Authorization': f'Bearer {token_obtain(user1_response.json())}',
            'content-type': 'application/json',
        }
    )
    assert response.status_code == 200

    data = user_data.copy()
    data['username'] = 'User2'
    user2_response = C.client.post(C.user_url, data)
    with pytest.raises(ValidationError, match="Vous n'êtes pas affecté au projet"):
        C.client.post(
            f'{C.api_url}issue/',
            data={
                'project': project.id,
                'title': 'test',
                'description': 'test',
                'status': 'To-Do',
                'priority': 'LOW',
                'tag': 'BUG',
            },
            headers={'Authorization': f'Bearer {token_obtain(user2_response.json())}'}
        )

    response = C.client.delete(
        f'{C.api_url}issue/1/',
        headers={'Authorization': f'Bearer {token_obtain(user1_response.json())}'}
    )
    assert response.status_code == 204
