from django.test import Client
import datetime

# Constantes
client = Client()
username = 'client-test'
password = 'password-test'
birthday = datetime.date(2000, 1, 1)
can_be_contacted = True
can_data_be_shared = True
url = '/user/'
