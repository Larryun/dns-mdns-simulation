import copy
import ipaddress

import simpy

from common.constant import DEVICE_QUEUE_SIZE
from common.link import Link


class Device:

    def __init__(self, env, name: str, ip: ipaddress.IPv4Address):
        self.name = name
        self.ip = ip
        self.group_ip = None
        self.link = set()
        self.queue = simpy.Store(env, capacity=DEVICE_QUEUE_SIZE)
        self.env = env

    def join_group(self, group_ip: ipaddress.IPv4Address):
        self.group_ip = group_ip

    def leave_group(self):
        self.group_ip = None

    def unicast(self, packet):
        for l in self.link:
            for dev in l.devices:
                if dev == packet.dest:
                    self.env.process(l.transmit(packet))
                    return

    def multicast(self, group_ip, packet):
        for l in self.link:
            for dev in l.devices:
                if dev != self and dev.group_ip == group_ip:
                    packet = copy.copy(packet)
                    packet.dest = dev
                    # print(self, packet)
                    self.env.process(l.transmit(packet))

    def process(self):
        raise NotImplementedError

    def __str__(self):
        return "%s|%s" % (self.name, self.ip)

    def __repr__(self):
        return "%s|%s" % (self.name, self.ip)

    def __eq__(self, other):
        return isinstance(other, type(self)) and self.ip == other.ip and self.name == other.name

    def __hash__(self):
        return hash(self.name + str(self.ip))
