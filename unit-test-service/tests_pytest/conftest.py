"""
pytest
- set environments | PYTHONPATH=project | BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD
- run command with : pytest [directory_to_conftest.py] -vv -o log_cli=true
"""

import logging
import os

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from server.main import app

LOGGER = logging.getLogger(__name__)
client = TestClient(app)
payload = {
    'username': 'dev',
    'firstname': 'watcharapon',
    'lastname': 'weeraborirak'
}


@pytest.fixture
def get_home_page():
    response = client.get('/')
    return response.json()


@pytest.fixture
def authorization_header():
    return {'user-agent': os.environ.get('USER_AGENT')}


@pytest.fixture
def created_user_by_id(authorization_header):
    response = client.post('/user/create', json=payload, headers=authorization_header)
    created_id = response.json()['_id']
    yield created_id
    LOGGER.info(created_id)

    client.delete(f'/user/delete/{created_id}', headers=authorization_header)


def test_create_success(created_user_by_id, authorization_header):
    response = client.get(f'/user/find/{created_user_by_id}', headers=authorization_header)
    assert response.status_code == status.HTTP_200_OK


# testing method post status code 400
def test_create_duplicate(created_user_by_id, authorization_header):
    response = client.post('/user/create', json=payload, headers=authorization_header)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# testing method post status code 422
def test_create_user_unprocessable(authorization_header):
    n_payload = payload.copy()
    del n_payload['username']
    response = client.post('/user/create', json=n_payload, headers=authorization_header)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# testing method put status code 200
def test_update_user_success(created_user_by_id, authorization_header):
    payload['username'] = 'kane'
    response = client.put(f'/user/update/{created_user_by_id}', json=payload, headers=authorization_header)
    assert response.status_code == status.HTTP_200_OK


# testing method put status code 400
def test_update_user_duplicate(created_user_by_id, authorization_header):
    payload['username'] = 'kane'
    response = client.put(f'/user/update/{created_user_by_id}', json=payload, headers=authorization_header)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_delete_user(created_user_by_id, authorization_header):
    response = client.delete(f'/user/delete/{created_user_by_id}', headers=authorization_header)
    assert response.status_code == status.HTTP_204_NO_CONTENT
