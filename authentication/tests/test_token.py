import pytest
import CONST as C


@pytest.fixture
def user_data():
    return {
        'username': C.username,
        'password1': C.password,
        'password2': C.password,
        'birthday': C.birthday,
        'can_be_contacted': C.can_be_contacted,
        'can_data_be_shared': C.can_data_be_shared,
    }


@pytest.fixture
def created_user(user_data):
    C.client.post(C.user_url, user_data)
    return user_data


@pytest.mark.django_db
def test_token_obtain_success(created_user):
    response = C.client.post('/user/login/', {
        'username': created_user['username'],
        'password': created_user['password1'],
    })
    assert response.status_code == 200
    assert 'refresh' in response.json()
    assert 'access' in response.json()


@pytest.mark.django_db
def test_token_obtain_not_success(created_user):
    response = C.client.post('/user/login/', {
        'username': created_user['username'],
        'password': 'wrong_password',
    })
    assert response.status_code == 401
    assert 'detail' in response.json()
