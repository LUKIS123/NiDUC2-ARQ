import sys
from threading import Thread

import PIL.Image as Image

import ByteUtils
from Channel import Channel
from Enums.EncodingTypeEnum import EncodingType
from Enums.NoiseTypeEnum import NoiseType
from Receiver import Receiver
from Sender import Sender

# ["generate", how_many_bytes]

# ["run", how_many_frames, channel_noise, coding_type, error_probability_of_good_state,
# error_probability_of_bad_state, switch_to_good_probability, switch_to_bad_probability]

print('Argument List:', str(sys.argv))

if str(sys.argv[1]) == "generate":
    byte_array = ByteUtils.generate_bytes(int(sys.argv[2]))
    ByteUtils.save_byte_file(byte_array, "data_file.txt")
    sys.exit()
elif str(sys.argv[1]) == "run":
    input_data = ByteUtils.get_binary_output_from_file("data_file.txt")
    if len(input_data) % int(sys.argv[2]) != 0:
        print("Invalid frame number given")
        sys.exit()

    data_sequences = int(sys.argv[2])
    frame_length = int(len(input_data) / data_sequences)

    src_frames = ByteUtils.separate_list_to_chunks(input_data, frame_length)
    print("Single frame length = ", str(len(src_frames[0])))
    src_hash = ByteUtils.calculate_md5_hash(ByteUtils.binary_to_byte_arr(ByteUtils.flatten_2d_list(src_frames)))
    print("Printing original data...")
    print(src_frames)
    print("\n")
    print("Starting simulation...")
    ch_noise_type = str(sys.argv[3])
    if ch_noise_type == "gilbert-eliot":
        ch_noise_type = NoiseType.gilbert_elliot
    elif ch_noise_type == "bsc":
        ch_noise_type = NoiseType.bsc_channel
    else:
        print("Invalid noise type...")
        print("Proceeding with BSC channel...")
        ch_noise_type = NoiseType.bsc_channel
    coding_type = str(sys.argv[4])

    match coding_type.lower():
        case "parity":
            coding_type = EncodingType.ParityBit
        case "crc8":
            coding_type = EncodingType.CRC_8
        case "crc32":
            coding_type = EncodingType.CRC_32
        case _:
            print("Invalid coding type...")
            print("Proceeding with parity bit coding...")
            coding_type = EncodingType.ParityBit

    try:
        p1 = float(sys.argv[5])
    except IndexError:
        p1 = 0.01
    try:
        p2 = float(sys.argv[6])
    except IndexError:
        p2 = 0.1
    try:
        p3 = float(sys.argv[7])
    except IndexError:
        p3 = 10
    try:
        p4 = float(sys.argv[8])
    except IndexError:
        p4 = 10

    channel = Channel(ch_noise_type)
    channel.set_probabilities_gilbert_elliot(p1, p2, p3, p4)
    sender = Sender(src_frames, channel, coding_type, coding_type, 16)
    receiver = Receiver(channel, coding_type, coding_type, 16)

    sender_thread = Thread(target=sender.threaded_sender_function)
    receiver_thread = Thread(target=receiver.threaded_receiver_function, args=(len(src_frames), 4))
    sender_thread.start()
    receiver_thread.start()

    # shutting down threads
    receiver_thread.join()
    sender_thread.join()
    print("Threads finished... Exiting...")
    print("Printing output data...")
    out_frames = receiver.output_bit_data_list_2d

    print(out_frames)
    print("MD5 comparison...")
    out_hash = ByteUtils.calculate_md5_hash(ByteUtils.binary_to_byte_arr(ByteUtils.flatten_2d_list(out_frames)))
    print(src_hash)
    print(out_hash)
    print("MD5 equal = " + str(src_hash == out_hash))

    # generating images
    img = Image.new('1', (data_sequences, frame_length))
    pixels = img.load()
    for i in range(img.size[0]):
        for j in range(img.size[1]):
            pixels[i, j] = src_frames[i][j]
    img.save('./pictures/original_image.bmp')

    img_after = Image.new('1', (data_sequences, frame_length))
    pixels_after = img_after.load()
    for i in range(img_after.size[0]):
        for j in range(img_after.size[1]):
            pixels_after[i, j] = out_frames[i][j]
    img_after.save('./pictures/decoded_image.bmp')

    sys.exit()

# =========== ARQ TEST ===========
# TODO: jedna ramka 100 bajtow czyli 800bit + naglowek i stopka
#   do zrobienia naglowek ramki z numerowaniem
# TODO: Zrobic aby wiadomosc ACK przesylala ktora rameczke chce z powrotem
#   (aktualnie rozwiazanie powoduje zapetlanie sie jesli w jednym w odbiornikow przeskoczy indeks)
#   obsluzyc przypadek gdy ilosc ramek przekroczy rozmiar naglowka
