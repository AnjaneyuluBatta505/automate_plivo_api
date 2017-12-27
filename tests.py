import re
import unittest
from plivo_api import PlivoAPI, Error


class TestPlivoAPI(unittest.TestCase):

    def setUp(self):
        self.auth_id = 'SAMDA0MWZLYZFHNTEWNT'
        self.auth_token = 'YjUzODc2NzM5MmU2M2E3OTYzMjY0NjBjY2U1Yzg5'
        self.api = PlivoAPI(self.auth_id, self.auth_token)
        self.src = '14153014770'
        self.dst = '14153014785'
        self.txt = 'Hello world'

    def test_get_acc_cash_credits(self):
        cash_credits = self.api.get_acc_cash_credits()
        self.assertTrue(isintance(cash_credits, float))

    def test_get_message_uuid(self):
        msg_uuid = self.api.get_message_uuid(self.src, self.dst, self.txt)
        UUID_PATTERN = re.compile(r'^[\da-f]{8}-([\da-f]{4}-){3}[\da-f]{12}$', re.IGNORECASE)
        self.assertTrue(UUID_PATTERN.match(msg_uuid))

    def test_handle_success_message(self):
        msg_uuid = self.api.get_message_uuid(self.src, self.dst, self.txt)
        result = self.api.handle_success_message(msg_uuid)
        self.assertTrue(result)

    def test_send_message(self):
        result = self.api.send_message(self.src, self.dst, self.txt)
        self.assertTrue(result)

    def tearDown(self):
        del self.api
        del self.auth_id
        del self.auth_token
        del self.src
        del self.dst
        del self.txt


class TestPlivoAPIError(unittest.TestCase):

    def setUp(self):
        self.auth_id = self.auth_token = 'Invalid'
        self.api = PlivoAPI(self.auth_id, self.auth_token)
        self.src = '14153014770'
        self.dst = '14153014785'
        self.txt = 'Hello world'

    def test_raise_error(self):
        with self.assertRaises(Error):
            self.api.send_message(self.src, self.dst, self.txt)

    def tearDown(self):
        del self.api
        del self.auth_id
        del self.auth_token
        del self.src
        del self.dst
        del self.txt


if __name__ == '__main__':
    unittest.main()