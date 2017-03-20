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


class CordovaPluginOCFDemoAppButtonToggleTest(oeRuntimeTest):
    '''Automatize the Cordova plugin OCF demo app tests like
    checking if the resources are found, and resource information is readonly.
    '''
    pkg_id = 'com.example.CordovaPluginOcfDemo'
    button_toggle_item = None
    device_found = False
    resource_found = False

    details_btn = None
    id_item = None
    button_toggle_value_item = None
    button_toggle_value = None

    appmgr = AppMgr()

    @classmethod
    def setUpClass(cls):
        '''
        Launch the app and find the OCF resources.
        '''
        cls.appmgr.kill_app(cls.pkg_id)
        cls.appmgr.launch_app(cls.pkg_id)
        time.sleep(data_settings.app_launch_and_wait)


    def init_button_toggle_sensor(self):
        '''
        Go to the detailed page of the OCF resource.
        '''
        self.button_toggle_item = d(className='android.view.View', descriptionContains='Path: /a/button')
        self.button_toggle_item.click()
        time.sleep(1)

        self.details_btn = d(className='android.widget.Button')
        self.id_item = d(className='android.view.View', descriptionStartsWith='id')
        self.button_toggle_value_item = d(className='android.view.View', descriptionStartsWith='value')
        self.button_toggle_value = self.button_toggle_value_item.description.split(':')[-1].strip()


    def test_button_toggle_resource_found(self):
        '''Check if the button toggle resources can be found.'''
        self.appmgr.go_to_resources_for_ocfdemo()
        time.sleep(data_settings.app_found_res_and_wait)

        self.resource_found = d.exists(className='android.view.View', descriptionContains='/a/button')
        self.assertTrue(self.resource_found, 'The button toggle resource is not found.')


    def test_button_toggle_resource_properties_readonly(self):
        '''Check if the properties of the button toggle resources are readonly.'''
        self.init_button_toggle_sensor()

        self.assertEqual(len(self.details_btn), 1, 'The properties of button toggle are not readonly.')
        self.assertEqual(self.id_item.description.split(':')[-1].strip(), 'button', 
                        'Id of button resource not found.')
        self.assertEqual(self.button_toggle_value, 'false', 'Initial button toggle value is not false!')


    def test_button_toggle_z_device_found(self):
        '''Check if the OCF device can be found.'''
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

