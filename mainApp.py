import PIL.Image as Image
import DataGenerator
import ChannelNoise

# image width
data_sequences = 8
# image height
single_sequence_length = 16

data = DataGenerator.generate_bit_data(data_sequences, single_sequence_length)

img = Image.new('1', (data_sequences, single_sequence_length))
pixels = img.load()
for i in range(img.size[0]):
    for j in range(img.size[1]):
        pixels[i, j] = data[i][j]

# img.show()
img.save('./pictures/original_image.bmp')

# simulating channel noise
# noise_data = ChannelNoise.bsc_channel(data, 30)
noise_data = ChannelNoise.gilbert_elliot_channel(data, 10, 50, 20, 30)

# after decoding
img_after = Image.new('1', (data_sequences, single_sequence_length))
pixels_after = img_after.load()
for i in range(img_after.size[0]):
    for j in range(img_after.size[1]):
        pixels_after[i, j] = noise_data[i][j]

# img_after.show()
img_after.save('./pictures/decoded_image.bmp')
