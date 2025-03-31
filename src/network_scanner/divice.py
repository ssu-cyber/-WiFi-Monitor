class Device:
    def __init__(self, ip, mac, vendor, hostname):
        self.ip = ip
        self.mac = mac
        self.vendor = vendor
        self.hostname = hostname
        self.first_seen = None
        self.last_seen = None
        self.is_authorized = False
        self.is_blocked = False
        self.notes = ""

    def to_dict(self):
        return {
            'ip': self.ip,
            'mac': self.mac,
            'vendor': self.vendor,
            'hostname': self.hostname,
            'is_authorized': self.is_authorized,
            'is_blocked': self.is_blocked,
            'notes': self.notes
        }