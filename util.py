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
