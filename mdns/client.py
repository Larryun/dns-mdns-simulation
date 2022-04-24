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
        """ Simulate a query operation by sending a multicast query packet to server.
            If name in dns_cache then increase metric cache hit count by 1
            If corresponding cache entry is expired or not in cache then make query to server.
        """
        if name == self.name:
            return

        self.metric.query_count += 1
        if name not in self.dns_cache:
            self.multicast(self.group_ip, DNSQueryPacket(self, None, name))
        elif self.dns_cache[name][1] < self.env.now:
            del self.dns_cache[name]
            self.multicast(self.group_ip, DNSQueryPacket(self, None, name))
        else:
            self.metric.cache_hit_count += 1

    def process(self):
        """ Process incoming packet and update dns_cache.
            If incoming packet is DNSResponsePacket, update dns_cache with new expiration time.
            If incoming packet is DNSQueryPacket, respond with its IP if the query name matches with
            its name
        """
        while True:
            # Wait for packet to arrive before processing
            packet = yield self.queue.get()
            # Start processing
            yield self.env.timeout(CLIENT_PROCESS_TIME)
            logger.info("%s: Received: %s" % (self.name, packet))
            if isinstance(packet, DNSResponsePacket):
                self.dns_cache[packet.name] = (packet.ip,
                                               self.env.now + ENTRY_EXPIRATION_TIME)
            elif isinstance(packet, DNSQueryPacket):
                if packet.name == self.name:
                    self.multicast(self.group_ip, DNSResponsePacket(self, None, self.name, self.ip))

    def generate(self, names):
        """ Generate DNS query by randomly select a domain name """
        while True:
            yield self.env.timeout(QUERY_INTERVAL)
            name = random.choice(names)
            self.query(name)
