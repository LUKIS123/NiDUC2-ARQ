import random


def random_noise(bit_data):
    for i in range(50):
        for j in range(50):
            choice = random.choice((0, 4))
            if choice <= 1:
                bit_data[i][j] = random.choice((0, 1))
    print("\n")
    print(bit_data)
    return bit_data
