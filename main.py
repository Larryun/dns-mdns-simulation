import ipaddress
import logging

import simpy

from common.constant import ETH_TRANS_TIME, ETH_PACKET_CAPACITY
from common.link import Link
from dns.client import DNSClient
from dns.server import DNSServer


def setup_root_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


if __name__ == "__main__":
    setup_root_logger()
    NUM_CLIENT = 100
    CLIENTS_NAME = ["client%d" % i for i in range(NUM_CLIENT)]

    env = simpy.Environment()
    s1 = DNSServer(env, "dns-server", ipaddress.IPv4Address("1.0.0.1"))
    clients = [DNSClient(env, CLIENTS_NAME[i], ipaddress.IPv4Address("1.0.0.2") + i, s1) for i in range(NUM_CLIENT)]

    # add DNS record to DNS server
    for c in clients:
        s1.add_dns_record(c.name, c.ip)

    # create ethernet link
    eth = Link(env, "local", ETH_TRANS_TIME, ETH_PACKET_CAPACITY)

    # connect clients and server
    for c in clients:
        eth.connect(s1, c)

    # start simulation
    env.process(s1.process())
    for c in clients:
        env.process(c.generate(CLIENTS_NAME))
    env.run(until=300)

    # print metrics
    print(eth.metric_packet_counts)
    print(eth.metric_link_total_waiting_time / eth.metric_packet_counts)
