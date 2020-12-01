import config
from numpy import pi, cos, sin


def between(a, b, c, include_left=False, include_right=False):
    if a == c:
        return (b != a) or include_left or include_right
    b_delta = (b - a) % (2 ** config.ring_size_bits)
    c_delta = (c - a) % (2 ** config.ring_size_bits)
    lb = 0 if include_left else 1
    ub = c_delta if include_right else (c_delta - 1)
    return lb <= b_delta <= ub


def shift(a, b, backward=False):
    delta = -b if backward else b
    # print("pre shift: {}".format(a))
    res = (a + delta) % (2 ** config.ring_size_bits)
    # print("post shift: {}".format(res))
    return res


def chord_id_to_coordinate(node_id):
    theta = node_id / float(2 ** config.ring_size_bits) * 2 * pi
    x, y = cos(theta), sin(theta)
    return x, y


def midpoint_of_nodes(id1, id2):
    theta1 = id1 / float(2 ** config.ring_size_bits) * 2 * pi
    theta2 = id2 / float(2 ** config.ring_size_bits) * 2 * pi
    theta_mid = (id1 + id2) / 2
    x, y = cos(theta_mid), sin(theta_mid)
    return x, y


def chord_dist(n1, n2):
    """
    Returns the distance between two points on the chord, as fraction of the circle
    that separates them in the _shortest_ direction.
    :param n1:
    :param n2:
    :return:
    """
    return min(((n2.node_id - n1.node_id) % (2 ** config.ring_size_bits)),
               ((n1.node_id - n2.node_id) % (2 ** config.ring_size_bits)),
               ) / float(2 ** config.ring_size_bits)
