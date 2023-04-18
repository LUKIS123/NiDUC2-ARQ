import random
import hashlib
from itertools import chain


def generate_bytes(size):
    int_list = []
    for i in range(size):
        int_list.append(random.randint(0, 255))
    return bytearray(int_list)


def save_byte_file(bytes_array, filename):
    binary_file = open(filename, "wb")
    binary_file.write(bytes_array)
    binary_file.close()


def read_bytes_from_file(file_name):
    in_file = open(file_name, "rb")
    data = in_file.read()
    in_file.close()
    return data


# Metoda zwraca liste 1d z danych wczytanych z pliku
def get_binary_output_from_file(file_name):
    byte_arr = read_bytes_from_file(file_name)
    read_bytes_length = 8 * len(byte_arr)
    binary_output = list(map(int, bin(int.from_bytes(byte_arr, byteorder="big")).strip('0b')))
    for i in range(read_bytes_length - len(binary_output)):
        binary_output.insert(0, 0)
    return binary_output


# Metoda do podzialu danych wczytanych z pliku na osobne ramki
def separate_list_to_chunks(list_1d, chunk_size):
    return [list_1d[x:x + chunk_size] for x in range(0, len(list_1d), chunk_size)]


# Metoda do zlaczenia otrzymanych przez Receiver danych to jednej listy
def flatten_2d_list(list_2d):
    return list(chain.from_iterable(list_2d))


# Metoda do konwersji listy 1d danych w bitach na bytearray
def binary_to_byte_arr(data_list_1d):
    chunks = [data_list_1d[x:x + 8] for x in range(0, len(data_list_1d), 8)]
    int_list = []
    for i in range(len(chunks)):
        weight = 7
        result = 0
        for j in range(len(chunks[i])):
            result += chunks[i][j] * pow(2, weight)
            weight -= 1
        int_list.append(result)
    return bytearray(int_list)


# Metoda do liczenia sumy kontrolnej md5 z bytearray'a
def calculate_md5_hash(byte_arr):
    result = hashlib.md5(byte_arr)
    return result.hexdigest()

# ======================== FILE UTILS ================================
# byte_array = ByteUtils.generate_bytes(800)
# ByteUtils.save_byte_file(byte_array, "data_file.txt")
# print(byte_array)
# bin_input = ByteUtils.get_binary_output_from_file("data_file.txt")
# print(bin_input)
# print(len(bin_input))
# print(type(bin_input))
# t = ByteUtils.binary_to_byte_arr(bin_input)
# print(t)
# ======================== FILE UTILS ================================
