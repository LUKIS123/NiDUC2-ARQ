import sys
from threading import Thread

import PIL.Image as Image

import ByteUtils
from Channel import Channel
from Enums.EncodingTypeEnum import EncodingType
from Enums.NoiseTypeEnum import NoiseType
from Receiver import Receiver
from Sender import Sender

# ========== simulation modes ==========
# ->    ["generate", how_many_bytes]

# ->    ["run", how_many_frames, channel_noise, coding_type, error_probability_of_good_state,
#       error_probability_of_bad_state, switch_to_good_probability, switch_to_bad_probability, ack_len, arq_protocol]

# ->    ["test", how_many_frames, channel_noise, coding_type, error_probability_of_good_state,
#       error_probability_of_bad_state, switch_to_good_probability, switch_to_bad_probability, ack_len, arq_protocol,
#       test_repeats]
# ======================================

# ============================TEST===============================

print('Argument List:', str(sys.argv))
testing = False
test_repeats = 1

if str(sys.argv[1]) == "generate":
    byte_array = ByteUtils.generate_bytes(int(sys.argv[2]))
    ByteUtils.save_byte_file(byte_array, "resources/data_file.txt")
    sys.exit()
elif str(sys.argv[1]) == "run" or str(sys.argv[1]) == "test":
    input_data = ByteUtils.get_binary_output_from_file("resources/data_file.txt")
    if len(input_data) % int(sys.argv[2]) != 0:
        print("Invalid frame number given")
        sys.exit()

    if str(sys.argv[1]) == "test":
        testing = True
        input_data = ByteUtils.get_binary_output_from_file("resources/data_file.txt")
        if len(input_data) % int(sys.argv[2]) != 0:
            print("Invalid frame number given")
            sys.exit()
        try:
            test_repeats = int(sys.argv[11])
        except IndexError:
            test_repeats = 10

    data_sequences = int(sys.argv[2])
    frame_length = int(len(input_data) / data_sequences)

    src_frames = ByteUtils.separate_list_to_chunks(input_data, frame_length)
    print("Single frame length = ", str(len(src_frames[0])))
    src_hash = ByteUtils.calculate_md5_hash(ByteUtils.binary_to_byte_arr(ByteUtils.flatten_2d_list(src_frames)))
    if not testing:
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

    try:
        ack_len = int(sys.argv[9])
    except IndexError:
        ack_len = 4

    channel = Channel(ch_noise_type)
    channel.set_probabilities_gilbert_elliot(p1, p2, p3, p4)
    sender = Sender(src_frames, channel, coding_type, coding_type, 16)
    receiver = Receiver(channel, coding_type, coding_type, 16)

    for iteration in range(test_repeats):
        arq_protocol = str(sys.argv[10]).lower()
        if arq_protocol == "stop_and_wait" or arq_protocol == "saw":
            sender_thread = Thread(target=sender.threaded_stop_and_wait_sender_function)
            receiver_thread = Thread(target=receiver.threaded_stop_and_wait_receiver_function,
                                     args=(len(src_frames), ack_len))
        else:
            window_size = 4
            sender_thread = Thread(target=sender.threaded_go_back_n_sender_function,
                                   args=(range(window_size), window_size, ack_len))
            receiver_thread = Thread(target=receiver.threaded_go_back_n_receiver_function,
                                     args=(len(src_frames), ack_len, window_size))

        sender_thread.start()
        receiver_thread.start()

        # shutting down threads
        receiver_thread.join()
        sender_thread.join()

        out_frames = receiver.output_bit_data_list_2d
        out_hash = ByteUtils.calculate_md5_hash(ByteUtils.binary_to_byte_arr(ByteUtils.flatten_2d_list(out_frames)))
        md5_cmp = src_hash == out_hash

        # BIT ERROR RATE COUNT
        bit_count = len(src_frames) * frame_length
        error_count = 0
        for i in range(len(src_frames)):
            for j in range(len(src_frames[0])):
                if src_frames[i][j] != out_frames[i][j]:
                    error_count += 1

        if not testing:
            print("Threads finished... Exiting...")
            print("Printing output data...")
            print(out_frames)
            print("\nMD5 comparison...")
            print(src_hash)
            print(out_hash)
            print("MD5 equal = " + str(md5_cmp))

            # printing simulation info
            print("\nBit error rate comparison...")
            print(
                f"Undetected error count: {error_count}, Bit Error Rate = {(error_count / bit_count) * 100}% "
                f"by {bit_count} data bits total")
            print("\nGeneral simulation data...")
            print("SENDER:")
            print(f"Total frames sent: {sender.frames_sent}")
            print(f"Ack fail message count: {sender.ack_fail_count}")
            print(f"Ack success message count: {sender.ack_success_count}")
            print(f"Ack message corrupted: {sender.ack_error_count}")
            print("RECEIVER:")
            print(f"Corrupted frames detected: {receiver.frame_error_detected_count}")

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
        else:
            filename = "resources/test_results.txt"
            file = open(filename, "a")
            if iteration == 0:
                file.write(f"Basic info: Single frame length={frame_length}, args=" + str(sys.argv))
                file.write("\n----------------------------------------------------------------------------\n\n")
            file.write(f"TEST ITERATION: {iteration}\nMD5 comparison...\nMD5 equal = {md5_cmp}")
            file.write("\n\nBit error rate comparison...")
            file.write(
                f"\nUndetected error count: {error_count} bits, Bit Error Rate = {(error_count / bit_count) * 100}% "
                f"by {bit_count} data bits total")
            file.write("\n\nGeneral simulation data...")
            if arq_protocol == "stop_and_wait" or arq_protocol == "saw":
                file.write(f"\nSENDER:\nTotal frames sent: {sender.frames_sent}\nAck fail message count: "
                           f"{sender.ack_fail_count}\nAck success message count: {sender.ack_success_count}\n"
                           f"Ack message corrupted: {sender.ack_error_count}")
            else:
                file.write(
                    f"\nSENDER:\nTotal frames sent: {sender.frames_sent} == {int(sender.frames_sent / window_size)}"
                    f" window sized sequences\nAck fail message count: {receiver.ack_fail_count}\n"
                    f"Ack success message count: "
                    f"{receiver.ack_success_count}\nAck message corrupted: {sender.ack_error_count}")
            file.write(f"\nRECEIVER:\nCorrupted frames detected: {receiver.frame_error_detected_count}")
            file.write("\n----------------------------------------------------------------------------\n\n")
            file.close()

            sender.clear_data()
            receiver.clear_data()

    sys.exit()

# TODO: jedna ramka 100 bajtow czyli 800bit + naglowek i stopka
