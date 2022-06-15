from utils import *
from machine import Pin, PWM, SoftI2C
import machine

import network
import ubinascii
import neopixel
import time
import os
import ujson
from umqtt.robust import MQTTClient
import gc
import micropython
import ntptime
# import traceback

# class LOUNGE():
#     def __init__(self):

#         # Color Led Parameters
#         self.LED_DATA_PIN = 4
#         self.LED_NUM = 11
#         self.startup_flag = True
#         self._init_led()
#         self.set_led_color(C_PURPLE) # 전원 연결되면 보라색


#         self.setting_file_name = 'settings.txt'
#         self.mac_address = ubinascii.hexlify(network.WLAN().config('mac'),':').decode().replace(':','').upper()
#         self.deviceId = 'lounge_' + self.mac_address
#         self.ownerId = ''

#         self.synctime = 0
#         self.click_flag = True  # light up indicators when start up
#         self.timestamp = 0

#         # Dimming 초기화
#         self.is_dimming = False
#         self.dimming_color = 'blue'
#         self.dimming_count = 0
#         self.dimming_direction = UP
#         self.dimming_lastTime = 0

#         self.fan1 = 0
#         self.fan2 = 0
#         self.fan3 = 0
#         self.fan4 = 0
        
#         # Motor Parameters
#         self.MOTOR1_PIN = 17
#         self.MOTOR2_PIN = 16
#         self.MOTOR3_PIN = 2
#         self.MOTOR4_PIN = 15
#         self.PWM_FREQ = 20000

#         # Button Parameters
#         self.BTN_PWR_PIN = 33
#         self.BTN_LED_PIN = 32
#         self.BTN_MTR1_PIN = 36
#         self.BTN_MTR2_PIN = 39
#         self.BTN_MTR3_PIN = 34
#         self.BTN_MTR4_PIN = 35

#         # RF 
#         self.SCK_PIN = 18
#         self.MOSI_PIN = 23
#         self.MISO_PIN = 19
#         self.CS1_PIN = 5
#         self.CS2_PIN = 13
#         self.RFID_SW1_PIN = 26
#         self.RFID_SW2_PIN = 25
#         self.RFID_SW3_PIN = 14
#         self.RFID_SW4_PIN = 27
        
#         # Touch Board LED Control Parameters
#         self.SCL_PIN = 22
#         self.SDA_PIN = 21
#         self.PCA_FREQ = 400000
#         self.PCA_ADDR = 85  # 0x55

#         # Button Parameters
#         self.PW_FLAG = True
#         self.led_cnt = 2    # when it is positive, it means button set / when it is negative, it means aws call
#         self.sw1_cnt = 0
#         self.sw2_cnt = 0
#         self.sw3_cnt = 0
#         self.sw4_cnt = 0

#         # Bluetooth
#         self.RECEIVED_DATA = ''
#         self.RECEIVE_FINISHED = False

#         # MQTT
#         self.mqtt_client = None

#         # RF
#         self.OK = 0
#         self.NOTAGERR = 1
#         self.ERR = 2

#         self.REQIDL = 0x26
#         self.REQALL = 0x52
#         self.AUTHENT1A = 0x60
#         self.AUTHENT1B = 0x61

#         self._initSettings()
#         self._init_motor()
#         self._init_wifi()
#         self._init_rf()
#         self._init_touch_board()

#         if self.device_run_mode == 'BLE':
#             self._init_bluetooth()
#         elif self.device_run_mode == 'MQTT':
#             self._init_mqtt()

#         print("HARDWARES INITIALIZED.\n")
        

#     # Functions
#     def _initSettings(self):        
#         if self.setting_file_name in os.listdir():
#             settings = open(self.setting_file_name, 'r')
#             for line in settings:
#                 data = line.split(':')
#                 if data[0] == 'ssid':
#                     self.ssid = data[1][:-1]
#                 elif data[0] == 'WIFIPW':
#                     self.WIFI_PW = data[1][:-1]
#                 elif data[0] == 'owner_id':
#                     self.owner_id = data[1][:-1]
#                 elif data[0] == 'MQTTSERVER':
#                     self.mqtt_server_address = data[1][:-1]
#                 elif data[0] == 'RUNMODE':
#                     self.device_run_mode = data[1][:-1]
#                 elif data[0] == 'fan1':
#                     self.fan1 = int(data[1][:-1])
#                 elif data[0] == 'fan2':
#                     self.fan2 = int(data[1][:-1])
#                 elif data[0] == 'fan3':
#                     self.fan3 = int(data[1][:-1])
#                 elif data[0] == 'fan4':
#                     self.fan4 = int(data[1][:-1])
#                 elif data[0] == 'red':
#                     self.red = int(data[1][:-1])
#                 elif data[0] == 'green':
#                     self.green = int(data[1][:-1])
#                 elif data[0] == 'blue':
#                     self.blue = int(data[1][:-1])
#                 elif data[0] == 'light':
#                     self.light = int(data[1][:-1])
#             settings.close()

#         else:
#             # 설정값 및 설정 파일 초기화
#             # this block will excute once at the first time
#             self.ssid = ''
#             self.WIFI_PW = ''
#             self.owner_id = ''
#             self.mqtt_server_address = ''
#             self.device_run_mode = 'BLE'
#             self.fan1 = 0
#             self.fan2 = 0
#             self.fan3 = 0
#             self.fan4 = 0

#             # set default led color as purple
#             self.red = 102
#             self.green = 0
#             self.blue = 102
#             self.light = 0

#             self._saveSettings()


#     def getState(self, mode='reported'):
#         SHADOW = '''
# {
#     "state": {
#         "%s": {
#             "red":%d,
#             "green":%d,
#             "blue":%d,
#             "light":%d,
#             "capsule1_id":"",
#             "capsule2_id":"",
#             "capsule3_id":"",
#             "capsule4_id":"",
#             "fan1": %d,
#             "fan2": %d,
#             "fan3": %d,
#             "fan4": %d,
#             "owner_id": "%s",
#             "power": "%s",
#             "ssid": "%s",
#             "timestamp": %d
#         }
#     }
# }''' % (mode, self.red, self.green, self.blue, self.light, self.fan1, self.fan2, self.fan3, self.fan4, self.owner_id, self.PW_FLAG, self.ssid, self.timestamp)

#         return SHADOW

#     def _saveSettings(self):
#         settings = open(self.setting_file_name, 'w')
#         data = 'ssid:%s\n' % (self.ssid)
#         data += 'WIFIPW:%s\n' % (self.WIFI_PW)
#         data += 'owner_id:%s\n' % (self.owner_id)
#         data += 'MQTTSERVER:%s\n' % (self.mqtt_server_address)
#         data += 'RUNMODE:%s\n' % (self.device_run_mode)
#         data += 'fan1:%d\n' % (self.fan1)
#         data += 'fan2:%d\n' % (self.fan2)
#         data += 'fan3:%d\n' % (self.fan3)
#         data += 'fan4:%d\n' % (self.fan4)
#         data += 'red:%s\n' % (self.red)
#         data += 'green:%s\n' % (self.green)
#         data += 'blue:%s\n' % (self.blue)
#         data += 'light:%s\n' % (self.light)

#         settings.write(data)
#         settings.close()

#     def _init_led(self):
#         self.color_leds = neopixel.NeoPixel(Pin(self.LED_DATA_PIN), self.LED_NUM, bpp=3)


#     def _init_motor(self):
#         print("INITIALIZE MOTORS...\n")

#         self.motor1 = PWM(Pin(self.MOTOR1_PIN))
#         self.motor2 = PWM(Pin(self.MOTOR2_PIN))
#         self.motor3 = PWM(Pin(self.MOTOR3_PIN))
#         self.motor4 = PWM(Pin(self.MOTOR4_PIN))

#         self.motor1.freq(self.PWM_FREQ)
#         self.motor2.freq(self.PWM_FREQ)
#         self.motor3.freq(self.PWM_FREQ)
#         self.motor4.freq(self.PWM_FREQ)

#         self.set_fan_speed_all(0)


#     def _init_wifi(self):
#         print("INITIALIZE WIFI...\n")

#         try:
#             self.WIFI = network.WLAN(network.STA_IF)
#             self.AP_IF = network.WLAN(network.AP_IF)
#             if not self.WIFI.active():
#                 self.WIFI.active(True)
#         except Exception as e:
#             print('Wifi Init ERROR:', e)
#             self.WIFI = False
#             self.AP_IF = False

#         if self.ssid != '' and self.WIFI_PW != '' and not self.is_connected_wifi():
#             self.connect_wifi()
        
    
#     def _init_rf(self):
#         print("INITIALIZE RF...\n")

#         self.rf = mfrc522(self.SCK_PIN, self.MOSI_PIN, self.MISO_PIN, \
#             self.CS1_PIN, self.CS2_PIN, self.RFID_SW1_PIN, self.RFID_SW2_PIN, self.RFID_SW3_PIN, self.RFID_SW4_PIN)


#     def _init_touch_board(self):
#         print("INITIALIZE TOUCH BOARD...\n")

#         self.pw_sw = Pin(self.BTN_PWR_PIN, Pin.IN)
#         self.led_sw = Pin(self.BTN_LED_PIN, Pin.IN)
#         self.sw1 = Pin(self.BTN_MTR1_PIN, Pin.IN)
#         self.sw2 = Pin(self.BTN_MTR2_PIN, Pin.IN)
#         self.sw3 = Pin(self.BTN_MTR3_PIN, Pin.IN)
#         self.sw4 = Pin(self.BTN_MTR4_PIN, Pin.IN)
        
#         self.touch_board_leds = PCA9685(SoftI2C(scl=Pin(self.SCL_PIN), sda=Pin(self.SDA_PIN), freq=self.PCA_FREQ), self.PCA_ADDR)
#         self.touch_board_leds.freq(60)


#     def _init_bluetooth(self):
#         print("INITIALIZE BLUETOOTH...\n")

#         self.bleSerial = BLESerial(bluetooth.BLE())   
#         self.bleSerial.on_write(self.bluetooth_on_rx_handler)


#     def _init_mqtt(self):
#         print(self.is_connected_wifi())

#         print('MQTT - connected wifi : {}\n MQTT - run_mode : {}\n MQTT - address : {}'.format(self.is_connected_wifi(), self.device_run_mode, self.mqtt_server_address))

#         if self.is_connected_wifi() and self.device_run_mode == 'MQTT' and self.mqtt_server_address != '':
#             CERT_FILE = "aws.crt.pem"
#             KEY_FILE = "aws.key.pem"
#             MQTT_PORT = 8883
#             MQTT_HOST = self.mqtt_server_address
#             THING_NAME = self.deviceId

#             self.MQTT_KEEPALIVE_INTERVAL = 45

#             # publish
#             self.SHADOW_GET_TOPIC = "$aws/things/" + THING_NAME + "/shadow/get" 
#             self.SHADOW_UPDATE_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update"
#             # subscribe
#             self.SHADOW_GET_ACCEPTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/get/accepted"
#             self.SHADOW_UPDATE_DELTA_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/delta"
#             self.RESPONSE_RECEIVED = False

#             # TODO: 최초 연결 시 말고도 도중에 mqtt가 정상적으로 연결되어있는지 확인하는 함수가 필요합니다.
#             # 만일 사용 도중 mqtt와 연결이 끊어졌다면 주황색으로 변경해야 하는데 그럴 때를 위한 체킹 알고리즘 혹은 함수가 필요합니다.
#             try:
#                 with open(KEY_FILE, "r") as f:
#                     key = f.read()
#                 with open(CERT_FILE, "r") as f:
#                     cert = f.read()

#                 self.mqtt_client = MQTTClient(client_id=THING_NAME, server=MQTT_HOST, port=MQTT_PORT, keepalive=5000, ssl=True, ssl_params={"cert":cert, "key":key, "server_side":False})
#                 self.mqtt_client.set_callback(self.sub_cb)
#                 self.mqtt_client.connect()
#                 self.mqtt_client.subscribe(self.SHADOW_GET_ACCEPTED_TOPIC)
#                 self.mqtt_client.subscribe(self.SHADOW_UPDATE_DELTA_TOPIC)
#                 self.is_dimming = False
#                 self.set_led_color(C_COOL)
#             except Exception as e:
#                 print('MQTT init error:', e)
#                 self.is_dimming = False
#                 # set led color orange
#                 self.set_led_color(C_ORANGE)


#     def sub_cb(self, topic, msg):
#         # print('[sub_cb] topic : {}, msg : {}'.format(topic, msg))
#         parsed = ujson.loads(msg)
#         # print('[sub_cb] type : {}'.format(parsed))
#         try:
#             # get/accepted
#             if str(topic, 'utf-8').split('/')[-1] == 'accepted':
#                 # print('[sub_cb] Accepted')
#                 desired_timestamp = parsed['state']['desired']['timestamp']
#                 # Desired Timestamp가 유효하지 않으면 현재 시각 Timestamp 적용
#                 if desired_timestamp == None or desired_timestamp == '':
#                     self.timestamp = self.getTimestamp()
#                 # Desired Timestamp와 현재(Reported) Timestamp가 다르면 동기화
#                 elif desired_timestamp != self.timestamp:
#                     self.timestamp = desired_timestamp
#             # update/delta 
#             elif str(topic, 'utf-8').split('/')[-1] == 'delta':
#                 if 'desired' in parsed['state']:
#                     state = parsed['state']['desired']
#                     print(state)
                
#                     changed_led, changed_fan, changed_power = False, False, False

#                     for key, value in state.items():
#                         if key == "red" or key == "green" or key == "blue" or key == "light":
#                             changed_led = True
#                             if key == 'red': self.red = state['red']
#                             if key == 'green': self.green = state['green']
#                             if key == 'blue': self.blue = state['blue']
#                             if key == 'light': self.light = state['light']

#                         if "fan" in key:
#                             changed_fan = True
#                             if key == 'fan1': self.fan1 = state['fan1']
#                             if key == 'fan2': self.fan2 = state['fan2']
#                             if key == 'fan3': self.fan3 = state['fan3']
#                             if key == 'fan4': self.fan4 = state['fan4']

#                         if key == 'power':
#                             changed_power = True
#                             self.PW_FLAG = state['power']

#                     if changed_led:
#                         self.led_cnt = -1
#                         self.set_led_color([self.red, self.green, self.blue])
                        
#                     if changed_fan:
#                         self.set_fan_speed(1, self.fan1)
#                         self.set_fan_speed(2, self.fan2)
#                         self.set_fan_speed(3, self.fan3)
#                         self.set_fan_speed(4, self.fan4)
                        
#                     if changed_power:
#                         if self.PW_FLAG: # POWER ON
#                             self.set_led_color([self.red, self.green, self.blue])
#                             self.set_fan_speed(1, self.fan1)
#                             self.set_fan_speed(2, self.fan2)
#                             self.set_fan_speed(3, self.fan3)
#                             self.set_fan_speed(4, self.fan4)
#                         else: # POWER OFF
#                             self.set_fan_speed(1, 0)
#                             self.set_fan_speed(2, 0)
#                             self.set_fan_speed(3, 0)
#                             self.set_fan_speed(4, 0)
#                             self.set_led_color(C_OFF)


#                     # AWS IoT Update          
#                     if changed_led or changed_fan or changed_power:
#                         self.update_reported_shadow()
#                     time.sleep(0.2)

#                 # TODO : reset 동작 구현 필요
#                 # BLE로 전환시 사용
#                 # if reset:
#                 #     machine.reset()
#         except KeyError as e:
#             print("MQTT Message parsing error(KeyError)\n{}".format(e))

#     def set_wifi_ssid(self, ssid):
#         self.ssid = ssid

#         self.ssid = ssid
#         self.update_reported_shadow()

#     def set_wifi_pw(self, pw):
#         self.WIFI_PW = pw
    
#     def get_wifi_ssid(self):
#         return self.ssid

#     def get_wifi_pw(self):
#         return self.WIFI_PW

#     def connect_wifi(self):
#         try:
#             # 기존에 연결된 와이파이 연결 해제(와이파이 연결 시 새로운 와이파이 연결 불가능)
#             if self.WIFI.isconnected():
#                 self.WIFI.disconnect()
#                 time.sleep(3)

#             trycnt = 0
#             while True:
#                 try:
#                     if self.WIFI.isconnected():
#                         self.set_led_color([self.red, self.green, self.blue])
#                         break
#                     elif trycnt > 5:
#                         self.set_led_color(C_RED)
#                         break
#                     else:
#                         self.WIFI.connect(self.ssid, self.WIFI_PW)
#                         time.sleep(5)
#                 except Exception as e:
#                     print("[WIFI] Connection error1: ", e)
#                 finally:
#                     trycnt += 1
#         except Exception as e:
#             print("[WIFI] Connection error2: ", e)
    
#     def is_connected_wifi(self):
#         try:
#             return self.WIFI.isconnected()
#         except:
#             return False
    
#     def get_wifi_status(self):
#         try:
#             return self.WIFI.status()
#         except:
#             return 'STAT_ERROR'

#     def set_led_color(self, color):
#         r = color[0]
#         g = color[1]
#         b = color[2]
#         for i in range(self.LED_NUM):
#             self.color_leds[i] = (r,g,b)
#         self.color_leds.write()

#         # AWS Shadow Update
#         self.red, self.green, self.blue = (r,g,b)
    
#     def set_fan_speed(self, fan_no, speed):
#         print("set fan speed")
#         # speed range: 0% - 100%
#         # 0 -> 0
#         # 100 -> 1023
#         speed = int(10.23 * speed)

#         if fan_no == 1:
#             self.motor1.duty(speed)
#         elif fan_no == 2:
#             self.motor2.duty(speed)
#         elif fan_no == 3:
#             self.motor3.duty(speed)
#         elif fan_no == 4:
#             self.motor4.duty(speed)


#     def set_fan_speed_all(self, speed):
#         print("set fan speed all")
#         speed = int(10.23 * speed)

#         for motor in [self.motor1, self.motor2, self.motor3, self.motor4]:
#             motor.duty(speed)
        
#         self.fan1, self.fan2, self.fan3, self.fan4 = (speed for _ in range(4))
#         self.update_desired_shadow()

#     def unicode2uString(self, unicode_string):
#         # ex 딥센트  
#         # input: '\ub525\uc13c\ud2b8'
#         # output: '525B C13C D2B8'
#         result_string = ''
#         for c in unicode_string:
#             result_string += hex(ord(c))[2:] + ' '
#         return result_string[:-1]

#     def uString2unicode(self,uString):
#         # ex 딥센트  
#         # input: '525B C13C D2B8'
#         # output: '\ub525\uc13c\ud2b8'
#         uStr = uString.split(' ')
#         result_string = ''
#         for c in uStr:
#             h = '0x'+c
#             result_string += chr(int(h))
#         return result_string
    
#     def syncTime(self):
#         self.synctime = time.time()
#         if self.is_connected_wifi():
#             ntptime.settime()

#     def getTimestamp(self):
#         # mpython starts from 2000-01-01, not 1970-01-01
#         if time.time() > 700000000:
#             return 946684800 + time.time()
#         else:
#             return 0
    
#     def resetDevice(self):
#         # 기기 초기화
#         print("!!HARDWARE RESET!!")
        
#         # 와이파이 연결 해제
#         if self.WIFI.isconnected():
#             self.WIFI.disconnect()

#         # 설정 파일 초기화
#         self.ssid = ''
#         self.WIFI_PW = ''
#         self.owner_id = ''
#         self.mqtt_server_address = ''
#         self.device_run_mode = 'BLE'
#         self.fan1 = 0
#         self.fan2 = 0
#         self.fan3 = 0
#         self.fan4 = 0
#         self.red = 0
#         self.green = 0
#         self.blue = 0
#         self.light = 0

#         self._saveSettings()

#         time.sleep(3)
#         machine.reset()

#     def updateDimming(self):
#         if self.is_dimming:
#             if time.ticks_ms() - self.dimming_lastTime > 50:
#                 self.dimming_lastTime = time.ticks_ms()
#                 if self.dimming_color == 'blue':
#                     self.set_led_color([0,0,self.dimming_count])
#                 elif self.dimming_color == 'green':
#                     self.set_led_color([0,self.dimming_count,0])
#                 elif self.dimming_color == 'cool':
#                     # (60,60,160)
#                     self.set_led_color([int((60/255)*self.dimming_count),int((60/255)*self.dimming_count),int((160/255)*self.dimming_count)])

#                 if self.dimming_direction == UP:
#                     self.dimming_count += 10
#                     if self.dimming_count > 255: self.dimming_count = 255
#                 elif self.dimming_direction == DOWN:
#                     self.dimming_count -= 10
#                     if self.dimming_count < 0: self.dimming_count = 0

#                 if self.dimming_count == 255:
#                     self.dimming_direction = DOWN
#                 if self.dimming_count == 0:
#                     self.dimming_direction = UP
                
#     def updateTime(self):
#         # ntp time sync per every 12 hours
#         if time.time() - self.synctime > 12*60*60:
#             try:
#                 self.syncTime()
#             except Exception as e:
#                 print('Time Sync Error:',e)
    
#     def checkMQTTMsg(self):
#         # MQTT MOD
#         if self.device_run_mode == 'MQTT':
#             try:
#                 self.mqtt_client.check_msg()
#             except Exception as e:
#                 print('MQTT Check Msg Error:', e)
    
#     def updateDevice(self):
#         self.button_handler()
        
#         if self.click_flag and self.PW_FLAG:                
#             self.touch_board_leds.on(0)
#             self.touch_board_leds.on(3)

#             if self.led_cnt < 0:
#                 self.set_led_color([int(self.red),int(self.green),int(self.blue)])
            
#             self.LEDUpdate()
#             self.fanUpdate()
#             self.update_desired_shadow()
#             time.sleep(0.2)

#         elif self.click_flag and not self.PW_FLAG:
#             # turn off leds, fans, indicators
#             for i in range(16):
#                 self.touch_board_leds.off(i)

#             self.set_fan_speed(1,0)
#             self.set_fan_speed(2,0)
#             self.set_fan_speed(3,0)
#             self.set_fan_speed(4,0)
#             self.set_led_color(C_OFF)
#             self.update_desired_shadow()

#         self.click_flag = False

#     def LEDUpdate(self):
#         if self.startup_flag:
#             self.startup_flag = False
#         elif self.led_cnt == 0:
#             self.touch_board_leds.off(1)
#             self.touch_board_leds.off(2)
#             self.light = 0
#             self.set_led_color(C_OFF)
#         elif self.led_cnt == 1:
#             self.touch_board_leds.on(1)
#             self.touch_board_leds.off(2)
#             self.light = 50
#             self.set_led_color([100, 100, 100])
#         elif self.led_cnt == 2:
#             self.touch_board_leds.on(1)
#             self.touch_board_leds.on(2)
#             self.light = 100
#             self.set_led_color(C_WHITE)
    
#     def fanUpdate(self):
#         # Fan 1
#         if self.sw1_cnt == 0:
#             self.fan1 = 0
#             self.touch_board_leds.off(13)
#             self.touch_board_leds.off(14)
#             self.touch_board_leds.off(15)
#         elif self.sw1_cnt == 1:
#             self.fan1 = 30
#             self.touch_board_leds.off(13)
#             self.touch_board_leds.off(14)
#             self.touch_board_leds.on(15) 
#         elif self.sw1_cnt == 2:
#             self.fan1 = 60
#             self.touch_board_leds.off(13)
#             self.touch_board_leds.on(14)
#             self.touch_board_leds.on(15) 
#         elif self.sw1_cnt == 3:
#             self.fan1 = 100
#             self.touch_board_leds.on(13)
#             self.touch_board_leds.on(14)
#             self.touch_board_leds.on(15)
        
#         # Fan 2
#         if self.sw2_cnt == 0:
#             self.fan2 = 0
#             self.touch_board_leds.off(10)
#             self.touch_board_leds.off(11)
#             self.touch_board_leds.off(12)   
#         elif self.sw2_cnt == 1:
#             self.fan2 = 30
#             self.touch_board_leds.off(10)
#             self.touch_board_leds.off(11)
#             self.touch_board_leds.on(12) 
#         elif self.sw2_cnt == 2:
#             self.fan2 = 60
#             self.touch_board_leds.off(10)
#             self.touch_board_leds.on(11)
#             self.touch_board_leds.on(12) 
#         elif self.sw2_cnt == 3:
#             self.fan2 = 100
#             self.touch_board_leds.on(10)
#             self.touch_board_leds.on(11)
#             self.touch_board_leds.on(12)    

#         # Fan 3
#         if self.sw3_cnt == 0:
#             self.fan3 = 0
#             self.touch_board_leds.off(7)
#             self.touch_board_leds.off(8)
#             self.touch_board_leds.off(9)   
#         elif self.sw3_cnt == 1:
#             self.fan3 = 30
#             self.touch_board_leds.off(7)
#             self.touch_board_leds.off(8)
#             self.touch_board_leds.on(9) 
#         elif self.sw3_cnt == 2:
#             self.fan3 = 60
#             self.touch_board_leds.off(7)
#             self.touch_board_leds.on(8)
#             self.touch_board_leds.on(9) 
#         elif self.sw3_cnt == 3:
#             self.fan3 = 100
#             self.touch_board_leds.on(7)
#             self.touch_board_leds.on(8)
#             self.touch_board_leds.on(9)    

#         # Fan 4
#         if self.sw4_cnt == 0:
#             self.fan4 = 0
#             self.touch_board_leds.off(4)
#             self.touch_board_leds.off(5)
#             self.touch_board_leds.off(6)   
#         elif self.sw4_cnt == 1:
#             self.fan4 = 30
#             self.touch_board_leds.off(4)
#             self.touch_board_leds.off(5)
#             self.touch_board_leds.on(6) 
#         elif self.sw4_cnt == 2:
#             self.fan4 = 60
#             self.touch_board_leds.off(4)
#             self.touch_board_leds.on(5)
#             self.touch_board_leds.on(6) 
#         elif self.sw4_cnt == 3:
#             self.fan4 = 100
#             self.touch_board_leds.on(4)
#             self.touch_board_leds.on(5)
#             self.touch_board_leds.on(6)


#         if self.fan1 == 0:
#             self.set_fan_speed(1, 0)
#         elif self.fan1 == 30:
#             self.set_fan_speed(1, 72)
#         elif self.fan1 == 60:
#             self.set_fan_speed(1, 80)
#         elif self.fan1 == 100:
#             self.set_fan_speed(1, 100)
        
#         if self.fan2 == 0:
#             self.set_fan_speed(2, 0)
#         elif self.fan2 == 30:
#             self.set_fan_speed(2, 75)
#         elif self.fan2 == 60:
#             self.set_fan_speed(2, 83)
#         elif self.fan2 == 100:
#             self.set_fan_speed(2, 100)
        
#         if self.fan3 == 0:
#             self.set_fan_speed(3, 0)
#         elif self.fan3 == 30:
#             self.set_fan_speed(3, 72)
#         elif self.fan3 == 60:
#             self.set_fan_speed(3, 80)
#         elif self.fan3 == 100:
#             self.set_fan_speed(3, 100)
        
#         if self.fan4 == 0:
#             self.set_fan_speed(4, 0)
#         elif self.fan4 == 30:
#             self.set_fan_speed(4, 72)
#         elif self.fan4 == 60:
#             self.set_fan_speed(4, 89)
#         elif self.fan4 == 100:
#             self.set_fan_speed(4, 100)

#     def button_handler(self):
#         if not self.click_flag:
#             if self.led_sw.value() == 0:
#                 self.click_flag = True
#                 self.led_cnt += 1
#                 if self.led_cnt == 3:
#                     self.led_cnt = 0
            
#             if self.sw1.value() == 0:
#                 self.click_flag = True
#                 self.sw1_cnt += 1
#                 if self.sw1_cnt == 4:
#                     self.sw1_cnt = 0
                    
#             if self.sw2.value() == 0:
#                 self.click_flag = True
#                 self.sw2_cnt += 1
#                 if self.sw2_cnt == 4:
#                     self.sw2_cnt = 0
                    
#             if self.sw3.value() == 0:
#                 self.click_flag = True
#                 self.sw3_cnt += 1
#                 if self.sw3_cnt == 4:
#                     self.sw3_cnt = 0
                    
#             if self.sw4.value() == 0:
#                 self.click_flag = True
#                 self.sw4_cnt += 1
#                 if self.sw4_cnt == 4:
#                     self.sw4_cnt = 0


#     # bluetooth handler
#     def bluetooth_on_rx_handler(self, cmd):
#         print("RX", cmd)

#         temp = cmd.decode('utf-8')
#         if temp.startswith('#{') and temp.endswith('}$'):
#             self.RECEIVE_FINISHED = True
#             self.RECEIVED_DATA = temp[1:-1]
#         elif temp.startswith('#{'):
#             print('[BLE] Received SOF')

#             self.RECEIVED_DATA = temp[1:]
#         elif temp.endswith('}$'):
#             print('[BLE] Received EOF')

#             self.RECEIVE_FINISHED = True
#             self.RECEIVED_DATA += temp[:-1]
#         else:
#             self.RECEIVED_DATA += temp

#         if self.RECEIVE_FINISHED:
#             print('[BLE] Received data:', self.RECEIVED_DATA)

#             sData_to_be_transfered = ''

#             try:
#                 parsed = ujson.loads(self.RECEIVED_DATA)
                
#                 print('[BLE] Parsed data: ', parsed)
                
#                 if parsed['method'] == 'ping':
#                     sData_to_be_transfered = """{"method":"ping","src":"%s","result":true}""" % (self.deviceId)

#                 elif parsed['method'] == 'getDeviceId':
#                     sData_to_be_transfered = """{"method":"getDeviceId","src":"%s","result":{"deviceId":"%s"}}""" % (self.deviceId, self.deviceId)

#                 elif parsed['method'] == 'setDeviceOwner':
#                     # dimming start
#                     self.dimming_color = 'blue'
#                     self.dimming_count = 0
#                     self.is_dimming = True

#                     self.ownerId = parsed['data']['ownerId']
#                     self._saveSettings()
#                     sData_to_be_transfered = """{"method":"setDeviceOwner","src":"%s","result":true}""" % (self.deviceId)

#                 elif parsed['method'] == 'setCert':
#                     key = parsed['data']['key']
#                     key_file = open('aws.key.pem', 'w')
#                     key_file.write(key)
#                     key_file.close()

#                     crt = parsed['data']['crt']
#                     crt_file = open('aws.crt.pem', 'w')
#                     crt_file.write(crt)
#                     crt_file.close()

#                     sData_to_be_transfered = """{"method":"setCert","src":"%s","result":true}""" % (self.deviceId)

#                     # dimming stop
#                     self.is_dimming = False
#                     self.set_led_color(C_OFF)

#                 elif parsed['method'] == 'wifiScan':
#                     if self.WIFI != False:
#                         # 기존에 연결된 와이파이 연결 해제(와이파이 연결 시 스캔 불가능)
#                         if self.WIFI.isconnected():
#                             self.WIFI.disconnect()
#                             time.sleep(2)

#                         self.wifi_list = self.WIFI.scan()

#                         print(self.wifi_list)

#                         if (len(self.wifi_list) > 0):
#                             self.total_frame = 6
#                         else:
#                             self.total_frame = 0

#                         self.frame_index = 0
                        
#                         sData_to_be_transfered = """{"method":"wifiScan","src":"%s","result":%d}""" % (self.deviceId, self.total_frame)
#                     else:
#                         sData_to_be_transfered = """{"method":"wifiScan","src":"%s","result":%d}""" % (self.deviceId, 0)

#                 elif parsed['method'] == 'wifiList':
#                     self.set_led_color(C_GREEN)
#                     if self.total_frame != 0 and self.frame_index < self.total_frame:
#                         _ssid = self.unicode2uString(self.wifi_list[self.frame_index][0].decode('utf-8'))
#                         _authmode = self.wifi_list[self.frame_index][4]
#                         _rssi = self.wifi_list[self.frame_index][3]

#                         wifi = """{"ssid":"%s","authmode":%d,"rssi":%d}""" % (_ssid, _authmode, _rssi)

#                         self.frame_index += 1

#                         sData_to_be_transfered = """{"method":"wifiList","src":"%s","totalFrame":%d,"frameIndex":%d,"result":%s}""" % (self.deviceId, self.total_frame, self.frame_index, wifi)
#                     else:
#                         sData_to_be_transfered = """{"method":"wifiList","src":"%s","result":false}""" % (self.deviceId)

#                 elif parsed['method'] == 'setWifi':
#                     # dimming start
#                     self.dimming_color = 'green'
#                     self.dimming_count = 0
#                     self.is_dimming = True

#                     # 와이파이 정보 업데이트
#                     self.ssid = self.uString2unicode(parsed['data']['ssid'])
#                     self.WIFI_PW = parsed['data']['pwd']
#                     self._saveSettings()

#                     # 와이파이 연결 (기존 연결시 연결 해제 후 업데이트 된 와이파이정보로 연결)
#                     self.connect_wifi()
                    
#                     # 10초 내 연결 완료되면 true 응답, 그렇지 않을경우 false 응답
#                     t = time.time()
#                     sData_to_be_transfered = """{"method":"setWifi","src":"%s","result":false}""" % (self.deviceId)
                    
#                     # set color red
#                     result = False
#                     while time.time() - t > 10:
#                         if self.is_connected_wifi():
#                             sData_to_be_transfered = """{"method":"setWifi","src":"%s","result":true}""" % (self.deviceId)
#                             # set color green (wifi connected)
#                             result = True
#                             break
#                         time.sleep(1)
                    
#                     # dimming stop
#                     self.is_dimming = False

#                 elif parsed['method'] == 'wifiConnected':
#                     status_message = ''
#                     if self.WIFI != False:
#                         status = self.WIFI.status()
#                         if status == network.STAT_IDLE:
#                             status_message = 'STAT_IDLE'
#                         elif status == network.STAT_WRONG_PASSWORD:
#                             status_message = 'STAT_WRONG_PASSWORD'
#                         elif status == network.STAT_NO_AP_FOUND:
#                             status_message = 'STAT_NO_AP_FOUND'
#                         elif status == network.STAT_GOT_IP:
#                             status_message = 'STAT_GOT_IP'
#                     if self.is_connected_wifi():
#                         self.set_led_color(C_WHITE)

#                         try:
#                             self.syncTime()
#                         except Exception as e:
#                             print('Time Sync failed in wifiConnected:', e)

#                         sData_to_be_transfered = """{"method":"wifiConnected","src":"%s","result":{"ssid":"%s","status":"%s","connected":true}}""" % (self.deviceId, self.unicode2uString(self.ssid), status_message)
#                     else:
#                         self.set_led_color(C_RED)
#                         sData_to_be_transfered = """{"method":"wifiConnected","src":"%s","result":{"ssid":"%s","status":"%s","connected":false}}""" % (self.deviceId, self.unicode2uString(self.ssid), status_message)

#                 elif parsed['method'] == 'setMqttServer':
#                     self.mqtt_server_address = parsed['data']['server']

#                     # crt 파일과 key 파일이 없을경우 MQTT 모드로 넘기지 않음. (블루투스가 끊어지는것을 방지)
#                     # 앱에서 setMqttServer 명령을 실행하기전에 유저에게 블루투스가 끊어질 것임을 알림 필요
#                     if 'aws.crt.pem' in os.listdir() and 'aws.key.pem' in os.listdir():
#                         self.device_run_mode = 'MQTT'
#                         self._saveSettings()
#                         sData_to_be_transfered = """{"method":"setMqttServer","src":"%s","result":true}""" % (self.deviceId)
#                     else:
#                         # False가 반환될 경우 mqtt 인증파일 전송 필요
#                         sData_to_be_transfered = """{"method":"setMqttServer","src":"%s","result":false}""" % (self.deviceId)


#                 if sData_to_be_transfered:
#                     # print('[BLE] Send data:', sData_to_be_transfered)

#                     self.bleSerial.send(sData_to_be_transfered)

#                     self.RECEIVE_FINISHED = False
#                     self.RECEIVED_DATA = ''
#                     sData_to_be_transfered = ''

#                     if self.device_run_mode == 'MQTT':
#                         # 인증서 전송이 끝나면 녹색 켜기
#                         self.set_led_color(C_GREEN)
                        
#                         time.sleep(5)
#                         # 기기 리셋한 후 MQTT 모드로 진입
#                         machine.reset()
#                 else:
#                     print('[BLE] No data to be sent.')

#                     self.RECEIVE_FINISHED = False
#                     self.RECEIVED_DATA = ''
#                     sData_to_be_transfered = ''

#             except Exception as e:
#                 pass

#     def update_desired_shadow(self):
#         desired_shadow = self.getState('desired')
#         self._update_shadow(desired_shadow)

#     def update_reported_shadow(self):
#         reported_shadow = self.getState('reported')
#         self._update_shadow(reported_shadow)

#     def _update_shadow(self, shadow):
#         try:
#             if self.mqtt_client:
#                 # print("[Update Shadow] MQTT Update Publish\n")
#                 # print("[Update Shadow] Shadow : {}".format(shadow))
#                 self.mqtt_client.publish(self.SHADOW_UPDATE_TOPIC, shadow)
#             else:
#                 print("[Update Shadow] MQTT Client is None")
#         except Exception as e:
#             # traceback.print_exc()
#             print("MQTT Publish Error : {}".format(e))

#     def run(self):
#         timecount = 0

#         while True:
#             # power button
#             if self.pw_sw.value() == 0:
#                 if timecount == 0:
#                     self.click_flag = True
#                     timecount = time.time()
#                     self.PW_FLAG = not self.PW_FLAG

#                 elif time.time() - timecount > 2 and time.time() - timecount < 5:
#                     # reset press
#                     for i in range(3):
#                         self.set_led_color(C_WHITE)
#                         time.sleep(0.5)
#                         self.set_led_color(C_OFF)
#                         time.sleep(0.5)

#                 elif time.time() - timecount > 5:
#                     # reset
#                     self.resetDevice()

#                 time.sleep(0.1)

#             else:
#                 timecount = 0
#                 self.checkMQTTMsg()
#                 self.updateTime()
#                 self.updateDimming()
#                 self.updateDevice()


# micropython.alloc_emergency_exception_buf(100)
# gc.enable()
# class LOUNGE():
#     def __init__(self):

#         # Color Led Parameters
#         self.LED_DATA_PIN = 4
#         self.LED_NUM = 11
#         self.startup_flag = True
#         self._init_led()
#         self.set_led_color(C_PURPLE) # 전원 연결되면 보라색


#         self.setting_file_name = 'settings.txt'
#         self.mac_address = ubinascii.hexlify(network.WLAN().config('mac'),':').decode().replace(':','').upper()
#         self.deviceId = 'lounge_' + self.mac_address
#         self.ownerId = ''

#         self.synctime = 0
#         self.click_flag = True  # light up indicators when start up
#         self.timestamp = 0

#         # Dimming 초기화
#         self.is_dimming = False
#         self.dimming_color = 'blue'
#         self.dimming_count = 0
#         self.dimming_direction = UP
#         self.dimming_lastTime = 0

#         self.fan1 = 0
#         self.fan2 = 0
#         self.fan3 = 0
#         self.fan4 = 0
        
#         # Motor Parameters
#         self.MOTOR1_PIN = 17
#         self.MOTOR2_PIN = 16
#         self.MOTOR3_PIN = 2
#         self.MOTOR4_PIN = 15
#         self.PWM_FREQ = 20000

#         # Button Parameters
#         self.BTN_PWR_PIN = 33
#         self.BTN_LED_PIN = 32
#         self.BTN_MTR1_PIN = 36
#         self.BTN_MTR2_PIN = 39
#         self.BTN_MTR3_PIN = 34
#         self.BTN_MTR4_PIN = 35

#         # RF 
#         self.SCK_PIN = 18
#         self.MOSI_PIN = 23
#         self.MISO_PIN = 19
#         self.CS1_PIN = 5
#         self.CS2_PIN = 13
#         self.RFID_SW1_PIN = 26
#         self.RFID_SW2_PIN = 25
#         self.RFID_SW3_PIN = 14
#         self.RFID_SW4_PIN = 27
        
#         # Touch Board LED Control Parameters
#         self.SCL_PIN = 22
#         self.SDA_PIN = 21
#         self.PCA_FREQ = 400000
#         self.PCA_ADDR = 85  # 0x55

#         # Button Parameters
#         self.PW_FLAG = True
#         self.led_cnt = 2    # when it is positive, it means button set / when it is negative, it means aws call
#         self.sw1_cnt = 0
#         self.sw2_cnt = 0
#         self.sw3_cnt = 0
#         self.sw4_cnt = 0

#         # Bluetooth
#         self.RECEIVED_DATA = ''
#         self.RECEIVE_FINISHED = False

#         # MQTT
#         self.mqtt_client = None

#         # RF
#         self.OK = 0
#         self.NOTAGERR = 1
#         self.ERR = 2

#         self.REQIDL = 0x26
#         self.REQALL = 0x52
#         self.AUTHENT1A = 0x60
#         self.AUTHENT1B = 0x61

#         self._initSettings()
#         self._init_motor()
#         self._init_wifi()
#         self._init_rf()
#         self._init_touch_board()

#         if self.device_run_mode == 'BLE':
#             self._init_bluetooth()
#         elif self.device_run_mode == 'MQTT':
#             self._init_mqtt()

#         print("HARDWARES INITIALIZED.\n")
        

#     # Functions
#     def _initSettings(self):        
#         if self.setting_file_name in os.listdir():
#             settings = open(self.setting_file_name, 'r')
#             for line in settings:
#                 data = line.split(':')
#                 if data[0] == 'ssid':
#                     self.ssid = data[1][:-1]
#                 elif data[0] == 'WIFIPW':
#                     self.WIFI_PW = data[1][:-1]
#                 elif data[0] == 'owner_id':
#                     self.owner_id = data[1][:-1]
#                 elif data[0] == 'MQTTSERVER':
#                     self.mqtt_server_address = data[1][:-1]
#                 elif data[0] == 'RUNMODE':
#                     self.device_run_mode = data[1][:-1]
#                 elif data[0] == 'fan1':
#                     self.fan1 = int(data[1][:-1])
#                 elif data[0] == 'fan2':
#                     self.fan2 = int(data[1][:-1])
#                 elif data[0] == 'fan3':
#                     self.fan3 = int(data[1][:-1])
#                 elif data[0] == 'fan4':
#                     self.fan4 = int(data[1][:-1])
#                 elif data[0] == 'red':
#                     self.red = int(data[1][:-1])
#                 elif data[0] == 'green':
#                     self.green = int(data[1][:-1])
#                 elif data[0] == 'blue':
#                     self.blue = int(data[1][:-1])
#                 elif data[0] == 'light':
#                     self.light = int(data[1][:-1])
#             settings.close()

#         else:
#             # 설정값 및 설정 파일 초기화
#             # this block will excute once at the first time
#             self.ssid = ''
#             self.WIFI_PW = ''
#             self.owner_id = ''
#             self.mqtt_server_address = ''
#             self.device_run_mode = 'BLE'
#             self.fan1 = 0
#             self.fan2 = 0
#             self.fan3 = 0
#             self.fan4 = 0

#             # set default led color as purple
#             self.red = 102
#             self.green = 0
#             self.blue = 102
#             self.light = 0

#             self._saveSettings()


#     def getState(self, mode='reported'):
#         SHADOW = '''
# {
#     "state": {
#         "%s": {
#             "red":%d,
#             "green":%d,
#             "blue":%d,
#             "light":%d,
#             "capsule1_id":"",
#             "capsule2_id":"",
#             "capsule3_id":"",
#             "capsule4_id":"",
#             "fan1": %d,
#             "fan2": %d,
#             "fan3": %d,
#             "fan4": %d,
#             "owner_id": "%s",
#             "power": "%s",
#             "ssid": "%s",
#             "timestamp": %d
#         }
#     }
# }''' % (mode, self.red, self.green, self.blue, self.light, self.fan1, self.fan2, self.fan3, self.fan4, self.owner_id, self.PW_FLAG, self.ssid, self.timestamp)

#         return SHADOW

#     def _saveSettings(self):
#         settings = open(self.setting_file_name, 'w')
#         data = 'ssid:%s\n' % (self.ssid)
#         data += 'WIFIPW:%s\n' % (self.WIFI_PW)
#         data += 'owner_id:%s\n' % (self.owner_id)
#         data += 'MQTTSERVER:%s\n' % (self.mqtt_server_address)
#         data += 'RUNMODE:%s\n' % (self.device_run_mode)
#         data += 'fan1:%d\n' % (self.fan1)
#         data += 'fan2:%d\n' % (self.fan2)
#         data += 'fan3:%d\n' % (self.fan3)
#         data += 'fan4:%d\n' % (self.fan4)
#         data += 'red:%s\n' % (self.red)
#         data += 'green:%s\n' % (self.green)
#         data += 'blue:%s\n' % (self.blue)
#         data += 'light:%s\n' % (self.light)

#         settings.write(data)
#         settings.close()

#     def _init_led(self):
#         self.color_leds = neopixel.NeoPixel(Pin(self.LED_DATA_PIN), self.LED_NUM, bpp=3)


#     def _init_motor(self):
#         print("INITIALIZE MOTORS...\n")

#         self.motor1 = PWM(Pin(self.MOTOR1_PIN))
#         self.motor2 = PWM(Pin(self.MOTOR2_PIN))
#         self.motor3 = PWM(Pin(self.MOTOR3_PIN))
#         self.motor4 = PWM(Pin(self.MOTOR4_PIN))

#         self.motor1.freq(self.PWM_FREQ)
#         self.motor2.freq(self.PWM_FREQ)
#         self.motor3.freq(self.PWM_FREQ)
#         self.motor4.freq(self.PWM_FREQ)

#         self.set_fan_speed_all(0)


#     def _init_wifi(self):
#         print("INITIALIZE WIFI...\n")

#         try:
#             self.WIFI = network.WLAN(network.STA_IF)
#             self.AP_IF = network.WLAN(network.AP_IF)
#             if not self.WIFI.active():
#                 self.WIFI.active(True)
#         except Exception as e:
#             print('Wifi Init ERROR:', e)
#             self.WIFI = False
#             self.AP_IF = False

#         if self.ssid != '' and self.WIFI_PW != '' and not self.is_connected_wifi():
#             self.connect_wifi()
        
    
#     def _init_rf(self):
#         print("INITIALIZE RF...\n")

#         self.rf = mfrc522(self.SCK_PIN, self.MOSI_PIN, self.MISO_PIN, \
#             self.CS1_PIN, self.CS2_PIN, self.RFID_SW1_PIN, self.RFID_SW2_PIN, self.RFID_SW3_PIN, self.RFID_SW4_PIN)


#     def _init_touch_board(self):
#         print("INITIALIZE TOUCH BOARD...\n")

#         self.pw_sw = Pin(self.BTN_PWR_PIN, Pin.IN)
#         self.led_sw = Pin(self.BTN_LED_PIN, Pin.IN)
#         self.sw1 = Pin(self.BTN_MTR1_PIN, Pin.IN)
#         self.sw2 = Pin(self.BTN_MTR2_PIN, Pin.IN)
#         self.sw3 = Pin(self.BTN_MTR3_PIN, Pin.IN)
#         self.sw4 = Pin(self.BTN_MTR4_PIN, Pin.IN)
        
#         self.touch_board_leds = PCA9685(SoftI2C(scl=Pin(self.SCL_PIN), sda=Pin(self.SDA_PIN), freq=self.PCA_FREQ), self.PCA_ADDR)
#         self.touch_board_leds.freq(60)


#     def _init_bluetooth(self):
#         print("INITIALIZE BLUETOOTH...\n")

#         self.bleSerial = BLESerial(bluetooth.BLE())   
#         self.bleSerial.on_write(self.bluetooth_on_rx_handler)


#     def _init_mqtt(self):
#         print(self.is_connected_wifi())

#         print('MQTT - connected wifi : {}\n MQTT - run_mode : {}\n MQTT - address : {}'.format(self.is_connected_wifi(), self.device_run_mode, self.mqtt_server_address))

#         if self.is_connected_wifi() and self.device_run_mode == 'MQTT' and self.mqtt_server_address != '':
#             CERT_FILE = "aws.crt.pem"
#             KEY_FILE = "aws.key.pem"
#             MQTT_PORT = 8883
#             MQTT_HOST = self.mqtt_server_address
#             THING_NAME = self.deviceId

#             self.MQTT_KEEPALIVE_INTERVAL = 45

#             # publish
#             self.SHADOW_GET_TOPIC = "$aws/things/" + THING_NAME + "/shadow/get" 
#             self.SHADOW_UPDATE_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update"
#             # subscribe
#             self.SHADOW_GET_ACCEPTED_TOPIC = "$aws/things/" + THING_NAME + "/shadow/get/accepted"
#             self.SHADOW_UPDATE_DELTA_TOPIC = "$aws/things/" + THING_NAME + "/shadow/update/delta"
#             self.RESPONSE_RECEIVED = False

#             # TODO: 최초 연결 시 말고도 도중에 mqtt가 정상적으로 연결되어있는지 확인하는 함수가 필요합니다.
#             # 만일 사용 도중 mqtt와 연결이 끊어졌다면 주황색으로 변경해야 하는데 그럴 때를 위한 체킹 알고리즘 혹은 함수가 필요합니다.
#             try:
#                 with open(KEY_FILE, "r") as f:
#                     key = f.read()
#                 with open(CERT_FILE, "r") as f:
#                     cert = f.read()

#                 self.mqtt_client = MQTTClient(client_id=THING_NAME, server=MQTT_HOST, port=MQTT_PORT, keepalive=5000, ssl=True, ssl_params={"cert":cert, "key":key, "server_side":False})
#                 self.mqtt_client.set_callback(self.sub_cb)
#                 self.mqtt_client.connect()
#                 self.mqtt_client.subscribe(self.SHADOW_GET_ACCEPTED_TOPIC)
#                 self.mqtt_client.subscribe(self.SHADOW_UPDATE_DELTA_TOPIC)
#                 self.is_dimming = False
#                 self.set_led_color(C_COOL)
#             except Exception as e:
#                 print('MQTT init error:', e)
#                 self.is_dimming = False
#                 # set led color orange
#                 self.set_led_color(C_ORANGE)


#     def sub_cb(self, topic, msg):
#         # print('[sub_cb] topic : {}, msg : {}'.format(topic, msg))
#         parsed = ujson.loads(msg)
#         # print('[sub_cb] type : {}'.format(parsed))
#         try:
#             # get/accepted
#             if str(topic, 'utf-8').split('/')[-1] == 'accepted':
#                 # print('[sub_cb] Accepted')
#                 desired_timestamp = parsed['state']['desired']['timestamp']
#                 # Desired Timestamp가 유효하지 않으면 현재 시각 Timestamp 적용
#                 if desired_timestamp == None or desired_timestamp == '':
#                     self.timestamp = self.getTimestamp()
#                 # Desired Timestamp와 현재(Reported) Timestamp가 다르면 동기화
#                 elif desired_timestamp != self.timestamp:
#                     self.timestamp = desired_timestamp
#             # update/delta 
#             elif str(topic, 'utf-8').split('/')[-1] == 'delta':
#                 if 'desired' in parsed['state']:
#                     state = parsed['state']['desired']
#                     print(state)
                
#                     changed_led, changed_fan, changed_power = False, False, False

#                     for key, value in state.items():
#                         if key == "red" or key == "green" or key == "blue" or key == "light":
#                             changed_led = True
#                             if key == 'red': self.red = state['red']
#                             if key == 'green': self.green = state['green']
#                             if key == 'blue': self.blue = state['blue']
#                             if key == 'light': self.light = state['light']

#                         if "fan" in key:
#                             changed_fan = True
#                             if key == 'fan1': self.fan1 = state['fan1']
#                             if key == 'fan2': self.fan2 = state['fan2']
#                             if key == 'fan3': self.fan3 = state['fan3']
#                             if key == 'fan4': self.fan4 = state['fan4']

#                         if key == 'power':
#                             changed_power = True
#                             self.PW_FLAG = state['power']

#                     if changed_led:
#                         self.led_cnt = -1
#                         self.set_led_color([self.red, self.green, self.blue])
                        
#                     if changed_fan:
#                         self.set_fan_speed(1, self.fan1)
#                         self.set_fan_speed(2, self.fan2)
#                         self.set_fan_speed(3, self.fan3)
#                         self.set_fan_speed(4, self.fan4)
                        
#                     if changed_power:
#                         if self.PW_FLAG: # POWER ON
#                             self.set_led_color([self.red, self.green, self.blue])
#                             self.set_fan_speed(1, self.fan1)
#                             self.set_fan_speed(2, self.fan2)
#                             self.set_fan_speed(3, self.fan3)
#                             self.set_fan_speed(4, self.fan4)
#                         else: # POWER OFF
#                             self.set_fan_speed(1, 0)
#                             self.set_fan_speed(2, 0)
#                             self.set_fan_speed(3, 0)
#                             self.set_fan_speed(4, 0)
#                             self.set_led_color(C_OFF)


#                     # AWS IoT Update          
#                     if changed_led or changed_fan or changed_power:
#                         self.update_reported_shadow()
#                     time.sleep(0.2)

#                 # TODO : reset 동작 구현 필요
#                 # BLE로 전환시 사용
#                 # if reset:
#                 #     machine.reset()
#         except KeyError as e:
#             print("MQTT Message parsing error(KeyError)\n{}".format(e))

#     def set_wifi_ssid(self, ssid):
#         self.ssid = ssid

#         self.ssid = ssid
#         self.update_reported_shadow()

#     def set_wifi_pw(self, pw):
#         self.WIFI_PW = pw
    
#     def get_wifi_ssid(self):
#         return self.ssid

#     def get_wifi_pw(self):
#         return self.WIFI_PW

#     def connect_wifi(self):
#         try:
#             # 기존에 연결된 와이파이 연결 해제(와이파이 연결 시 새로운 와이파이 연결 불가능)
#             if self.WIFI.isconnected():
#                 self.WIFI.disconnect()
#                 time.sleep(3)

#             trycnt = 0
#             while True:
#                 try:
#                     if self.WIFI.isconnected():
#                         self.set_led_color([self.red, self.green, self.blue])
#                         break
#                     elif trycnt > 5:
#                         self.set_led_color(C_RED)
#                         break
#                     else:
#                         self.WIFI.connect(self.ssid, self.WIFI_PW)
#                         time.sleep(5)
#                 except Exception as e:
#                     print("[WIFI] Connection error1: ", e)
#                 finally:
#                     trycnt += 1
#         except Exception as e:
#             print("[WIFI] Connection error2: ", e)
    
#     def is_connected_wifi(self):
#         try:
#             return self.WIFI.isconnected()
#         except:
#             return False
    
#     def get_wifi_status(self):
#         try:
#             return self.WIFI.status()
#         except:
#             return 'STAT_ERROR'

#     def set_led_color(self, color):
#         r = color[0]
#         g = color[1]
#         b = color[2]
#         for i in range(self.LED_NUM):
#             self.color_leds[i] = (r,g,b)
#         self.color_leds.write()

#         # AWS Shadow Update
#         self.red, self.green, self.blue = (r,g,b)
    
#     def set_fan_speed(self, fan_no, speed):
#         print("set fan speed")
#         # speed range: 0% - 100%
#         # 0 -> 0
#         # 100 -> 1023
#         speed = int(10.23 * speed)

#         if fan_no == 1:
#             self.motor1.duty(speed)
#         elif fan_no == 2:
#             self.motor2.duty(speed)
#         elif fan_no == 3:
#             self.motor3.duty(speed)
#         elif fan_no == 4:
#             self.motor4.duty(speed)


#     def set_fan_speed_all(self, speed):
#         print("set fan speed all")
#         speed = int(10.23 * speed)

#         for motor in [self.motor1, self.motor2, self.motor3, self.motor4]:
#             motor.duty(speed)
        
#         self.fan1, self.fan2, self.fan3, self.fan4 = (speed for _ in range(4))
#         self.update_desired_shadow()

#     def unicode2uString(self, unicode_string):
#         # ex 딥센트  
#         # input: '\ub525\uc13c\ud2b8'
#         # output: '525B C13C D2B8'
#         result_string = ''
#         for c in unicode_string:
#             result_string += hex(ord(c))[2:] + ' '
#         return result_string[:-1]

#     def uString2unicode(self,uString):
#         # ex 딥센트  
#         # input: '525B C13C D2B8'
#         # output: '\ub525\uc13c\ud2b8'
#         uStr = uString.split(' ')
#         result_string = ''
#         for c in uStr:
#             h = '0x'+c
#             result_string += chr(int(h))
#         return result_string
    
#     def syncTime(self):
#         self.synctime = time.time()
#         if self.is_connected_wifi():
#             ntptime.settime()

#     def getTimestamp(self):
#         # mpython starts from 2000-01-01, not 1970-01-01
#         if time.time() > 700000000:
#             return 946684800 + time.time()
#         else:
#             return 0
    
#     def resetDevice(self):
#         # 기기 초기화
#         print("!!HARDWARE RESET!!")
        
#         # 와이파이 연결 해제
#         if self.WIFI.isconnected():
#             self.WIFI.disconnect()

#         # 설정 파일 초기화
#         self.ssid = ''
#         self.WIFI_PW = ''
#         self.owner_id = ''
#         self.mqtt_server_address = ''
#         self.device_run_mode = 'BLE'
#         self.fan1 = 0
#         self.fan2 = 0
#         self.fan3 = 0
#         self.fan4 = 0
#         self.red = 0
#         self.green = 0
#         self.blue = 0
#         self.light = 0

#         self._saveSettings()

#         time.sleep(3)
#         machine.reset()

#     def updateDimming(self):
#         if self.is_dimming:
#             if time.ticks_ms() - self.dimming_lastTime > 50:
#                 self.dimming_lastTime = time.ticks_ms()
#                 if self.dimming_color == 'blue':
#                     self.set_led_color([0,0,self.dimming_count])
#                 elif self.dimming_color == 'green':
#                     self.set_led_color([0,self.dimming_count,0])
#                 elif self.dimming_color == 'cool':
#                     # (60,60,160)
#                     self.set_led_color([int((60/255)*self.dimming_count),int((60/255)*self.dimming_count),int((160/255)*self.dimming_count)])

#                 if self.dimming_direction == UP:
#                     self.dimming_count += 10
#                     if self.dimming_count > 255: self.dimming_count = 255
#                 elif self.dimming_direction == DOWN:
#                     self.dimming_count -= 10
#                     if self.dimming_count < 0: self.dimming_count = 0

#                 if self.dimming_count == 255:
#                     self.dimming_direction = DOWN
#                 if self.dimming_count == 0:
#                     self.dimming_direction = UP
                
#     def updateTime(self):
#         # ntp time sync per every 12 hours
#         if time.time() - self.synctime > 12*60*60:
#             try:
#                 self.syncTime()
#             except Exception as e:
#                 print('Time Sync Error:',e)
    
#     def checkMQTTMsg(self):
#         # MQTT MOD
#         if self.device_run_mode == 'MQTT':
#             try:
#                 self.mqtt_client.check_msg()
#             except Exception as e:
#                 print('MQTT Check Msg Error:', e)
    
#     def updateDevice(self):
#         self.button_handler()
        
#         if self.click_flag and self.PW_FLAG:                
#             self.touch_board_leds.on(0)
#             self.touch_board_leds.on(3)

#             if self.led_cnt < 0:
#                 self.set_led_color([int(self.red),int(self.green),int(self.blue)])
            
#             self.LEDUpdate()
#             self.fanUpdate()
#             self.update_desired_shadow()
#             time.sleep(0.2)

#         elif self.click_flag and not self.PW_FLAG:
#             # turn off leds, fans, indicators
#             for i in range(16):
#                 self.touch_board_leds.off(i)

#             self.set_fan_speed(1,0)
#             self.set_fan_speed(2,0)
#             self.set_fan_speed(3,0)
#             self.set_fan_speed(4,0)
#             self.set_led_color(C_OFF)
#             self.update_desired_shadow()

#         self.click_flag = False

#     def LEDUpdate(self):
#         if self.startup_flag:
#             self.startup_flag = False
#         elif self.led_cnt == 0:
#             self.touch_board_leds.off(1)
#             self.touch_board_leds.off(2)
#             self.light = 0
#             self.set_led_color(C_OFF)
#         elif self.led_cnt == 1:
#             self.touch_board_leds.on(1)
#             self.touch_board_leds.off(2)
#             self.light = 50
#             self.set_led_color([100, 100, 100])
#         elif self.led_cnt == 2:
#             self.touch_board_leds.on(1)
#             self.touch_board_leds.on(2)
#             self.light = 100
#             self.set_led_color(C_WHITE)
    
#     def fanUpdate(self):
#         # Fan 1
#         if self.sw1_cnt == 0:
#             self.fan1 = 0
#             self.touch_board_leds.off(13)
#             self.touch_board_leds.off(14)
#             self.touch_board_leds.off(15)
#         elif self.sw1_cnt == 1:
#             self.fan1 = 30
#             self.touch_board_leds.off(13)
#             self.touch_board_leds.off(14)
#             self.touch_board_leds.on(15) 
#         elif self.sw1_cnt == 2:
#             self.fan1 = 60
#             self.touch_board_leds.off(13)
#             self.touch_board_leds.on(14)
#             self.touch_board_leds.on(15) 
#         elif self.sw1_cnt == 3:
#             self.fan1 = 100
#             self.touch_board_leds.on(13)
#             self.touch_board_leds.on(14)
#             self.touch_board_leds.on(15)
        
#         # Fan 2
#         if self.sw2_cnt == 0:
#             self.fan2 = 0
#             self.touch_board_leds.off(10)
#             self.touch_board_leds.off(11)
#             self.touch_board_leds.off(12)   
#         elif self.sw2_cnt == 1:
#             self.fan2 = 30
#             self.touch_board_leds.off(10)
#             self.touch_board_leds.off(11)
#             self.touch_board_leds.on(12) 
#         elif self.sw2_cnt == 2:
#             self.fan2 = 60
#             self.touch_board_leds.off(10)
#             self.touch_board_leds.on(11)
#             self.touch_board_leds.on(12) 
#         elif self.sw2_cnt == 3:
#             self.fan2 = 100
#             self.touch_board_leds.on(10)
#             self.touch_board_leds.on(11)
#             self.touch_board_leds.on(12)    

#         # Fan 3
#         if self.sw3_cnt == 0:
#             self.fan3 = 0
#             self.touch_board_leds.off(7)
#             self.touch_board_leds.off(8)
#             self.touch_board_leds.off(9)   
#         elif self.sw3_cnt == 1:
#             self.fan3 = 30
#             self.touch_board_leds.off(7)
#             self.touch_board_leds.off(8)
#             self.touch_board_leds.on(9) 
#         elif self.sw3_cnt == 2:
#             self.fan3 = 60
#             self.touch_board_leds.off(7)
#             self.touch_board_leds.on(8)
#             self.touch_board_leds.on(9) 
#         elif self.sw3_cnt == 3:
#             self.fan3 = 100
#             self.touch_board_leds.on(7)
#             self.touch_board_leds.on(8)
#             self.touch_board_leds.on(9)    

#         # Fan 4
#         if self.sw4_cnt == 0:
#             self.fan4 = 0
#             self.touch_board_leds.off(4)
#             self.touch_board_leds.off(5)
#             self.touch_board_leds.off(6)   
#         elif self.sw4_cnt == 1:
#             self.fan4 = 30
#             self.touch_board_leds.off(4)
#             self.touch_board_leds.off(5)
#             self.touch_board_leds.on(6) 
#         elif self.sw4_cnt == 2:
#             self.fan4 = 60
#             self.touch_board_leds.off(4)
#             self.touch_board_leds.on(5)
#             self.touch_board_leds.on(6) 
#         elif self.sw4_cnt == 3:
#             self.fan4 = 100
#             self.touch_board_leds.on(4)
#             self.touch_board_leds.on(5)
#             self.touch_board_leds.on(6)


#         if self.fan1 == 0:
#             self.set_fan_speed(1, 0)
#         elif self.fan1 == 30:
#             self.set_fan_speed(1, 72)
#         elif self.fan1 == 60:
#             self.set_fan_speed(1, 80)
#         elif self.fan1 == 100:
#             self.set_fan_speed(1, 100)
        
#         if self.fan2 == 0:
#             self.set_fan_speed(2, 0)
#         elif self.fan2 == 30:
#             self.set_fan_speed(2, 75)
#         elif self.fan2 == 60:
#             self.set_fan_speed(2, 83)
#         elif self.fan2 == 100:
#             self.set_fan_speed(2, 100)
        
#         if self.fan3 == 0:
#             self.set_fan_speed(3, 0)
#         elif self.fan3 == 30:
#             self.set_fan_speed(3, 72)
#         elif self.fan3 == 60:
#             self.set_fan_speed(3, 80)
#         elif self.fan3 == 100:
#             self.set_fan_speed(3, 100)
        
#         if self.fan4 == 0:
#             self.set_fan_speed(4, 0)
#         elif self.fan4 == 30:
#             self.set_fan_speed(4, 72)
#         elif self.fan4 == 60:
#             self.set_fan_speed(4, 89)
#         elif self.fan4 == 100:
#             self.set_fan_speed(4, 100)

#     def button_handler(self):
#         if not self.click_flag:
#             if self.led_sw.value() == 0:
#                 self.click_flag = True
#                 self.led_cnt += 1
#                 if self.led_cnt == 3:
#                     self.led_cnt = 0
            
#             if self.sw1.value() == 0:
#                 self.click_flag = True
#                 self.sw1_cnt += 1
#                 if self.sw1_cnt == 4:
#                     self.sw1_cnt = 0
                    
#             if self.sw2.value() == 0:
#                 self.click_flag = True
#                 self.sw2_cnt += 1
#                 if self.sw2_cnt == 4:
#                     self.sw2_cnt = 0
                    
#             if self.sw3.value() == 0:
#                 self.click_flag = True
#                 self.sw3_cnt += 1
#                 if self.sw3_cnt == 4:
#                     self.sw3_cnt = 0
                    
#             if self.sw4.value() == 0:
#                 self.click_flag = True
#                 self.sw4_cnt += 1
#                 if self.sw4_cnt == 4:
#                     self.sw4_cnt = 0


#     # bluetooth handler
#     def bluetooth_on_rx_handler(self, cmd):
#         print("RX", cmd)

#         temp = cmd.decode('utf-8')
#         if temp.startswith('#{') and temp.endswith('}$'):
#             self.RECEIVE_FINISHED = True
#             self.RECEIVED_DATA = temp[1:-1]
#         elif temp.startswith('#{'):
#             print('[BLE] Received SOF')

#             self.RECEIVED_DATA = temp[1:]
#         elif temp.endswith('}$'):
#             print('[BLE] Received EOF')

#             self.RECEIVE_FINISHED = True
#             self.RECEIVED_DATA += temp[:-1]
#         else:
#             self.RECEIVED_DATA += temp

#         if self.RECEIVE_FINISHED:
#             print('[BLE] Received data:', self.RECEIVED_DATA)

#             sData_to_be_transfered = ''

#             try:
#                 parsed = ujson.loads(self.RECEIVED_DATA)
                
#                 print('[BLE] Parsed data: ', parsed)
                
#                 if parsed['method'] == 'ping':
#                     sData_to_be_transfered = """{"method":"ping","src":"%s","result":true}""" % (self.deviceId)

#                 elif parsed['method'] == 'getDeviceId':
#                     sData_to_be_transfered = """{"method":"getDeviceId","src":"%s","result":{"deviceId":"%s"}}""" % (self.deviceId, self.deviceId)

#                 elif parsed['method'] == 'setDeviceOwner':
#                     # dimming start
#                     self.dimming_color = 'blue'
#                     self.dimming_count = 0
#                     self.is_dimming = True

#                     self.ownerId = parsed['data']['ownerId']
#                     self._saveSettings()
#                     sData_to_be_transfered = """{"method":"setDeviceOwner","src":"%s","result":true}""" % (self.deviceId)

#                 elif parsed['method'] == 'setCert':
#                     key = parsed['data']['key']
#                     key_file = open('aws.key.pem', 'w')
#                     key_file.write(key)
#                     key_file.close()

#                     crt = parsed['data']['crt']
#                     crt_file = open('aws.crt.pem', 'w')
#                     crt_file.write(crt)
#                     crt_file.close()

#                     sData_to_be_transfered = """{"method":"setCert","src":"%s","result":true}""" % (self.deviceId)

#                     # dimming stop
#                     self.is_dimming = False
#                     self.set_led_color(C_OFF)

#                 elif parsed['method'] == 'wifiScan':
#                     if self.WIFI != False:
#                         # 기존에 연결된 와이파이 연결 해제(와이파이 연결 시 스캔 불가능)
#                         if self.WIFI.isconnected():
#                             self.WIFI.disconnect()
#                             time.sleep(2)

#                         self.wifi_list = self.WIFI.scan()

#                         print(self.wifi_list)

#                         if (len(self.wifi_list) > 0):
#                             self.total_frame = 6
#                         else:
#                             self.total_frame = 0

#                         self.frame_index = 0
                        
#                         sData_to_be_transfered = """{"method":"wifiScan","src":"%s","result":%d}""" % (self.deviceId, self.total_frame)
#                     else:
#                         sData_to_be_transfered = """{"method":"wifiScan","src":"%s","result":%d}""" % (self.deviceId, 0)

#                 elif parsed['method'] == 'wifiList':
#                     self.set_led_color(C_GREEN)
#                     if self.total_frame != 0 and self.frame_index < self.total_frame:
#                         _ssid = self.unicode2uString(self.wifi_list[self.frame_index][0].decode('utf-8'))
#                         _authmode = self.wifi_list[self.frame_index][4]
#                         _rssi = self.wifi_list[self.frame_index][3]

#                         wifi = """{"ssid":"%s","authmode":%d,"rssi":%d}""" % (_ssid, _authmode, _rssi)

#                         self.frame_index += 1

#                         sData_to_be_transfered = """{"method":"wifiList","src":"%s","totalFrame":%d,"frameIndex":%d,"result":%s}""" % (self.deviceId, self.total_frame, self.frame_index, wifi)
#                     else:
#                         sData_to_be_transfered = """{"method":"wifiList","src":"%s","result":false}""" % (self.deviceId)

#                 elif parsed['method'] == 'setWifi':
#                     # dimming start
#                     self.dimming_color = 'green'
#                     self.dimming_count = 0
#                     self.is_dimming = True

#                     # 와이파이 정보 업데이트
#                     self.ssid = self.uString2unicode(parsed['data']['ssid'])
#                     self.WIFI_PW = parsed['data']['pwd']
#                     self._saveSettings()

#                     # 와이파이 연결 (기존 연결시 연결 해제 후 업데이트 된 와이파이정보로 연결)
#                     self.connect_wifi()
                    
#                     # 10초 내 연결 완료되면 true 응답, 그렇지 않을경우 false 응답
#                     t = time.time()
#                     sData_to_be_transfered = """{"method":"setWifi","src":"%s","result":false}""" % (self.deviceId)
                    
#                     # set color red
#                     result = False
#                     while time.time() - t > 10:
#                         if self.is_connected_wifi():
#                             sData_to_be_transfered = """{"method":"setWifi","src":"%s","result":true}""" % (self.deviceId)
#                             # set color green (wifi connected)
#                             result = True
#                             break
#                         time.sleep(1)
                    
#                     # dimming stop
#                     self.is_dimming = False

#                 elif parsed['method'] == 'wifiConnected':
#                     status_message = ''
#                     if self.WIFI != False:
#                         status = self.WIFI.status()
#                         if status == network.STAT_IDLE:
#                             status_message = 'STAT_IDLE'
#                         elif status == network.STAT_WRONG_PASSWORD:
#                             status_message = 'STAT_WRONG_PASSWORD'
#                         elif status == network.STAT_NO_AP_FOUND:
#                             status_message = 'STAT_NO_AP_FOUND'
#                         elif status == network.STAT_GOT_IP:
#                             status_message = 'STAT_GOT_IP'
#                     if self.is_connected_wifi():
#                         self.set_led_color(C_WHITE)

#                         try:
#                             self.syncTime()
#                         except Exception as e:
#                             print('Time Sync failed in wifiConnected:', e)

#                         sData_to_be_transfered = """{"method":"wifiConnected","src":"%s","result":{"ssid":"%s","status":"%s","connected":true}}""" % (self.deviceId, self.unicode2uString(self.ssid), status_message)
#                     else:
#                         self.set_led_color(C_RED)
#                         sData_to_be_transfered = """{"method":"wifiConnected","src":"%s","result":{"ssid":"%s","status":"%s","connected":false}}""" % (self.deviceId, self.unicode2uString(self.ssid), status_message)

#                 elif parsed['method'] == 'setMqttServer':
#                     self.mqtt_server_address = parsed['data']['server']

#                     # crt 파일과 key 파일이 없을경우 MQTT 모드로 넘기지 않음. (블루투스가 끊어지는것을 방지)
#                     # 앱에서 setMqttServer 명령을 실행하기전에 유저에게 블루투스가 끊어질 것임을 알림 필요
#                     if 'aws.crt.pem' in os.listdir() and 'aws.key.pem' in os.listdir():
#                         self.device_run_mode = 'MQTT'
#                         self._saveSettings()
#                         sData_to_be_transfered = """{"method":"setMqttServer","src":"%s","result":true}""" % (self.deviceId)
#                     else:
#                         # False가 반환될 경우 mqtt 인증파일 전송 필요
#                         sData_to_be_transfered = """{"method":"setMqttServer","src":"%s","result":false}""" % (self.deviceId)


#                 if sData_to_be_transfered:
#                     # print('[BLE] Send data:', sData_to_be_transfered)

#                     self.bleSerial.send(sData_to_be_transfered)

#                     self.RECEIVE_FINISHED = False
#                     self.RECEIVED_DATA = ''
#                     sData_to_be_transfered = ''

#                     if self.device_run_mode == 'MQTT':
#                         # 인증서 전송이 끝나면 녹색 켜기
#                         self.set_led_color(C_GREEN)
                        
#                         time.sleep(5)
#                         # 기기 리셋한 후 MQTT 모드로 진입
#                         machine.reset()
#                 else:
#                     print('[BLE] No data to be sent.')

#                     self.RECEIVE_FINISHED = False
#                     self.RECEIVED_DATA = ''
#                     sData_to_be_transfered = ''

#             except Exception as e:
#                 pass

#     def update_desired_shadow(self):
#         desired_shadow = self.getState('desired')
#         self._update_shadow(desired_shadow)

#     def update_reported_shadow(self):
#         reported_shadow = self.getState('reported')
#         self._update_shadow(reported_shadow)

#     def _update_shadow(self, shadow):
#         try:
#             if self.mqtt_client:
#                 # print("[Update Shadow] MQTT Update Publish\n")
#                 # print("[Update Shadow] Shadow : {}".format(shadow))
#                 self.mqtt_client.publish(self.SHADOW_UPDATE_TOPIC, shadow)
#             else:
#                 print("[Update Shadow] MQTT Client is None")
#         except Exception as e:
#             # traceback.print_exc()
#             print("MQTT Publish Error : {}".format(e))

#     def run(self):
#         timecount = 0

#         while True:
#             # power button
#             if self.pw_sw.value() == 0:
#                 if timecount == 0:
#                     self.click_flag = True
#                     timecount = time.time()
#                     self.PW_FLAG = not self.PW_FLAG

#                 elif time.time() - timecount > 2 and time.time() - timecount < 5:
#                     # reset press
#                     for i in range(3):
#                         self.set_led_color(C_WHITE)
#                         time.sleep(0.5)
#                         self.set_led_color(C_OFF)
#                         time.sleep(0.5)

#                 elif time.time() - timecount > 5:
#                     # reset
#                     self.resetDevice()

#                 time.sleep(0.1)

#             else:
#                 timecount = 0
#                 self.checkMQTTMsg()
#                 self.updateTime()
#                 self.updateDimming()
#                 self.updateDevice()


# micropython.alloc_emergency_exception_buf(100)
# gc.enable()

lounge = LOUNGE()
lounge.run()
