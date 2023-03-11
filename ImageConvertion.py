import base64
import random


# do wywalenia => stara koncepcja
def image_to_data_url(filename):
    with open(filename, 'rb') as f:
        img = f.read()
    return base64.b64encode(img).decode('utf-8')


def generate_bit_data():
    data = [random.choice((0, 1)) for _ in range(2500)]
    data[:] = [data[i:i + 50] for i in range(0, 2500, 50)]
    print(data)
    return data
