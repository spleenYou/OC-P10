import pytest
import CONST as C
import json
from api.models import Comment


@pytest.mark.django_db
class TestComment:

    @classmethod
    def setup_class(cls):
        print('\nDébut des tests pour les commentaires')

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
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
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
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
        )
        self.contributor = C.client.post(
            f'{C.api_url}contributor/',
            {
                'user': self.user2.json()['id'],
                'project': self.project.json()['id']
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        self.comment = C.client.post(
            f'{C.api_url}comment/',
            {
                'issue': self.issue.json()['id'],
                'description': 'Solution de ouf',
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )

    def get_token_access(self, user_data):
        tokens = C.client.post(
            f"{C.user_url}login/",
            {
                'username': user_data['username'],
                'password': user_data['password1'],
            }
        )
        return tokens.json()['access']

    def test_comment_list_fail(self):
        response = C.client.get(
            f'{C.api_url}comment/',
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 403
        expected_response = {
            'detail': 'Impossible de lister'
        }
        assert response.json() == expected_response

    def test_comment_list_by_issue(self):
        response = C.client.get(
            f"{C.api_url}issue/{self.issue.json()['id']}/",
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
        )
        assert response.status_code == 200
        expected_response = {
            'id': self.issue.json()['id'],
            'assigned_user': {
                'id': self.user1.json()['id'],
                'username': self.user1.json()['username'],
            },
            'author': {
                'id': self.user1.json()['id'],
                'username': self.user1.json()['username']
            },
            'date_created': self.issue.json()['date_created'],
            'description': self.issue.json()['description'],
            'priority': self.issue.json()['priority'],
            'status': self.issue.json()['status'],
            'tag': self.issue.json()['tag'],
            'title': self.issue.json()['title'],
            'project': {
                'id': self.project.json()['id'],
                'author': {
                    'id': self.user1.json()['id'],
                    'username': self.user1.json()['username'],
                },
                'title': self.project.json()['title'],
                'description': self.project.json()['description'],
                'project_type': self.project.json()['project_type'],
                'date_created': self.project.json()['date_created'],
            },
            'comments': [
                {
                    'id': self.comment.json()['id'],
                    'author': {
                        'id': self.user2.json()['id'],
                        'username': self.user2.json()['username'],
                    },
                    'description': self.comment.json()['description'],
                    'date_created': self.comment.json()['date_created']
                }
            ]
        }
        assert response.json() == expected_response

    def test_comment_add(self):
        response = C.client.post(
            f'{C.api_url}comment/',
            data={
                'issue': self.issue.json()['id'],
                'description': 'Nouveau comment'
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 201
        expected_response = {
            'author': {
                'id': self.user2.json()['id'],
                'username': self.user2.json()['username'],
            },
            'description': 'Nouveau comment',
            'id': response.json()['id'],
            'date_created': response.json()['date_created']
        }
        assert response.json() == expected_response

    def test_comment_add_non_existent_issue_fail(self):
        response = C.client.post(
            f'{C.api_url}comment/',
            data={
                'issue': 10,
                'description': 'Nouveau comment'
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 403
        expected_response = {
            'detail': 'Création impossible'
        }
        assert response.json() == expected_response

    def test_comment_add_non_contributor_user_fail(self):
        response = C.client.post(
            f'{C.api_url}comment/',
            data={
                'issue': self.issue.json()['id'],
                'description': 'Nouveau comment'
            },
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user3_data)}',
        )
        assert response.status_code == 403
        expected_response = {
            'detail': 'Vous ne faites pas partie du projet'
        }
        assert response.json() == expected_response

    def test_comment_update(self):
        comment = Comment.objects.all()[0]
        response = C.client.patch(
            f"{C.api_url}comment/{comment.id}/",
            data=json.dumps(
                {
                    'description': 'Nouveau commentaire',
                }
            ),
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
            content_type='application/json',
        )
        assert response.status_code == 200
        expected_response = {
            'author': {
                'id': self.user2.json()['id'],
                'username': self.user2.json()['username'],
            },
            'description': 'Nouveau commentaire',
            'date_created': response.json()['date_created'],
            'id': response.json()['id']
        }
        assert response.json() == expected_response

    def test_comment_update_not_by_author(self):
        comment = Comment.objects.all()[0]
        response = C.client.patch(
            f"{C.api_url}comment/{comment.id}/",
            data=json.dumps(
                {
                    'description': 'Nouveau commentaire',
                }
            ),
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
            content_type='application/json',
        )
        assert response.status_code == 200
        expected_response = {
            'author': {
                'id': self.user2.json()['id'],
                'username': self.user2.json()['username'],
            },
            'description': 'Nouveau commentaire',
            'date_created': response.json()['date_created'],
            'id': response.json()['id']
        }
        assert response.json() == expected_response

    def test_comment_delete_by_another_user_fail(self):
        comment = Comment.objects.all()[0]
        response = C.client.delete(
            f"{C.api_url}comment/{comment.id}/",
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user1_data)}',
        )
        assert response.status_code == 403
        expected_response = {
            'detail': "Vous devez être l'auteur"
        }
        assert response.json() == expected_response

    def test_comment_delete(self):
        comment = Comment.objects.all()[0]
        response = C.client.delete(
            f"{C.api_url}comment/{comment.id}/",
            HTTP_AUTHORIZATION=f'Bearer {self.get_token_access(C.user2_data)}',
        )
        assert response.status_code == 204
