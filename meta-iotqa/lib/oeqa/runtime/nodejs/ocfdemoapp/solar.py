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

class CordovaPluginOCFDemoAppSolarTest(oeRuntimeTest):
    '''Automatize the Cordova plugin OCF demo app tests like
    checking if the resources are found, and resource information is readonly.
    '''
    pkg_id = 'com.example.CordovaPluginOcfDemo'
    solar_item = None
    device_found = False
    resource_found = False

    details_btn = None
    id_item = None
    lcd1_item = None
    lcd2_item = None
    simu_item = None
    solar_value_item = None
    solar_value = None

    appmgr = AppMgr()

    @classmethod
    def setUpClass(cls):
        '''
        Launch the app and find the OCF resources.
        '''
        cls.appmgr.kill_app(cls.pkg_id)
        cls.appmgr.launch_app(cls.pkg_id)
        time.sleep(data_settings.app_launch_and_wait)


    def init_solar_sensor(self):
        '''
        Go to the detaisolar page of the OCF resource.
        '''
        self.solar_item = d(className='android.view.View', descriptionContains='Path: /a/solar')
        self.solar_item.click()
        time.sleep(1)

        self.details_btn = d(className='android.widget.Button')
        self.id_item = d(className='android.view.View', descriptionStartsWith='id')
        self.lcd1_item = d(className='android.view.View', descriptionStartsWith='lcd1')
        self.lcd2_item = d(className='android.view.View', descriptionStartsWith='lcd2')
        self.simu_item = d(className='android.view.View', descriptionStartsWith='simulationMode')
        self.solar_value_item = d(className='android.view.View', index=17).child(className='android.view.View', index=1)
        self.solar_value = self.solar_value_item.description


    def test_solar_resource_found(self):
        '''Check if the solar resources can be found.'''
        self.appmgr.go_to_resources_for_ocfdemo()
        time.sleep(data_settings.app_found_res_and_wait)

        self.resource_found = d.exists(className='android.view.View', descriptionContains='/a/solar')
        self.assertTrue(self.resource_found, 'The solar resource is not found.')


    def test_solar_resource_has_properties(self):
        '''Check if the solar resource has properties like id and value.'''
        self.init_solar_sensor()

        self.assertEqual(len(self.details_btn), 3)
        self.assertEqual(self.id_item.description.split(':')[-1].strip(), 'solar', 
                         'Id of solar resource not found.', )
        self.assertEqual(self.lcd1_item.description.split(':')[-1].strip(), 'Solar Connected!!',
                         'LCD1 text is empty!')
        self.assertEqual(self.lcd2_item.description.split(':')[-1].strip(), '',
                         'LCD2 text is not empty!')
        self.assertEqual(self.solar_value, '0', 'solar value is empty!')


    def test_solar_z_device_found(self):
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

