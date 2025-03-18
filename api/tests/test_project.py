import pytest
import datetime
from django.test import Client
from django.urls import reverse_lazy

from authentication.models import User
from api.models import Project


def format_datetime(value):
    return (value + datetime.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.%f+01:00')


def get_project_list(projects):
    return [
        {
            'id': project.id,
            'title': project.title,
            'date_created': format_datetime(project.date_created),
            'author': {
                'id': project.author.id,
                'username': project.author.username
            },
            'project_type': project.project_type
        } for project in projects
    ]


@pytest.mark.django_db
def test_list():
    client = Client()
    user = User.objects.create(
        username='client_test',
        password='password-test',
        birthday=datetime.date(2000, 1, 1),
        can_be_contacted=True,
        can_data_be_shared=True
    )
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
    response = client.get(url)
    assert response.status_code == 200
    assert response.json()['results'] == get_project_list(projects)
