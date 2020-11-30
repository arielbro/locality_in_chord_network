from matplotlib import pyplot as plt
from util import chord_id_to_coordinate
import matplotlib.patches as patches


def plot_network(nodes):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    circle = plt.Circle((0, 0), radius=1, edgecolor='b', facecolor='None')
    ax.add_patch(circle)

    style = "Simple, tail_width=0.5, head_width=8, head_length=12"
    kw = dict(arrowstyle=style)

    for node in nodes:
        x, y = chord_id_to_coordinate(node.node_id)
        ax.plot(x, y, marker="o", color="r")

        x_prime, y_prime = chord_id_to_coordinate(node.successor.node_id)
        # plt.arrow(x, y, (x_prime - x), (y_prime - y))
        patch = patches.FancyArrowPatch((x, y), (x_prime + 0.01, y_prime + 0.01),
                                        connectionstyle="arc3,rad=0.5", color='b',
                                        **kw)
        plt.gca().add_patch(patch)

        x_prime, y_prime = chord_id_to_coordinate(node.predecessor.node_id)
        patch = patches.FancyArrowPatch((x_prime, y_prime), (x + 0.01, y + 0.01),
                                        connectionstyle="arc3,rad=-0.6", color='r',
                                        **kw)
        plt.gca().add_patch(patch)

    # plt.show()
    return fig


def plot_key(key):
    plt.plot(*chord_id_to_coordinate(key), marker="X", color="g")

