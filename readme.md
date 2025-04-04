<img src='https://user.oc-static.com/upload/2023/06/28/16879473703315_P10-02.png' alt='SoftDesk support'>

# SoftDesk Support

## Presentation

SoftDesk support is an API RESTful which manage issues by projects

## Getting started

- Python version used 3.10.12

### Packages used for application

- Django v5.1.7
- djangorestframework v3.15.2
- djangorestframework_simplejwt v5.5.0

### Packages used for test

- coverage v7.8.0
- pytest v8.3.5
- pytest-cov v6.1.0
- pytest-django v4.10.0

### Virtual environment

#### Creation

Create the virtual environment.

Replace :
- \<version> by your version number of python
- <nom_de_l_environnement_virtuel> by the name you like

```
python<version> -m venv <nom_de_l_environnement_virtuel>
```

#### Activation

Activate the virtual environment.

For windows
```
<nom_de_l_environnement_virtuel>/Scripts/activate
```

For Unix/macOs

```
source .<nom_de_l_environnement_virtuel>/bin/activate
```

### Download application


Clone this repository
```
git clone https://github.com/spleenYou/OC-P10.git
```

### Install packages

Be sure to be in your vitual environment.  
Install needed packages.
```
pip install -r OC-P10/requirements.txt
```

### Start server

Change directory to be in Django project where you can find the file "manage.py"
```
cd OC-P10/
```

And start running Django server
```
python manage.py runserver
```

## Request API RESTful

To test the API in local mode, the start url will be http://127.0.0.1:8000/

Responses are paginted by 10.

All action are executed directly and can't be undone

### Authenticated

Endpoints for authenticated manage users and tokens

#### User actions
<details>
    <summary>List</summary>

- Endpoint: user/
- HTTP Method: GET
- Token needed: Yes
- Access: Login users

Success response Exemple:
- HTTP status: 200
```
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "user1",
            "birthday": "1985-01-01",
            "can_be_contacted": true,
            "can_data_be_shared": true,
            "projects_created": []
        },
        {
            "id": 2,
            "username": "user2",
            "birthday": "2000-01-01",
            "can_be_contacted": false,
            "can_data_be_shared": true,
            "projects_created": []
        }
    ]
}
```
</details>
<details>
    <summary>Create</summary>

To success, the user must be at least 15 years old

- Endpoint: user/
- HTTP Method: POST
- Token needed: No
- Access: Everyone
- Data needed (with exemple):
    - username (user1)
    - password1 (password-test)
    - password2 (password-test)
    - birthday (2000-01-01)
    - can_be_contacted (True)
    - can_data_be_shared (False)

Success response Exemple:
- HTTP status: 201
```
{
    "id": 1,
    "username": "user1",
    "birthday": "2000-01-01",
    "can_be_contacted": true,
    "can_data_be_shared": false
}
```
</details>
<details>
    <summary>Update</summary>

- Endpoint: user/\<id>/
- HTTP Method: PATCH
- Token needed: Yes
- Access: the connected user for himself
- Data can be choosen (exemple with id=1):
    - username (user-test-1)
    - password
    - birthday
    - can_be_contacted
    - can_data_be_shared

Success response Exemple:
- HTTP status: 200
```
{
    "id": 1,
    "username": "user-test-1",
    "birthday": "2000-01-01",
    "can_be_contacted": true,
    "can_data_be_shared": false
}
```
</details>
<details>
    <summary>Delete</summary>

- Endpoint: user/\<id>/
- HTTP Method: DELETE
- Token needed: Yes
- Access: the connected user for himself

Success response Exemple:
- HTTP status: 204

</details>

#### Token actions

The access token is valid for 5 minutes.

The refresh token is valid for 5 days.

<details>
    <summary>Get token access</summary>

- Endpoint: user/login/
- HTTP Method: POST
- Access: Everyone
- Data needed:
    - username
    - password

Success response Exemple:
- HTTPstatus: 200
```
{
    "refresh": <token>,
    "access": <token>
}
```
</details>
<details>
    <summary>Get access token by refresh token</summary>

- Endpoint: user/login/refresh/
- HTTP Method: POST
- Access: Everyone
- Data needed:
    - refresh token

Success response Exemple:
- HTTP status: 200
```
{
    "access": <token>
}
```
</details>

## Database

If you need a new and clean database, delete the database file "db.sqlite3"

Build a new one with the following command

```
python manage.py migrate

```

Now there is a new empty database available.

## Pytest Verification

Every possibilities are already testable with pytest.

For all test, type the following command :
```
pytest -s
```

To test a specific section, type the command you want :
- To test user :
```
pytest -s authentication/tests/test_user.py
```
- To test token :
```
pytest -s authentication/tests/test_token.py
```
- To test project :
```
pytest -s api/tests/test_project.py
```
- To test issue :
```
pytest -s api/tests/test_issue.py
```
- To test comment :
```
pytest -s api/tests/test_comment.py
```
- To test contributor :
```
pytest -s api/tests/test_contributor.py
```

## Coverage test

If you want to check test coverage, type the following command :

```
pytest --cov=. --cov-report html

```

All test will be executed and a html report will be generated in the folder 'htmlcov'