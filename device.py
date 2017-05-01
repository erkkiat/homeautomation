class Time:
    "Fake time for debugging purposes only"
    now = 0

    def tick(self):
        "Pass time one unit"
        self.now = self.now + 1

time = Time()


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

    class Types:
        DOOR_SENSOR = 1
        MOTION_SENSOR = 2
        LIGHT = 3
        SWITCH = 4
        TEMPERATURE_SENSOR = 5
        HUMIDITY_SENSOR = 6
        LIGHT_SENSOR = 7

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
        global time
        self.is_on = is_on
        if self.type == self.Types.MOTION_SENSOR:
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
            self.off_time = time.now + self.max_time
        # Switching off? No need for automatic off_time
        if not is_on:
            self.off_time = 0
        print(self.status())

    def toggle(self):
        self.set_on(not self.is_on)

    def tick(self):
        global time
        if self.off_time and time.now >= self.off_time:
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

    def tick(self):
        """Call this every second or after each input"""
        global time
        time.tick()

        for id, d in self.list.items():
            assert isinstance(d, Device)
            d.tick()

    def now(self):
        global time
        return time.now
