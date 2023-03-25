import copy


# =============================== ENCODE ===============================
# encode 2D list with parity bit information
def parity_bit_encode(bit_data_list):
    output_list = copy.deepcopy(bit_data_list)
    for i in range(len(bit_data_list)):
        parity_check = 0
        for j in range(len(bit_data_list[i])):
            parity_check = parity_check ^ bit_data_list[i][j]
        output_list[i].append(parity_check)
    return output_list


# =============================== DECODE ===============================
# returns a new decoded 2D list without parity bit
def parity_bit_decode(encoded_bit_data_list):
    output_list = [[] for _ in range(len(encoded_bit_data_list))]
    for i in range(len(encoded_bit_data_list)):
        for j in range(len(encoded_bit_data_list[i]) - 1):
            output_list[i].append(encoded_bit_data_list[i][j])
    return output_list


# returns a new decoded 1D list without parity bit
def parity_bit_decode_single(encoded_list_1d):
    output_list = []
    for i in range(len(encoded_list_1d) - 1):
        output_list.append(encoded_list_1d[i])
    return output_list


# =============================== UTILS ===============================
# check parity of decoded 1D list
def check_parity(bit_list1d):
    parity_check = 0
    for i in range(len(bit_list1d)):
        parity_check = parity_check ^ bit_list1d[i]
    return parity_check


# check parity of encoded 1D list
def get_parity_bit(bit_list1d):
    return bit_list1d[len(bit_list1d) - 1]
