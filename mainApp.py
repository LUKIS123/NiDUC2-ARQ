from threading import Thread

import PIL.Image as Image

import ChannelNoise
import DataGenerator
import ParityBitCoding
# channel
from Channel import Channel
from EncodingTypeEnum import EncodingType
from NoiseTypeEnum import NoiseType
from Receiver import Receiver
from Sender import Sender

# image width == frame length
data_sequences = 8
# image height == frame quantity
single_sequence_length = 16

data = DataGenerator.generate_bit_data(data_sequences, single_sequence_length)

img = Image.new('1', (data_sequences, single_sequence_length))
pixels = img.load()
for i in range(img.size[0]):
    for j in range(img.size[1]):
        pixels[i, j] = data[i][j]

# img.show()
img.save('./pictures/original_image.bmp')

# =========== parity bit encoding ===========
enc = ParityBitCoding.parity_bit_encode(data)
parity_bit = ParityBitCoding.get_parity_bit(enc[0])
# test = ParityBitCoding.parity_bit_decode_single(enc[0])
# test for parity code
dec = ParityBitCoding.parity_bit_decode(enc)
check_parity = ParityBitCoding.check_parity(dec[0])
# true or false
print(parity_bit == check_parity)
# =========== parity bit encoding ===========

# simulating channel noise
# noise_data = ChannelNoise.bsc_channel(data, 30)
noise_data = ChannelNoise.gilbert_elliot_channel(data, 10, 50, 20, 30)
# single_bsc = ChannelNoise.bsc_channel_single(data[0], 30)
# single_gil = ChannelNoise.gilbert_elliot_channel_single(data[0], 10, 50, 20, 30)

# after decoding
img_after = Image.new('1', (data_sequences, single_sequence_length))
pixels_after = img_after.load()
for i in range(img_after.size[0]):
    for j in range(img_after.size[1]):
        pixels_after[i, j] = noise_data[i][j]

# img_after.show()
img_after.save('./pictures/decoded_image.bmp')

# =========== ARQ TEST ===========
print("Printing original data...")
print(data)
channel = Channel(NoiseType.gilbert_elliot)
sender = Sender(data, channel, EncodingType.ParityBit, EncodingType.ParityBit)
receiver = Receiver(channel, EncodingType.ParityBit, EncodingType.ParityBit)

sender_thread = Thread(target=sender.threaded_sender_function)
receiver_thread = Thread(target=receiver.threaded_receiver_function, args=(len(data), 8))
sender_thread.start()
receiver_thread.start()
sender_thread.join()
receiver_thread.join()
print("Threads finished...exiting")
