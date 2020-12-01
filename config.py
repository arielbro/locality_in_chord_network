import enum

ring_size_bits = 16
final_network_size = 10 ** 3

# define probabilities of different operations in the network
join_weight = 1.1
lookup_weight = 2
leave_weight = 0
localize_weight = 1

localization_modes = enum.Enum("LocalizationMode", ["switch_two_fingers",
                                                    "switch_random_finger_based",
                                                    "switch_random_neighbor_based"])
localization_mode = localization_modes.switch_random_neighbor_based
