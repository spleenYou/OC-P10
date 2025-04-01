from django.test import Client
import datetime

# Constantes
client = Client()
username = 'client-test'
password = 'password-test'
birthday = datetime.date(2000, 1, 1)
can_be_contacted = True
can_data_be_shared = True
user_url = '/user/'
api_url = '/api/'
user1_data = {
    'username': username,
    'password1': password,
    'password2': password,
    'birthday': birthday,
    'can_be_contacted': can_be_contacted,
    'can_data_be_shared': can_data_be_shared,
}
user2_data = user1_data.copy()
user2_data['username'] = 'Client2-test'
user3_data = user1_data.copy()
user3_data['username'] = 'Client3-test'
