import random


def generate_bytes(size):
    int_list = []
    for i in range(size):
        int_list.append(random.randint(0, 255))
    return bytearray(int_list)


def save_byte_file(bytes_array):
    binary_file = open("my_file.txt", "wb")
    binary_file.write(bytes_array)
    binary_file.close()


def read_bytes_from_file(file_name):
    in_file = open(file_name, "rb")
    data = in_file.read()
    in_file.close()
    return data

# lol = bin(int.from_bytes(b"hello world", byteorder="big")).strip('0b')
# a = bytearray(b'\x05\x05\x05')
# # dlugosc
# print(len(a))
# # dlugosc
# print(a)
# lol = bin(int.from_bytes(a, byteorder="big")).strip('0b')
# print(lol)
# # lol = bin(int.from_bytes(b"hello world", byteorder="big"))
# listlist = list(map(int, lol))
# print(listlist)
# print(len(listlist))
# print('=========================================================')
# test = lol.split()
# # test2 = [int(d) for d in str(bin(lol))[2:]]
# # print(test2)
# # a = bytearray(b'\x10\x10\x10')
# # b = bin(int.from_bytes(a, byteorder=sys.byteorder))
# # print(b)
# t = "Hello MD5".encode("utf-8")
# print(t)
