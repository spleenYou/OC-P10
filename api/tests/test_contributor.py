import pytest
import CONST as C
import datetime
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
        self.method = method.__name__
        self.length = len(f'    Début du test : {self.method}')
        print('\r' + '-' * self.length)
        print(f'\r    Début du test : {self.method}')

    def teardown_method(self, method):
        print(f'\r    Fin du test : {self.method}')
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
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
        )
        if 'update' in self.method:
            self.project2 = C.client.post(
                f'{C.api_url}project/',
                {
                    'title': 'Projet 2',
                    'description': 'Description du projet 2',
                    'project_type': "back-end",
                },
                HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
            )
        self.contributor = C.client.post(
            f'{C.api_url}contributor/',
            {
                'user': self.user3.json()['id'],
                'project': self.project.json()['id']
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user3_data)}',
        )

    def formated_datetime(self, date):
        return (date + datetime.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M:%S.%f+02:00')

    def get_token_access(self, user):
        tokens = C.client.post(
            f"{C.user_url}login/",
            {
                'username': user['username'],
                'password': user['password1'],
            }
        )
        return tokens.json()['access_token']

    def test_contributor_list(self):
        response = C.client.get(
            f'{C.api_url}contributor/',
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 200
        contributor = Contributor.objects.all()
        expected_response = {
            'count': len(contributor),
            'next': None,
            'previous': None,
            'results': [
                {
                    'id': contributor[0].id,
                    'date_created': self.formated_datetime(contributor[0].date_created),
                    'project': {
                        'id': self.project.json()['id'],
                        'author': {
                            'id': self.user1.json()['id'],
                            'username': self.user1.json()['username']
                        },
                        'title': self.project.json()['title'],
                        'project_type': self.project.json()['project_type'],
                        'date_created': self.project.json()['date_created'],
                        'description': self.project.json()['description'],
                    },
                    'user': {
                        'id': self.user1.json()['id'],
                        'username': self.user1.json()['username']
                    }
                },
                {
                    'id': contributor[1].id,
                    'date_created': self.formated_datetime(contributor[1].date_created),
                    'project': {
                        'id': self.project.json()['id'],
                        'author': {
                            'id': self.user1.json()['id'],
                            'username': self.user1.json()['username']
                        },
                        'title': self.project.json()['title'],
                        'project_type': self.project.json()['project_type'],
                        'date_created': self.project.json()['date_created'],
                        'description': self.project.json()['description'],
                    },
                    'user': {
                        'id': self.user3.json()['id'],
                        'username': self.user3.json()['username']
                    }
                }
            ]
        }
        assert response.json() == expected_response

    def test_contributor_detail(self):
        response = C.client.get(
            f'{C.api_url}contributor/1/',
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 200
        contributor = Contributor.objects.get(pk=1)
        expected_response = {
            'id': contributor.id,
            'date_created': self.formated_datetime(contributor.date_created),
            'project': {
                'id': self.project.json()['id'],
                'author': {
                    'id': self.user1.json()['id'],
                    'username': self.user1.json()['username']
                },
                'title': self.project.json()['title'],
                'project_type': self.project.json()['project_type'],
                'date_created': self.project.json()['date_created'],
                'description': self.project.json()['description'],
            },
            'user': {
                'id': self.user1.json()['id'],
                'username': self.user1.json()['username']
            }
        }
        assert response.json() == expected_response

    def test_contributor_detail_fail(self):
        response = C.client.get(
            f'{C.api_url}contributor/10/',
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 404
        expected_response = {
            'detail': 'No Contributor matches the given query.'
        }
        assert response.json() == expected_response

    def test_contributor_list_not_logged_fail(self):
        response = C.client.get(
            f'{C.api_url}contributor/',
        )
        assert response.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_response

    def test_contributor_add_to_project(self):
        response = C.client.post(
            f'{C.api_url}contributor/',
            data={
                'project': self.project.json()['id']
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 201
        contributor = Contributor.objects.get(pk=3)
        expected_response = {
            'id': contributor.id,
            'date_created': self.formated_datetime(contributor.date_created),
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

    def test_contributor_add_to_project_by_user_not_logged_fail(self):
        response = C.client.post(
            f'{C.api_url}contributor/',
            data={
                'project': self.project.json()['id']
            },
        )
        assert response.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_response

    def test_contributor_add_to_non_existent_project_fail(self):
        response = C.client.post(
            f'{C.api_url}contributor/',
            data={
                'project': 3
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 400
        expected_response = {
            'detail': 'Création impossible'
        }
        assert response.json() == expected_response

    def test_contributor_add_user_already_contributor(self):
        response = C.client.post(
            f'{C.api_url}contributor/',
            data={
                'project': self.project.json()['id']
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
        )
        assert response.status_code == 403
        expected_response = {
            'detail': "Création impossible"
        }
        assert response.json() == expected_response

    def test_contributor_partial_update_fail(self):
        contributor = Contributor.objects.all()[0]
        response = C.client.patch(
            f"/api/contributor/{contributor.id}/",
            data={'user': ''},
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
            content_type='application/octet-stream',
        )
        assert response.status_code == 403
        expected_response = {
            'detail': 'Mise à jour impossible'
        }
        assert response.json() == expected_response

    def test_contributor_update_fail(self):
        contributor = Contributor.objects.all()[0]
        response = C.client.put(
            f"/api/contributor/{contributor.id}/",
            data={'user': ''},
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
            content_type='application/octet-stream',
        )
        assert response.status_code == 403
        expected_response = {
            'detail': 'Mise à jour impossible'
        }
        assert response.json() == expected_response

    def test_contributor_delete_by_another_user_fail(self):
        contributor = Contributor.objects.all()[0]
        response = C.client.delete(
            f"{C.api_url}contributor/{contributor.id}/",
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
            )
        assert response.status_code == 403
        expected_response = {
            'detail': 'Suppression impossible'
        }
        assert response.json() == expected_response

    def test_contributor_delete(self):
        contributor = Contributor.objects.all()[0]
        response = C.client.delete(
            f"{C.api_url}contributor/{contributor.id}/",
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
            )
        assert response.status_code == 204

    def test_contributor_delete_by_deleting_project(self):
        response = C.client.delete(
            f"{C.api_url}project/{self.project.json()['id']}/",
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
            )
        assert response.status_code == 204
        contributor = Contributor.objects.all()
        assert len(contributor) == 0
