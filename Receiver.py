import copy

import DataGenerator
import Decoder
import Encoder
from Enums import EncodingTypeEnum
from FrameSequencingUtils import FrameSequencing


class Receiver:
    output_bit_data_list_2d = []
    channel = None
    frame_sequence_util = None
    frame_coding_type = None
    ack_coding_type = None
    stop_msg = None
    previous_ack = None
    ack_success = None
    ack_fail = None

    def __init__(self, channel, frame_coding_type, ack_coding_type, heading_len):
        self.channel = channel
        self.frame_coding_type = frame_coding_type
        self.ack_coding_type = ack_coding_type
        self.frame_sequence_util = FrameSequencing(heading_len)

    def threaded_stop_and_wait_receiver_function(self, frame_count, acknowledgement_bit_length):
        self.stop_msg = Encoder.encode_frame(DataGenerator.generate_stop_msg(2 * acknowledgement_bit_length),
                                             self.ack_coding_type)
        self.ack_success = DataGenerator.generate_ack(acknowledgement_bit_length, True)
        self.ack_fail = DataGenerator.generate_ack(acknowledgement_bit_length, False)
        frame_index = 0
        while frame_index < frame_count:
            success = False
            self.frame_sequence_util.set_frame_number(frame_index)
            while not success:
                encoded_frame_received = self.channel.receive_data()
                # Obsluga sekwencjonowania ramek
                frame_data = self.frame_sequence_util.split_sequence_from_frame(encoded_frame_received)
                frame_number_received = self.frame_sequence_util.get_int_from_heading(frame_data[0])

                encoded_frame = frame_data[1]
                decoded_frame = None
                ack_list = None
                ack_encoded = None

                match self.frame_coding_type:

                    case EncodingTypeEnum.EncodingType.ParityBit:
                        # Obsluga sytuacji jesli Sender jest do tylu
                        if self.previous_ack == self.ack_success and \
                                frame_number_received < self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_success)
                            self.channel.transmit_data(
                                Encoder.encode_frame(ack_list, self.ack_coding_type))
                            # Klasa przechowuje poprzedni stan ACK
                            self.previous_ack = ack_list
                            continue
                        # Obsluga sekwencjonowania ramek
                        if frame_number_received != self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_fail)
                            self.channel.transmit_data(
                                Encoder.encode_frame(ack_list, self.ack_coding_type))
                            # Klasa przechowuje poprzedni stan ACK
                            self.previous_ack = ack_list
                            continue

                        decoded_frame = Decoder.decode_parity_bit_encoded_frame(encoded_frame)
                        if Decoder.check_for_error_parity_bit(encoded_frame, decoded_frame):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)

                    case EncodingTypeEnum.EncodingType.CRC_32:
                        # Obsluga sytuacji jesli Sender jest do tylu
                        if self.previous_ack == self.ack_success and \
                                frame_number_received < self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_success)
                            self.channel.transmit_data(
                                Encoder.encode_frame(ack_list, self.ack_coding_type))
                            # Klasa przechowuje poprzedni stan ACK
                            self.previous_ack = ack_list
                            continue
                        # Obsluga sekwencjonowania ramek
                        if frame_number_received != self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_fail)
                            self.channel.transmit_data(
                                Encoder.encode_frame(ack_list, self.ack_coding_type))
                            # Klasa przechowuje poprzedni stan ACK
                            self.previous_ack = ack_list
                            continue

                        received_data = Decoder.decode_crc32_encoded_frame_and_check_sum(encoded_frame)
                        decoded_frame = received_data[0]
                        if Decoder.check_for_error_crc32(decoded_frame, received_data[1]):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)

                    case EncodingTypeEnum.EncodingType.CRC_8:
                        # Obsluga sytuacji jesli Sender jest do tylu
                        if self.previous_ack == self.ack_success and \
                                frame_number_received < self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_success)
                            self.channel.transmit_data(
                                Encoder.encode_frame(ack_list, self.ack_coding_type))
                            # Klasa przechowuje poprzedni stan ACK
                            self.previous_ack = ack_list
                            continue
                        # Obsluga sekwencjonowania ramek
                        if frame_number_received != self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_fail)
                            self.channel.transmit_data(
                                Encoder.encode_frame(ack_list, self.ack_coding_type))
                            # Klasa przechowuje poprzedni stan ACK
                            self.previous_ack = ack_list
                            continue

                        received_data = Decoder.decode_crc8_encoded_frame_and_check_sum(encoded_frame)
                        decoded_frame = received_data[0]
                        if Decoder.check_for_error_crc8(decoded_frame, received_data[1]):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)

                    case _:
                        print("Invalid ack coding type")

                if success:
                    # Receiver przyjmuje ramke, zostaje zapisana
                    self.output_bit_data_list_2d.append(decoded_frame)
                    frame_index += 1

                # Transmisja ramki zgloszenia o powodzeniu/niepowodzeniu
                self.channel.transmit_data(ack_encoded)
                # Klasa przechowuje poprzedni stan ACK
                self.previous_ack = ack_list

        print("\nPrinting received data...")
        print(self.output_bit_data_list_2d)
        # Powiadomienie do Sender'a aby zakonczyl dzialanie
        self.channel.send_stop_msg(self.stop_msg)

    def threaded_go_back_n_receiver_function(self, frame_count, acknowledgement_bit_length, window_size):
        self.stop_msg = Encoder.encode_frame(DataGenerator.generate_stop_msg(2 * acknowledgement_bit_length),
                                             self.ack_coding_type)
        self.ack_success = DataGenerator.generate_ack(acknowledgement_bit_length, True)
        self.ack_fail = DataGenerator.generate_ack(acknowledgement_bit_length, False)
        frame_index = 0
        while frame_index < frame_count:
            tmp_encoded_frame_list = []
            for sequence in range(window_size):
                tmp_index = frame_index + sequence
                encoded_frame_received = self.channel.receive_data()
                # Obsluga sekwencjonowania ramek
                frame_data = self.frame_sequence_util.split_sequence_from_frame(encoded_frame_received)
                frame_number_received = self.frame_sequence_util.get_int_from_heading(frame_data[0])
                if frame_number_received == tmp_index:
                    encoded_frame = frame_data[1]
                    tmp_encoded_frame_list.append(encoded_frame)
                if tmp_index == frame_count - 1:
                    break

            ack_list = copy.deepcopy(self.ack_fail)
            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)

            advance = 0
            for frame_received_index in range(len(tmp_encoded_frame_list)):
                success = False
                decoded_frame = None
                match self.frame_coding_type:

                    case EncodingTypeEnum.EncodingType.ParityBit:
                        decoded_frame = Decoder.decode_parity_bit_encoded_frame(
                            tmp_encoded_frame_list[frame_received_index])
                        if Decoder.check_for_error_parity_bit(tmp_encoded_frame_list[frame_received_index],
                                                              decoded_frame):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = False

                    case EncodingTypeEnum.EncodingType.CRC_32:
                        received_data = Decoder.decode_crc32_encoded_frame_and_check_sum(
                            tmp_encoded_frame_list[frame_received_index])
                        decoded_frame = received_data[0]
                        if Decoder.check_for_error_crc32(decoded_frame, received_data[1]):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = False

                    case EncodingTypeEnum.EncodingType.CRC_8:
                        received_data = Decoder.decode_crc8_encoded_frame_and_check_sum(
                            tmp_encoded_frame_list[frame_received_index])
                        decoded_frame = received_data[0]
                        if Decoder.check_for_error_crc8(decoded_frame, received_data[1]):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = False

                    case _:
                        print("Invalid ack coding type")
                if success:
                    self.output_bit_data_list_2d.append(decoded_frame)
                    advance += 1
                else:
                    break
            frame_index += advance
            self.frame_sequence_util.set_frame_number(frame_index)
            print(f"Sender request: {frame_index} ")

            if len(self.output_bit_data_list_2d) == frame_count:
                self.channel.send_stop_msg(self.stop_msg)
                break
            else:
                # Receiver odpowiada - jaka ramke o danym indeksie aktualnie oczekuje
                self.channel.transmit_data(self.frame_sequence_util.append_sequence_number(ack_encoded))

        print("\nPrinting received data...")
        print(self.output_bit_data_list_2d)
