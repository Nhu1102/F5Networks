# -*- coding: utf-8 -*-
#
# Copyright: (c) 2020, F5 Networks Inc.
# GNU General Public License v3.0 (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import os

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.f5networks.f5_bigip.plugins.modules.bigip_config import (
    Parameters, ModuleManager, ArgumentSpec
)
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
            save='yes',
            reset='yes',
            merge_content='asdasd',
            verify='no',
        )
        p = Parameters(params=args)
        assert p.save == 'yes'
        assert p.reset == 'yes'
        assert p.merge_content == 'asdasd'


class TestManager(unittest.TestCase):

    def setUp(self):
        self.spec = ArgumentSpec()
        self.p1 = patch('time.sleep')
        self.p2 = patch('ansible_collections.f5networks.f5_bigip.plugins.modules.bigip_config.send_teem')
        self.p3 = patch('ansible_collections.f5networks.f5_bigip.plugins.modules.bigip_config.F5Client')
        self.p1.start()
        self.m2 = self.p2.start()
        self.m2.return_value = True
        self.m3 = self.p3.start()
        self.m3.return_value = MagicMock()

    def tearDown(self):
        self.p1.stop()
        self.p2.stop()

    def test_start_save_config_task(self, *args):
        task_id = "e7550a12-994b-483f-84ee-761eb9af6750"
        set_module_args(dict(
            save='yes'
        )
        )
        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.save_on_device = Mock(return_value=task_id)
        mm._start_task_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True
        assert results['task_id'] == task_id
        assert results['message'] == 'Save config async task started with id: {0}'.format(task_id)

    def test_start_merge_config_task(self, *args):
        task_id = "e7550a12-994b-483f-84ee-761eb9af6750"
        set_module_args(dict(
            merge_content='asdas'
        )
        )
        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.merge = Mock(return_value=task_id)
        mm._start_task_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True
        assert results['task_id'] == task_id
        assert results['message'] == 'Merge config async task started with id: {0}'.format(task_id)

    def test_start_reset_config_task(self, *args):
        task_id = "e7550a12-994b-483f-84ee-761eb9af6750"
        set_module_args(dict(
            reset='yes'
        )
        )
        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.reset_device = Mock(return_value=task_id)
        mm._start_task_on_device = Mock(return_value=True)

        results = mm.exec_module()

        assert results['changed'] is True
        assert results['task_id'] == task_id
        assert results['message'] == 'Load config defaults async task started with id: {0}'.format(task_id)

    def test_verify_config(self, *args):
        set_module_args(dict(
            verify='yes',
            merge_content='asdas'
        )
        )
        module = AnsibleModule(
            argument_spec=self.spec.argument_spec,
            supports_check_mode=self.spec.supports_check_mode
        )
        mm = ModuleManager(module=module)

        # Override methods to force specific logic in the module to happen
        mm.upload_to_device = Mock(return_value=True)
        mm.move_on_device = Mock(return_value=True)
        mm.remove_temporary_file = Mock(return_value=True)
        mm.client.post = Mock(return_value=dict(code=200, contents=dict()))
        results = mm.exec_module()

        mm.client.post.assert_called_once()
        assert results['changed'] is False
        assert results['message'] == 'Validating configuration process succeeded.'
