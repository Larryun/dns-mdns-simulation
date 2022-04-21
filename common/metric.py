class ClientMetric:

    def __init__(self):
        self.query_count = 0
        self.cache_hit_count = 0

    def __str__(self):
        res = "Query Count: %d\n" % self.query_count
        res += "Cache Hit Count: %d\n" % self.cache_hit_count
        res += "Cache Hit: %f%%" % (self.cache_hit_count / self.query_count)
        return res


class LinkMetric:

    def __init__(self):
        self.packet_counts = 0
        self.link_total_waiting_time = 0

    def __str__(self):
        res = "Packet Count: %d\n" % self.packet_counts
        res += "Link Total Waiting Time: %f\n" % self.link_total_waiting_time
        res += "Link Average Waiting Time: %f" % (self.link_total_waiting_time / self.packet_counts)
        return res
