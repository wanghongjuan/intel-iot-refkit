#!/usr/bin/env python3

import os
import sys
import time
import json

from oeqa.oetest import oeRuntimeTest

sys.path.append(os.path.dirname(__file__))
import copy_necessary_files
import restapi_case_config

class RestApiOneOcfServerTest(oeRuntimeTest):
    
    case_config = restapi_case_config.RestApiCaseConfiguration()

    @classmethod
    def setUpClass(cls):
        '''
        Launch the OCF server on target device.
        '''
        if cls.case_config.need_copy_files:
            copy_necessary_files.copy_smarthome_demo_ocf_server(cls.tc.target.ip)

        cls.case_config.launch_ocf_server(cls.tc.target.ip, 'led.js')
        time.sleep(cls.case_config.wait_launch_ocf_server)

        cls.case_config.prepare_test(cls.tc.target)
        cls.case_config.send_multi_requests(cls.tc.target.ip, 2)

    def test_unique_ocf_device_remote(self):
        '''
        Send REST request again and find only one OCF device.
        '''
        response = self.case_config.session.get(self.case_config.url_oic_d.format(ip = self.target.ip))
        data = response.content
        devices = json.loads(data.decode('utf8'))

        self.assertEqual(1, len(devices), 'Only one OCF device should be found!')
        self.assertEqual('Smart Home LED', devices[0].get('n'))

    def test_unique_ocf_platform_remote(self):
        '''
        Send a REST request again and find only one OCF platform.
        '''
        response = self.case_config.session.get(self.case_config.url_oic_p.format(ip = self.target.ip))
        data = response.content
        platforms = json.loads(data.decode('utf8'))

        self.assertEqual(1, len(platforms), 'Only one OCF platform should be found!')
        self.assertEqual('Intel', platforms[0].get('mnmn'))

    def test_unique_ocf_resource_remote(self):
        '''
        Send a REST request again and find only one OCF resource.
        '''
        response = self.case_config.session.get(self.case_config.url_oic_res.format(ip = self.target.ip))
        data = response.content
        resources = json.loads(data.decode('utf8'))

        ledHrefNum = 0
        ledRt = ''

        for resource in resources:
            if resource.get('links')[0].get('href') == '/a/led':
                ledHrefNum += 1
                ledRt = resource.get('links')[0].get('rt')

        self.assertEqual(1, ledHrefNum, 'Only one LED resource should be found!')
        self.assertEqual('oic.r.led', ledRt)

    @classmethod
    def tearDownClass(cls):
        '''
        Clean up work.
        '''
        cls.case_config.kill_ocf_server(cls.tc.target, 'led.js')
        time.sleep(cls.case_config.wait_kill_ocf_server)

        cls.case_config.clean_up(cls.tc.target)