import pytest
import CONST as C
import datetime
import json
from authentication.models import User
from api.models import Project


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

    def test_issue_add_fail(self):
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
            'id': 1,
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

        # response = C.client.patch(
        #     f'{C.api_url}issue/1/',
        #     json.dumps(
        #         {
        #             'title': 'Meilleur titre',
        #         },
        #     ),
        #     headers={
        #         'Authorization': f'Bearer {token_obtain(user1_response.json())}',
        #         'content-type': 'application/json',
        #     }
        # )
        # assert response.status_code == 200

        # data = user_data.copy()
        # data['username'] = 'User2'
        # user2_response = C.client.post(C.user_url, data)
        # with pytest.raises(ValidationError, match="Vous n'êtes pas affecté au projet"):
        #     C.client.post(
        #         f'{C.api_url}issue/',
        #         data={
        #             'project': project.id,
        #             'title': 'test',
        #             'description': 'test',
        #             'status': 'To-Do',
        #             'priority': 'LOW',
        #             'tag': 'BUG',
        #         },
        #         headers={'Authorization': f'Bearer {token_obtain(user2_response.json())}'}
        #     )

        # response = C.client.delete(
        #     f'{C.api_url}issue/1/',
        #     headers={'Authorization': f'Bearer {token_obtain(user1_response.json())}'}
        # )
        # assert response.status_code == 204
