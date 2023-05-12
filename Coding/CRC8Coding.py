import copy
from _ExternalLibraries.CRC8Lib.crc import Calculator, Crc8

calculator = Calculator(Crc8.CCITT)


def encode_list1d_crc_8(bit_data_list1d):
    output_list = copy.deepcopy(bit_data_list1d)
    byte_like_list = bytes(bit_data_list1d)
    global calculator
    checksum = calculator.checksum(byte_like_list)
    bits_checksum = format(checksum, "08b")  # uzupelnienie zerami jak utnie
    checksum_as_list = [int(x) for x in str(bits_checksum)]
    for i in range(len(checksum_as_list)):
        output_list.append(checksum_as_list[i])

    return output_list


def encode_list2d_crc_8(bit_data_list2d):
    output_list = copy.deepcopy(bit_data_list2d)
    for i in range(len(output_list)):
        byte_like_list = bytes(output_list[i])
        global calculator
        checksum = calculator.checksum(byte_like_list)
        bits_checksum = format(checksum, "08b")
        checksum_as_list = [int(x) for x in str(bits_checksum)]
        for j in range(len(checksum_as_list)):
            output_list[i].append(checksum_as_list[j])

    return output_list


def split_and_ret_crc8(bit_data_list_1d):
    input_list = copy.deepcopy(bit_data_list_1d)
    crc8_received = input_list[-8:]
    del input_list[-8:]

    return input_list, crc8_received


def check_crc8_match(data_list, checksum_list):
    byte_like_list = bytes(data_list)
    global calculator
    checksum = calculator.checksum(byte_like_list)
    bits_checksum = format(checksum, "08b")
    checksum_as_list = [int(x) for x in str(bits_checksum)]
    if checksum_as_list == checksum_list:
        return True
    else:
        return False
