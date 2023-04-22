import copy
import zlib


# Zwraca ramke z dodanym kodem detekcyjnym
def encode_list1d_crc_32_get(bit_data_list1d):
    output_list = copy.deepcopy(bit_data_list1d)
    byte_like_list = bytes(bit_data_list1d)
    checksum = zlib.crc32(byte_like_list)
    bits_checksum = format(checksum, "032b")  # uzupelnienie zerami jak utnie
    checksum_as_list = [int(x) for x in str(bits_checksum)]
    for i in range(len(checksum_as_list)):
        output_list.append(checksum_as_list[i])

    return output_list


def encode_list2d_crc_32(bit_data_list2d):
    output_list = copy.deepcopy(bit_data_list2d)
    for i in range(len(output_list)):
        byte_like_list = bytes(output_list[i])
        checksum = zlib.crc32(byte_like_list)
        bits_checksum = format(checksum, "032b")
        checksum_as_list = [int(x) for x in str(bits_checksum)]
        for j in range(len(checksum_as_list)):
            output_list[i].append(checksum_as_list[j])

    return output_list


# Zwraca ramke z wycietym kodem detekcyjnym oraz wyciety kod detekcyjny
def decode_crc32_and_check_errors(bit_data_list_1d):
    input_list = copy.deepcopy(bit_data_list_1d)
    crc32_received = input_list[-32:]
    del input_list[-32:]

    return input_list, crc32_received


def check_crc32_match(data_list, checksum_list):
    byte_like_list = bytes(data_list)
    checksum = zlib.crc32(byte_like_list)
    bits_checksum = format(checksum, "032b")
    checksum_as_list = [int(x) for x in str(bits_checksum)]
    if checksum_as_list == checksum_list:
        return True
    else:
        return False
