import random


def generate_bit_data(data_sequences, data_sequence_length):
    data = [random.choice((0, 1)) for _ in range(data_sequences * data_sequence_length)]
    data[:] = [data[i:i + data_sequence_length] for i in
               range(0, data_sequences * data_sequence_length, data_sequence_length)]
    return data
