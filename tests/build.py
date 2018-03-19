from vault_configure import applicator
import hvac
import unittest


class BuildTests(unittest.TestCase):
    def setUp(self):
        vault_address = 'http://localhost:8200'
        vault_token = 'myroot'
        self.client = hvac.Client(url=vault_address, token=vault_token)
        self.client.enable_audit_backend('file', options={"file_path": "/vault/logs/test.log"})

    def test_client_is_authenticated(self):
        self.assertTrue(self.client.is_authenticated())
        self.client.close()

    def test_bad_audit_is_removed(self):
        applicator.execute()
        self.assertTrue('file/' not in self.client.list_audit_backends())


