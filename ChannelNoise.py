import random


def random_noise(bit_data_list):
    new_list = bit_data_list.copy()
    for i in range(len(bit_data_list)):
        for j in range(len(bit_data_list[i])):
            choice = random.choice((0, 1))
            if choice == 1:
                new_list[i][j] = random.choice((0, 1))
    return new_list


# input: 2D list of bits, error probability (0-100)%
def bsc_channel(bit_data_list, error_probability):
    bsc_processed_list = bit_data_list.copy()
    for i in range(len(bit_data_list)):
        for j in range(len(bit_data_list[i])):
            if random.uniform(0, 1) <= (error_probability / 100):
                if bsc_processed_list[i][j] == 1:
                    bsc_processed_list[i][j] = 0
    return bsc_processed_list
