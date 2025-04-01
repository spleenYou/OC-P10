import pytest
import CONST as C
from api.models import Contributor


@pytest.mark.django_db
class TestContributor:

    @classmethod
    def setup_class(cls):
        print('\nDébut des tests pour les contributeurs')

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
        self.user3 = C.client.post(C.user_url, C.user3_data)
        self.project = C.client.post(
            f'{C.api_url}project/',
            {
                'title': 'Projet 1',
                'description': 'Description du projet 1',
                'project_type': "front-end",
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'}
        )
        self.contributor = C.client.post(
            f'{C.api_url}contributor/',
            {
                'user': self.user1.json()['id'],
                'project': self.project.json()['id']
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user3_data)}'}
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

    def test_contributor_add_to_project(self):
        response = C.client.post(
            f'{C.api_url}contributor/',
            data={
                'user': self.user2.json()['id'],
                'project': self.project.json()['id']
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user2_data)}'}
        )
        assert response.status_code == 201
        expected_response = {
            'user':
            {
                'id': self.user2.json()['id'],
                'username': self.user2.json()['username']
            },
            'project':
            {
                'id': self.project.json()['id'],
                'author':
                {
                    'id': self.user1.json()['id'],
                    'username': self.user1.json()['username']
                },
                'title': self.project.json()['title'],
                'description': self.project.json()['description'],
                'project_type': self.project.json()['project_type'],
                'date_created': self.project.json()['date_created']
            }
        }
        assert response.json() == expected_response

    def test_contributor_add_to_project_by_user_not_logged(self):
        response = C.client.post(
            f'{C.api_url}contributor/',
            data={
                'user': self.user2.json()['id'],
                'project': self.project.json()['id']
            },
        )
        assert response.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_response

    def test_contributor_add_to_non_existent_project(self):
        response = C.client.post(
            f'{C.api_url}contributor/',
            data={
                'user': self.user2.json()['id'],
                'project': 3
            },
            headers={'Authorization': f'Bearer {self.get_token_access(C.user2_data)}'}
        )
        assert response.status_code == 403
        expected_response = {
            'detail': 'Le projet est inexistant'
        }
        assert response.json() == expected_response

    def test_contributor_delete(self):
        contributor = Contributor.objects.all()[0]
        delete_response = C.client.delete(
            f"{C.api_url}contributor/{contributor.id}/",
            headers={'Authorization': f'Bearer {self.get_token_access(C.user1_data)}'}
            )
        assert delete_response.status_code == 204
