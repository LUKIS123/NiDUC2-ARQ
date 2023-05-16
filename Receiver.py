import copy

import DataGenerator
import Decoder
import Encoder
from Enums import EncodingTypeEnum
from FrameSequencingUtils import FrameSequencing
from time import sleep


class Receiver:
    output_bit_data_list_2d = []
    channel = None
    frame_sequence_util = None
    frame_coding_type = None
    ack_coding_type = None
    stop_msg = None
    ack_success = None
    ack_fail = None
    stop_receiving = False
    # zbieranie danych na temat symulacji
    frame_error_detected_count = 0
    go_back_n_numbering_error = 0
    ack_fail_count = 0
    ack_success_count = 0

    def __init__(self, channel, frame_coding_type, ack_coding_type, heading_len):
        self.channel = channel
        self.frame_coding_type = frame_coding_type
        self.ack_coding_type = ack_coding_type
        self.frame_sequence_util = FrameSequencing(heading_len)

    def clear_data(self):
        self.output_bit_data_list_2d = []
        self.frame_error_detected_count = 0
        self.ack_fail_count = 0
        self.ack_success_count = 0
        self.stop_receiving = False

    def threaded_stop_and_wait_receiver_function(self, frame_count, acknowledgement_bit_length):
        self.stop_msg = Encoder.encode_frame(DataGenerator.generate_stop_msg(2 * acknowledgement_bit_length),
                                             self.ack_coding_type)
        self.ack_success = DataGenerator.generate_ack(acknowledgement_bit_length, True)
        self.ack_fail = DataGenerator.generate_ack(acknowledgement_bit_length, False)
        frame_index = 0
        sleep(0.01)

        while frame_index < frame_count:
            # Sygnal do przerwania symulacji
            if self.stop_receiving:
                break

            success = False
            self.frame_sequence_util.set_frame_number(frame_index)
            while not success:

                # Sygnal do przerwania symulacji
                if self.stop_receiving:
                    break

                print(f" Receiver index: {frame_index}")
                encoded_frame_received = self.channel.receive_data()
                # Obsluga sekwencjonowania ramek
                frame_data = self.frame_sequence_util.split_sequence_from_frame(encoded_frame_received)
                frame_number_received = self.frame_sequence_util.get_int_from_heading(frame_data[0])

                encoded_frame = frame_data[1]
                decoded_frame = None
                ack_encoded = None

                match self.frame_coding_type:

                    case EncodingTypeEnum.EncodingType.ParityBit:
                        decoded_frame = Decoder.decode_parity_bit_encoded_frame(encoded_frame)

                        # Obsluga sekwencjonowania ramek
                        if frame_number_received != self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_fail)
                            self.channel.transmit_data(
                                Encoder.encode_frame(self.frame_sequence_util.append_sequence_number(ack_list),
                                                     self.ack_coding_type))
                            continue

                        if Decoder.check_for_error_parity_bit(encoded_frame, decoded_frame):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = False

                    case EncodingTypeEnum.EncodingType.CRC_32:
                        received_data = Decoder.decode_crc32_encoded_frame_and_check_sum(encoded_frame)
                        decoded_frame = received_data[0]

                        # Obsluga sekwencjonowania ramek
                        if frame_number_received != self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_fail)
                            self.channel.transmit_data(
                                Encoder.encode_frame(self.frame_sequence_util.append_sequence_number(ack_list),
                                                     self.ack_coding_type))
                            continue

                        if Decoder.check_for_error_crc32(decoded_frame, received_data[1]):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, self.ack_coding_type)
                            success = False

                    case EncodingTypeEnum.EncodingType.CRC_8:
                        received_data = Decoder.decode_crc8_encoded_frame_and_check_sum(encoded_frame)
                        decoded_frame = received_data[0]

                        # Obsluga sekwencjonowania ramek
                        if frame_number_received != self.frame_sequence_util.frame_number:
                            ack_list = copy.deepcopy(self.ack_fail)
                            self.channel.transmit_data(
                                Encoder.encode_frame(self.frame_sequence_util.append_sequence_number(ack_list),
                                                     self.ack_coding_type))
                            continue

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

                # Sygnal do przerwania symulacji
                if self.stop_receiving:
                    break

                if success:
                    # Receiver przyjmuje ramke, zostaje zapisana
                    self.output_bit_data_list_2d.append(decoded_frame)
                    frame_index += 1
                else:
                    self.frame_error_detected_count += 1

                if len(self.output_bit_data_list_2d) == frame_count:
                    # Powiadomienie do Sender'a aby zakonczyl dzialanie
                    self.channel.send_stop_msg(self.frame_sequence_util.append_sequence_number(self.stop_msg))
                else:
                    # Transmisja ramki zgloszenia o powodzeniu/niepowodzeniu
                    self.frame_sequence_util.set_frame_number(frame_index)
                    self.channel.transmit_data(self.frame_sequence_util.append_sequence_number(ack_encoded))

        print("STOP - Receiver")

    def threaded_go_back_n_receiver_function(self, frame_count, acknowledgement_bit_length, window_size):
        self.stop_msg = Encoder.encode_frame(DataGenerator.generate_stop_msg(2 * acknowledgement_bit_length),
                                             self.ack_coding_type)
        self.ack_success = DataGenerator.generate_ack(acknowledgement_bit_length, True)
        self.ack_fail = DataGenerator.generate_ack(acknowledgement_bit_length, False)
        frame_index = 0
        while frame_index < frame_count:
            tmp_encoded_frame_list = []

            window_fail = False
            for sequence in range(window_size):
                tmp_index = frame_index + sequence
                encoded_frame_received = self.channel.receive_data()
                if window_fail:
                    self.go_back_n_numbering_error += 1
                    continue
                # Jesli ramka to StopMSG - jesli sender wyjdzie poza zakres ramek - uzupelnienie do 4 ramek
                if self.check_for_stop_msg(acknowledgement_bit_length, encoded_frame_received, self.ack_coding_type,
                                           frame_count, window_size):
                    window_fail = True
                    continue
                # Obsluga sekwencjonowania ramek
                frame_data = self.frame_sequence_util.split_sequence_from_frame(encoded_frame_received)
                frame_number_received = self.frame_sequence_util.get_int_from_heading(frame_data[0])
                if tmp_index == frame_count:
                    continue

                if frame_number_received == tmp_index:
                    encoded_frame = frame_data[1]
                    tmp_encoded_frame_list.append(encoded_frame)
                else:
                    window_fail = True
                    self.go_back_n_numbering_error += 1

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
                            self.frame_error_detected_count += 1

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
                            self.frame_error_detected_count += 1

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
                            self.frame_error_detected_count += 1

                    case _:
                        print("Invalid ack coding type")

                if success:
                    self.output_bit_data_list_2d.append(decoded_frame)
                    advance += 1
                else:
                    break

            frame_index += advance

            self.frame_sequence_util.set_frame_number(frame_index)
            print(f"Receiver request: {frame_index}\n")

            if len(self.output_bit_data_list_2d) == frame_count:
                self.channel.send_stop_msg(self.stop_msg)
                print("STOP - Receiver\n")
            else:
                # Receiver odpowiada - jaka ramke o danym indeksie aktualnie oczekuje
                self.channel.transmit_data(self.frame_sequence_util.append_sequence_number(ack_encoded))

            # zbieranie informacji o przebiegu
            if advance == window_size:
                # jesli wszystkie ramki w oknie przeslane z sukcesem - success
                self.ack_success_count += 1
            else:
                # jesli nie - fail
                self.ack_fail_count += 1

    def check_for_stop_msg(self, ack_bit_len, encoded_ack_list_received, ack_coding_type, frame_count, window_size):
        if len(self.output_bit_data_list_2d) <= (frame_count - window_size - 1):
            return False
        one_count = 0
        zero_count = 0
        decoded_ack_list_received = []
        match ack_coding_type:
            case EncodingTypeEnum.EncodingType.ParityBit:
                decoded_ack_list_received = Decoder.decode_parity_bit_encoded_frame(encoded_ack_list_received)
            case EncodingTypeEnum.EncodingType.CRC_32:
                decoded_ack_list_received = Decoder.decode_crc32_encoded_frame_and_check_sum(encoded_ack_list_received)
            case EncodingTypeEnum.EncodingType.CRC_8:
                decoded_ack_list_received = Decoder.decode_crc8_encoded_frame_and_check_sum(encoded_ack_list_received)

        if len(decoded_ack_list_received) <= ack_bit_len:
            return False
        else:
            for i in range(len(decoded_ack_list_received)):
                if decoded_ack_list_received[i] == 1:
                    one_count += 1
                else:
                    zero_count += 1
            if abs(one_count - zero_count) <= 1:
                return True
            else:
                return False
