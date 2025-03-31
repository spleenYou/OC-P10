import pytest
import CONST as C


@pytest.mark.django_db
class TestToken:
    @classmethod
    def setup_class(cls):
        print('\nDébut des tests pour les tokens')

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
        'Initiate the database with an user'

        self.user_data = {
            'username': C.username,
            'password1': C.password,
            'password2': C.password,
            'birthday': C.birthday,
            'can_be_contacted': C.can_be_contacted,
            'can_data_be_shared': C.can_data_be_shared,
        }
        C.client.post(C.user_url, self.user_data)

    def test_token_success(self):
        # Obtain token
        response = C.client.post(f'{C.user_url}login/', {
            'username': self.user_data['username'],
            'password': self.user_data['password1'],
        })
        assert response.status_code == 200
        assert 'refresh' in response.json()
        assert 'access' in response.json()

        # Obtain a new tokain from refresh token
        token_refresh = response.json()['refresh']
        response = C.client.post(
            f'{C.user_url}login/refresh/',
            {
                'refresh': token_refresh,
            },
        )
        assert response.status_code == 200
        assert 'access' in response.json()

    @pytest.mark.django_db
    def test_token_obtain_not_success(self):
        'Check the failure with a wrong password'

        response = C.client.post(f'{C.user_url}login/', {
            'username': self.user_data['username'],
            'password': 'wrong_password',
        })
        assert response.status_code == 401
        assert 'detail' in response.json()
