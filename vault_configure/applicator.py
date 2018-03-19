#!/usr/bin/env python

import os
import glob
import audit


def execute():
    # data_dir is the absolute path of the "data" directory from the project root
    data_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data'))

    # use glob to search recursively through the data directory and return the absolute path of any JSON format files
    # NOTE: This functionality is only available from Python 3.5 onwards (https://docs.python.org/3/library/glob.html)
    results = glob.glob(data_dir + '/**/*.json', recursive=True)

    # if len(results) == 0:
    #     print("Nothing to do!")
    #     exit(0)

    audit_files = []
    for file in results:
        if 'sys/audit' in file:
            audit_files.append(file)
    # POC to be modularised and *heavily* re-written to not break everything
    # Trial - destroy before creating
    import hvac
    import json
    client = hvac.Client(url='http://localhost:8200', token='myroot')
    audits = client.list_audit_backends()
    paths = []
    for file in audit_files:
        with open(file, 'r') as openfile:
            temp_conf = json.loads(openfile.read())
        paths.append(temp_conf['path']+'/')

    removals = [path for path in audits if path not in paths and path.endswith('/')]

    print("Paths: {}".format(paths))
    print("Removals: {}".format(removals))
    if len(removals) > 0:
        print("Caught some removals!")
        for removal in removals:
            my_audit = audit.Audit({'name': removal})
        my_audit.destroy()
    else:
        print("No removals found!")



    # Always create before destroying?
    for file in audit_files:
        print("Running check for audit file: {}".format(file))
        my_audit = audit.Audit(file)
        print("Authorisation: {}".format(my_audit.is_authorised()))
        if not my_audit.is_authorised():
            raise ValueError("The provided Vault token does not have sufficient access to perform this task.")

        if not my_audit.verify():
            print("Check failed - config application required.")
            my_audit.enable()
        else:
            print("Check passed - no action required.")


    # Check for items to be destroyed.



if __name__ == '__main__':
    execute()


