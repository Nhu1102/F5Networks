# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.f5networks.f5_bigip.plugins.modules.bigip_as3_deploy import (
    Parameters, ArgumentSpec, ModuleManager
)

from ansible_collections.f5networks.f5_bigip.plugins.module_utils.common import F5ModuleError
from ansible_collections.f5networks.f5_bigip.tests.compat import unittest
from ansible_collections.f5networks.f5_bigip.tests.compat.mock import Mock, patch, MagicMock
from ansible_collections.f5networks.f5_bigip.tests.modules.utils import set_module_args


fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures')
fixture_data = {}


def load_fixture(name):
    path = os.path.join(fixture_path, name)

    if path in fixture_data:
        return fixture_data[path]

    with open(path) as f:
        data = f.read()

    try:
        data = json.loads(data)
    except Exception:
        pass

    fixture_data[path] = data
    return data


class TestParameters(unittest.TestCase):
    def test_module_parameters(self):
        args = dict(
            content=dict(param1='foo', param2='bar'),
            tenant='test_tenant',
            timeout=600,
        )
        p = Parameters(params=args)
        assert p.content == dict(param1='foo', param2='bar')
        assert p.timeout == 600


class TestManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()
        self.p1 = patch('time.sleep')
        self.p1.start()
        self.p2 = patch('ansible_collections.f5networks.f5_bigip.plugins.modules.bigip_as3_deploy.send_teem')
        self.m2 = self.p2.start()
        self.m2.return_value = True
        self.p3 = patch(
            'ansible_collections.f5networks.f5_bigip.plugins.modules.bigip_as3_deploy.F5Client'
        )
        self.m3 = self.p3.start()
        self.m3.return_value = MagicMock()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def test_upsert_tenant_declaration(self, *args):
        declaration = load_fixture('as3_declare.json')
        set_module_args(dict(
            content=declaration,
            tenant='Sample_01',
            state='present',
            timeout=600
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode,
            required_if=self.spec.required_if
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.exists = Mock(return_value=False)
        mm.upsert_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True
        assert mm.want.timeout == (6, 100)

    def test_remove_tenant_declaration(self, *args):
        set_module_args(dict(
            tenant='Sample_01',
            state='absent',
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode,
            required_if=self.spec.required_if
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.resource_exists = Mock(side_effect=[True, False])
        mm.remove_from_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True
        assert mm.want.timeout == (3, 100)

    def test_upsert_tenant_declaration_generates_errors(self, *args):
        declaration = load_fixture('as3_declaration_invalid.json')
        set_module_args(dict(
            content=declaration,
            state='present',
            timeout=600
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode,
            required_if=self.spec.required_if
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.exists = Mock(return_value=False)
        mm.client.post = Mock(return_value=dict(
            code=202, contents=load_fixture('as3_invalid_declaration_task_start.json')
        ))
        mm.client.get = Mock(return_value=dict(
            code=200, contents=load_fixture('as3_error_message.json')
        ))

        with self.assertRaises(F5ModuleError) as err:
            mm.exec_module()

        assert "declaration is invalid. /Sample_02/A1/web_pool2/members/0: " \
               "should have required property 'bigip'" in str(err.exception)

    def test_upsert_multi_tenant_declaration_generates_errors(self, *args):
        declaration = load_fixture('as3_multiple_tenants_invalid.json')
        set_module_args(dict(
            content=declaration,
            state='present',
            timeout=600
        ))

        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode,
            required_if=self.spec.required_if
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.exists = Mock(return_value=False)
        mm.client.post = Mock(return_value=dict(
            code=202, contents=load_fixture('as3_multi_tenant_declare_task_start.json')
        ))
        mm.client.get = Mock(return_value=dict(
            code=200, contents=load_fixture('as3_multi_tenant_error_message.json')
        ))

        with self.assertRaises(F5ModuleError) as err:
            mm.exec_module()

        assert "declaration failed. 0107176c:3: Invalid Node, the IP " \
               "address 192.0.1.12 already exists." in str(err.exception)
