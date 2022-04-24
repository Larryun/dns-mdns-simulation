import ipaddress
import random
from logging import getLogger

from common.constant import ENTRY_EXPIRATION_TIME, QUERY_INTERVAL, CLIENT_PROCESS_TIME
from common.device import Device
from common.metric import ClientMetric
from common.packet import DNSQueryPacket, DNSResponsePacket
from dns.server import DNSServer

logger = getLogger()


class DNSClient(Device):

    def __init__(self, env, name: str, ip: ipaddress.IPv4Address, dns_server: DNSServer):
        super().__init__(env, name, ip)
        self.dns_cache = {}
        self.dns_server = dns_server

        self.metric = ClientMetric()

    def query(self, name):
        if name == self.name:
            return

        self.metric.query_count += 1
        if name not in self.dns_cache:
            self.unicast(DNSQueryPacket(self, self.dns_server, name))
        elif self.dns_cache[name][1] < self.env.now:
            del self.dns_cache[name]
            self.unicast(DNSQueryPacket(self, self.dns_server, name))
        else:
            self.metric.cache_hit_count += 1

    def process(self):
        while True:
            # Wait for packet to arrive before processing
            packet = yield self.queue.get()
            # Start processing
            yield self.env.timeout(CLIENT_PROCESS_TIME)
            logger.info("%s: Received: %s" % (self.name, packet))
            if isinstance(packet, DNSResponsePacket):
                self.dns_cache[packet.name] = (packet.ip,
                                               self.env.now + ENTRY_EXPIRATION_TIME)

    def generate(self, names):
        while True:
            yield self.env.timeout(QUERY_INTERVAL)
            name = random.choice(names)
            self.query(name)
