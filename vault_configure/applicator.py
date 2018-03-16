#!/usr/bin/env python

import hvac
import json
import os
import glob


def error_check(config_dict):
    if 'type' not in config_dict:
        raise ValueError("Audit type not specified")
    if config_dict['type'] not in ['file', 'socket', 'syslog']:
        raise ValueError("Incorrect value for audit backend type.")


def enable_audit(config_file):
    with open(config_file, 'r') as openfile:
        config = json.loads(openfile.read())
    error_check(config)
    try:
        name = config['path']
    except KeyError:
        name = None
    try:
        description = config['description']
    except KeyError:
        description = None
    try:
        options = config['options']
    except KeyError:
        options = None
    client = hvac.Client(url='http://localhost:8200', token='myroot')
    client.enable_audit_backend(config['type'], description, options, name)


def check_audit(config_file):
    with open(config_file, 'r') as openfile:
        config = json.loads(openfile.read())
    error_check(config)
    client = hvac.Client(url='http://localhost:8200', token='myroot')
    audits = client.list_audit_backends()
    if config['path']+'/' not in audits:
        return False
    else:
        audit = audits[config['path']+'/']
        audit = {k: v for k, v in audit.items() if k in config}
        return {k: v for k, v in audit.items() if k != 'path'} == {k: v for k, v in config.items() if k != 'path'}


if __name__ == '__main__':
    data_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data'))
    results = glob.glob(data_dir + '/**/*.json', recursive=True)

    if len(results) == 0:
        print("Nothing to do!")
        exit(0)

    for file in results:
        if 'sys/audit' in file:
            print("Running check for audit file: {}".format(file))
            if not check_audit(file):
                print("Check failed - config application required.")
                enable_audit(file)
            else:
                print("Check passed - no action required.")