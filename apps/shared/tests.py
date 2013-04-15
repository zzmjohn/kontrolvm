from django.test import Client
from django.contrib.auth.models import User

def check_url_perms(test, user, url):
  client = Client()
  response = client.get(url, follow=False)
  test.assertEqual(404, response.status_code)
  client.login(email="test@example.com", password="test-password")
  response = client.get(url, follow=False)
  test.assertEqual(404, response.status_code)
  # upgrade user
  user.is_staff = True
  user.save()
  response = client.get(url, follow=False)
  test.assertEqual(200, response.status_code)
  # downgrade user
  user.is_staff = False
  user.save()

def get_dummy_user():
  user, created = User.objects.get_or_create(email="test@example.com")
  user.set_password("test-password")
  user.save()
  return user
