import base64
import requests, json

from pyaes import *
from pyaes import aes

from common import *

import datetime
import os
import onionGpio
import threading
import time
import pickle

VERSION = '1.2'

class SMART_RELAY():
    def __init__(self):
        # init mac address
        self.macAddr = ''
        self.setMacAddr()
        self.reboot_signal = False

        self.startedTime_1 = 0
        self.startedTime_2 = 0
        self.startedTime_3 = 0
        self.autoTimeLimit_1 = 0
        self.autoTimeLimit_2 = 0
        self.autoTimeLimit_3 = 0
        self.isAutoMsg = -1

        # get server address and port
        self.server_ip, self.port = self.getServerInfo()
        
        self.URL = 'http://%s:%s/device/order/%s' % (self.server_ip, self.port, self.macAddr[-4:])
        self.headers = {'Content-Type': 'application/json'}
        self.runCommand = [
            {'mode': '0', 
            'schedule': '',
            'period': '',
            'autoModeMsg': '',
            'currentState': 0,
            'autoTimeLimit': 0},
            {'mode': '0', 
            'schedule': '',
            'period': '',
            'autoModeMsg': '',
            'currentState': 0,
            'autoTimeLimit': 0},
            {'mode': '0', 
            'schedule': '',
            'period': '',
            'autoModeMsg': '',
            'currentState': 0,
            'autoTimeLimit': 0}
        ]

        try:
            # init gpio ports
            self.relay1 = onionGpio.OnionGpio(15)
            self.relay2 = onionGpio.OnionGpio(16)
            self.relay3 = onionGpio.OnionGpio(17)
            self.waterSensor_H = onionGpio.OnionGpio(19)
            self.waterSensor_L = onionGpio.OnionGpio(18)
            self.network_led = onionGpio.OnionGpio(2)
            self.server_led = onionGpio.OnionGpio(3)
            self.waterSensor_H_led = onionGpio.OnionGpio(1)
            self.waterSensor_L_led = onionGpio.OnionGpio(0)
            # set relay off
            self.relay1.setOutputDirection(1)
            self.relay2.setOutputDirection(1)
            self.relay3.setOutputDirection(1)
            self.waterSensor_H.setInputDirection()
            self.waterSensor_L.setInputDirection()
            self.network_led.setOutputDirection(0)
            self.server_led.setOutputDirection(0)
            self.waterSensor_H_led.setOutputDirection(0)
            self.waterSensor_L_led.setOutputDirection(0)
        except Exception:
            # self.saveparams()
            self.reboot_signal = True
            os.system('reboot')

        # self.runCommand = ''
        self.loadparams()
        print(self.runCommand)

        # init run sequence
        self.runCommand[0] = self.runCommand[0]
        self.runCommand[1] = self.runCommand[1]
        self.runCommand[2] = self.runCommand[2]
        # ['Run Mode', 'Schedule', 'CurrentState']
        ### Run Mode
        # 1,0 -> [M]anual
        # S -> [S]cheduled
        # A -> Water Works with [W]ater level sensor
        # R -> Repeated
        ### Schedule
        # Monday/Tuesday/Wednesday/Thursday/Friday/Saturday/Sunday
        # ex) '0/06000910/23000200,06000910/23000200,06000910/
        #      23000200,06000910/23000200/23000200,06000910

        # schedule time min : 0000
        # schedule time max : 2400

        self.Run_Schedule = ''.zfill(60*24)
        # Schedule : 60 * 24 byte
        # 3 bits for CH3 | CH2 | CH1
        # ex) 7 -> ON | ON | ON
        # ex) 5 -> ON | OFF| ON
        self.updateSchedule()

        self.recv_thread_state = True
        self.run_thread_state = True

        self.watchdog_th = threading.Thread(target=self.network_watchdog, args=())
        self.watchdog_th.start()

        self.run_th = threading.Thread(target=self.run_process, args=())
        self.run_th.start()

        # create and run thread
        self.recv_th = threading.Thread(target=self.recv_process, args=())
        self.recv_th.start()
    

    def network_watchdog(self):
        while True:
            if self.checkNetwork():
                self.recv_thread_state = True
            else:
                self.recv_thread_state = False

            if self.reboot_signal:
                break

            time.sleep(1)

    def saveparams(self):
        with open('/root/params.pickle', 'wb') as fw:
            pickle.dump(self.runCommand, fw)
    
    def loadparams(self):
        try:
            if os.path.isfile('/root/params.pickle'):
                with open('/root/params.pickle', 'rb') as fr:
                    self.runCommand = pickle.load(fr)

            else:
                self.runCommand = [
                    {'mode': '0', 
                    'schedule': '',
                    'period': '',
                    'autoModeMsg': '',
                    'currentState': 0,
                    'autoTimeLimit': 0},
                    {'mode': '0', 
                    'schedule': '',
                    'period': '',
                    'autoModeMsg': '',
                    'currentState': 0,
                    'autoTimeLimit': 0},
                    {'mode': '0', 
                    'schedule': '',
                    'period': '',
                    'autoModeMsg': '',
                    'currentState': 0,
                    'autoTimeLimit': 0}
                ]
        except Exception:
            pass
        
        self.autoTimeLimit_1 = self.runCommand[0]['autoTimeLimit']
        self.autoTimeLimit_2 = self.runCommand[1]['autoTimeLimit']
        self.autoTimeLimit_3 = self.runCommand[2]['autoTimeLimit']
        
    def json_logging(self, data):
        self.resultFile = open('/root/output.txt', 'a')
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))
        current_time = '[%d-%02d-%02d %02d:%02d:%02d]-----------------------------------------\n' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        self.resultFile.write(current_time)
        for i in range(3):
            mode = data[i]['mode']
            
            if data[i]['schedule'] == None:
                schedule = 'None'
            else:
                schedule = data[i]['schedule']

            if data[i]['period'] == None:
                period = 'None'
            else:
                period = data[i]['period']

            if data[i]['autoModeMsg'] == None:
                autoModeMsg = 'None'
            else:
                autoModeMsg = data[i]['autoModeMsg']

            currentState = str(data[i]['currentState'])
            autoTimeLimit = str(data[i]['autoTimeLimit'])

            sData = "{'mode': %s, 'schedule': %s, 'period': %s, 'autoModeMsg': %s, 'currentState': %s, 'autoTimeLimit': %s}\n" % (mode, schedule, period, autoModeMsg, currentState, autoTimeLimit)
            self.resultFile.write(sData)
        self.resultFile.close()

    def msg_logging(self, data):
        self.resultFile = open('/root/output.txt', 'a')
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))
        current_time = '[%d-%02d-%02d %02d:%02d:%02d]-----------------------------------------\n' % (now.year, now.month, now.day, now.hour, now.minute, now.second)
        self.resultFile.write(current_time)
        self.resultFile.write(data)
        self.resultFile.close()

    def recv_process(self):
        count = 0
        while True:
            if self.reboot_signal:
                break

            if self.recv_thread_state:
                try:
                    if self.isAutoMsg != -1:
                        self.runCommand[self.isAutoMsg]['autoModeMsg'] = '수위센서 이상이 감지되어 릴레이 작동을 중지하였습니다. 센서를 확인해주세요.'
                        self.isAutoMsg = -1
                    elif self.isAutoMsg == -1:
                        self.runCommand[0]['autoModeMsg'] = ''
                        self.runCommand[1]['autoModeMsg'] = ''
                        self.runCommand[2]['autoModeMsg'] = ''
                        
                    res = requests.post(self.URL, headers=self.headers, data=json.dumps(self.runCommand))
                    if res.status_code==200 and len(res.json()):
                        self.tmp = res.json()
                        # print(self.tmp)
                        # self.json_logging(self.tmp)
                        #[{'mode': 'x', 'schedule': None, 'period': None, 'autoModeMsg': None, 'currentState': 0, 'autoTimeLimit': 0}, 
                        # {'mode': 'x', 'schedule': None, 'period': None, 'autoModeMsg': None, 'currentState': 0, 'autoTimeLimit': 0}, 
                        # {'mode': 'a', 'schedule': None, 'period': None, 'autoModeMsg': None, 'currentState': 0, 'autoTimeLimit': 6430}]
                        if self.tmp[0]['mode'] != 'x':
                            self.runCommand[0] = self.tmp[0]
                            self.autoTimeLimit_1 = self.tmp[0]['autoTimeLimit']
                            self.saveparams()
                        if self.tmp[1]['mode'] != 'x':
                            self.runCommand[1] = self.tmp[1]
                            self.autoTimeLimit_2 = self.tmp[1]['autoTimeLimit']
                            self.saveparams()
                        if self.tmp[2]['mode'] != 'x':
                            self.runCommand[2] = self.tmp[2]
                            self.autoTimeLimit_3 = self.tmp[2]['autoTimeLimit']
                            self.saveparams()
                        self.server_led.setValue(1)
                        count = 0

                        # update
                        if self.runCommand[0]['mode'] == 'u' or self.runCommand[1]['mode'] == 'u' or self.runCommand[2]['mode'] == 'u':
                            try:
                                if float(self.runCommand[0]['period']) > float(VERSION):
                                    # update here
                                    os.system('python3 /root/updater.py')
                                    self.reboot_signal = True
                                    break
                            except Exception as e:
                                print(e)
                        
                        if self.runCommand[0]['mode'] == 's' or self.runCommand[1]['mode'] == 's' or self.runCommand[2]['mode'] == 's' or self.runCommand[0]['mode'] == 'r' or self.runCommand[1]['mode'] == 'r' or self.runCommand[2]['mode'] == 'r':
                            self.updateSchedule()


                    elif res.status_code==200:
                        self.server_led.setValue(1)
                        count = 0
                        # self.msg_logging('response: 200, no data\n')
                    else:
                        self.server_led.setValue(0)
                        count += 1
                        # get server address and port
                        # print('server ip reset..')
                        # self.msg_logging('server ip reset..\n')
                        self.server_ip, self.port = self.getServerInfo()
                        self.URL = 'http://%s:%s/device/order/%s' % (self.server_ip, self.port, self.macAddr[-4:])
                except Exception as e:
                    self.server_led.setValue(0)
                    count += 1
                    # print('recv_process error')
                    # self.msg_logging('recv_process error\n')
                    print(e)
            else:
                count += 1
            
            # print('count:', count)
            if count > 4:
                self.reboot_signal = True
                break

            time.sleep(10)
        # self.msg_logging('reboot\n')
        os.system('reboot')


    def run_process(self):
        toggle = True
        today = -1
        autoToggle = False
        while True:
            if self.reboot_signal:
                break

            if self.run_thread_state:
                now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))

                # scheduled relay control
                if now.second == 0 and toggle:
                    if today != datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).weekday():
                        today = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).weekday()
                        self.updateSchedule()

                    index = now.hour*60 + now.minute
                    runbit = 7-int(self.Run_Schedule[index])
                    # runbit    ->  CH3 | CH2 | CH1
                    #   7       ->  1   | 1   | 1
                    #   0       ->  0   | 0   | 0
                    CH3 = runbit//4
                    CH2 = (runbit%4)//2
                    CH1 = runbit%2

                    if self.runCommand[0]['mode'] == 's' or self.runCommand[0]['mode'] == 'r':
                        self.setRelay(1, CH1)
                    if self.runCommand[1]['mode'] == 's' or self.runCommand[1]['mode'] == 'r':
                        self.setRelay(2, CH2)
                    if self.runCommand[2]['mode'] == 's' or self.runCommand[2]['mode'] == 'r':
                        self.setRelay(3, CH3)
                    toggle = False
                else:
                    toggle = True

                # relay control with water level sensor
                # Water sensor ON when no water -> gpio LOW when no water (pull-up)
                low = int(self.waterSensor_L.getValue())
                high = int(self.waterSensor_H.getValue())

                self.waterSensor_H_led.setValue(high)
                self.waterSensor_L_led.setValue(low)

                if low and high:    # Water tank Full
                    if self.runCommand[0]['mode'] == 'a': self.setRelay(1, 1)
                    if self.runCommand[1]['mode'] == 'a': self.setRelay(2, 1)
                    if self.runCommand[2]['mode'] == 'a': self.setRelay(3, 1)
                    autoToggle = False
                elif not low and not high: # Water tank Empty
                    if not autoToggle:
                        if self.runCommand[0]['mode'] == 'a': self.setRelay(1, 0)
                        if self.runCommand[1]['mode'] == 'a': self.setRelay(2, 0)
                        if self.runCommand[2]['mode'] == 'a': self.setRelay(3, 0)
                        self.startedTime_1 = self.startedTime_2 = self.startedTime_3 = time.time()
                        autoToggle = True

                if self.runCommand[0]['mode'] == 'a' and time.time() - self.startedTime_1 > self.autoTimeLimit_1 and self.runCommand[0]['currentState'] == 1:
                    self.setRelay(1, 1)
                    self.isAutoMsg = 0
                if self.runCommand[1]['mode'] == 'a' and time.time() - self.startedTime_2 > self.autoTimeLimit_2 and self.runCommand[1]['currentState'] == 1:
                    self.setRelay(2, 1)
                    self.isAutoMsg = 1
                if self.runCommand[2]['mode'] == 'a' and time.time() - self.startedTime_3 > self.autoTimeLimit_3 and self.runCommand[2]['currentState'] == 1:
                    self.setRelay(3, 1)
                    self.isAutoMsg = 2
                # print(time.time() - self.startedTime_3, self.autoTimeLimit_3)

                if self.runCommand[0]['mode'] == '1':
                    self.setRelay(1, 0)
                elif self.runCommand[0]['mode'] == '0':
                    self.setRelay(1, 1)
                if self.runCommand[1]['mode'] == '1':
                    self.setRelay(2, 0)
                elif self.runCommand[1]['mode'] == '0':
                    self.setRelay(2, 1)
                if self.runCommand[2]['mode'] == '1':
                    self.setRelay(3, 0)
                elif self.runCommand[2]['mode'] == '0':
                    self.setRelay(3, 1)
                    
            time.sleep(0.5)


    def updateSchedule(self):
        try:
            ch1 = self.convert_schedule_to_minuteSequence(self.runCommand[0]['mode'], self.runCommand[0]['schedule'])  # ex) 23000200,06000910
            ch2 = self.convert_schedule_to_minuteSequence(self.runCommand[1]['mode'], self.runCommand[1]['schedule'])
            ch3 = self.convert_schedule_to_minuteSequence(self.runCommand[2]['mode'], self.runCommand[2]['schedule'])
        
            res = list(''.zfill(60*24))
            for i in range(len(res)):
                bit = 0
                if ch1[i] == '1':
                    bit += 1
                if ch2[i] == '1':
                    bit += 2
                if ch3[i] == '1':
                    bit += 4
                res[i] = str(bit)
            self.Run_Schedule = ''.join(res)
        except Exception as e:
            print(22, e)


    def convert_schedule_to_minuteSequence(self, mode, strData):
        # EX
        # input     : strData = 23000200,06000910
        # output    : 1440 byte minute sequence
        
        today = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).weekday()
        res = ''.zfill(60*24)
        if mode == 's':
            strData = strData.split('/')[today]
            for data in strData.split(','):
                if data == '0':
                    break
                elif len(data) == 8:
                    start = data[:4]
                    end = data[4:]
                    start_sequence = int(start[:2])*60 + int(start[2:])
                    end_sequence = int(end[:2])*60 + int(end[2:])

                    res = list(res)
                    for i in range(start_sequence, end_sequence):
                        res[i] = '1'
                    res = ''.join(res)
                else:
                    print('schedule parsing error')
            # self.resultFile = open('/root/output.txt', 'a')
            # for i in range(24):
            #     h = res[60*i:60*(i+1)]
            #     print(i, 'hours : ', end='')
            #     strData = '%d hours : ' % i
            #     self.resultFile.write(strData)
            #     for j in range(6):
            #         strData = h[10*j:10*(j+1)] + '_'
            #         print(strData, end='')
            #         self.resultFile.write(strData)
            #     print('')
            #     self.resultFile.write('\n')
            # self.resultFile.write('\n')
            # self.resultFile.close()
        elif mode == 'r':
            if len(strData) == 4:
                hours = int(strData[0:2])
                minutes = int(strData[2:4])
        return res


    def setRelay(self, ch, output):
        # output : 0 -> ON
        # output : 1 -> OFF
        if ch == 1:
            self.relay1.setValue(output)
            if output == 0: self.runCommand[0]['currentState'] = 1
            elif output == 1: self.runCommand[0]['currentState'] = 0
        elif ch == 2:
            self.relay2.setValue(output)
            if output == 0: self.runCommand[1]['currentState'] = 1
            elif output == 1: self.runCommand[1]['currentState'] = 0
        elif ch == 3:
            self.relay3.setValue(output)
            if output == 0: self.runCommand[2]['currentState'] = 1
            elif output == 1: self.runCommand[2]['currentState'] = 0

    def getServerInfo(self):
        try:
            # sync time
            os.system('onion time sync')
            
            r = requests.get(awslambdaurl)
            ciphertext = base64.b64decode(r.text.replace('"', ''))
            _aes = aes.AESModeOfOperationCBC(key.encode('utf-8'), iv = iv)
            decrypted = b''
            if len(ciphertext)%16 == 0:
                it = len(ciphertext) // 16
                for i in range(it):
                    decrypted += _aes.decrypt(ciphertext[i*16:(i+1)*16])
                decrypted = unpad(decrypted).decode('utf-8')

            data = decrypted.split('$')
            # print(data)
            server_ip = ''
            port = 0
            for d in data:
                if 'SMART_RELAY_SERVER' in d:
                    server_ip = d.split(',')[1]
                    port = int(d.split(',')[2])
                    break
        except Exception as e:
            print('network error.. reboot...')
            os.system('reboot')

        return server_ip, port

    def setMacAddr(self):
        res = os.popen('ifconfig br-wlan | grep HWaddr').readline()
        self.macAddr = res.lstrip().split('HWaddr')[1][1:-1].replace(':','').replace(' ', '')

    def checkNetwork(self):
        res = os.popen('ping -c 1 -W 1 -w 1 8.8.8.8 | grep loss').readline()
        if '100%' in res:
            self.network_led.setValue(0)
            self.server_led.setValue(0)
            return False
        else:
            self.network_led.setValue(1)
            return True


if __name__ == '__main__':

    sr = SMART_RELAY()
    while not sr.reboot_signal:
        pass