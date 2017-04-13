#!/usr/bin/env python3

import os
import sys
import json
import time

import requests
from oeqa.oetest import oeRuntimeTest

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                'restapiserver'))
import restapi_case_config


class OcfSimulatedModeTest(oeRuntimeTest):
    '''
    Tests for OCF servers running in simulated mode.
    '''
    sh_demo = '/tmp/SmartHome-Demo'
    sh_demo_url = 'https://github.com/01org/SmartHome-Demo.git'
    target_sh_demo = '/home/root/SmartHome-Demo/'
    case_config = restapi_case_config.RestApiCaseConfiguration()

    @classmethod
    def setUpClass(cls):
        '''Prepare work before the tests'''
        if not os.path.exists(cls.sh_demo):
            os.system('cd {0};git clone --depth 1 --single-branch --branch master {1}'.format(
                        cls.sh_demo,
                        cls.sh_demo_url))
        else:
            os.system('cd {0};git pull'.format(cls.sh_demo))
        os.system('ssh root@{0} "test -d {1} || mkdir -pv {2}"'.format(
                    cls.tc.target.ip, cls.target_sh_demo, cls.target_sh_demo))
        os.system('cd {0};scp -r ocf-servers root@{1}:{2}/'.format(
                    cls.sh_demo, cls.tc.target.ip, cls.target_sh_demo))
        cls.case_config.prepare_test(cls.tc.target)
        time.sleep(2)

    def launch_ocf_server(self, ocf_server, simulated = True):
        '''Launch the OCF server in simulated mode'''
        self.case_config.launch_ocf_server(self.target.ip, ocf_server, simulated)

    def test_ocf_server_ambient_light(self):
        self.check_response('ambient_light.js', 'Illuminance Sensor', '/a/illuminance')        
    
    def test_ocf_server_button(self):
        self.check_response('button.js', 'Button Sensor', '/a/button')

    def test_ocf_server_button_toggle(self):
        self.check_response('button-toggle.js', 'Button Toggle Sensor', '/a/button')

    def test_ocf_server_buzzer(self):
        self.check_response('buzzer.js', 'Buzzer', '/a/buzzer')

    def test_ocf_server_environmental_sensor(self):
        self.check_response('environmental_sensor.js','Environmental Sensor', '/a/env')        

    def test_ocf_server_fan(self):
        self.check_response('fan.js', 'Fan', '/a/fan') 

    def test_ocf_server_gas(self):
        self.check_response('gas.js', 'Gas Sensor', '/a/gas')

    def test_ocf_server_led(self):
        self.check_response('led.js', 'LED', '/a/led')

    def test_ocf_server_motion(self):
        self.check_response('motion.js', 'Motion Sensor', '/a/pir')
    
    def test_ocf_server_power_uart(self):
        self.check_response('power-uart.js', 'Energy Consumption', '/a/power')    

    def test_ocf_server_rgb_led(self):
        self.check_response('rgb_led.js', 'RGB LED', '/a/rgbled')

    def test_ocf_server_solar(self):
        self.check_response('solar.js', 'Solar', '/a/solar')

    def test_ocf_server_switch(self):
        self.check_response('switch.js', 'Binary Switch', '/a/binarySwitch')             

    def test_ocf_server_temperature(self):
        self.check_response('temperature.js', 'Temperature Sensor', '/a/temperature') 

    def check_response(self, ocf_server, device_name, resource_type, platform_name = 'Intel'):
        '''Launch the OCF server and discovery it via REST API.
        '''
        self.launch_ocf_server(ocf_server)
        time.sleep(2)
        
        resp_d = self.case_config.session.get(self.case_config.url_oic_d.format(ip = self.target.ip))
        devices = json.loads(resp_d.content.decode('utf8'))
        led_device_found = False
        for device in devices:
            if device.get('n') == 'Smart Home ' + device_name:
                led_device_found = True
        self.assertTrue(led_device_found, 'OCF device not found!')

        resp_p = self.case_config.session.get(self.case_config.url_oic_p.format(ip = self.target.ip))
        platforms = json.loads(resp_p.content.decode('utf8'))
        led_platform_found = False
        for platform in platforms:
            if platform.get('mnmn') == platform_name:
                led_platform_found = True
        self.assertTrue(led_platform_found, 'OCF platform not found!')

        resp_res = self.case_config.session.get(self.case_config.url_oic_res.format(ip = self.target.ip))
        resources = json.loads(resp_res.content.decode('utf8'))
        led_resource_found = False
        for resource in resources:
            if resource.get('links')[0].get('href') == resource_type:
                led_resource_found = True
        self.assertTrue(led_resource_found, 'OCF resource not found!')

        self.kill_ocf_server(ocf_server)

    def kill_ocf_server(self, ocf_server):
        '''Kill the OCF server process'''
        self.case_config.kill_ocf_server(self.target, ocf_server)

    @classmethod
    def tearDownClass(cls):
        '''Clean up'''
        cls.case_config.close_ports_for_cleanup(cls.tc.target)