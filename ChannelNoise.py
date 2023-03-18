import copy
import random

# Gilbert-Elliot channel state
current_state = True


def random_noise(bit_data_list):
    new_list = copy.deepcopy(bit_data_list)
    for i in range(len(bit_data_list)):
        for j in range(len(bit_data_list[i])):
            choice = random.choice((0, 1))
            if choice == 1:
                new_list[i][j] = random.choice((0, 1))
    return new_list


# input: 2D list of bits, error probability (0-100)%
def bsc_channel(bit_data_list, error_probability):
    bsc_processed_list = copy.deepcopy(bit_data_list)
    for i in range(len(bit_data_list)):
        for j in range(len(bit_data_list[i])):
            if random.uniform(0, 1) <= (error_probability / 100):
                if bsc_processed_list[i][j] == 1:
                    bsc_processed_list[i][j] = 0
                else:
                    bsc_processed_list[i][j] = 1
    return bsc_processed_list


def bsc_channel_single(bit_list1d, error_probability):
    output_list = []
    for i in range(len(bit_list1d)):
        if random.uniform(0, 1) <= (error_probability / 100):
            if bit_list1d[i] == 1:
                output_list.append(0)
            else:
                output_list.append(1)
        else:
            output_list.append(bit_list1d[i])
    return output_list


# input: 2D list of bits, probability (0-100)%, (0-100)%, (0-100)%, (0-100)%
def gilbert_elliot_channel(bit_data_list, error_probability_of_good_state, error_probability_of_bad_state,
                           switch_to_good_probability, switch_to_bad_probability):
    # True => good state, False => bad state
    global current_state
    current_state = random.choice((True, False))
    gilbert_elliot_processed_list = copy.deepcopy(bit_data_list)

    for i in range(len(bit_data_list)):
        for j in range(len(bit_data_list[i])):
            if current_state:
                if random.uniform(0, 1) <= (error_probability_of_good_state / 100):
                    if gilbert_elliot_processed_list[i][j] == 1:
                        gilbert_elliot_processed_list[i][j] = 0
                    else:
                        gilbert_elliot_processed_list[i][j] = 1
                if random.uniform(0, 1) <= (switch_to_bad_probability / 100):
                    current_state = False
            else:
                if random.uniform(0, 1) <= (error_probability_of_bad_state / 100):
                    if gilbert_elliot_processed_list[i][j] == 1:
                        gilbert_elliot_processed_list[i][j] = 0
                    else:
                        gilbert_elliot_processed_list[i][j] = 1
                if random.uniform(0, 1) <= switch_to_good_probability:
                    current_state = True

    return gilbert_elliot_processed_list


def gilbert_elliot_channel_single(bit_list1d, error_probability_of_good_state, error_probability_of_bad_state,
                                  switch_to_good_probability, switch_to_bad_probability):
    # True => good state, False => bad state
    global current_state
    current_state = random.choice((True, False))
    output_list = []

    for i in range(len(bit_list1d)):
        if current_state:
            if random.uniform(0, 1) <= (error_probability_of_good_state / 100):
                if bit_list1d[i] == 1:
                    output_list.append(0)
                else:
                    output_list.append(1)
            else:
                output_list.append(bit_list1d[i])
            if random.uniform(0, 1) <= (switch_to_bad_probability / 100):
                current_state = False
        else:
            if random.uniform(0, 1) <= (error_probability_of_bad_state / 100):
                if bit_list1d[i] == 1:
                    output_list.append(0)
                else:
                    output_list.append(1)
            else:
                output_list.append(bit_list1d[i])
            if random.uniform(0, 1) <= switch_to_good_probability:
                current_state = True

    return output_list
