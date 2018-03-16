from vault_configure import applicator
import hvac
import unittest


class BuildTests(unittest.TestCase):
    def setUp(self):
        vault_address = 'http://localhost:8200'
        vault_token = 'myroot'
        self.client = hvac.Client(url=vault_address, token=vault_token)

    def test_client_is_authenticated(self):
        self.assertTrue(self.client.is_authenticated())
        self.client.close()

