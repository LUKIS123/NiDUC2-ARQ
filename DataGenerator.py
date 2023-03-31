import random


def generate_bit_data(data_sequences, data_sequence_length):
    data = [random.choice((0, 1)) for _ in range(data_sequences * data_sequence_length)]
    data[:] = [data[i:i + data_sequence_length] for i in
               range(0, data_sequences * data_sequence_length, data_sequence_length)]
    return data


def generate_ack(length, success):
    if success:
        data = [1 for _ in range(length)]
    else:
        data = [0 for _ in range(length)]
    return data


def generate_stop_msg(length):
    data_list = []
    current = 1
    for i in range(length):
        data_list.append(current)
        if current == 1:
            current = 0
        else:
            current = 1
    return data_list
