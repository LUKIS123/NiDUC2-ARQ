import ParityBitCoding


def decode_parity_bit_encoded_frame(bit_data_list_1d):
    return ParityBitCoding.parity_bit_decode_single(bit_data_list_1d)


def check_for_error(bit_data_list1d_encoded, bit_data_list1d_decoded):
    parity_decoded = ParityBitCoding.check_parity(bit_data_list1d_decoded)
    parity_received = ParityBitCoding.get_parity_bit(bit_data_list1d_encoded)
    return parity_decoded == parity_received
