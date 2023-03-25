import copy

import ParityBitCoding


def decode_parity_bit_encoded_frame(bit_data_list_1d):
    return ParityBitCoding.parity_bit_decode_single(bit_data_list_1d)


def check_for_error_parity_bit(bit_data_list1d_encoded, bit_data_list1d_decoded):
    parity_decoded = ParityBitCoding.check_parity(copy.deepcopy(bit_data_list1d_decoded))
    parity_received = ParityBitCoding.get_parity_bit(copy.deepcopy(bit_data_list1d_encoded))
    return parity_decoded == parity_received


# niepotrzebne
def get_parity_bit_of_decoded(bit_data_list1d_decoded):
    return ParityBitCoding.get_parity_bit(bit_data_list1d_decoded)
