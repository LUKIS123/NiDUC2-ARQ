import DataGenerator
import PIL.Image as Image
import io
import base64
from bitstring import BitArray
import binascii

filepath = 'notebook_icon.png'

string_base64 = ImageConvertion.image_to_data_url(filepath)
byte_string = string_base64.encode()

decoded_bytes = base64.b64decode(byte_string)

print(decoded_bytes)
print("\n\n\n")

# zamiana na liste bitow


bit_str_list = ["{:08b}".format(x) for x in decoded_bytes]
print("".join(bit_str_list))

# new_bytes = base64.b64decode(bit_str_list.__str__())
# print(new_bytes)

# jeszcze raz
# image_data = (base64.b64encode(bit_str_list.__str__()).decode('ascii'))

# lolo = binascii.hexlify(bytes(bit_str_list.__str__(), encoding='ascii'))

string = bit_str_list.__str__()


def bin_string_to_bin_value(input):
    highest_order = len(input) - 1
    result = 0
    for bit in input:
        result = result + int(bit) * pow(2, highest_order)
        highest_order = highest_order - 1
    return bin(result)


lololo = bin_string_to_bin_value(bit_str_list[0])
print(lololo)



# def to_unsigned(x, num_bits=8):
#     uplim_uint = 2 ** num_bits
#     return x % uplim_uint
#
#
# l = [-10, -48, 100, -20]
# lll = (hex(x) for x in bit_str_list)
# print(lll)
# base64.b64encode(hex(x) for x in bit_str_list)

#
# c = BitArray(decoded_bytes)
# print(c.bin[2:])
# bbb = c.bin[2:]

# cmap = {'0': (255, 255, 255),
#         '1': (0, 0, 0)}
#
# data = [cmap[letter] for letter in bbb]
# img = Image.new('RGB', (8, len(bbb) // 8), "white")
# img.putdata(data)
# img.show()

#

image = Image.open(io.BytesIO(decoded_bytes))
image.show()
image.save('result.png')

# new_img = Image.open(io.BytesIO(image_data))
# new_img.show()
