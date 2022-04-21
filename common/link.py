import simpy


class Link:

    def __init__(self, env, tag, trans_time, packet_capacity):
        self.env = env
        self.tag = tag
        self.trans_time = trans_time
        self.packet_count = 0
        self.packet_capacity = packet_capacity
        self.devices = {}

        self.metric_packet_counts = 0

    def transmit(self, packet):
        while self.packet_count >= self.packet_capacity:
            yield self.env.timeout(0.01)

        self.metric_packet_counts += 1

        self.packet_count += 1
        yield self.env.timeout(self.trans_time)
        print("%s: Transmitted: %s" % (packet.src.name, packet))
        self.packet_count -= 1
        yield packet.dest.queue.put(packet)

    def connect(self, dev1, dev2):
        self.devices[dev1] = dev2
        self.devices[dev2] = dev1
        dev1.link.append(self)
        dev2.link.append(self)

    def __str__(self):
        return self.tag

    def __eq__(self, other):
        return isinstance(other, Link) and self.tag == other.tag



