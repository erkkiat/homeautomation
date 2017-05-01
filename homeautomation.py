import signal
import json
from device import Device, Devices

TIMEOUT = 3 # number of seconds your want for timeout
SETTINGS_FILE = 'settings.json'

rooms = [
    {'name': 'living'},
    {'name': 'kitchen'},
    {'name': 'toilet'},
    {'name': 'bathroom'},
    {'name': 'bedroom'},
]

class device_types:
    DOOR_SENSOR=1
    MOTION_SENSOR=2
    LIGHT=3
    SWITCH=4
    TEMPERATURE_SENSOR=5
    HUMIDITY_SENSOR=6
    LIGHT_SENSOR=7

device_type_names = ['', 'Door sensor', 'Motion sensor', 'Lamp', 'Switch',
                     'Temperature sensor', 'Humidity sensor', 'Light sensor']

def control(id):
    d = devices[id]
    for c in d['control']:
        device = devices[c]
        action_by_device_type(device['type'])(device, c)

def motion(device, id):
    print('Motion detected at %s' % (id,))
    control(id)

def flip(device, id):
    print('Switch %s flipped' % (id,))
    control(id)

def switch(device, id, state=0):
    if state:
        result = state
    else:
        if 'state' in device and device['state']:
            print('Light %s switched off' % (id,))
        else:
            print('Light %s switched on' % (id,))
    device['state'] = state


def action_by_device_type(type):
    actions = [None, None, motion, switch, flip, None, None, None]
    return actions[type]

def activate(s):
    if not s:
        return False
    if s not in devices:
        print('No such device found')
        return False
    device = devices[s]
    f = action_by_device_type(device['type'])
    f(device, s)

def list_devices():
    for id, d in device_list.items():
        print('%5s %s in %s' % (id, device_type_names[d.type], d.room))


def interrupted(signum, frame):
    "called when read times out"
    global now
    print ('interrupted %d' % (now,))
    now = now + 1
    signal.alarm(TIMEOUT)

# signal.signal(signal.SIGALRM, interrupted)

def my_input():
    try:
        foo = input('Time=%d> ' % (device_list.now(),))
        device_list.tick()
        return foo
    except:
        raise
        exit(0)


device_list = Devices()

# Read settings from file
try:
    with open(SETTINGS_FILE, 'r') as file:
        a = ''.join(file.readlines())
        # print(a)
        devices = json.loads(a)
        print('Settings read from "%s"' % (SETTINGS_FILE,))
        # Create the device objects based on settings file
        for id, device in devices.items():
            assert isinstance(id, str)
            device['id'] = id
            d = Device(**device)
            device_list.append(d)
        device_list.post_load()
except FileNotFoundError:
    print('Error reading file "%s". Creating it.' % (SETTINGS_FILE,))
    devices = {
        'mk': {'type': device_types.MOTION_SENSOR, 'room': 'kitchen', 'control': ['lk']},
        'sk': {'type': device_types.SWITCH, 'room': 'kitchen', 'control': ['lk']},
        'lk': {'type': device_types.LIGHT, 'room': 'kitchen'},
    }
    with open(SETTINGS_FILE, 'w') as file:
            print(json.dumps(devices, indent=4), file=file)

for i in range(0,15):
    # set alarm
    # signal.alarm(TIMEOUT)
    s = my_input()
    if s == 'list':
        list_devices()
    else:
        if s:
            try:
                device_list.toggle(s)
            except KeyError:
                print('Use device names such as %s' % ','.join(device_list.list))