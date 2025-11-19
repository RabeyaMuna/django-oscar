from http import client as http_client

from django.urls import reverse

from oscar.test.factories import create_order
from oscar.test.testcases import WebTestCase


class TestAnAnonymousUser(WebTestCase):
    # Note: UserFactory._after_postgeneration will stop saving the instance after postgeneration hooks in the next major release.
    def test_gets_a_404_when_requesting_an_unknown_order(self):
        path = reverse(
            "customer:anon-order", kwargs={"order_number": 1000, "hash": "1231231232"}
        )
        response = self.app.get(path, status="*")
        self.assertEqual(http_client.NOT_FOUND, response.status_code)

    def test_can_see_order_status(self):
        order = create_order()
        path = reverse(
            "customer:anon-order",
            kwargs={"order_number": order.number, "hash": order.verification_hash()},
        )
        response = self.app.get(path)
        self.assertEqual(
            http_client.OK, response.status_code, "Expected HTTP 200 OK status code."
        )

    def test_gets_404_when_using_incorrect_hash(self):
        order = create_order()
        path = reverse(
            "customer:anon-order", kwargs={"order_number": order.number, "hash": "bad"}
        )
        response = self.app.get(path, status="*")
        self.assertEqual(http_client.NOT_FOUND, response.status_code)
