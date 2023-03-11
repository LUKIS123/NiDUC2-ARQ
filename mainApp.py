import PIL.Image as Image
import ImageConvertion
import ChannelNoise

data = ImageConvertion.generate_bit_data()

img = Image.new('1', (50, 50))
pixels = img.load()
for i in range(img.size[0]):
    for j in range(img.size[1]):
        pixels[i, j] = data[i][j]

img.show()
img.save('original_image.bmp')

# simulating channel noise
noise_data = ChannelNoise.random_noise(data)

# after decoding
img_after = Image.new('1', (50, 50))
pixels_after = img_after.load()
for i in range(img_after.size[0]):
    for j in range(img_after.size[1]):
        pixels_after[i, j] = noise_data[i][j]

img_after.show()
img_after.save('decoded_image.bmp')
