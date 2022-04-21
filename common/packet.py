class Packet:

    def __init__(self, src, dest):
        self.src = src
        self.dest = dest


class DNSQueryPacket(Packet):
    def __init__(self, src, dest, name):
        super().__init__(src, dest)
        self.name = name

    def __str__(self):
        return "<%s -> %s | (%s)>" % (self.src, self.dest, self.name)


class DNSResponsePacket(Packet):
    def __init__(self, src, dest, name, ip):
        super().__init__(src, dest)
        self.name = name
        self.ip = ip

    def __str__(self):
        return "<%s -> %s | (%s, %s)>" % (self.src, self.dest, self.name, self.ip)
