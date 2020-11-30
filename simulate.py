from node import Node
from numpy import random
from collections import namedtuple
from latency_logger import LatencyLogger
from config import *
from rendering import plot_network, plot_key
from matplotlib import pyplot as plt


Event = namedtuple("Event", "run_time network_size event_index")

sum_weights = float(join_weight + lookup_weight + leave_weight + localize_weight)
join_p = join_weight / sum_weights
lookup_p = lookup_weight / sum_weights
leave_p = leave_weight / sum_weights
localize_p = localize_weight / sum_weights

nodes = []
logger = LatencyLogger()

print("op_type, op_index, network_size, n_connections, total_time")
fig = None
round = 0
while round < n_rounds:
    op = random.choice(["join", "lookup", "leave", "localize"], p=[join_p, lookup_p, leave_p, localize_p])

    if (len(nodes) == 0) and op in ("lookup", "leave", "localize"):
        continue

    if op == "join":

        # plot_network(nodes)

        if len(nodes) == 0:
            node = Node(node_id=random.randint(0, 2 ** ring_size_bits), logger=logger)
        else:
            contact = random.choice(nodes)
            node = Node(node_id=random.randint(0, 2 ** ring_size_bits), contact_node=contact, logger=logger)
        nodes.append(node)

        # plt.show()

    elif op == "lookup":
        requester = random.choice(nodes)
        key = random.randint(0, 2 ** ring_size_bits)
        requester.lookup_key(key)
    elif op == "leave":
        continue
    elif op == "localize":
        requester = random.choice(nodes)
        requester.localize()
    else:
        raise ValueError("What kind of op is this even?")

    operation_latencies = logger.flush_latencies()
    print("{}, {}, {}, {}, {}".format(op, round, len(nodes), len(operation_latencies), sum(operation_latencies)))

    # TODO: print distance correlation statistics

    round += 1

    # if not (round + 1) % 1000:
    #     print("{} rounds done".format(round + 1))

