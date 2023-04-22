import copy

from Coding import ParityBitCoding
from Coding import CRC32Coding
from Coding import CRC8Coding


def decode_parity_bit_encoded_frame(bit_data_list_1d):
    return ParityBitCoding.parity_bit_decode_single(bit_data_list_1d)


def check_for_error_parity_bit(bit_data_list1d_encoded, bit_data_list1d_decoded):
    parity_decoded = ParityBitCoding.check_parity(copy.deepcopy(bit_data_list1d_decoded))
    parity_received = ParityBitCoding.get_parity_bit(copy.deepcopy(bit_data_list1d_encoded))
    return parity_decoded == parity_received


def decode_crc32_encoded_frame_and_check_sum(bit_data_list_1d):
    return CRC32Coding.decode_crc32_and_check_errors(bit_data_list_1d)


def check_for_error_crc32(bit_data_list1d_decoded, crc32_checksum):
    return CRC32Coding.check_crc32_match(bit_data_list1d_decoded, crc32_checksum)


def decode_crc8_encoded_frame_and_check_sum(bit_data_list_1d):
    return CRC8Coding.split_and_ret_crc8(bit_data_list_1d)


def check_for_error_crc8(bit_data_list1d_decoded, crc8_checksum):
    return CRC8Coding.check_crc8_match(bit_data_list1d_decoded, crc8_checksum)
