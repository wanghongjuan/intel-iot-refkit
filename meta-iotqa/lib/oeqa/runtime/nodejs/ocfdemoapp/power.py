#!/usr/bin/power python3

import os
import sys
import time
import subprocess

from uiautomator import device as d

from oeqa.oetest import oeRuntimeTest

sys.path.append(os.path.dirname(__file__))
from appmgr import AppMgr
import data_settings


class CordovaPluginOCFDemoAppPowerTest(oeRuntimeTest):
    '''Automatize the Cordova plugin OCF demo app tests like
    checking if the resources are found, and resource information is readonly.
    '''
    pkg_id = 'com.example.CordovaPluginOcfDemo'
    power_item = None
    device_found = False
    resource_found = False

    details_btn = None
    power1_item = None
    power1_value = 0.0
    id_item = None
    power2_item = None
    power2_value = 0.0

    appmgr = AppMgr()

    @classmethod
    def setUpClass(cls):
        '''
        Launch the app and find the OCF resources.
        '''
        cls.appmgr.kill_app(cls.pkg_id)
        cls.appmgr.launch_app(cls.pkg_id)
        time.sleep(data_settings.app_launch_and_wait)


    def init_power_sensor(self):
        '''
        Go to the detaipower page of the OCF resource.
        '''
        self.power_item = d(className='android.view.View', descriptionContains='Path: /a/power')
        self.power_item.click()
        time.sleep(1)

        self.details_btn = d(className='android.widget.Button')
        self.power1_item = d(className='android.view.View', descriptionStartsWith='power1')
        self.power1_value = float(self.power1_item.description.split(':')[-1].strip())

        self.id_item = d(className='android.view.View', descriptionStartsWith='id')

        self.power2_item = d(className='android.view.View', descriptionStartsWith='power2')
        self.power2_value = float(self.power2_item.description.split(':')[-1].strip())


    def test_power_resource_found(self):
        '''Check if the power resources can be found.'''
        self.appmgr.go_to_resources_for_ocfdemo()
        time.sleep(data_settings.app_found_res_and_wait)

        self.resource_found = d.exists(className='android.view.View', descriptionContains='/a/power')
        self.assertTrue(self.resource_found, 'The power resource is not found.')


    def test_power_resource_has_properties(self):
        '''Check if the power resource has properties like id and value.'''
        self.init_power_sensor()

        self.assertEqual(len(self.details_btn), 1)
        self.assertEqual(self.id_item.description.split(':')[-1].strip(), 'power',
                         'Id of power resource not found.', )
        self.assertTrue(self.power1_value >= 0.0, 'power1 value seems not sensible')
        self.assertTrue(self.power2_value >= 0.0, 'power2 value seems not sensible')


    def test_power_z_device_found(self):
        ''''Check if the OCF device can be found.'''
        self.appmgr.go_to_devices_for_ocfdemo()
        time.sleep(data_settings.app_found_dev_and_wait)

        self.device_found = d.exists(descriptionContains='UUID')
        self.device_found = self.device_found and d.exists(descriptionContains='URL')
        self.device_found = self.device_found and d.exists(descriptionContains='Name')
        self.device_found = self.device_found and d.exists(descriptionContains='Data models')
        self.device_found = self.device_found and d.exists(descriptionContains='Core spec version')
        self.device_found = self.device_found and d.exists(descriptionContains='Role')

        self.assertTrue(self.device_found, 'OCF device is not found.')


    @classmethod
    def tearDownClass(cls):
        '''Terminate the app.'''
        cls.appmgr.kill_app(cls.pkg_id)

