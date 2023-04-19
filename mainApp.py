import sys
from threading import Thread
import PIL.Image as Image

import DataGenerator
from Channel import Channel
from Enums.EncodingTypeEnum import EncodingType
from Enums.NoiseTypeEnum import NoiseType
from Receiver import Receiver
from Sender import Sender
import ByteUtils

# ===============================================================
# image width == frame quantity
data_sequences = 160
# image height == frame length
single_sequence_length = 8000
# =========== ARQ TEST ===========

# TODO: jedna ramka 100 bajtow czyli 800bit + naglowek i stopka
# do zrobienia naglowek ramki z numerowaniem
# TODO: Zrobic aby wiadomosc ACK przesylala ktora rameczke chce z powrotem (aktualnie rozwiazanie powoduje zapetlanie sie jesli w jednym w odbiornikow przeskoczy indeks)
#   obsluzyc przypadek gdy ilosc ramek przekroczy rozmiar naglowka

data = DataGenerator.generate_bit_data(data_sequences, single_sequence_length)
# md5 poczatkowe
src_hash = ByteUtils.calculate_md5_hash(ByteUtils.binary_to_byte_arr(ByteUtils.flatten_2d_list(data)))

print("Printing original data...")
print(data)
print("\n")

channel = Channel(NoiseType.gilbert_elliot)

# sender = Sender(data, channel, EncodingType.ParityBit, EncodingType.ParityBit, 16)
# receiver = Receiver(channel, EncodingType.ParityBit, EncodingType.ParityBit, 16)
sender = Sender(data, channel, EncodingType.CRC_32, EncodingType.CRC_32, 16)
receiver = Receiver(channel, EncodingType.CRC_32, EncodingType.CRC_32, 16)

sender_thread = Thread(target=sender.threaded_sender_function)
receiver_thread = Thread(target=receiver.threaded_receiver_function, args=(len(data), 4))
sender_thread.start()
receiver_thread.start()

# shutting down threads
receiver_thread.join()
sender_thread.join()
print("Threads finished... Exiting...")

# generating images
img = Image.new('1', (data_sequences, single_sequence_length))
pixels = img.load()
for i in range(img.size[0]):
    for j in range(img.size[1]):
        pixels[i, j] = data[i][j]
img.save('./pictures/original_image.bmp')

out = receiver.output_bit_data_list_2d

img_after = Image.new('1', (data_sequences, single_sequence_length))
pixels_after = img_after.load()
for i in range(img_after.size[0]):
    for j in range(img_after.size[1]):
        pixels_after[i, j] = out[i][j]
img_after.save('./pictures/decoded_image.bmp')

print("MD5...")
# md5 poczatkowe
out_hash = ByteUtils.calculate_md5_hash(ByteUtils.binary_to_byte_arr(ByteUtils.flatten_2d_list(out)))
print(src_hash)
print(out_hash)
print(src_hash == out_hash)

sys.exit()

# =========== END OF ARQ TEST ===========

# data = DataGenerator.generate_bit_data(data_sequences, single_sequence_length)
#
# img = Image.new('1', (data_sequences, single_sequence_length))
# pixels = img.load()
# for i in range(img.size[0]):
#     for j in range(img.size[1]):
#         pixels[i, j] = data[i][j]
#
# # img.show()
# img.save('./pictures/original_image.bmp')

# =========== parity bit encoding ===========
# enc = ParityBitCoding.parity_bit_encode(data)
# parity_bit = ParityBitCoding.get_parity_bit(enc[0])
# test = ParityBitCoding.parity_bit_decode_single(enc[0])
# test for parity code
# dec = ParityBitCoding.parity_bit_decode(enc)
# check_parity = ParityBitCoding.check_parity(dec[0])
# true or false
# print(parity_bit == check_parity)
# =========== parity bit encoding ===========

# simulating channel noise
# noise_data = ChannelNoise.bsc_channel(data, 30)
# noise_data = ChannelNoise.gilbert_elliot_channel(data, 10, 50, 20, 30)
# single_bsc = ChannelNoise.bsc_channel_single(data[0], 30)
# single_gil = ChannelNoise.gilbert_elliot_channel_single(data[0], 10, 50, 20, 30)

# after decoding
# img_after = Image.new('1', (data_sequences, single_sequence_length))
# pixels_after = img_after.load()
# for i in range(img_after.size[0]):
#     for j in range(img_after.size[1]):
#         pixels_after[i, j] = noise_data[i][j]
#
# # img_after.show()
# img_after.save('./pictures/decoded_image.bmp')
