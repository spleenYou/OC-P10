import pytest
import CONST as C
import datetime
from authentication.models import User
from api.models import Project, Issue


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
        headers={'Authorization': f'Bearer {token_obtain(user1_response.json())}'}
    )
    data = user_data.copy()
    data['username'] = 'User2'
    user2_response = C.client.post(C.user_url, data)
    issue_response = C.client.post(
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
    issue = Issue.objects.get(pk=issue_response.json()['id'])

    comment_response = C.client.post(
        f'{C.api_url}comment/', {
            'issue': issue.id,
            'description': 'Description test'
        },
        headers={'Authorization': f'Bearer {token_obtain(user1_response.json())}'}
    )
    assert comment_response.status_code == 201
    expected_response = {
        'id': 1,
        'issue': issue.id,
        'description': 'Description test',
        'date_created': comment_response.json()['date_created'],
        'author': {
            'id': user1.id,
            'username': user1.username
        }
    }
    assert comment_response.json() == expected_response
    response = C.client.post(
        f'{C.api_url}comment/', {
            'issue': issue.id,
            'description': 'Description test'
        },
        headers={'Authorization': f'Bearer {token_obtain(user2_response.json())}'}
    )
    assert response.status_code == 401
    expected_response = {
        'detail': "Vous n'êtes pas affecté au projet"
    }
    assert response.json() == expected_response
