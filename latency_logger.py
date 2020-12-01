from node import Node
from numpy import random, pi, sin, cos, arccos, arcsin, sqrt
from util import chord_dist


class LatencyLogger:
    """
    Logs messages between nodes in the network. Assigns nodes arbitrary locations
    so that messages have an associated latency.
    """
    def __init__(self):
        self.node_to_locations = dict()
        self.latencies = []
        self.chord_distances = []

    def register_node(self, node):
        # sample a random point on a unit sphere
        theta = random.random() * 2 * pi  # also longitute
        phi = arccos(random.random() * 2 - 1)  # also latitude (measured from pole)
        self.node_to_locations[node] = theta, phi

    def dist(self, node1, node2):
        (theta1, phi1), (theta2, phi2) = self.node_to_locations[node1], self.node_to_locations[node2]
        haversine = lambda x: sin(x / 2.0) ** 2
        haversine_dist = haversine(phi2 - phi1) + cos(phi1) * cos(phi2) * haversine(theta2 - theta1)
        return 2 * arcsin(sqrt(haversine_dist))

    def unregister_node(self, node):
        self.node_to_locations.pop(node)

    def flush_latencies(self):
        res = tuple(self.latencies)
        self.latencies = []
        return res

    def flush_chord_dists(self):
        res = tuple(self.chord_distances)
        self.chord_distances = []
        return res

    def log(self, node1, node2):
        self.latencies.append(self.dist(node1, node2))
        self.chord_distances.append(chord_dist(node1, node2))

# TODO: handle virtual nodes