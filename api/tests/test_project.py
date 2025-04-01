import pytest
import CONST as C
import datetime
import json
from django.urls import reverse_lazy

from authentication.models import User
from api.models import Project


@pytest.mark.django_db
class TestProject:

    @classmethod
    def setup_class(cls):
        print('\nDébut des tests pour les projets')

    @classmethod
    def teardown_class(cls):
        print('\rFin des tests')

    def setup_method(self, method):
        self.length = len(f'    Début du test : {method.__name__}')
        print('\r' + '-' * self.length)
        print(f'\r    Début du test : {method.__name__}')

    def teardown_method(self, method):
        print(f'\r    Fin du test : {method.__name__}')
        print('\r' + '-' * self.length)

    @pytest.fixture(autouse=True)
    def setup(self):
        self.user1 = C.client.post(C.user_url, C.user1_data)
        self.user2 = C.client.post(C.user_url, C.user2_data)
        user = User.objects.get(pk=self.user1.json()['id'])
        self.projects = []
        self.projects.append(
            Project.objects.create(
                title='Projet 1',
                description='Description du projet 1',
                project_type="front-end",
                author=user
            )
        )
        self.projects.append(
            Project.objects.create(
                title='Projet 2',
                description='Description du projet 2',
                project_type="back-end",
                author=user
            )
        )
        self.projects.append(
            Project.objects.create(
                title='Projet 3',
                description='Description du projet 3',
                project_type="iOS",
                author=user
            )
        )
        self.projects.append(
            Project.objects.create(
                title='Projet 4',
                description='Description du projet 4',
                project_type="Android",
                author=user
            )
        )

    def birthday_formated(self, birthday=C.birthday):
        return birthday.strftime('%Y-%m-%d')

    def format_datetime(self, value):
        return (value + datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S.%f+02:00')

    def get_project_list(self, projects):
        return [
            {
                'id': project.id,
                'title': project.title,
                'description': project.description,
                'date_created': self.format_datetime(project.date_created),
                'author': {
                    'id': project.author.id,
                    'username': project.author.username
                },
                'project_type': project.project_type
            } for project in projects
        ]

    def get_token_access(self, user_data):
        tokens = C.client.post(
            f"{C.user_url}login/",
            {
                'username': user_data['username'],
                'password': user_data['password1'],
            }
        )
        return tokens.json()['access']

    def test_project_add_fail(self):
        self.user1
        project_response = C.client.post(
            f'{C.api_url}project/',
            data={
                'title': 'test',
                'description': 'test',
                'project_type': 'Android'
            },
        )
        assert project_response.status_code == 401

    def test_project_add(self):
        self.user1
        project_response = C.client.post(
            f'{C.api_url}project/',
            data={
                'title': 'test',
                'description': 'test',
                'project_type': 'Android'
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'}
        )
        assert project_response.status_code == 201

    def test_project_update_fail(self):
        project = self.projects[0]
        project_id = project.id
        response_update = C.client.patch(
            f'{C.api_url}project/{project_id}/',
            data=json.dumps({'description': 'changement de description'}),
            headers={
                'content-type': 'application/json',
            }
        )
        assert response_update.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response_update.json() == expected_response

    def test_project_update_by_another_user(self):
        project = self.projects[0]
        project_id = project.id
        response_update = C.client.patch(
            f'{C.api_url}project/{project_id}/',
            data=json.dumps({'description': 'changement de description'}),
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {self.get_token_access(C.user2_data)}'
            }
        )
        assert response_update.status_code == 403
        expected_response = {
            'detail': "Seul l'auteur peut effectuer une mise à jour"
        }
        assert response_update.json() == expected_response

    def test_project_update(self):
        project = self.projects[0]
        project_id = project.id
        response_update = C.client.patch(
            f'{C.api_url}project/{project_id}/',
            data=json.dumps({'description': 'changement de description'}),
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'
            }
        )
        assert response_update.status_code == 200
        expected_response = {
            'id': project_id,
            'title': response_update.json()['title'],
            'description': 'changement de description',
            'author': response_update.json()['author'],
            'project_type': response_update.json()['project_type'],
            'date_created': response_update.json()['date_created'],
        }
        assert response_update.json() == expected_response

    def test_project_list(self):
        url = reverse_lazy('project-list')
        response = C.client.get(
            url,
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'
            }
        )
        assert response.status_code == 200
        assert response.json()['results'] == self.get_project_list(self.projects)

    def test_project_list_by_user_not_in_project(self):
        url = reverse_lazy('project-list')
        response = C.client.get(
            url,
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user2_data)}'
            }
        )
        assert response.status_code == 200
        assert response.json()['results'] == self.get_project_list(self.projects)

    def test_project_list_fail(self):
        url = reverse_lazy('project-list')
        response = C.client.get(url)
        assert response.status_code == 401

    def test_project_detail(self):
        response = C.client.get(
            f'{C.api_url}project/1/',
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'
            }
        )
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

    def test_project_detail_by_user_not_in_project(self):
        response = C.client.get(
            f'{C.api_url}project/1/',
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user2_data)}'
            }
        )
        assert response.status_code == 403
        expected_response = {
            'detail': 'Vous ne faites pas partie du projet'
        }
        assert response.json() == expected_response

    def test_project_detail_fail(self):
        response = C.client.get(
            f'{C.api_url}project/1/',
        )
        assert response.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_response

    def test_project_delete_fail(self):
        response = C.client.delete(
            f'{C.api_url}project/1/',
        )
        assert response.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_response

    def test_project_delete_by_user_not_in_project(self):
        response = C.client.delete(
            f'{C.api_url}project/1/',
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user2_data)}'
            }
        )
        assert response.status_code == 403
        expected_response = {
            'detail': "Seul l'auteur peut effectuer une suppression"
        }
        assert response.json() == expected_response

    def test_project_delete(self):
        response = C.client.delete(
            f'{C.api_url}project/1/',
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'
            }
        )
        assert response.status_code == 204
