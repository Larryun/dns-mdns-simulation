import ipaddress
import random
from logging import getLogger

from common.constant import ENTRY_EXPIRATION_TIME, CLIENT_PROCESS_TIME, QUERY_INTERVAL
from common.device import Device
from common.packet import DNSQueryPacket, DNSResponsePacket
from common.metric import ClientMetric

logger = getLogger()


class MDNSClient(Device):

    def __init__(self, env, name: str, ip: ipaddress.IPv4Address):
        super().__init__(env, name, ip)
        self.dns_cache = {}

        self.metric = ClientMetric()

    def query(self, name):
        if name == self.name:
            return

        # print(self.env.now, self.dns_cache)

        self.metric.query_count += 1
        if name not in self.dns_cache:
            self.multicast(self.group_ip, DNSQueryPacket(self, None, name))
        elif self.dns_cache[name][1] < self.env.now:
            del self.dns_cache[name]
            self.multicast(self.group_ip, DNSQueryPacket(self, None, name))
        else:
            self.metric.cache_hit_count += 1

    def process(self):
        while True:
            yield self.env.timeout(CLIENT_PROCESS_TIME)
            packet = yield self.queue.get()
            logger.info("%s: Received: %s" % (self.name, packet))
            if isinstance(packet, DNSResponsePacket):
                self.dns_cache[packet.name] = (packet.ip,
                                               self.env.now + ENTRY_EXPIRATION_TIME)
            elif isinstance(packet, DNSQueryPacket):
                if packet.name == self.name:
                    self.multicast(self.group_ip, DNSResponsePacket(self, None, self.name, self.ip))

    def generate(self, names):
        while True:
            yield self.env.timeout(QUERY_INTERVAL)
            name = random.choice(names)
            self.query(name)
