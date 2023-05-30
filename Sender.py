import DataGenerator
import Decoder
import Encoder
from Enums import EncodingTypeEnum
from FrameSequencingUtils import FrameSequencing


class Sender:
    bit_data_list_2d = None
    encoded_bit_list = None
    channel = None
    receiver = None
    frame_sequence_util = None
    frame_coding_type = None
    ack_coding_type = None
    ack_success = None
    ack_match = None
    acknowledgement_decoded = []
    regular_acknowledgement_length = None
    stop = False
    stop_msg = None
    frame_repeat_limit = 100
    simulation_failure = False
    # zbieranie danych na temat symulacji
    frames_sent = 0
    ack_fail_count = 0
    ack_success_count = 0
    ack_error_count = 0
    frame_repeats_counter_list = None

    def __init__(self, bit_list_2d, channel, frame_coding_type, ack_coding_type, receiver, frame_limit, heading_len):
        self.bit_data_list_2d = bit_list_2d
        self.channel = channel
        self.frame_coding_type = frame_coding_type
        self.ack_coding_type = ack_coding_type
        # Narzedzie do numerowania ramek
        self.frame_sequence_util = FrameSequencing(heading_len)
        # encoded 2D data list
        self.encoded_bit_list = Encoder.encode_frame(bit_list_2d, self.frame_coding_type)
        self.frame_repeats_counter_list = [0] * len(self.bit_data_list_2d)
        self.receiver = receiver
        self.frame_repeat_limit = frame_limit

    def clear_data(self):
        self.stop = False
        self.frames_sent = 0
        self.ack_fail_count = 0
        self.ack_success_count = 0
        self.ack_error_count = 0
        self.frame_repeats_counter_list = [0] * len(self.bit_data_list_2d)
        self.simulation_failure = False

    def threaded_stop_and_wait_sender_function(self, acknowledgement_bit_length, ack_sequencing_delimiter):
        self.stop_msg = Encoder.encode_frame(DataGenerator.generate_stop_msg(2 * acknowledgement_bit_length),
                                             self.ack_coding_type)
        index = 0
        while index != len(self.bit_data_list_2d):
            if self.stop:
                break

            self.ack_success = False

            while not self.ack_success:
                print(f" Frame: {index}")
                encoded_frame = self.encoded_bit_list[index]

                self.frame_sequence_util.set_frame_number(index)
                self.channel.transmit_data(self.frame_sequence_util.append_sequence_number(encoded_frame))

                # Zbieranie danych o tym ile razy ta sama ramka zostala wyslana
                self.frame_repeats_counter_list[index] += 1

                # Limit powtorzen zostal przekroczony - przerywanie symulacji
                if self.frame_repeats_counter_list[index] == self.frame_repeat_limit:
                    self.simulation_failure = True
                    self.receiver.stop_receiving = True
                    self.stop = True
                    self.channel.send_stop_msg(self.stop_msg)
                    break

                frame_data = self.frame_sequence_util.split_sequence_from_frame(self.channel.receive_data())
                frame_number_received = self.frame_sequence_util.get_int_from_heading(frame_data[0])

                acknowledgement_encoded = frame_data[1]

                self.acknowledgement_decoded = []
                self.frames_sent += 1

                match self.ack_coding_type:

                    case EncodingTypeEnum.EncodingType.ParityBit:
                        self.acknowledgement_decoded = Decoder.decode_parity_bit_encoded_frame(acknowledgement_encoded)

                        if index > 1:
                            if self.check_for_stop_msg():
                                self.stop = True
                                break
                        else:
                            self.regular_acknowledgement_length = len(self.acknowledgement_decoded)

                        if Decoder.check_for_error_parity_bit(acknowledgement_encoded, self.acknowledgement_decoded):
                            self.ack_match = True
                        else:
                            self.ack_success = False
                            self.ack_match = False

                    case EncodingTypeEnum.EncodingType.CRC_32:
                        split_data = Decoder.decode_crc32_encoded_frame_and_check_sum(
                            acknowledgement_encoded)
                        self.acknowledgement_decoded = split_data[0]
                        crc32_checksum = split_data[1]

                        if index > 1:
                            if self.check_for_stop_msg():
                                self.stop = True
                                break
                        else:
                            self.regular_acknowledgement_length = len(self.acknowledgement_decoded)

                        if Decoder.check_for_error_crc32(self.acknowledgement_decoded, crc32_checksum):
                            self.ack_match = True
                        else:
                            self.ack_success = False
                            self.ack_match = False

                    case EncodingTypeEnum.EncodingType.CRC_8:
                        split_data = Decoder.decode_crc8_encoded_frame_and_check_sum(
                            acknowledgement_encoded)
                        self.acknowledgement_decoded = split_data[0]
                        crc8_checksum = split_data[1]

                        if index > 1:
                            if self.check_for_stop_msg():
                                self.stop = True
                                break
                        else:
                            self.regular_acknowledgement_length = len(self.acknowledgement_decoded)

                        if Decoder.check_for_error_crc8(self.acknowledgement_decoded, crc8_checksum):
                            self.ack_match = True
                        else:
                            self.ack_success = False
                            self.ack_match = False

                    case _:
                        print("Invalid ack coding type")

                if self.ack_match:
                    self.ack_success = True
                    one_count = 0
                    for bit in range(len(self.acknowledgement_decoded)):
                        if self.acknowledgement_decoded[bit] == 1:
                            one_count += 1

                    if one_count < len(self.acknowledgement_decoded):
                        self.ack_success = False
                        self.ack_fail_count += 1
                    else:
                        self.ack_success = True
                        index += 1
                        self.ack_success_count += 1
                else:
                    self.ack_error_count += 1

                if not self.ack_success:
                    if frame_number_received == index or frame_number_received == index + ack_sequencing_delimiter \
                            or frame_number_received == index - ack_sequencing_delimiter:
                        if frame_number_received == index + ack_sequencing_delimiter:
                            self.ack_success = True
                            if self.ack_match:
                                self.ack_fail_count -= 1
                            else:
                                self.ack_error_count -= 1
                            self.ack_success_count += 1
                        elif frame_number_received == index - ack_sequencing_delimiter:
                            self.ack_success_count -= 1
                            self.ack_fail_count += 1
                        index = frame_number_received
        print("STOP - Sender")

    def check_for_stop_msg(self):
        one_count = 0
        zero_count = 0
        if len(self.acknowledgement_decoded) <= self.regular_acknowledgement_length:
            return False
        else:
            for i in range(len(self.acknowledgement_decoded)):
                if self.acknowledgement_decoded[i] == 1:
                    one_count += 1
                else:
                    zero_count += 1
            if abs(one_count - zero_count) <= 2:
                return True
            else:
                return False

    def threaded_go_back_n_sender_function(self, window_size_iterable, window_size, acknowledgement_bit_length):
        stop_msg = Encoder.encode_frame(DataGenerator.generate_stop_msg(2 * acknowledgement_bit_length),
                                        self.ack_coding_type)
        lower_window_index = 0
        higher_window_index = window_size - 1

        while not self.stop:
            print("-------------------------")
            for sequence in window_size_iterable:
                current_index = lower_window_index + sequence

                if current_index >= len(self.bit_data_list_2d):
                    self.channel.transmit_data(stop_msg)
                    continue

                self.frame_sequence_util.set_frame_number(current_index)
                encoded_frame = self.encoded_bit_list[current_index]
                print(f"Frame: {current_index}")
                self.channel.transmit_data(self.frame_sequence_util.append_sequence_number(encoded_frame))
                self.frames_sent += 1
                # Zbieranie danych o tym ile razy ta sama ramka zostala wyslana
                self.frame_repeats_counter_list[current_index] += 1

                # Limit powtorzen zostal przekroczony - przerywanie symulacji
                if self.frame_repeats_counter_list[current_index] == self.frame_repeat_limit:
                    self.simulation_failure = True
                    self.receiver.stop_receiving = True
                    self.stop = True
                    self.channel.send_stop_msg(stop_msg)
                    break
            print("-------------------------")

            if self.stop:
                break

            encoded_frame_received = self.channel.receive_data()
            frame_data = self.frame_sequence_util.split_sequence_from_frame(encoded_frame_received)
            acknowledgement_encoded = frame_data[1]

            if self.check_for_stop_msg_go_back_n(encoded_frame_received, lower_window_index):
                # Sender exiting...
                break

            match self.ack_coding_type:

                case EncodingTypeEnum.EncodingType.ParityBit:
                    self.acknowledgement_decoded = Decoder.decode_parity_bit_encoded_frame(acknowledgement_encoded)

                    if lower_window_index <= window_size + 1:
                        self.regular_acknowledgement_length = len(self.acknowledgement_decoded)

                    if len(acknowledgement_encoded) == 0:
                        acknowledgement_encoded = encoded_frame_received
                    if Decoder.check_for_error_parity_bit(acknowledgement_encoded, self.acknowledgement_decoded):
                        self.ack_match = True
                    else:
                        self.ack_match = False

                case EncodingTypeEnum.EncodingType.CRC_32:
                    split_data = Decoder.decode_crc32_encoded_frame_and_check_sum(
                        acknowledgement_encoded)
                    self.acknowledgement_decoded = split_data[0]
                    crc32_checksum = split_data[1]

                    if lower_window_index <= window_size + 1:
                        self.regular_acknowledgement_length = len(self.acknowledgement_decoded)

                    if Decoder.check_for_error_crc32(self.acknowledgement_decoded, crc32_checksum):
                        self.ack_match = True
                    else:
                        self.ack_match = False

                case EncodingTypeEnum.EncodingType.CRC_8:
                    split_data = Decoder.decode_crc8_encoded_frame_and_check_sum(
                        acknowledgement_encoded)
                    self.acknowledgement_decoded = split_data[0]
                    crc8_checksum = split_data[1]

                    if lower_window_index <= window_size + 1:
                        self.regular_acknowledgement_length = len(self.acknowledgement_decoded)

                    if Decoder.check_for_error_crc8(self.acknowledgement_decoded, crc8_checksum):
                        self.ack_match = True
                    else:
                        self.ack_match = False

                case _:
                    print("Invalid ack coding type")

            if not self.acknowledgement_decoded:
                # Sender exiting...
                break

            if self.ack_match:
                # Obsluga sekwencjonowania ramek
                frame_number_received = self.frame_sequence_util.get_int_from_heading(frame_data[0])
                if lower_window_index - window_size <= frame_number_received <= higher_window_index + 1:

                    lower_window_index = frame_number_received

                    if lower_window_index >= len(self.bit_data_list_2d) - 1:
                        higher_window_index = len(self.bit_data_list_2d)
                    else:
                        higher_window_index = lower_window_index + window_size
            else:
                self.ack_error_count += 1
        print("STOP - Sender")

    def check_for_stop_msg_go_back_n(self, frame_data, index):
        one_count = 0
        zero_count = 0
        if index <= len(self.bit_data_list_2d) - 1:
            return False

        ack = frame_data
        decoded_ack_list_received = []
        match self.ack_coding_type:
            case EncodingTypeEnum.EncodingType.ParityBit:
                decoded_ack_list_received = Decoder.decode_parity_bit_encoded_frame(ack)
            case EncodingTypeEnum.EncodingType.CRC_32:
                decoded_ack_list_received = Decoder.decode_crc32_encoded_frame_and_check_sum(ack)
            case EncodingTypeEnum.EncodingType.CRC_8:
                decoded_ack_list_received = Decoder.decode_crc8_encoded_frame_and_check_sum(ack)

        if len(decoded_ack_list_received) <= self.regular_acknowledgement_length:
            return False
        else:
            for i in range(len(self.acknowledgement_decoded)):
                if self.acknowledgement_decoded[i] == 1:
                    one_count += 1
                else:
                    zero_count += 1
            if abs(one_count - zero_count) <= 1:
                return True
            else:
                return False
