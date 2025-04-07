import pytest
import CONST as C
import datetime
import json
from authentication.models import User


@pytest.mark.django_db
class TestUser:

    user1 = None

    @classmethod
    def setup_class(cls):
        print('\nDébut des tests pour les users')

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
        'Initialise variables'

        self.user1_data = {
            'username': C.username,
            'password1': C.password,
            'password2': C.password,
            'birthday': C.birthday,
            'can_be_contacted': C.can_be_contacted,
            'can_data_be_shared': C.can_data_be_shared,
        }
        self.user2_data = self.user1_data.copy()
        self.user2_data['username'] = 'client2-test'

    def birthday_formated(self, birthday=C.birthday):
        return birthday.strftime('%Y-%m-%d')

    def token_obtain(self, user_data):
        '''Return access token

        Args:
            user_data (dict): data's user

        Returns:
            Access token
        '''
        tokens = C.client.post(
            f"{C.user_url}login/",
            {
                'username': user_data['username'],
                'password': user_data['password1'],
            },
        )
        return tokens.json()['access_token']

    def get_user1(self):
        'Return the response of creating user1'
        if not self.user1:
            self.user1 = C.client.post(C.user_url, self.user1_data)
        return self.user1

    def test_user_return_str(self):
        user = self.get_user1()
        assert user.json()['username'] == User.objects.get(pk=1).__str__()

    def test_create_user_missing_fields_failed(self):
        data = self.user1_data.copy()
        del data['birthday']
        del data['can_be_contacted']
        del data['can_data_be_shared']
        response = C.client.post(C.user_url, data)
        expected_response = {
            'birthday': ['Ce champ est obligatoire.'],
            'can_be_contacted': ['Ce champ ne peut être nul.'],
            'can_data_be_shared': ['Ce champ ne peut être nul.'],
        }
        assert response.status_code == 400
        assert response.json() == expected_response

    def test_create_user_too_young(self):
        data = self.user1_data.copy()
        data['birthday'] = datetime.date(datetime.datetime.now().year, 1, 1)
        response = C.client.post(C.user_url, data)
        expected_response = {
            'birthday':
            [
                'You are too young'
            ]
        }
        assert response.status_code == 400
        assert response.json() == expected_response

    def test_user_created_success(self):
        response = self.get_user1()
        assert response.status_code == 201
        expected_response = {
            'id': 1,
            'birthday': self.birthday_formated(),
            'username': self.user1_data['username'],
            'can_be_contacted': self.user1_data['can_be_contacted'],
            'can_data_be_shared': self.user1_data['can_data_be_shared'],
        }
        assert response.json() == expected_response

    def test_create_user_passwords_do_not_match_failed(self):
        data = self.user1_data.copy()
        data['password2'] += 'e'
        response = C.client.post(C.user_url, data)
        expected_response = {
            'detail':
            [
                "Aucun compte actif n'a été trouvé avec les identifiants fournis",
            ]
        }
        assert response.status_code == 400
        assert response.json() == expected_response

    def test_user_details(self):
        user = self.get_user1()
        user_id = user.json()['id']
        response = C.client.get(
            C.user_url + str(user_id) + "/",
            headers={
                'Authorization': f'Bearer {self.token_obtain(self.user1_data)}'
            }
        )
        assert response.status_code == 200
        expected_response = {
            'id': user_id,
            'username': self.user1_data['username'],
            'birthday': self.birthday_formated(),
            'can_be_contacted': self.user1_data['can_be_contacted'],
            'can_data_be_shared': self.user1_data['can_data_be_shared'],
            'projects_created': []
        }
        assert response.json() == expected_response

    def test_user_update(self):
        user = self.get_user1()
        user_id = user.json()['id']
        response = C.client.patch(
            C.user_url + str(user_id) + "/",
            data=json.dumps({'username': 'testeur'}),
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {self.token_obtain(self.user1_data)}'
            }
        )
        assert response.status_code == 200
        assert response.json() == {
            'id': user_id,
            'username': 'testeur',
            'birthday': self.birthday_formated(),
            'can_be_contacted': self.user1_data['can_be_contacted'],
            'can_data_be_shared': self.user1_data['can_data_be_shared'],
            'projects_created': []
        }

    def test_user_update_by_another_user_failed(self):
        user = self.get_user1()
        C.client.post(C.user_url, self.user2_data)
        user_id = user.json()['id']
        response = C.client.patch(
            C.user_url + str(user_id) + "/",
            data=json.dumps({'username': 'testeur'}),
            headers={
                'content-type': 'application/json',
                'Authorization': f'Bearer {self.token_obtain(self.user2_data)}'
            }
        )
        assert response.status_code == 403
        assert response.json() == {
            'detail': "Vous n'avez pas la permission d'effectuer cette action.",
        }

    def test_user_delete_by_another_user_failed(self):
        user = self.get_user1()
        C.client.post(C.user_url, self.user2_data)
        user_id = user.json()['id']
        response = C.client.delete(
            C.user_url + str(user_id) + "/",
            headers={
                'Authorization': f'Bearer {self.token_obtain(self.user2_data)}'
            }
        )
        assert response.status_code == 403
        assert response.json() == {
            'detail': "Vous n'avez pas la permission d'effectuer cette action.",
        }

    def test_user_delete(self):
        user = self.get_user1()
        user_id = user.json()['id']
        response = C.client.delete(
            C.user_url + str(user_id) + "/",
            headers={
                'Authorization': f'Bearer {self.token_obtain(self.user1_data)}'
            }
        )
        assert response.status_code == 204

    def test_user_already_exist(self):
        self.get_user1()
        response = C.client.post(C.user_url, self.user1_data)
        assert response.status_code == 400
        expected_response = {
            'username': [
                'Un utilisateur avec ce nom existe déjà.'
            ]
        }
        assert response.json() == expected_response

    def test_user_logging_without_token_failed(self):
        user = self.get_user1()
        response = C.client.get(f"{C.user_url}{user.json()['id']}/")
        assert response.status_code == 401
        expected_response = {
            'detail': "Informations d'authentification non fournies."
        }
        assert response.json() == expected_response

    def test_user_logging_with_token(self):
        user = self.get_user1()
        response = C.client.get(
            f"{C.user_url}{user.json()['id']}/",
            headers={
                'Authorization': f'Bearer {self.token_obtain(self.user1_data)}'
            }
        )
        assert response.status_code == 200
        expected_response = {
            'id': user.json()['id'],
            'username': self.user1_data['username'],
            'birthday': self.birthday_formated(),
            'can_be_contacted': self.user1_data['can_be_contacted'],
            'can_data_be_shared': self.user1_data['can_data_be_shared'],
            'projects_created': []
        }
        assert response.json() == expected_response
