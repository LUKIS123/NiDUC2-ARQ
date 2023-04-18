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

    def threaded_receiver_function(self, frame_count, acknowledgement_bit_length):
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

                if frame_number_received != frame_index:
                    ack_list = copy.deepcopy(self.ack_fail)
                    self.channel.transmit_data(Encoder.encode_frame(ack_list, EncodingTypeEnum.EncodingType.ParityBit))
                    # saving ack of this iteration
                    self.previous_ack = ack_list
                    continue

                encoded_frame = frame_data[1]
                # Jesli numer ramki zgadza sie z licznikiem petli, przejdz dalej
                decoded_frame = None
                ack_list = None
                ack_encoded = None

                match self.ack_coding_type:

                    case EncodingTypeEnum.EncodingType.ParityBit:
                        decoded_frame = Decoder.decode_parity_bit_encoded_frame(encoded_frame)
                        if Decoder.check_for_error_parity_bit(encoded_frame, decoded_frame):
                            ack_list = copy.deepcopy(self.ack_success)
                            ack_encoded = Encoder.encode_frame(ack_list, EncodingTypeEnum.EncodingType.ParityBit)
                            success = True
                        else:
                            ack_list = copy.deepcopy(self.ack_fail)
                            ack_encoded = Encoder.encode_frame(ack_list, EncodingTypeEnum.EncodingType.ParityBit)

                    case _:
                        print("Invalid ack coding type")
                if success:
                    self.output_bit_data_list_2d.append(decoded_frame)
                    frame_index += 1
                    # # appending decoded frame if success, checking for reoccurrence
                    # if self.previous_ack == self.ack_success:
                    #     if not self.check_if_recurrence(decoded_frame, frame_index):
                    #         # success, frame is appended
                    #         self.output_bit_data_list_2d.append(decoded_frame)
                    #         frame_index += 1
                    # else:
                    #     # success, frame is appended
                    #     self.output_bit_data_list_2d.append(decoded_frame)
                    #     frame_index += 1
                # transmitting back acknowledgment
                self.channel.transmit_data(ack_encoded)
                # saving ack of this iteration
                self.previous_ack = ack_list

        print("\nPrinting received data...")
        print(self.output_bit_data_list_2d)
        # acknowledge the receiver to stop receiving
        self.channel.send_stop_msg(self.stop_msg)

    # if the acknowledgment gets corrupted the receiver will send the identical frames
    def check_if_recurrence(self, decoded_frame, index):
        try:
            previous_frame = self.output_bit_data_list_2d[index - 1]
            if previous_frame == decoded_frame:
                return True
            else:
                return False
        except IndexError:
            return False

# TODO: dodac funckje ktora bedzie porownywala wiadomosc z poprzednia, jesli sa zgodne w 100% to pomin => done
#       => mozliwe tez ze trzeba bedzie dodac numerowanie pakietow do kodera

# TODO: do przemyslenia => frame count zastapic jakims framem oznaczajacym koniec transmisji
