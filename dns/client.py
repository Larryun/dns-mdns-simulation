import ipaddress

from common.device import Device
from common.packet import DNSQueryPacket, DNSResponsePacket
from common.constant import DNS_ENTRY_EXPIRATION_TIME
from dns.server import DNSServer
import random


class DNSClient(Device):

    def __init__(self, env, name: str, ip: ipaddress.IPv4Address, dns_server: DNSServer):
        super().__init__(env, name, ip)
        self.dns_cache = {}
        self.dns_server = dns_server

    def query(self, name):
        if name == self.name:
            return
        if name not in self.dns_cache:
            self.unicast(DNSQueryPacket(self, self.dns_server, name))
        elif self.dns_cache[name] < self.env.now:
            del self.dns_cache[name]
            self.unicast(DNSQueryPacket(self, self.dns_server, name))

    def process(self):
        while True:
            yield self.env.timeout(1)
            packet = yield self.queue.get()
            print("%s: Received: %s" % (self.name, packet))
            if isinstance(packet, DNSResponsePacket):
                self.dns_cache[packet.name] = (packet.ip,
                                               self.env.now + DNS_ENTRY_EXPIRATION_TIME)

    def generate(self, names):
        while True:
            yield self.env.timeout(5)
            name = random.choice(names)
            if name not in self.dns_cache:
                self.query(name)

