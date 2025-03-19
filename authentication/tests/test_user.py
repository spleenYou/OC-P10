import pytest
from django.test import Client
import datetime


client = Client()
username = 'client-test'
password = 'password-test'
birthday = datetime.date(2000, 1, 1)
can_be_contacted = True
can_data_be_shared = True
url = '/user/'


@pytest.mark.django_db
def test_create_user_error_400():
    response = client.post(url, {
        'username': username,
        'password1': password,
        'password2': password
    })
    expected_response = {
        'birthday': ['Ce champ est obligatoire.'],
        'can_be_contacted': ['Ce champ ne peut être nul.'],
        'can_data_be_shared': ['Ce champ ne peut être nul.'],
    }
    assert response.status_code == 400
    assert response.json() == expected_response

    response = client.post(url, {
        'username': username,
        'password1': password,
        'password2': password,
        'birthday': birthday,
    })
    expected_response = {
        'can_be_contacted': ['Ce champ ne peut être nul.'],
        'can_data_be_shared': ['Ce champ ne peut être nul.'],
    }
    assert response.status_code == 400
    assert response.json() == expected_response

    response = client.post(url, {
        'username': username,
        'password1': password,
        'password2': password,
        'birthday': birthday,
        'can_be_contacted': can_be_contacted,
    })
    expected_response = {
        'can_data_be_shared': ['Ce champ ne peut être nul.'],
    }
    assert response.status_code == 400
    assert response.json() == expected_response

    response = client.post(url, {
        'username': username,
        'password1': password,
        'password2': password + 'e',
        'birthday': birthday,
        'can_be_contacted': can_be_contacted,
        'can_data_be_shared': can_data_be_shared,
    })
    expected_response = {
        'password': ["Password fields didn't match"],
    }
    assert response.status_code == 400
    assert response.json() == expected_response


@pytest.mark.django_db
def test_user_created_success():
    response = client.post(url, {
        'username': username,
        'password1': password,
        'password2': password,
        'birthday': birthday,
        'can_be_contacted': can_be_contacted,
        'can_data_be_shared': can_data_be_shared,
    })
    assert response.status_code == 201
    expected_response = {
        'birthday': birthday.strftime('%Y-%m-%d'),
        'username': username,
        'can_be_contacted': can_be_contacted,
        'can_data_be_shared': can_data_be_shared,
    }
    assert response.json() == expected_response
