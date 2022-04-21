import ipaddress

import simpy

from common.link import Link
from common.constant import ETH_TRANS_TIME, ETH_PACKET_CAPACITY
from dns.client import DNSClient
from dns.server import DNSServer

NUM_CLIENT = 10
CLIENTS_NAME = ["client%d" % i for i in range(NUM_CLIENT)]

env = simpy.Environment()
s1 = DNSServer(env, "dns-server", ipaddress.IPv4Address("1.0.0.1"))
clients = [DNSClient(env, CLIENTS_NAME[i], ipaddress.IPv4Address("1.0.0.2") + i, s1) for i in range(NUM_CLIENT)]

for c in clients:
    s1.add_dns_record(c.name, c.ip)

eth = Link(env, "local", ETH_TRANS_TIME, ETH_PACKET_CAPACITY)
print(clients)

for c in clients:
    eth.connect(s1, c)

env.process(s1.process())
for c in clients:
    env.process(c.generate(CLIENTS_NAME))
env.run(until=300)

print(eth.metric_packet_counts)