from logging import getLogger

from common.constant import LINK_BACKOFF_TIME
from common.metric import LinkMetric

logger = getLogger()


class Link:

    def __init__(self, env, tag, trans_time, packet_capacity):
        self.env = env
        self.tag = tag
        self.trans_time = trans_time
        self.packet_count = 0
        self.packet_capacity = packet_capacity
        self.devices = set()

        self.metric = LinkMetric()

    def transmit(self, packet):
        t0 = self.env.now
        while self.packet_count >= self.packet_capacity:
            yield self.env.timeout(LINK_BACKOFF_TIME)
        self.metric.link_total_waiting_time += (self.env.now - t0)

        self.metric.packet_counts += 1

        self.packet_count += 1
        yield self.env.timeout(self.trans_time)
        logger.info("%s: Transmitted: %s" % (packet.src.name, packet))
        self.packet_count -= 1
        yield packet.dest.queue.put(packet)

    def connect(self, dev1, dev2):
        if dev2 is not None:
            self.devices.add(dev2)
            dev2.link.add(self)
        self.devices.add(dev1)
        dev1.link.add(self)

    def __str__(self):
        return self.tag

    def __eq__(self, other):
        return isinstance(other, Link) and self.tag == other.tag

    def __hash__(self):
        return hash(self.tag)
