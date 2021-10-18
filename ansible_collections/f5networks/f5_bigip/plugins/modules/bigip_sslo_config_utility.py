#!/usr/bin/python
# -*- coding: utf-8 -*-
# 
# Copyright: (c) 2021, kevin-dot-g-dot-stewart-at-gmail-dot-com
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
# Version: 1.0

#### Updates:
#### 1.0.1 - added 9.0 support (same as 8.3 so just changed max version)
####       - added rpm-update utility support


from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: bigip_sslo_config_utility
short_description: Manage the set of SSL Orchestrator utility functions
description:
  - Manage the set of SSL Orchestrator utility functions
version_added: "1.0.0"
options:
  utility:
    description:
        - Specifies the utility function to perform.
    type: str
    choices:
        - delete-all
        - rpm-update
  packages:
    description:
        - Used with the rpm-update utility function, this specifies the local path of the RPM file to push to the BIG-IP
    type: str  
  
extends_documentation_fragment: f5networks.f5_modules.f5
author:
  - Kevin Stewart (kevin-dot-g-dot-stewart-at-gmail-dot-com)
'''

EXAMPLES = r'''
- name: SSLO utility functions (delete-all)
  hosts: localhost
  gather_facts: False
  connection: local

  collections:
    - kevingstewart.f5_sslo_ansible
  
  vars: 
    provider:
      server: 172.16.1.77
      user: admin
      password: admin
      validate_certs: no
      server_port: 443

  tasks:
    - name: SSLO Utility Functions
      bigip_sslo_config_utility:
        provider: "{{ provider }}"
        
        utility: delete-all

      delegate_to: localhost

- name: SSLO utility functions (rpm-update)
  hosts: localhost
  gather_facts: False
  connection: local

  collections:
    - kevingstewart.f5_sslo_ansible
  
  vars: 
    provider:
      server: 172.16.1.77
      user: admin
      password: admin
      validate_certs: no
      server_port: 443

  tasks:
    - name: SSLO Utility Functions
      bigip_sslo_config_utility:
        provider: "{{ provider }}"
        
        utility: rpm-update
        package: ./f5-iappslx-ssl-orchestrator-16.0.1.1-8.4.15.noarch.rpm

      delegate_to: localhost
'''

RETURN = r'''
utility:
  description:
    - Defines the utility function to perform.
  type: str
  sample: delete-all
package:
  description:
    - Used with the rpm-update function, defines the local path of RPM file to push to BIG-IP
  type: str
  sample: ./f5-iappslx-ssl-orchestrator-16.0.1.1-8.4.15.noarch.rpm
'''

import time
import os
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection

from ..module_utils.client import F5Client

from ..module_utils.common import (
    F5ModuleError, AnsibleF5Parameters,
)

global print_output
global json_template
global obj_attempts
global min_version
global max_version

print_output = []

## define object creation attempts count (with 1 seconds pause between each attempt)
obj_attempts = 20

## define minimum supported tmos version - min(SSLO 5.x)
min_version = 5.0

## define maximum supported tmos version - max(SSLO 8.x)
max_version = 9.0

json_template = {}



class Parameters(AnsibleF5Parameters):
    api_map = {}
    updatables = []
    api_attributes = []
    returnables = []


class ApiParameters(Parameters):
    pass


class ModuleParameters(Parameters):
    global print_output

    @property
    def utility(self):
        utility = self._values['utility']
        if utility == None:
            return None
        return utility

    @property
    def package(self):
        package = self._values['package']
        if package == None:
            return None
        return package


class ModuleManager(object):
    global print_output
    global json_template
    global obj_attempts
    global min_version
    global max_version

    def __init__(self, *args, **kwargs):
        self.module = kwargs.pop('module', None)
        self.connection = kwargs.get('connection', None)
        self.client = F5Client(module=self.module, client=self.connection)
        self.want = ModuleParameters(params=self.module.params)

    def getSsloVersion(self):
        # use this method to get the SSLO version (first two digits (x.y))
        uri = "/mgmt/shared/iapp/installed-packages"

        response = self.client.get(uri)
        if response['code'] in [200, 201, 202]:
            for x in response['contents']["items"]:
                if x["appName"] == "f5-iappslx-ssl-orchestrator":
                    tmpversion = x["release"].split(".")
                    version = tmpversion[0] + "." + tmpversion[1]
                    return float(version)
        raise F5ModuleError("SSL Orchestrator package does not appear to be installed. Aborting.")

    def deleteOperation(self, id):
        # use this method to delete an operation that failed
        uri = "/mgmt/shared/iapp/blocks/{0}".format(id)
        response = self.client.delete(uri)

        if response['code'] in [200, 201, 202]:
            return True
        else:
            return False

    def exec_module(self):
        self.ssloVersion = self.getSsloVersion()
        changed = False
        result = dict()
        state = self.want.state


        ## test for correct TMOS version
        if self.ssloVersion < min_version or self.ssloVersion > max_version:
            raise F5ModuleError("Unsupported SSL Orchestrator version, requires a version between min(" + str(min_version) + ") and max(" + str(max_version) + ")")

        
        ## use this to initiate the different utility functions
        if self.want.utility == "delete-all":
            changed = self.deleteAll()

        elif self.want.utility == "rpm-update":
            if self.want.package == None:
                raise F5ModuleError("The rpm-update utility function requires a 'package' key that defines the local path of the RPM file to push to the BIG-IP")
            else:
                changed = self.rpmUpdate()


        result.update(dict(changed=changed))
        print_output.append('changed=' + str(changed))
        return result


    def deleteAll(self):
        if self.module.check_mode:
            return True

        ## use this to perform the SSLO delete-all function
        uri = "/mgmt/shared/iapp/f5-iappslx-ssl-orchestrator/appsCleanup"
        jsonstr = {"operationType": "CLEAN_ALL_GC_APP"}
        response = self.client.post(uri, data=jsonstr)
        if response['code'] not in [200, 201, 202]:
            raise F5ModuleError(response['contents'])

        ## poll the request to see if any errors are generated
        attempts = 1
        while attempts <= obj_attempts:
            uri = "/mgmt/shared/iapp/f5-iappslx-ssl-orchestrator/appsCleanup"
            response = self.client.post(uri, data=jsonstr)
            if response['code'] not in [200, 201, 202]:
                raise F5ModuleError(response['contents'])
            time.sleep(1)
            try:
                if response['contents']["running"] == False and response['contents']["message"] == "Cleanup process completed. Press ok to continue.":
                    break
                elif response['contents']["running"] == False and len(response['contents']["successMessage"]) > 0 and response['contents']["successMessage"][0]["type"] == "error":
                    raise F5ModuleError(str(response['contents']["successMessage"][0]["message"]))
                else:
                    attempts += 1
            except Exception as err:
                raise F5ModuleError("Utility(delete-all) failed with the following message: " + str(err))

    def rpmUpdate(self):
        if self.module.check_mode:
            return True

        ## upload the file
        name = os.path.split(self.want.package)[1]
        try:
            self.client.plugin.upload_file("/mgmt/shared/file-transfer/uploads", name)
        except F5ModuleError:
            raise F5ModuleError(
                "Failed to upload the file."
            )

        ## install package
        jsonstr = {"operation": "INSTALL", "packageFilePath": "/var/config/rest/downloads/" + name}
        response = self.client.post('/mgmt/shared/iapp/package-management-tasks', data=jsonstr)

        if response['code'] not in [200, 201, 202]:
            raise F5ModuleError(response['contents'])

        id = response['contents']['id']
        
        ## poll the request to see if any errors are generated
        attempts = 1
        while attempts <= obj_attempts:
            uri = "/mgmt/shared/iapp/package-management-tasks/{0}".format(id)
            response = self.client.get(uri)
            if response['code'] not in [200, 201, 202]:
                raise F5ModuleError(response['contents'])
            time.sleep(1)
            try:
                if response['contents']["status"] == "FINISHED":
                    break
                elif response['contents']["status"] == "FAILED":
                    raise F5ModuleError(str(response['contents']["errorMessage"]))
                else:
                    attempts += 1
            except Exception as err:
                raise F5ModuleError("Utility(rpm-update) failed with the following message: " + str(err))


class ArgumentSpec(object):
    def __init__(self):
        self.supports_check_mode = True
        argument_spec = dict(
            utility=dict(
                choices=["delete-all","rpm-update"],
                required=True
            ),
            package=dict(),
            mode=dict(
                choices=["update","output"],
                default="update"
            )
        )
        self.argument_spec = {}
        self.argument_spec.update(argument_spec)


def main():
    ## start here

    ## define global print_output
    global print_output
    print_output = []

    ## define argumentspec
    spec = ArgumentSpec()
    module = AnsibleModule(
        argument_spec=spec.argument_spec,
        supports_check_mode=spec.supports_check_mode
    )

    ## send to exec_module, result contains output of tasks
    try:
        mm = ModuleManager(module=module, connection=Connection(module._socket_path))
        results = mm.exec_module()
        result = dict(
          **results,
          print_output=print_output
        )
        module.exit_json(**result)
    except F5ModuleError as ex:
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()