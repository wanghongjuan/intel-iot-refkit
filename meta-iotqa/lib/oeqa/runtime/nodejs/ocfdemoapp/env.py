#!/usr/bin/env python3

import os
import sys
import time
import subprocess

from uiautomator import device as d

from oeqa.oetest import oeRuntimeTest

sys.path.append(os.path.dirname(__file__))
from appmgr import AppMgr
import data_settings


class CordovaPluginOCFDemoAppEnvTest(oeRuntimeTest):
    '''Automatize the Cordova plugin OCF demo app tests like
    checking if the resources are found, and resource information is readonly.
    '''
    pkg_id = 'com.example.CordovaPluginOcfDemo'
    env_item = None
    device_found = False
    resource_found = False

    details_btn = None
    humidity_item = None
    humidity_value = 0.0
    id_item = None
    pressure_item = None
    pressure_value = 0.0
    temperature_item = None
    temperature_value = 0.0
    unindex_item = None
    uvindex_value = None

    appmgr = AppMgr()

    @classmethod
    def setUpClass(cls):
        '''
        Launch the app and find the OCF resources.
        '''
        cls.appmgr.kill_app(cls.pkg_id)
        cls.appmgr.launch_app(cls.pkg_id)
        time.sleep(data_settings.app_launch_and_wait)


    def init_env_sensor(self):
        '''
        Go to the detaienv page of the OCF resource.
        '''
        self.env_item = d(className='android.view.View', descriptionContains='Path: /a/env')
        self.env_item.click()
        time.sleep(1)

        self.details_btn = d(className='android.widget.Button')
        self.humidity_item = d(className='android.view.View', descriptionStartsWith='humidity')
        self.humidity_value = float(self.humidity_item.description.split(':')[-1].strip())

        self.id_item = d(className='android.view.View', descriptionStartsWith='id')

        self.pressure_item = d(className='android.view.View', descriptionStartsWith='pressure')
        self.pressure_value = float(self.pressure_item.description.split(':')[-1].strip())

        self.temperature_item = d(className='android.view.View', descriptionStartsWith='temperature')
        self.temperature_value = float(self.temperature_item.description.split(':')[-1].strip())

        self.uvindex_item = d(className='android.view.View', descriptionStartsWith='uvIndex')
        self.uvindex_value = int(self.uvindex_item.description.split(':')[-1].strip())


    def test_env_resource_found(self):
        '''Check if the env resources can be found.'''
        self.appmgr.go_to_resources_for_ocfdemo()
        time.sleep(data_settings.app_found_res_and_wait)

        self.resource_found = d.exists(className='android.view.View', descriptionContains='/a/env')
        self.assertTrue(self.resource_found, 'The environment resource is not found.')


    def test_env_resource_has_properties(self):
        '''Check if the env resource has properties like id and value.'''
        self.init_env_sensor()

        self.assertEqual(len(self.details_btn), 1)
        self.assertTrue(self.humidity_value >= 0.0, 'Invalid humidity number.')
        self.assertEqual(self.id_item.description.split(':')[-1].strip(), 'environmentalSensor',
                         'Id of env resource not found.', )
        self.assertTrue(self.pressure_value >= 1000.0, 'Pressure seems not sensible!')
        self.assertTrue(self.temperature_value >= 15.0, 'Temperature seems not sensible!')
        self.assertTrue(self.uvindex_value >= 0, 'env value is empty!')


    def test_env_z_device_found(self):
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

