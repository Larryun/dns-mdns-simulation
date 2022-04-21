import ipaddress
import logging

import simpy

from common.constant import LINK_TRANS_TIME, LINK_PACKET_CAPACITY
from common.link import Link
from dns.client import DNSClient
from dns.server import DNSServer
from mdns.client import MDNSClient

SIMULATION_TIME = 100000
NUM_CLIENTS = 5


def setup_root_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def run_dns_simulation(num_clients):
    CLIENTS_NAME = ["client%d" % i for i in range(num_clients)]

    env = simpy.Environment()
    s1 = DNSServer(env, "dns-server", ipaddress.IPv4Address("1.0.0.1"))
    clients = [DNSClient(env, CLIENTS_NAME[i], ipaddress.IPv4Address("1.0.0.2") + i, s1) for i in range(num_clients)]

    # add DNS record to DNS server
    for c in clients:
        s1.add_dns_record(c.name, c.ip)

    # create ethernet link
    eth = Link(env, "dns_local", LINK_TRANS_TIME, LINK_PACKET_CAPACITY)

    # connect clients and server
    for c in clients:
        eth.connect(s1, c)

    # start simulation
    env.process(s1.process())
    for c in clients:
        env.process(c.process())
        env.process(c.generate(CLIENTS_NAME))
    env.run(until=SIMULATION_TIME)

    # print metrics
    print(eth.metric)
    for c in clients:
        print(c.metric)


def run_mdns_simulation(num_clients):
    CLIENTS_NAME = ["client%d" % i for i in range(num_clients)]
    GROUP_IP = ipaddress.IPv4Address("224.0.0.1")

    env = simpy.Environment()
    clients = [MDNSClient(env, CLIENTS_NAME[i], ipaddress.IPv4Address("1.0.0.1") + i) for i in range(num_clients)]

    # add DNS record to DNS server
    for c in clients:
        c.join_group(GROUP_IP)

    # create ethernet link
    eth = Link(env, "mdns_local", LINK_TRANS_TIME, LINK_PACKET_CAPACITY)

    # connect clients and server
    for c in clients:
        eth.connect(c, None)

    for c in clients:
        env.process(c.process())
        env.process(c.generate(CLIENTS_NAME))
    env.run(until=SIMULATION_TIME)

    # print metrics
    print(eth.metric)
    for c in clients:
        print(c.metric)


if __name__ == "__main__":
    # setup_root_logger()

    run_dns_simulation(NUM_CLIENTS)
    run_mdns_simulation(NUM_CLIENTS)
