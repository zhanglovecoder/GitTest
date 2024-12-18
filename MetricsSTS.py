import subprocess
import os
import time
import re
import sys
import numpy as np
import logging
import time
from uiautomator import Device
# Check if the device is connected properly
DevicesIP = input("Enter the ip or DSN of the device you want to test:")
d = Device(DevicesIP)
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The TV IP to be tested is : %s" % DevicesIP)
assert subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c', ('adb -s %s shell logcat -v threadtime >>STS_Metrics_logcat.log' % DevicesIP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE), 'Failed::Can not open logcat Thermal,please check'
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'The terminal about logcat_logs in has been opened')
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'Start the SOC Thermal Shutdown test for Metrcis')
devicesconnect = os.popen('adb devices').read()#Considering multi device testing and stability, changes are needed
assert DevicesIP in devicesconnect, 'Failed::Test TV not connect success,so please check'
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The information of the connected devices is : %s" % devicesconnect)
devicesName = os.popen('adb -s %s shell "getprop | grep "ro.product.name""' % DevicesIP).read()
devicepattern = r'\[(.*?)\]'
deviceresult = re.findall(devicepattern, devicesName)
devicesVersion = os.popen('adb -s %s shell "getprop | grep "ro.build.version.fireos""' % DevicesIP).read()
Versionresult = re.findall(devicepattern, devicesVersion)
TvVersion = Versionresult[-1]
TvName = deviceresult[-1]
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The TV TvVersion to be tested is : %s" % TvVersion)
assert TvName is not None, 'Fail::Unable to obtain the name of the TV, please check'
#d.watcher("AUTO_FC_WHEN_ANR").when(text="(?i)can\'t find remote").click(text="OK")

#Japan device ranges are not supported
japan_tv_region = {
    'colorado',
    'colorado-H',
    'montana',
    'nevada'
}

#Some device ranges are not supported
tv_region = {
    'maribronze',
    'shine',
    'vale',
    'almond',
    'grove',
    'meridian',
    'hazel',
    'goldfinsh',
    'wyoming',
    'lassen'
}

#Restart the device and connect it
def DevicesRebootcheck(Rebootcommand):
    if devicesconnect is not None:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The name of the connected devices is : %s" % TvName)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'Now,will Start reboot devices')
        time.sleep(3)
        os.popen(Rebootcommand).read()
        start_time = time.time()
        time.sleep(60)
        while True:
            assert time.time() - start_time < 300, 'Fail::Abnormal connection after device restart, please check'
            if(DevicesIP not in devicesconnect):
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"devices is not connect : %s" % devicesconnect,"Will retry connect")
                time.sleep(10)
                Resultconnect = os.popen('adb connect %s' % DevicesIP).read()
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"devices retry connect : %s" % Resultconnect)
            else:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"reboot connect success : %s" % devicesconnect)
                break
    else:
        assert devicesconnect is not None, 'Fail::No device connected, please check the connection of the device'
Rebootcommand = ('adb -s %s shell "reboot"' % DevicesIP)
DevicesRebootcheck(Rebootcommand)

#Prevent device from entering offline after restarting, so check
while True:
    TV_Online_Check = os.popen('adb devices | grep %s' % DevicesIP).read()
    if 'offline' in TV_Online_Check:
        ConnectResult = os.popen('adb -s %s reconnect' % DevicesIP).read()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The device is in an offline state after restarting, so reconnecting is in progress : %s' % ConnectResult)
        time.sleep(20)
        os.popen('adb connect %s' % DevicesIP)
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'Now,devices is reconnect ok and devices online')
        os.popen('adb connect %s' % DevicesIP)
        break
while True:
    os.popen('adb connect %s' % DevicesIP)
    Result_Home = os.popen('adb -s %s shell "getprop sys.boot_completed"' % DevicesIP).read()
    if '1' in Result_Home:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The device has been sys.boot_completed')
        break
    else:
        os.system('adb -s %s shell "input keyevent KEYCODE_HOME"' % DevicesIP)
        time.sleep(3)
assert subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c', ('adb -s %s shell logcat -v threadtime >>STS_Metrics_logcat.log' % DevicesIP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE), 'Failed::Can not open logcat Thermal,please check'
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal about logcat_logs in has been opened')
#Confirm on the Home interface
for x in range(3):
    os.system('adb -s %s shell "input keyevent KEYCODE_HOME"' % DevicesIP)
    time.sleep(3)

#starting temperature check and heating up
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'starting temperature check and heating up')
start_time_TvName = time.time()
if TvName in tv_region:
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The device is in tv_region TV, so other functions are used to execute it')
    if "8" in TvVersion:
        point_result0 = os.popen('adb -s %s shell "echo 2000 > /sys/class/thermal/thermal_zone0/trip_point_0_temp"' % DevicesIP).read()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'point_o_result high temperature:point_0_temp%s' % point_result0)
        time.sleep(60)
        point_result1 = os.popen('adb -s %s shell "echo 2000 > /sys/class/thermal/thermal_zone0/trip_point_1_temp"' % DevicesIP)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'point_o_result high temperature:point_1_temp%s' % point_result1)
        time.sleep(60)
        DevicesKeyvalueC(Keyvalue_command, Keyvalue_pattern)
        def DevicesRebootcheck(Rebootcommand):
            process = subprocess.Popen(Rebootcommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'point_o_result high temperature:point_2_temp:%s' % DevicesIP)
            time.sleep(60)
            if devicesconnect is not None:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The name of the connected devices is : %s" % TvName)
                time.sleep(60)
                start_time_Reboot = time.time()
                while True:
                    assert time.time() - start_time_Reboot < 300,'Fail::device reboot connected time out, please check the connection of the device'
                    if (DevicesIP not in devicesconnect):
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"devices is not connect : %s" % devicesconnect, "Will retry connect")
                        time.sleep(10)
                        Resultconnect = os.popen('adb connect %s' % DevicesIP).read()
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"devices retry connect : %s" % Resultconnect)
                    else:
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"reboot connect success : %s" % devicesconnect)
                        break
            else:
                assert devicesconnect is not None, 'Fail::No device connected, please check the connection of the device'
        Rebootcommand = ('adb -s %s shell "echo 2000 > /sys/class/thermal/thermal_zone0/trip_point_2_temp"' % DevicesIP)
        DevicesRebootcheck(Rebootcommand)
        for x in range(3):
            resultReconnect = os.popen('adb connect %s' % DevicesIP).read()
            print(resultReconnect)
            time.sleep(2)
            # When devices reboot success ,start device test
        if not subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c',('adb -s %s shell logcat -v threadtime >>STS_Metrics_logcat.log' % DevicesIP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE):
            assert False, 'Can not open logcat Thermal,please check'
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal about logcat_logs in has been opened')
        if not subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c', ('adb -s %s logcat -b vitals -v time | grep Screen_On_Thermal' % DevicesIP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE):
            assert False, 'Can not open vitals time Thermal,please check'
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal interface for intercepting logs in Vitals has been opened')
        if not subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c', ('adb -s %s logcat -b metrics -v time | grep Screen_On_Thermal' % DevicesIP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE):
            assert False, 'Can not open metrics time Thermal,please check'
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal interface for intercepting logs in metrics has been opened')
        time.sleep(3)
        #When devices reboot success ,start device test
        for x in range(3):
            os.popen('adb -s %s shell "input keyevent KEYCODE_HOME"' % DevicesIP)
            time.sleep(2)
        def DevicesKeyvalueA(Keyvalue_command, Keyvalue_pattern):
            os.system("adb -s %s shell ps | grep logd | awk '{print $2}' | xargs adb -s %s shell kill -s SIGUSR1" % (DevicesIP, DevicesIP))
            time.sleep(5)
            process = subprocess.Popen(Keyvalue_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            while True:
                output = process.stdout.readline().decode('utf-8')
                if output:
                    if re.search(Keyvalue_pattern, output):
                        resultgrep = (output.strip())
                        if resultgrep is not None:
                            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'start devices getlog')
                            os.system('./get_logs.sh -D %s STS_Metrics_getlog.log' % DevicesIP)
                            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'PASS:1/1 The devices related to testing STS in tv_region have successfully run the instructions. Please check the results')
                            break
            return process.returncode
        Keyvalue_command = ("adb -s %s logcat -b metrics -v time" % DevicesIP)
        Keyvalue_pattern = "Thermal_Shutdown"
        DevicesKeyvalueA(Keyvalue_command, Keyvalue_pattern)
        sys.exit(0)
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'The device is not in 8.0 Version,is Version 7.0,so go on other Version test')
        point_result0 = os.popen('adb -s %s shell "echo 2000 > /sys/class/thermal/thermal_zone0/trip_point_0_temp"' % DevicesIP).read()
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'point_o_result high temperature:point_0_temp%s' % point_result0)
        time.sleep(60)
        point_result1 = os.popen('adb -s %s shell "echo 2000 > /sys/class/thermal/thermal_zone0/trip_point_1_temp"' % DevicesIP)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'point_o_result high temperature:point_1_temp%s' % point_result1)
        time.sleep(60)
        point_result2 = os.popen('adb -s %s shell "echo 2000 > /sys/class/thermal/thermal_zone0/trip_point_2_temp"' % DevicesIP)
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'point_o_result high temperature:point_2_temp%s' % point_result2)
        time.sleep(60)
        def DevicesRebootcheck(Rebootcommand):
            process = subprocess.Popen(Rebootcommand, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'point_o_result high temperature:point_3_temp%s')
            time.sleep(60)
            if devicesconnect is not None:
                print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The name of the connected devices is : %s" % TvName)
                while True:
                    time.sleep(60)
                    if (DevicesIP not in devicesconnect):
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"devices is not connect : %s" % devicesconnect, "Will retry connect")
                        time.sleep(10)
                        Resultconnect = os.popen('adb connect %s' % DevicesIP).read()
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"devices retry connect : %s" % Resultconnect)
                    else:
                        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"reboot connect success : %s" % devicesconnect)
                        break
            else:
                assert False, 'Abnormal connection after device restart, please check'
        Rebootcommand = ('adb -s %s shell "echo 2000 > /sys/class/thermal/thermal_zone0/trip_point_3_temp"' % DevicesIP)
        DevicesRebootcheck(Rebootcommand)
        time.sleep(10)
        for x in range(3):
            resultReconnect = os.popen('adb connect %s' % DevicesIP).read()
            print(resultReconnect)
            time.sleep(2)
        if not subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c',('adb -s %s shell logcat -v threadtime >>STS_Metrics_logcat.log' % DevicesIP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE):
            assert False, 'Can not open logcat Thermal,please check'
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal about logcat_logs in has been opened')
        if not subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c', ('adb -s %s logcat -b vitals -v time | grep Screen_On_Thermal' % DevicesIP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE):
            assert False, 'Can not open vitals time Thermal,please check'
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal interface for intercepting logs in Vitals has been opened')
        if not subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c', ('adb -s %s logcat -b metrics -v time | grep Screen_On_Thermal' % DevicesIP)],stdout=subprocess.PIPE, stderr=subprocess.PIPE):
            assert False, 'Can not open metrics time Thermal,please check'
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal interface for intercepting logs in metrics has been opened')
        time.sleep(3)
        def DevicesKeyvalue(Keyvalue_command, Keyvalue_pattern):
            os.system('adb -s %s shell "echo 2000 > /sys/class/thermal/thermal_zone0/trip_point_2_temp"' % DevicesIP)
            time.sleep(5)
            process = subprocess.Popen(Keyvalue_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            while True:
                output = process.stdout.readline().decode('utf-8')
                if output:
                    if re.search(Keyvalue_pattern, output):
                        resultgrep = (output.strip())
                        if resultgrep is not None:
                            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'start devices getlog')
                            os.system('./get_logs.sh -D %s STS_Metrics_getlog.log' % DevicesIP)
                            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'PASS:1/1 The devices related to testing STS in tv_region have successfully run the instructions. Please check the results')
                            break
            return process.returncode
        Keyvalue_command = ("adb -s %s logcat -b metrics -v time" % DevicesIP)
        Keyvalue_pattern = "Thermal_Shutdown"
        DevicesKeyvalue(Keyvalue_command, Keyvalue_pattern)
        sys.exit(0)
else:
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The device is not in tv_region,so go on test')
#starting temperature check and heating up
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'starting temperature check and heating up')
def DevicesCputemp(Cputempcommand,Cpu_pattern):
    DevicesCputemp = os.popen(Cputempcommand).read()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The Devices temperature of each CPU is : %s" % DevicesCputemp)
    match_obj = re.findall(Cpu_pattern,DevicesCputemp)
    CPU_MAXtemp = max(match_obj)
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The Devices highest cpu temperature is : %s" % CPU_MAXtemp)
    if TvName in japan_tv_region:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The device is a Japanese TV, so other functions are used to execute it')
        if 30<=int(CPU_MAXtemp)<=40:
            os.popen('adb -s %s shell "echo 130 > /proc/mstar_dvfs/temperature"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 110 > /proc/mstar_dvfs/over_temp_debug")
        elif 40<=int(CPU_MAXtemp)<=50:
            os.popen('adb -s %s shell "echo 120 > /proc/mstar_dvfs/temperature"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 100 > /proc/mstar_dvfs/over_temp_debug")
        elif 50<=int(CPU_MAXtemp)<=60:
            os.popen('adb -s %s shell "echo 110 > /proc/mstar_dvfs/temperature"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 90 > /proc/mstar_dvfs/over_temp_debug")
        elif 60<=int(CPU_MAXtemp)<=70:
            os.popen('adb -s %s shell "echo 100 > /proc/mstar_dvfs/temperature"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 80 > /proc/mstar_dvfs/over_temp_debug")
        elif 70<=int(CPU_MAXtemp)<=80:
            os.popen('adb -s %s shell "echo 90 > /proc/mstar_dvfs/temperature"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 70 > /proc/mstar_dvfs/over_temp_debug")
        else:
            assert False, 'The TV CPU is not within the normal range, please check'
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The device is not Japanese TV, so normal functions are used to execute it')
        if 30<=int(CPU_MAXtemp)<=40:
            os.popen('adb -s %s shell "echo 130 > /proc/mstar_dvfs/over_temp_debug"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 110 > /proc/mstar_dvfs/over_temp_debug")
        elif 40<=int(CPU_MAXtemp)<=50:
            os.popen('adb -s %s shell "echo 120 > /proc/mstar_dvfs/over_temp_debug"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 100 > /proc/mstar_dvfs/over_temp_debug")
        elif 50<=int(CPU_MAXtemp)<=60:
            os.popen('adb -s %s shell "echo 110 > /proc/mstar_dvfs/over_temp_debug"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 90 > /proc/mstar_dvfs/over_temp_debug")
        elif 60<=int(CPU_MAXtemp)<=70:
            os.popen('adb -s %s shell "echo 100 > /proc/mstar_dvfs/over_temp_debug"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 80 > /proc/mstar_dvfs/over_temp_debug")
        elif 70<=int(CPU_MAXtemp)<=80:
            os.popen('adb -s %s shell "echo 90 > /proc/mstar_dvfs/over_temp_debug"' % DevicesIP)
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"The command executed is echo 70 > /proc/mstar_dvfs/over_temp_debug")
        else:
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Fail::The temperature of the TV CPU is not within the normal range")
            sys.exit()
    NewDevicesCputem = os.popen(Cputempcommand).read()
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"Now The Devices temperature of each CPU is : %s" % NewDevicesCputem)
Cputempcommand = ('adb -s %s shell "cat /proc/mstar_dvfs/temperature"' % DevicesIP)
Cpu_pattern = r'\d+'
DevicesCputemp(Cputempcommand,Cpu_pattern)

#TV CPU overheating causes connection check after restart
time.sleep(60)
while True:
    Rebootresult = os.popen('adb devices').read()
    if(DevicesIP not in devicesconnect):
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"devices is not connect : %s" % Rebootresult,"Will retry connect")
        time.sleep(10)
        Retryconnect = os.popen('adb connect %s' %DevicesIP).read()
        print(Retryconnect)
    else:
        print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),"reboot connect success : %s" % Rebootresult)
        break

#The heating operation is completed, start testing and capture logs
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The heating operation is completed, start testing and capture logs')
time.sleep(5)
subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c', 'adb logcat -b vitals -v time | grep Thermal_Shutdown'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal interface for intercepting logs in Vitals has been opened')
subprocess.Popen(['gnome-terminal', '-x', 'bash', '-c', 'adb logcat -b metrics -v time | grep Thermal_Shutdown'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),'The terminal interface for intercepting logs in metrics has been opened')

#Start judging the key value and searching for it
def DevicesKeyvalue(Keyvalue_command, Keyvalue_pattern):
    os.system("adb -s %s shell ps | grep logd | awk '{print $2}' | xargs adb -s %s shell kill -s SIGUSR1" % (DevicesIP, DevicesIP))
    time.sleep(5)
    process = subprocess.Popen(Keyvalue_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    while True:
        output = process.stdout.readline().decode('utf-8')
        if output:
            if re.search(Keyvalue_pattern, output):
                resultgrep = (output.strip())
                if resultgrep is not None:
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'start devices getlog')
                    os.system('./get_logs.sh -D %s STS_Metrics_getlog.log' % DevicesIP)
                    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'PASS:1/1 The devices related to testing STS in tv_region have successfully run the instructions. Please check the results')
                    break
    return process.returncode
Keyvalue_command = ("adb -s %s logcat -b metrics -v time" % DevicesIP)
Keyvalue_pattern = "Thermal_Shutdown"
DevicesKeyvalue(Keyvalue_command, Keyvalue_pattern)

#The entire test is over


