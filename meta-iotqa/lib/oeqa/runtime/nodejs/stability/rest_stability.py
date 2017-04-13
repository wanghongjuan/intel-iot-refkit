#!/usr/bin/env python3

import os
import sys
import time
import json
import subprocess
import urllib.parse

from oeqa.oetest import oeRuntimeTest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'restapiserver'))
import copy_necessary_files
import restapi_case_config

class RestApiStabilityTest(oeRuntimeTest):

    case_config = restapi_case_config.RestApiCaseConfiguration()
    test_times = 10
    res_uuid = None
    query_res_url = None
    response = None
    # test time for the stability cases, in hour
    test_duration = 4

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
        cls.find_res_uuid('/a/led')

    def test_rest_stability_with_int_exit(self):
        '''
        Kill with SIGINT and restart it.
        Then send a REST request again and find only one OCF resource.
        '''
        start = time.time()
        while True:
            self.check_query_request_test()
            self.check_restart_and_discovery_test('-INT')
            self.check_query_request_test()

            end = time.time()
            duration = end - start
            if duration > self.test_duration * 3600:
                break

    def test_rest_stability_with_term_exit(self):
        '''
        Kill with SIGTERM and restart it.
        Then send a REST request again and find only one OCF resource.
        '''
        start = time.time()
        while True:
            self.check_query_request_test()
            self.check_restart_and_discovery_test('-TERM')
            self.check_query_request_test()

            end = time.time()
            duration = end - start
            if duration > self.test_duration * 3600:
                break

    def check_query_request_test(self):
        '''
        Check /api/oic/a/led?di=<xxx>
        '''
        query_resp = self.case_config.session.get(self.query_res_url)
        status = query_resp.status_code
        self.assertEqual(200, status, 'Response error!')

    def check_restart_and_discovery_test(self, signal):
        '''
        Shutdown the OCF server: 
            Check /api/oic/a/led?di=<xxx>
        Restart the OCF server:
            Check /api/oic/res
        '''
        # Close LED resource with SIGINT and the resource should disappear
        self.case_config.kill_ocf_server(self.target, 'led.js', signal)
        time.sleep(self.case_config.wait_kill_ocf_server)

        query_status_cmd = 'curl -s -o /dev/null -w %{http_code} --noproxy "*" ' + self.query_res_url
        query_proc = subprocess.Popen(query_status_cmd.split(),stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        query_proc.wait()
        status = query_proc.stdout.read().strip().decode('utf8')
        self.assertEqual('404', status, 'OCF server is down, the resource should disappear!')

        # Restart
        self.case_config.launch_ocf_server(self.target.ip, 'led.js')
        time.sleep(self.case_config.wait_launch_ocf_server)
        response = self.case_config.session.get(self.case_config.url_oic_res.format(ip = self.target.ip))
        status = response.status_code
        self.assertEqual(200, status, 'Response error!')

        ledHrefNum = 0
        ledRt = ''

        data = response.content
        resources = json.loads(data.decode('utf8'))
        for resource in resources:
            if resource.get('links')[0].get('href') == '/a/led':
                ledHrefNum += 1
                ledRt = resource.get('links')[0].get('rt')
        self.assertEqual(1, ledHrefNum, 'Only one LED resource should be found!')
        self.assertEqual('oic.r.led', ledRt)

    @classmethod
    def find_res_uuid(cls, res_path):
        '''
        Find a resource uuid with res_path.
        '''
        cls.response = cls.case_config.session.get(cls.case_config.url_oic_res.format(ip = cls.tc.target.ip))
        data = cls.response.content
        resources = json.loads(data.decode('utf8'))
        for resource in resources:
            if resource.get('links')[0].get('href') == res_path:
                cls.res_uuid = resource.get('di')
        if cls.res_uuid:
            cls.query_res_url = urllib.parse.urljoin(cls.case_config.url_oic_res.format(
                                                    ip = cls.tc.target.ip),
                                                    'a/led?di={uuid}'.format(uuid = cls.res_uuid))
        print(cls.query_res_url)

    @classmethod
    def tearDownClass(cls):
        '''
        Clean up work.
        '''
        cls.case_config.kill_ocf_server(cls.tc.target, 'led.js')
        time.sleep(cls.case_config.wait_kill_ocf_server)

        cls.case_config.clean_up(cls.tc.target)