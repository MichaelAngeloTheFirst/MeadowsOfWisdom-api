import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.urls import reverse


def api_client():
    user = User.objects.create_user(username="test_user", password="passwd")
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    return client


@pytest.mark.django_db
def test_register_user():
    client = api_client()
    payload = dict(username="test_user2", password="test_password")
    url = reverse("register_test-list")
    response = client.post(url, payload)
    data = response.data

    assert data["message"] == "successful"


@pytest.mark.django_db
def test_register_userexist():
    client = api_client()
    url = reverse("register_test-list")
    payload = dict(username="test_user", password="test_password")
    response = client.post(url, payload)
    data = response.data
    assert data["username"][0] == "A user with that username already exists."


@pytest.mark.django_db
def test_get_user():
    client = api_client()
    url = reverse("user_test-list")
    response = client.get(url)
    data = response.data
    assert data[0]["username"] == "test_user"


@pytest.mark.django_db
def test_tokens():
    client = api_client()
    url = reverse("token_obtain_pair")
    payload = dict(username="test_user", password="passwd")
    response = client.post(url, payload)
    assert response.status_code == 200


@pytest.mark.django_db
def test_token_refresh():
    client = api_client()
    url = reverse("token_refresh")
    payload = dict(username="test_user", password="passwd")
    response = client.post("/api/token", payload)
    refresh = response.data["refresh"]
    response = client.post(url, {"refresh": refresh})
    assert response.status_code == 200


@pytest.mark.django_db
def test_funfact():
    client = api_client()
    url = reverse("funfacts_test-list")
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_add_funfact():
    client = api_client()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    assert response.status_code == 201


@pytest.mark.django_db
def test_add_funfact_unauthorized():
    client = APIClient()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    assert response.status_code == 401


@pytest.mark.django_db
def test_add_funfact_empty():
    client = api_client()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="")
    response = client.post(url, payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_add_funfact_long():
    client = api_client()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact" * 100)
    response = client.post(url, payload)
    assert response.status_code == 201


@pytest.mark.django_db
def test_add_comment():
    client = api_client()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 3})
    payload = dict(comment_text="test comment", username="test_user", parent_id=0)
    response = client.post(url, payload)
    assert response.status_code == 201


@pytest.mark.django_db
def test_add_comment_unauthorized():
    client = APIClient()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 3})
    payload = dict(comment_text="test comment", username="test_user", parent_id=0)
    response = client.post(url, payload)
    assert response.status_code == 401


@pytest.mark.django_db
def test_add_comment_empty():
    client = api_client()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 3})
    payload = dict(comment_text="", username="test_user", parent_id=0)
    response = client.post(url, payload)
    assert response.status_code == 400


@pytest.mark.django_db
def test_add_comment_long():
    client = api_client()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 5})
    payload = dict(comment_text="test comment" * 100, username="test_user", parent_id=0)
    response = client.post(url, payload)
    assert response.status_code == 201


@pytest.mark.django_db
def test_add_reply():
    client = api_client()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 6})
    payload = dict(comment_text="test comment", username="test_user", parent_id=0)
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 6})
    payload = dict(comment_text="test reply", username="test_user", parent_id=3)
    response = client.post(url, payload)
    assert response.status_code == 201


@pytest.mark.django_db
def test_add_reply_unauthorized():
    client = APIClient()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 6})
    payload = dict(comment_text="test comment", username="test_user", parent_id=0)
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 6})
    payload = dict(comment_text="test reply", username="test_user", parent_id=3)
    response = client.post(url, payload)
    assert response.status_code == 401


@pytest.mark.django_db
def test_add_reply_empty():
    client = api_client()
    url = reverse("funfacts_test-list")
    payload = dict(fact_text="test fact")
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 6})
    payload = dict(comment_text="test comment", username="test_user", parent_id=0)
    response = client.post(url, payload)
    url = reverse("comments_test-list", kwargs={"fact_id": 6})
    payload = dict(comment_text="", username="test_user", parent_id=3)
    response = client.post(url, payload)
    assert response.status_code == 400
