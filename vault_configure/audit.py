import hvac
import json


class Audit():
    def __init__(self, configuration):
        if type(configuration) == dict:
            self.configuration = configuration
        else:
            with open(configuration, 'r') as openfile:
                self.configuration = json.loads(openfile.read())
        # Hard coded configuration for Dev
        self.client = hvac.Client(url='http://localhost:8200', token='myroot')

    def is_authorised(self):
        try:
            self.client.list_audit_backends()
            return True
        except hvac.exceptions.Forbidden:
            return False

    def verify_config(self):
        if 'type' not in self.configuration:
            raise ValueError("Audit type not specified")
        if self.configuration['type'] not in ['file', 'socket', 'syslog']:
            raise ValueError("Incorrect value for audit backend type.")

    def enable(self):
        try:
            name = self.configuration['path']
        except KeyError:
            name = None
        try:
            description = self.configuration['description']
        except KeyError:
            description = None
        try:
            options = self.configuration['options']
        except KeyError:
            options = None
        self.client.enable_audit_backend(self.configuration['type'], description, options, name)

    def verify(self):
        audits = self.client.list_audit_backends()
        if self.configuration['path']+'/' not in audits:
            return False
        else:
            audit = audits[self.configuration['path']+'/']
            audit = {k: v for k, v in audit.items() if k in self.configuration}
            return {k: v for k, v in audit.items() if k != 'path'} == {k: v for k, v in self.configuration.items() if k != 'path'}

    def destroy(self):
        self.client.disable_audit_backend(self.configuration['name'])