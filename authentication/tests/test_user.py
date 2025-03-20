import pytest
import authentication.tests.CONST as C


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


@pytest.mark.django_db
def test_create_user_error_400_missing_fields(user_data):
    # Supprimer des champs pour simuler une erreur
    data = user_data.copy()
    del data['birthday']
    del data['can_be_contacted']
    del data['can_data_be_shared']

    response = C.client.post(C.url, data)
    expected_response = {
        'birthday': ['Ce champ est obligatoire.'],
        'can_be_contacted': ['Ce champ ne peut être nul.'],
        'can_data_be_shared': ['Ce champ ne peut être nul.'],
    }
    assert response.status_code == 400
    assert response.json() == expected_response


@pytest.mark.django_db
def test_user_created_success(user_data):
    response = C.client.post(C.url, user_data)
    assert response.status_code == 201
    expected_response = {
        'birthday': C.birthday.strftime('%Y-%m-%d'),
        'username': C.username,
        'can_be_contacted': C.can_be_contacted,
        'can_data_be_shared': C.can_data_be_shared,
    }
    assert response.json() == expected_response


# Exemple pour un utilisateur avec mot de passe incorrect
@pytest.mark.django_db
def test_create_user_error_400_passwords_do_not_match(user_data):
    data = user_data.copy()
    data['password2'] += 'e'  # Pour simuler une erreur de correspondance

    response = C.client.post(C.url, data)
    expected_response = {
        'password': ["Password fields didn't match"],
    }
    assert response.status_code == 400
    assert response.json() == expected_response
