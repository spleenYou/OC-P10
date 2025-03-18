import pytest
from django.test import Client
from django.urls import reverse

from authentication.models import User
from api.models import Project


def format_datetime(self, value):
    return value.strftime('%Y-%m-%dT%H:%M:%S.%fZ')


@pytest.mark.django_db
def test_list():
    client = Client()
    url = reverse('/project/')
    user = User.objects.create(
        username='client_test',
        password='password-test',
        birthday='2000-01-01',
        can_be_contacted=True,
        can_data_be_shared=True
    )
    project = Project.objects.create(title='Projet 1', description='Description du projet 1', author=user)
    response = client.get(url)
    assert response.status_code == 200
    expected = [
        {
            'count': 1,
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': project.id,
                    'title': project.title,
                    'date_created': format_datetime(project.date_created),
                    'author': {
                        'id': user.id,
                        'username': user.username
                    },
                    'project-type': project.project_type
                }
            ]
        }
    ]
    assert response.json() == expected
