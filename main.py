import json
import websockets
import asyncio
import os
import datetime
# import onionGpio
import time 
import shutil
        
# RELAY1_PIN = onionGpio.OnionGpio(15)
# RELAY2_PIN = onionGpio.OnionGpio(16)
# RELAY3_PIN = onionGpio.OnionGpio(17)
# waterSensor_H = onionGpio.OnionGpio(19)
# waterSensor_L = onionGpio.OnionGpio(18)
# network_led = onionGpio.OnionGpio(2)
# server_led = onionGpio.OnionGpio(3)
# waterSensor_H_led = onionGpio.OnionGpio(1)
# waterSensor_L_led = onionGpio.OnionGpio(0)

RELAY1_PIN = 15
RELAY2_PIN = 16
RELAY3_PIN = 17
network_led = 2
server_led = 3


SERVER_STATUS = True
Manual_Relay_Info = [[False, 0],[False, 0],[False, 0],[False, 0],[False, 0],[False, 0],[False, 0],[False, 0]]

RELAYS_PARAM = []
VERSION = '2.2'


Relay_Pins = [RELAY1_PIN, RELAY2_PIN, RELAY3_PIN]
res = os.popen('ifconfig br-wlan | grep HWaddr').readline()
mac = res.lstrip().split('HWaddr')[1][1:-1].replace(':','').replace(' ', '')
setting_id = mac[-4:]
uri = 'wss://admin.azmo.kr/azmo_ws?%s' % (setting_id)

os.system('fast-gpio set-output 15')
time.sleep(1)
os.system('fast-gpio set-output 16')
time.sleep(1)
os.system('fast-gpio set-output 17')
time.sleep(1)
os.system('fast-gpio set-output 2')
time.sleep(1)
os.system('fast-gpio set-output 3')
time.sleep(1)

def setGpio(num, value):
    os.system('fast-gpio set %d %d' % (num, value))

def saveParams(RELAYS_PARAM):
    params = {
        "CONTROL": [json.loads(RELAYS_PARAM[0]),
                    json.loads(RELAYS_PARAM[1]),
                    json.loads(RELAYS_PARAM[2])
                    ]
        }
    with open('/root/saved3.json', 'w', encoding='utf-8') as make_file:
        json.dump(params, make_file, indent='\t')

def checkNetwork():
    res = os.popen('ping -c 1 -W 1 -w 1 8.8.8.8 | grep loss').readline()
    if '100%' in res:
        setGpio(network_led, 0)
        setGpio(server_led, 0)
        return False
    else:
        setGpio(network_led, 1)
        return True

def readParams():
    relay_list = [1,2,3]
    if os.path.exists('/root/saved3.json'):
        with open('/root/saved3.json', 'r', encoding='utf-8') as read_file:
            d = json.load(read_file)
            for relay in d['CONTROL']:
                j = json.dumps(relay)
                jj = int(json.loads(j)["RELAY"])
                relay_list.remove(jj)
                RELAYS_PARAM.append(j)
            
            for relay in relay_list:
                j = '''{"RELAY": "%d", "NAME": "", "MODE": "onoff", "ONOFFINFO": "off"}''' % (relay)
                RELAYS_PARAM.append(j)
                
    else:
        pData = '''
{
	"CONTROL": [
		{
			"RELAY": "1",
			"NAME": "RELAY1",
			"MODE": "onoff",
			"ONOFFINFO": "off"
		},
		{
			"RELAY": "2",
			"NAME": "RELAY2",
			"MODE": "onoff",
			"ONOFFINFO": "off"
		},
		{
			"RELAY": "3",
			"NAME": "RELAY3",
			"MODE": "onoff",
			"ONOFFINFO": "off"
		}
	]
}
'''
        with open('/root/saved3.json', 'w', encoding='utf-8') as save_file:
            save_file.write(pData)
        
        with open('/root/saved3.json', 'r', encoding='utf-8') as read_file:
            d = json.load(read_file)
            for relay in d['CONTROL']:
                RELAYS_PARAM.append(json.dumps(relay))

        # RELAYS_PARAM = ['{"RELAY":"1", "MODE":"onoff", "SETINFO":"off"}', '{"RELAY":"2", "MODE":"onoff", "SETINFO":"off"}', '{"RELAY":"3", "MODE":"onoff", "SETINFO":"off"}', '{"RELAY":"4", "MODE":"onoff", "SETINFO":"off"}', '{"RELAY":"5", "MODE":"onoff", "SETINFO":"off"}', '{"RELAY":"6", "MODE":"onoff", "SETINFO":"off"}', '{"RELAY":"7", "MODE":"onoff", "SETINFO":"off"}', '{"RELAY":"8", "MODE":"onoff", "SETINFO":"off"}']


def runManualMode(ONOFFINFO):
    if ONOFFINFO == 'on': return True
    else: return False
                
def runPeriodictMode(WEEKINFO):
    try:
        # "SETINFO": {"START_DT": "20220909", "REPEAT_DAY": "15", "START_TIME": "0030", "END_TIME": "0100"}}
        scheduled_date = datetime.datetime.strptime(WEEKINFO['START_DT'], '%Y-%m-%d').replace(tzinfo=datetime.timezone(datetime.timedelta(hours=9)))
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))
        diff = now - scheduled_date

        if diff.days % int(WEEKINFO['REPEAT_DAY']) == 0:
            if int(WEEKINFO['START_TIME']) <= now.hour*100 + now.minute < int(WEEKINFO['END_TIME']):
                return True

        return False
    except Exception as e:
        print('WEEK INFO ERROR:', e)
        return False

def runWeeklyRepeatMode(REPEATINFO):
    try:
        # "SETINFO": [{"WEEK_INFO": "1", "START_TIME": "0100", "END_TIME": "0200"}, {"WEEK_INFO": "2", "START_TIME": "0100", "END_TIME": "0200"}]
        # Mon(1), Tue(2), Wed(3), Thu(4), Fri(5), Sat(6), Sun(7)
        now = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9)))
        
        for element in REPEATINFO:
            if int(element['WEEK_INFO']) == now.weekday()+1:
                if int(element['START_TIME']) <= now.hour*100 + now.minute < int(element['END_TIME']):
                    return True
        
        return False
    except Exception as e:
        print('WEEK INFO ERROR:', e)
        return False


def updateRelay():
    # global RELAYS_PARAM, Manual_Relay_Info, Relay_Pins
    
    try:
        print('\n--------------- checking relay params ---------------')
        for idx, relay in enumerate(RELAYS_PARAM):
            result = False
            
            relay = json.loads(relay)
            print(relay)
            
            if relay['MODE'] == 'onoff':   # manual mode
                result = runManualMode(relay['ONOFFINFO'])
                if relay['ONOFFINFO'] == 'on' and Manual_Relay_Info[idx][0] == False:
                    Manual_Relay_Info[idx][0] = True
                    Manual_Relay_Info[idx][1] = time.time()
                elif relay['ONOFFINFO'] == 'off': Manual_Relay_Info[idx][0] = False
                
            
            elif relay['MODE'] == 'repeat':   # weekly repeat mode
                result = runWeeklyRepeatMode(relay['REPEATINFO'])
                Manual_Relay_Info[idx][0] = False

            elif relay['MODE'] == 'week': # periodic mode
                result = runPeriodictMode(relay['WEEKINFO'])
                Manual_Relay_Info[idx][0] = False
                
            
            if Manual_Relay_Info[idx][0] == True and time.time() - Manual_Relay_Info[idx][1] > 60*20:
                result = False
                RELAYS_PARAM[idx] = '''{"RELAY": "%d", "NAME": "%s", "MODE": "onoff", "ONOFFINFO": "off"}''' % (idx+1, relay['NAME'])
                Manual_Relay_Info[idx][0] = False
                saveParams(RELAYS_PARAM)


            if result:
                setGpio(Relay_Pins[idx], 0) # 0 means on
            else:
                setGpio(Relay_Pins[idx], 1) # 1 means off

        print('-----------------------------------------------------\n')
    except Exception as e:
        print('Update Realy Error:', e)

async def update(ws):
    global SERVER_STATUS
    ping_pong_time_check = 0
    while True:
        if not SERVER_STATUS: break
        try:
            await asyncio.sleep(5)
            updateRelay()
            checkNetwork()
        except Exception as e:
            print('update error', e)

        # ping pong 
        if int(time.time()) - ping_pong_time_check > 20:
            ping_pong_time_check = int(time.time())
            params = {
                "METHOD": "PING"
            }
            pData = json.dumps(params)
            await ws.send(pData)

async def recv_handler(ws):
    global RELAYS_PARAM, SERVER_STATUS
    
    while True:
        await asyncio.sleep(0)
        if not SERVER_STATUS: break
        try:
            data = await ws.recv()
            d = json.loads(data)
            print('recieved:', d)
            
            if d['METHOD'] == 'CALL_A':
                params = {
                "METHOD": "CALL_R",
                "CONTROL": [json.loads(RELAYS_PARAM[0]),
                            json.loads(RELAYS_PARAM[1]),
                            json.loads(RELAYS_PARAM[2])
                        ]
                }
                pData = json.dumps(params)
                await ws.send(pData)
                setGpio(server_led, 1)
            
            elif d['METHOD'] == 'TOTAL_STATUS':
                params = {
                    "METHOD": "TOTAL_STATUS",
                    "DEVICE_ID": setting_id,
                    "SENSOR_STATUS": False,
                    "VERSION": VERSION
                }
                pData = json.dumps(params)
                await ws.send(pData)
                
            
            elif d['METHOD'] == 'UPT_R':
                for relay in d['CONTROL']:
                    # print(relay)
                    if relay['RELAY'] == "1":
                        RELAYS_PARAM[0] = json.dumps(relay)
                    elif relay['RELAY'] == "2":
                        RELAYS_PARAM[1] = json.dumps(relay)
                    elif relay['RELAY'] == "3":
                        RELAYS_PARAM[2] = json.dumps(relay)
                saveParams(RELAYS_PARAM)
                setGpio(server_led, 1)

            elif d['METHOD'] == 'R_START':
                params = {
                    "METHOD": "R_START",
                    "RESULT": True
                }
                pData = json.dumps(params)
                await ws.send(pData)
                await asyncio.sleep(5)
                os.system('reboot')
                SERVER_STATUS = False
            
            elif d['METHOD'] == 'OTA':
                path = '/root/main.py'
                if os.path.isfile(path):
                    os.remove(path)
                os.system('wget -P /root/ https://raw.githubusercontent.com/picshbj/ecsmartrelay/master/main.py')

                await asyncio.sleep(10)
                os.system('reboot')

                params = {
                    "METHOD": "OTA",
                    "RESULT": True
                }
                pData = json.dumps(params)
                await ws.send(pData)
                SERVER_STATUS = False
                    

        except Exception as e:
            SERVER_STATUS = False
            print('Recieve Error', e)
            
            

async def main():
    global SERVER_STATUS
    readParams()
    
    while True:
        print('Updating Relays..')
        updateRelay()
        print('Creating a new websockets..')
        SERVER_STATUS = True
        os.system('ntpd -q -p ptbtime1.ptb.de')
        
        try:
            async with websockets.connect(uri) as ws:
                await asyncio.gather(
                    recv_handler(ws),
                    update(ws)
                )
        except Exception as e:
            print('Main Error:', e)
            SERVER_STATUS = False
            await asyncio.sleep(1)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
