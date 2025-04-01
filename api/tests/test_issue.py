import pytest
import CONST as C
import datetime
import json


@pytest.mark.django_db
class TestIssue:

    @classmethod
    def setup_class(cls):
        print('\nDébut des tests pour les questions')

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
        self.user2 = C.client.post(C.user_url, C.user2_data)
        self.user1 = C.client.post(C.user_url, C.user1_data)
        self.project = C.client.post(
            f'{C.api_url}project/',
            {
                'title': 'Projet 1',
                'description': 'Description du projet 1',
                'project_type': "front-end",
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'}
        )
        self.issue = C.client.post(
            f'{C.api_url}issue/',
            data={
                'project': self.project.json()['id'],
                'title': 'test',
                'description': 'test',
                'status': 'To-Do',
                'priority': 'LOW',
                'tag': 'BUG',
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'}
        )

    def get_token_access(self, user):
        tokens = C.client.post(
            f"{C.user_url}login/",
            {
                'username': user['username'],
                'password': user['password1'],
            }
        )
        return tokens.json()['access']

    def format_datetime(self, value):
        return (value + datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S.%f+02:00')

    def test_issue_add_by_author_not_logged(self):
        response = C.client.post(
            f'{C.api_url}issue/',
            data={
                'project': self.project.json()['id'],
                'title': 'test',
                'description': 'test',
                'status': 'To-Do',
                'priority': 'LOW',
                'tag': 'BUG',
            },
        )
        assert response.status_code == 401
        expected_value = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_value

    def test_issue_add_by_user_not_in_project(self):
        response = C.client.post(
            f'{C.api_url}issue/',
            data={
                'project': self.project.json()['id'],
                'title': 'test',
                'description': 'test',
                'status': 'To-Do',
                'priority': 'LOW',
                'tag': 'BUG',
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user2_data)}'}
        )
        assert response.status_code == 403
        expected_value = {
            'detail': 'Vous ne faites pas partie du projet'
        }
        assert response.json() == expected_value

    def test_issue_add(self):
        response = C.client.post(
            f'{C.api_url}issue/',
            data={
                'project': self.project.json()['id'],
                'title': 'test',
                'description': 'test',
                'status': 'To-Do',
                'priority': 'LOW',
                'tag': 'BUG',
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'}
        )
        assert response.status_code == 201
        expected_value = {
            'id': response.json()['id'],
            'author': {
                'id': self.user1.json()['id'],
                'username': self.user1.json()['username']
            },
            'project': {
                'id': self.project.json()['id'],
                'title': self.project.json()['title'],
                'description': self.project.json()['description'],
                'project_type': self.project.json()['project_type'],
                'date_created': self.project.json()['date_created'],
                'author': {
                    'id': self.user1.json()['id'],
                    'username': self.user1.json()['username']
                }
            },
            'title': 'test',
            'description': 'test',
            'status': 'To-Do',
            'priority': 'LOW',
            'tag': 'BUG',
            'assigned_user': {
                'id': self.user1.json()['id'],
                'username': self.user1.json()['username']
            },
            'date_created': response.json()['date_created'],
        }
        assert response.json() == expected_value

    def test_issue_add_fail(self):
        response = C.client.post(
            f'{C.api_url}issue/',
            data={
                'project': self.project.json()['id'],
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'}
        )
        assert response.status_code == 400
        expected_value = {
            'title': ['Ce champ est obligatoire.'],
            'description': ['Ce champ est obligatoire.'],
            'tag': ['Ce champ est obligatoire.'],
        }
        assert response.json() == expected_value

    def test_issue_list_not_allowed(self):
        response = C.client.get(
            f'{C.api_url}issue/',
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user2_data)}',
            }
        )
        assert response.status_code == 403
        expected_response = {
            'detail': "Impossible de lister les questions"
        }
        assert response.json() == expected_response

    def test_issue_update_by_user_not_in_project(self):
        response = C.client.patch(
            f'{C.api_url}issue/1/',
            json.dumps(
                {
                    'title': 'Meilleur titre',
                },
            ),
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {self.get_token_access(C.user2_data)}',
            }
        )
        assert response.status_code == 403
        expected_response = {
            'detail': "Vous ne pouvez pas effectuer la mise à jour"
        }
        assert response.json() == expected_response

    def test_issue_update_by_author_not_logged(self):
        response = C.client.patch(
            f'{C.api_url}issue/1/',
            json.dumps(
                {
                    'title': 'Meilleur titre',
                },
            ),
            headers={
                'content-type': 'application/json',
            }
        )
        assert response.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_response

    def test_issue_update(self):
        response = C.client.patch(
            f'{C.api_url}issue/1/',
            json.dumps(
                {
                    'title': 'Meilleur titre',
                },
            ),
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user1_data)}',
                'content-type': 'application/json',
            }
        )
        assert response.status_code == 200
        expected_response = {
            'id': response.json()['id'],
            'author': {
                'id': self.user1.json()['id'],
                'username': self.user1.json()['username']
            },
            'project': {
                'id': self.project.json()['id'],
                'title': self.project.json()['title'],
                'description': self.project.json()['description'],
                'project_type': self.project.json()['project_type'],
                'date_created': self.project.json()['date_created'],
                'author': {
                    'id': self.user1.json()['id'],
                    'username': self.user1.json()['username']
                }
            },
            'title': 'Meilleur titre',
            'description': 'test',
            'status': 'To-Do',
            'priority': 'LOW',
            'tag': 'BUG',
            'assigned_user': {
                'id': self.user1.json()['id'],
                'username': self.user1.json()['username']
            },
            'date_created': response.json()['date_created'],
        }
        assert response.json() == expected_response

    def test_issue_delete_by_another_user(self):
        response = C.client.delete(
            f'{C.api_url}issue/1/',
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user2_data)}',
            }
        )
        assert response.status_code == 403
        expected_response = {
            'detail': "Vous ne pouvez pas effectuer la suppression"
        }
        assert response.json() == expected_response

    def test_issue_delete_by_author_not_logged(self):
        response = C.client.delete(
            f'{C.api_url}issue/1/',
        )
        assert response.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_response

    def test_issue_delete(self):
        response = C.client.delete(
            f'{C.api_url}issue/1/',
            headers={
                'Authorization': f'Bearer {self.get_token_access(C.user1_data)}',
            }
        )
        assert response.status_code == 204
