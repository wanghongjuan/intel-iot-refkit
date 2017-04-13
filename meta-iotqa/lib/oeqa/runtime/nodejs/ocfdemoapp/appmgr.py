#!/usr/bin/env python3

import time
import subprocess
from uiautomator import device as d


class AppMgr:
    in_main_panel = True


    def install_app(self, apk_path):
        '''
        Install an apk file specified by apk_path.
        '''
        install_cmd = 'adb install {}'.format(apk_path).split()
        p = subprocess.Popen(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()

    def uninstall_app(self, package_name):
        '''
        Unstall an apk file specified by apk_path.
        '''
        uninstall_cmd = 'adb uninstall {}'.format(package_name).split()
        p = subprocess.Popen(uninstall_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()



    def launch_app(self, package_name):
        '''
        Launch an app by the package id.
        '''
        launch_cmd = 'adb shell am start -n {pkg_id}/.MainActivity'.format(pkg_id=package_name).split()
        p = subprocess.Popen(launch_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()


    def kill_app(self, package_name):
        '''Terminate an app.'''
        exit_cmd = 'adb shell am force-stop {pkg_id}'.format(pkg_id=package_name).split()
        p = subprocess.Popen(exit_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.communicate()


    # def app_goes_to_bg(self):
    #     d.screen.back()

    def go_to_panel_for_ocfdemo(self, title):
        '''
        Switch to the the panel specified by the title.
        '''
        # print('found:' + str(d.exists(className='android.widget.Button', index=0)))
        side_bar_btn = d(className='android.widget.Button', index=0)
        side_bar_btn.click()

        res_btn = d(className='android.view.View', description=title)
        res_btn.click()


    def go_back(self):
        '''
        Go back to the main panel from the resource detail panel.
        '''
        # if not self.in_main_panel:
        back_btn = d(className='android.widget.Button', index=0)
        back_btn.click()


    def go_to_resources_for_ocfdemo(self):
        '''
        Switch to the resource pandel
        '''
        self.go_to_panel_for_ocfdemo('Resources')


    def go_to_devices_for_ocfdemo(self):
        # self.go_back()
        self.go_to_panel_for_ocfdemo('Devices')


    def open_continuous_discovery(self, package_name):
        '''
        Open the Continuous discovery switch and enable it.
        Return if it's set to True.
        '''
        self.launch_app(package_name)
        time.sleep(2)

        side_bar_btn = d(className='android.widget.Button', index=0)
        side_bar_btn.click()
        time.sleep(2)

        settings_btn = d(className='android.view.View', description='Settings')
        settings_btn.click()
        time.sleep(2)

        switch_btn = d(className='android.view.View', index=6)
        switch_btn.click()



# if __name__ == '__main__':
#     appmgr = AppMgr()
#     appmgr.open_continuous_discovery('com.example.CordovaPluginOcfDemo')

#     time.sleep(2)

