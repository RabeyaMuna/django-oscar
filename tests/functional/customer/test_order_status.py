from http import client as http_client
from importlib import import_module

from django.conf import settings
from django.urls import reverse

from oscar.test.factories import create_order
from oscar.test.testcases import WebTestCase


class TestAnAnonymousUser(WebTestCase):
    is_anonymous = True

    def set_session_email(self, email):
        # self.app.session can't be written to until a session cookie
        # exists, so build the session directly and attach its cookie.
        engine = import_module(settings.SESSION_ENGINE)
        session = engine.SessionStore()
        session["anon_order_email"] = email
        session.save()
        self.app.set_cookie(settings.SESSION_COOKIE_NAME, session.session_key)

    def test_gets_a_404_when_requesting_an_unknown_order(self):
        path = reverse(
            "customer:anon-order", kwargs={"order_number": 1000, "hash": "1231231232"}
        )
        response = self.app.get(path, status="*")
        self.assertEqual(http_client.NOT_FOUND, response.status_code)

    def test_can_see_order_status(self):
        order = create_order(guest_email="test@example.com")
        path = reverse(
            "customer:anon-order",
            kwargs={"order_number": order.number, "hash": order.verification_hash()},
        )
        self.set_session_email(order.email)
        response = self.app.get(path)
        self.assertEqual(http_client.OK, response.status_code)

    def test_gets_404_when_using_incorrect_hash(self):
        order = create_order(guest_email="test@example.com")
        path = reverse(
            "customer:anon-order", kwargs={"order_number": order.number, "hash": "bad"}
        )
        self.set_session_email(order.email)
        response = self.app.get(path, status="*")
        self.assertEqual(http_client.NOT_FOUND, response.status_code)
