import ipaddress
import logging

import matplotlib.pyplot as plt
import simpy

from common import constant
from common.link import Link
from dns.client import DNSClient
from dns.server import DNSServer
from mdns.client import MDNSClient

SIMULATION_TIME = 10000


def setup_root_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def run_dns_simulation(num_clients):
    """ Run simulation with num_clients of DNS clients and 1 DNS server """
    CLIENTS_NAME = ["client%d" % i for i in range(num_clients)]

    env = simpy.Environment()
    s1 = DNSServer(env, "dns-server", ipaddress.IPv4Address("1.0.0.1"))
    clients = [DNSClient(env, CLIENTS_NAME[i], ipaddress.IPv4Address("1.0.0.2") + i, s1) for i in range(num_clients)]

    # Add DNS record to DNS server
    for c in clients:
        s1.add_dns_record(c.name, c.ip)

    # Create ethernet link
    eth = Link(env, "dns_local", constant.LINK_TRANS_TIME, constant.LINK_PACKET_CAPACITY)

    # Connect clients and server
    for c in clients:
        eth.connect(s1, c)

    # Start simulation
    env.process(s1.process())
    for c in clients:
        env.process(c.process())
        env.process(c.generate(CLIENTS_NAME))
    env.run(until=SIMULATION_TIME)

    return eth.metric, [c.metric for c in clients]


def run_mdns_simulation(num_clients):
    """ Run simulation with num_clients of mDNS clients """
    CLIENTS_NAME = ["client%d" % i for i in range(num_clients)]
    GROUP_IP = ipaddress.IPv4Address("224.0.0.1")

    env = simpy.Environment()
    clients = [MDNSClient(env, CLIENTS_NAME[i], ipaddress.IPv4Address("1.0.0.1") + i) for i in range(num_clients)]

    # Add DNS record to DNS server
    for c in clients:
        c.join_group(GROUP_IP)

    # Create ethernet link
    eth = Link(env, "mdns_local", constant.LINK_TRANS_TIME, constant.LINK_PACKET_CAPACITY)

    # Connect clients and server
    for c in clients:
        eth.connect(c, None)

    for c in clients:
        env.process(c.process())
        env.process(c.generate(CLIENTS_NAME))
    env.run(until=SIMULATION_TIME)

    return eth.metric, [c.metric for c in clients]


def plt_graph(x, dns_y, mdns_y, ylabel, title):
    plt.plot(x, dns_y, '--', marker=".", label="DNS")
    plt.plot(x, mdns_y, '-.', marker="v", label="mDNS")
    plt.xlabel("Number of Clients")
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.show()


def find_avg_client_cache_hit(client_m):
    res = [metric.cache_hit_count / metric.query_count for metric in client_m]
    return sum(res) / len(res)


if __name__ == "__main__":
    # Uncomment this line to enable logging
    # setup_root_logger()
    num_clients = range(3, 33, 3)
    dns_packet_count_y = []
    mdns_packet_count_y = []

    dns_avg_waiting_y = []
    mdns_avg_waiting_y = []

    dns_avg_cache_hit_y = []
    mdns_avg_cache_hit_y = []
    for num_client in num_clients:
        print("Running", num_client)
        link_metric, client_metric = run_dns_simulation(num_client)
        # print(link_metric, client_metric)
        dns_packet_count_y.append(link_metric.packet_counts)
        dns_avg_waiting_y.append(link_metric.link_total_waiting_time / link_metric.packet_counts)
        dns_avg_cache_hit_y.append(find_avg_client_cache_hit(client_metric))
        print(link_metric)
        for m in client_metric:
            print(m)

        link_metric, client_metric = run_mdns_simulation(num_client)
        mdns_packet_count_y.append(link_metric.packet_counts)
        mdns_avg_waiting_y.append(link_metric.link_total_waiting_time / link_metric.packet_counts)
        mdns_avg_cache_hit_y.append(find_avg_client_cache_hit(client_metric))
        print(link_metric)
        for m in client_metric:
            print(m)

    plt_graph(num_clients, dns_packet_count_y, mdns_packet_count_y, "Total Packet Counts", "Total Packet Counts")
    plt_graph(num_clients, dns_avg_waiting_y, mdns_avg_waiting_y, "Average Waiting Time", "Average Waiting Time")
    plt_graph(num_clients, dns_avg_cache_hit_y, mdns_avg_cache_hit_y, "Average Cache Hit Rate", "Average Cache Hit Rate")
