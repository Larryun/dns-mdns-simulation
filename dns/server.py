import ipaddress

from common.device import Device
from common.packet import DNSQueryPacket, DNSResponsePacket
from logging import getLogger

logger = getLogger()


class DNSServer(Device):

    def __init__(self, env, name: str, ip: ipaddress.IPv4Address):
        super().__init__(env, name, ip)
        self.dns_db = {}

    def add_dns_record(self, name, ip):
        self.dns_db[name] = ip

    def process(self):
        while True:
            yield self.env.timeout(0.1)
            packet = yield self.queue.get()
            logger.info("%s: Received: %s" % (self.name, packet))
            if isinstance(packet, DNSQueryPacket) and packet.name in self.dns_db:
                self.unicast(
                    DNSResponsePacket(self, packet.src, packet.name, self.dns_db[packet.name])
                )

