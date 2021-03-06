import signal
import time
from enum import IntEnum, unique


class Time:
    "Maintain the current time in seconds"
    now = 0

    def tick(self):
        self.now = time.time()

mytime = Time()

@unique
class Types(IntEnum):
    DOOR_SENSOR = 1
    MOTION_SENSOR = 2
    LIGHT = 3
    SWITCH = 4
    TEMPERATURE_SENSOR = 5
    HUMIDITY_SENSOR = 6
    LIGHT_SENSOR = 7

device_type_names = ['', 'Door sensor', 'Motion sensor', 'Lamp', 'Switch',
                     'Temperature sensor', 'Humidity sensor', 'Light sensor']

class Device:
    id = None
    room = None
    type = None
    control = []
    # State of lamp, led strip, switch, motion sensor or similar device
    is_on = False
    # Maximum amount of seconds for a device to be on before automatic off
    max_time = None
    # The time of automatic off, to be set runtime
    off_time = 0

    type_names = ['', 'Door sensor', 'Motion sensor', 'Lamp', 'Switch',
                         'Temperature sensor', 'Humidity sensor', 'Light sensor']

    def __unicode__(self):
        return '%5s %s in %s' % (self.id, self.type_names[self.type], self.room)

    def __init__(self, id, type, room, control=[], max_time=None):
        self.id = id
        assert 0 < int(type) < len(self.type_names)
        self.type = type
        self.room = room
        assert isinstance(control, list)
        self.control = control
        self.max_time = max_time
        print('Created device: ', self.__unicode__())

    def status(self):
        result = [self.__unicode__(), ' is now ', 'On' if self.is_on else 'Off']
        if self.off_time:
            result.append(' until %d' % (self.off_time,))
        return ''.join(result)

    def set_on(self, is_on):
        global mytime
        self.is_on = is_on
        if self.type == Types.MOTION_SENSOR:
            # If motion sensor noticed motion, switch all connected devices on
            if self.is_on:
                for d in self.control:
                    d.set_on(True)
        else:
            # For other types of devices, toggle all connected devices
            for d in self.control:
                d.toggle()
        # Make sure the device switches off after max_time
        if is_on and self.max_time:
            # Set automatic off time
            self.off_time = mytime.now + self.max_time
        # Switching off? No need for automatic off_time
        if not is_on:
            self.off_time = 0
        print(self.status())

    def toggle(self):
        self.set_on(not self.is_on)

    def tick(self):
        global mytime
        if self.off_time and mytime.now >= self.off_time:
            self.off_time = 0
            self.set_on(False)


class Devices:

    # A list of the connected home automation devices
    list = {}

    def append(self, device: Device):
        self.list[device.id] = device

    def toggle(self, device):
        if isinstance(device, str):
            device = self.find(device)
        assert isinstance(device, Device)
        device.toggle()
        self.tick()

    def items(self):
        return self.list.items()

    def find(self, id):
        return self.list[id]

    def post_load(self):
        for id, d in self.list.items():
            assert isinstance(d, Device)
            # Replace each string reference with the actual device
            l = d.control
            d.control = []
            assert isinstance(l, list)
            for i in l:
                controlled = self.find(i)
                # TODO: This is a copy, right? How to reference the instance?
                d.control.append(controlled)

    def set_next_alarm(self):
        "Figure out which device should be switched off next and when"
        seconds_list = []
        now = mytime.now
        for id, d in self.list.items():
            assert isinstance(d, Device)
            if d.off_time:
                seconds_until_off_time = int(d.off_time-now)
                seconds_list.append(seconds_until_off_time)
                # print('Device %s off in %d seconds.' % (d.id, seconds_until_off_time))
        if len(seconds_list):
            # Which seconds_until_off_time is the smallest, hence the next one?
            next_alarm_in_seconds = sorted(seconds_list)[0]
            # print('Next alarm in %d seconds.' % (next_alarm_in_seconds,))
            # Let's wake up again when the next device is to be switched off
            signal.alarm(next_alarm_in_seconds+1)

    def tick(self):
        """Call this every second or after each input"""
        global mytime
        mytime.tick()
        self.set_next_alarm()
        for id, device in self.list.items():
            assert isinstance(device, Device)
            # Let each device check if it needs to switch off
            device.tick()

    def now(self):
        global mytime
        return mytime.now

