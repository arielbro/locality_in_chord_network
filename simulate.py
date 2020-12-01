from node import Node
from numpy import random
from collections import namedtuple
from latency_logger import LatencyLogger
from config import *
from rendering import plot_network, plot_key
from matplotlib import pyplot as plt
from util import chord_dist
from itertools import combinations


Event = namedtuple("Event", "run_time network_size event_index")

sum_weights = float(join_weight + lookup_weight + leave_weight + localize_weight)
join_p = join_weight / sum_weights
lookup_p = lookup_weight / sum_weights
leave_p = leave_weight / sum_weights
localize_p = localize_weight / sum_weights

nodes = []
logger = LatencyLogger()

op_text = "op_type, network_size, n_connections, total_time\n"
while len(nodes) < final_network_size:
    op = random.choice(["join", "lookup", "leave", "localize"], p=[join_p, lookup_p, leave_p, localize_p])

    if (len(nodes) == 0) and op in ("lookup", "leave", "localize"):
        continue

    if op == "join":

        if len(nodes) == 0:
            node = Node(node_id=random.randint(0, 2 ** ring_size_bits), logger=logger)
        else:
            contact = random.choice(nodes)
            node = Node(node_id=random.randint(0, 2 ** ring_size_bits), contact_node=contact, logger=logger)
        nodes.append(node)

        # plot_network(nodes, logger)
        # plt.show()

    elif op == "lookup":
        requester = random.choice(nodes)
        key = random.randint(0, 2 ** ring_size_bits)
        requester.lookup_key(key)
    elif op == "leave":
        continue
    elif op == "localize":

        # plot_network(nodes, logger)
        # plt.show()

        requester = random.choice(nodes)
        if localization_mode == localization_modes.switch_two_fingers:
            requester.localize_switch_two_fingers()
        elif localization_mode == localization_modes.switch_random_finger_based:
            requester.localize_switch_random_finger_based()
        elif localization_mode == localization_modes.switch_random_neighbor_based:
            requester.localize_switch_random_neighbor_based()

        # plot_network(nodes, logger)
        # plt.show()
        # pass
    else:
        raise ValueError("What kind of op is this even?")

    operation_latencies = logger.flush_latencies()
    op_text += "{}, {}, {}, {}\n".format(op, len(nodes), len(operation_latencies), sum(operation_latencies))

distances_comparison_text = "chord_dist, latency_dist\n"
for n1, n2 in combinations(nodes, 2):
    pair_chord_dist = chord_dist(n1, n2)
    latency_dist = logger.dist(n1, n2)
    distances_comparison_text += "{}, {}\n".format(pair_chord_dist, latency_dist)

chord_distance_distribution_text = "chord_dist\n"
for d in logger.flush_chord_dists():
    chord_distance_distribution_text += "{}\n".format(d)

file_suffix = "probs=({}, {}, {}),bits={}," \
              "final_size={},localization={}".format(
    join_p, lookup_p, localize_p, ring_size_bits, final_network_size, localization_mode.name)

with open("simulation_logs/operation_log_{}.txt".format(file_suffix), "w") as text_file:
    text_file.write(op_text)
with open("simulation_logs/message_chord_distance_distribution_{}.txt".format(file_suffix), "w") as text_file:
    text_file.write(chord_distance_distribution_text)
with open("simulation_logs/distances_comparison_{}.txt".format(file_suffix), "w") as text_file:
    text_file.write(distances_comparison_text)
