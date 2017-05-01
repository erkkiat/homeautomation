import json
import signal

import device
import settings
from device import Device, Devices
from sun import Sun

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
    device_list.tick()
    signal.alarm(5)

signal.signal(signal.SIGALRM, interrupted)

def my_input():
    foo = input('Time=%d> ' % (device_list.now(),))
    device_list.tick()
    return foo


device_list = Devices()

# Read settings from file
try:
    with open(settings.DEVICES_FILE, 'r') as file:
        a = ''.join(file.readlines())
        # print(a)
        devices = json.loads(a)
        print('Settings read from "%s"' % (settings.DEVICES_FILE,))
        # Create the device objects based on settings file
        for id, device in devices.items():
            assert isinstance(id, str)
            device['id'] = id
            d = Device(**device)
            device_list.append(d)
        device_list.post_load()
except FileNotFoundError:
    print('Error reading file "%s". Creating it.' % (settings.DEVICES_FILE,))
    devices = {
        'mk': {'type': device.Types.MOTION_SENSOR, 'room': 'kitchen', 'control': ['lk']},
        'sk': {'type': device.Types.SWITCH, 'room': 'kitchen', 'control': ['lk']},
        'lk': {'type': device.Types.LIGHT, 'room': 'kitchen'},
    }
    with open(settings.DEVICES_FILE, 'w') as file:
            print(json.dumps(devices, indent=4), file=file)

sun = Sun()
print("Dawn is at %s and dusk at %s today." % (sun.datetime('dawn').strftime('%H:%M'),
                                               sun.datetime('dusk').strftime('%H:%M')))

for i in range(0,15):
    # set interrupt for switching lamps on and off when needed
    signal.alarm(5)
    s = my_input()
    if s == 'list':
        list_devices()
    else:
        if s:
            try:
                device_list.toggle(s)
            except KeyError:
                print('Use device names such as %s' % ','.join(device_list.list))
