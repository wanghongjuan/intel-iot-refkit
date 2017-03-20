#!/usr/bin/env python3

import os
import sys
import time
import subprocess

from uiautomator import device as d
sys.path.append(os.path.dirname(__file__))
from appmgr import AppMgr

from oeqa.oetest import oeRuntimeTest


class OCFDemoAppBuildAndLaunchTest(oeRuntimeTest):
    '''
    Build/Install/Launch the CordovaPluginOCFDemo app.
    '''
    workspace_dir = os.path.dirname(__file__)
    cordova_pluin_ocf_demo_url = 'https://github.com/siovene/cordova-plugin-ocf-demo.git'
    pkg_id = 'com.example.CordovaPluginOcfDemo'
    repo_dir = 'cordova-plugin-ocf-demo'
    prj_dir = os.path.join(workspace_dir, repo_dir)
    apk_path = 'platforms/android/build/outputs/apk/android-debug.apk'

    clean_up = False
    uninstall_app = False
    appmgr = AppMgr()

    def setUp(self):
        '''
        Check if the grunt-cli and bower are installed. Install them globally if not.
        '''
        self.appmgr.uninstall_app(self.pkg_id)

        cli_cmd = ['grunt', 'bower']
        for cmd in cli_cmd:
            detect_cmd = ['which'] + [cmd]
            proc = subprocess.Popen(detect_cmd, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
            proc.wait()

            if proc.returncode != 0:
                if cmd == 'grunt':
                    cli = 'grunt-cli'
                else:
                    cli = cmd
                print('{} not installed, install it...'.format(cli))
                proc_cli = subprocess.Popen(['sudo', '-E', 'npm', cli, '-g'])
                proc_cli.communicate()

            else:
                print('{} has been installed'.format(cmd))

        detect_dev = ['adb', 'devices']
        proc_adb = subprocess.Popen(detect_dev, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
        proc_adb.wait()

        adb_info = proc_adb.stdout.read().decode('utf8').strip()
        if proc_adb.returncode != 0 or not adb_info.endswith('device'):
            print('Please check if the android device is connected to the host.')


    def test_ocfdemo_build_install_launch(self):
        '''
        Check if there're any errors during the following steps:
        1. git clone the cordova-plugin-ocf-demo
        2. build the app
        3. install and launch it
        '''
        clone_cmd = ['git', 'clone', '--depth', '1', '--single-branch', '--branch', 'master', 
                    self.cordova_pluin_ocf_demo_url]
        clone_proc = subprocess.Popen(clone_cmd, cwd = self.workspace_dir)
        clone_proc.wait()

        self.assertEqual(clone_proc.returncode, 0, 'clone the cordova_pluin_ocf_demo failed.')

        build_cmds = [['npm', 'install'], ['bower', 'install'], 
                    ['grunt', 'platform:add:android'], ['grunt', 'build']]
        for build_cmd in build_cmds:
            build_proc = subprocess.Popen(build_cmd, cwd = self.prj_dir)
            build_proc.wait()

            self.assertEqual(build_proc.returncode, 0, 'Failed to build when running [{0}]'.format(build_cmd))

        self.assertTrue(os.path.exists(self.prj_dir), 'cordova-plugin-ocf-demo apk is not found!')
        install_cmd = ['adb', 'install',  self.apk_path]
        install_proc = subprocess.Popen(install_cmd, cwd = self.prj_dir)
        install_proc.wait()

        self.assertEqual(install_proc.returncode, 0, 'Failed to install OCF Demo apk')

        self.appmgr.launch_app(self.pkg_id)
        time.sleep(5)

        btn = d(className='android.widget.Button', index=0)
        btn.click()

        title_found = d.exists(className='android.view.View', descriptionContains='OCF Demo')
        self.assertTrue(title_found, 'Launching the app OK?')


    def tearDown(self):
        '''
        Remove the cordova-plugin-ocf-demo project as it not needed any more.
        '''
        if self.clean_up:
            os.chdir(self.workspace_dir)
            os.system('rm -fr {}'.format(self.repo_dir))

        if self.uninstall_app:
            self.appmgr.uninstall_app(self.pkg_id)
        