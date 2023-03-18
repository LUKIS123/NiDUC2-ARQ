import copy


# encode 2D list with parity bit information
def parity_bit_encode(bit_data_list):
    output_list = copy.deepcopy(bit_data_list)
    for i in range(len(bit_data_list)):
        parity_check = 0
        for j in range(len(bit_data_list[i])):
            parity_check = parity_check ^ bit_data_list[i][j]
        output_list[i].append(parity_check)
    return output_list


# returns a new decoded 2D list without parity bit
def parity_bit_decode(encoded_bit_data_list):
    output_list = [[] for _ in range(len(encoded_bit_data_list))]
    for i in range(len(encoded_bit_data_list)):
        for j in range(len(encoded_bit_data_list[i]) - 1):
            output_list[i].append(encoded_bit_data_list[i][j])
    return output_list


# check parity of decoded list
def check_parity(bit_list1d):
    parity_check = 0
    for i in range(len(bit_list1d)):
        parity_check = parity_check ^ bit_list1d[i]
    return parity_check


# check parity of encoded list
def get_parity_bit(bit_list1d):
    return bit_list1d[len(bit_list1d) - 1]
