import config
from util import *
from rendering import plot_key
from matplotlib import pyplot as plt
from itertools import combinations
from random import choice


class Node(object):

    def __init__(self, node_id, logger, contact_node=None):
        self.logger = logger
        self.node_id = node_id
        logger.register_node(self)
        self.fingers = [None for _ in range(config.ring_size_bits)]

        if contact_node is None:
            self.successor = self
            self.predecessor = self
            self.fingers = [self for _ in range(config.ring_size_bits)]
        else:
            self.successor = contact_node.find_successor(node_id)
            self.logger.log(self, contact_node)
            self.predecessor = self.successor.predecessor
            self.logger.log(self, self.successor)
            # self.predecessor = contact_node.find_predecessor(node_id)
            self.init_fingers()
            self.update_others()
            self.successor.transfer_keys(self)
            self.logger.log(self, self.successor)

    @property
    def successor(self):
        return self.fingers[0]

    @successor.setter
    def successor(self, val):
        self.fingers[0] = val

    def update_others(self):
        for i in range(0, config.ring_size_bits):
            candidate_for_update = self.find_predecessor(shift(self.node_id, 2 ** i, backward=True))
            self.logger.log(self, candidate_for_update)
            candidate_for_update.update_finger_entry(i, self)

    def update_finger_entry(self, i, node):
        if between(self.node_id, node.node_id, self.fingers[i].node_id, include_left=True):
            # print("Node {} is better than node {} for the {}th finger of {}".
            #       format(node.node_id, self.fingers[i].node_id, i, self.node_id))
            self.fingers[i] = node
            self.logger.log(self, self.predecessor)
            self.predecessor.update_finger_entry(i, node)

    def init_fingers(self):
        self.fingers[1:] = [self.find_successor(shift(self.node_id, 2 ** i))
                            for i in range(1, config.ring_size_bits)]

        for i in range(1, config.ring_size_bits):
            if between(self.node_id, shift(self.node_id, 2 ** i), self.fingers[i - 1].node_id, include_left=True):
                self.fingers[i] = self.fingers[i - 1]
            else:
                self.fingers[i] = self.find_successor(shift(self.node_id, 2 ** i))

    def closest_preceeding_finger(self, node_id):
        for finger in self.fingers[::-1]:
            if finger is None:
                continue
            if between(self.node_id, finger.node_id, node_id, include_right=True):
                # paper has right endpint exclusive
                return finger
        return self

    def find_predecessor(self, node_id):
        curr_node = self
        while not between(curr_node.node_id, node_id, curr_node.successor.node_id, include_left=True):
            # print("Found predecessor to key {} at node {}".format(node_id, self.node_id))
            next_node = curr_node.closest_preceeding_finger(node_id)
            self.logger.log(curr_node, next_node)
            curr_node = next_node
        # print("{} looking for key {} at contact {}".format(self.node_id, node_id, contact.node_id))

        # plt.ylim(-1, 1)
        # plt.xlim(-1, 1)
        # plot_key(node_id)

        return curr_node

    def find_successor(self, node_id):
        predecessor = self.find_predecessor(node_id)
        self.logger.log(self, predecessor)
        return predecessor.successor

    def transfer_keys(self, requester):
        pass

    def get_data(self, key):
        pass

    def lookup_key(self, key):
        # print("Lookup for key {}".format(key))
        holder = self.find_successor(key)
        holder.get_data(key)
        self.logger.log(self, holder)

    def localize(self):
        """
        Uniformly selects nodes n1 and n2 from finger table, such that
        n1 is closer on the circle but has a larger latency, and asks
        n1 and n2 to switch ids.
        :return:
        """
        bad_pairs = []
        for j in range(len(self.fingers)):
            for i in range(j):
                if self.logger.dist(self, self.fingers[j]) < self.logger.dist(self, self.fingers[i]):
                    bad_pairs.append((self.fingers[i], self.fingers[j]))

        if len(bad_pairs) == 0:
            return

        n1, n2 = choice(bad_pairs)
        self.logger.log(self, n1)
        n1.switch_with(n2)

    def switch_with(self, other):
        """
        Switched positions of self with other on the circle. That means that
        their ids are switched, they exchange keys, and both notify other
        nodes that may have pointers to them about the switch.
        :param other:
        :return:
        """

        self.update_others_switch(other)

        self.node_id, other.node_id = other.node_id, self.node_id
        other.transfer_keys(self)
        self.logger.log(self, other)
        self.transfer_keys(other)
        self.logger.log(other, self)

        # Assuming other references to other's field could be sorter out on previous message
        self.successor.predecessor = other
        self.logger.log(self, self.successor)

        other.successor.predecessor = self
        self.logger.log(self, other.successor)

        self.fingers, other.fingers = other.fingers, self.fingers

    def update_others_switch(self, replacement):
        """
        Finds candidate nodes who might have self or replacement in their finger table,
        and switches their pointers from one to another.
        Note that candidates are first all found using original
        chord search, and then all asked to update (since any partial update will break search).
        Also note that self initiates all of the messages here, including ones about replacing replacement.
        :return:
        """
        updates_needed_self = []
        updates_needed_other = []
        for (lst, node) in zip([updates_needed_self, updates_needed_other], [self, replacement]):
            for i in range(0, config.ring_size_bits):
                candidate_for_update = self.find_predecessor(shift(node.node_id, 2 ** i, backward=True))

                self.logger.log(self, candidate_for_update)
                candidate_for_update.get_outdated_fingers(i, node, lst)
                self.logger.log(candidate_for_update, self)

        for node, i in updates_needed_self:
            node.fingers[i] = replacement

        for node, i in updates_needed_other:
            node.fingers[i] = self

    def get_outdated_fingers(self, i, outdated_node, update_list, depth=0):
        depth += 1
        if self.fingers[i] == outdated_node:
            update_list.append((self, i))
            self.logger.log(self, self.predecessor)
            if self.predecessor != self:
                self.predecessor.get_outdated_fingers(i, outdated_node, update_list, depth)
