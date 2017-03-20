#!/usr/bin/env python3

import os
import sys
import time
import subprocess

from uiautomator import device as d
from uiautomator import JsonRPCError

from oeqa.oetest import oeRuntimeTest

sys.path.append(os.path.dirname(__file__))
from appmgr import AppMgr
import data_settings


class CordovaPluginOCFDemoAppTemperatureTest(oeRuntimeTest):
    '''Automatize the Cordova plugin OCF demo app tests like
    checking if the resources are found, and resource information is readonly.'''

    pkg_id = 'com.example.CordovaPluginOcfDemo'
    temperature_item = None
    device_found = False
    resource_found = False

    details_btn = None
    id_item = None
    range_item = None
    temperature_value_item = None
    temperature_value = 0.0
    units_item = None

    appmgr = AppMgr()

    @classmethod
    def setUpClass(cls):
        '''
        Launch the app and find the OCF resources.
        '''
        cls.appmgr.kill_app(cls.pkg_id)
        cls.appmgr.launch_app(cls.pkg_id)
        time.sleep(data_settings.app_launch_and_wait)


    def init_temperature_sensor(self):
        '''
        Go to the detailed page of the OCF resource.
        '''
        self.temperature_item = d(className='android.view.View', descriptionContains='Path: /a/temperature')
        self.temperature_item.click()
        time.sleep(1)

        self.details_btn = d(className='android.widget.Button')
        self.id_item = d(className='android.view.View', descriptionStartsWith='id')
        self.range_item = d(className='android.view.View', descriptionStartsWith='range')
        self.temperature_value_item = d(className='android.view.View', descriptionStartsWith='temperature')
        self.temperature_value = float(self.temperature_value_item.description.split(':')[-1].strip())

        self.units_item = d(className='android.view.View', descriptionStartsWith='units')


    def test_temeperature_resource_found(self):
        '''Check if the temperature resources can be found.'''
        self.appmgr.go_to_resources_for_ocfdemo()
        time.sleep(data_settings.app_found_res_and_wait)

        self.resource_found = d.exists(className='android.view.View', descriptionContains='/a/temperature')
        self.assertTrue(self.resource_found, 'The temperature resource is not found.')


    def test_temeperature_resource_properties_readonly(self):
        '''Check if the properties of temperature resources are readonly.'''
        self.init_temperature_sensor()

        self.assertEqual(len(self.details_btn), 1, 'The properties of temperature are not readonly.')
        self.assertEqual(self.id_item.description.split(':')[-1].strip(), 'temperature', 
                        'Device of temperature resource not found.')
        self.assertEqual(self.range_item.description.split(':')[-1].strip(), '-40,125',
                        'Temperature range is invalid.')
        self.assertTrue(self.temperature_value > 10.0, 'Temperature value seems not sensible in Zhizu1 Lab.')
        self.assertTrue(self.units_item.description.split(':')[-1].strip() in ('C', 'F', 'K'),
                        'Temperature units is invalid.')


    def test_temeperature_z_device_found(self):
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

