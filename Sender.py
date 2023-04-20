import Decoder
import Encoder
from Enums import EncodingTypeEnum
from FrameSequencingUtils import FrameSequencing


class Sender:
    bit_data_list_2d = None
    encoded_bit_list = None
    channel = None
    frame_sequence_util = None
    frame_coding_type = None
    ack_coding_type = None
    ack_success = None
    ack_match = None
    acknowledgement_decoded = None
    regular_acknowledgement_length = None
    stop = False

    def __init__(self, bit_list_2d, channel, frame_coding_type, ack_coding_type, heading_len):
        self.bit_data_list_2d = bit_list_2d
        self.channel = channel
        self.frame_coding_type = frame_coding_type
        self.ack_coding_type = ack_coding_type
        # Narzedzie do numerowania ramek
        self.frame_sequence_util = FrameSequencing(heading_len)
        # encoded 2D data list
        self.encoded_bit_list = Encoder.encode_frame(bit_list_2d, self.frame_coding_type)

    def threaded_sender_function(self):
        for index in range(len(self.bit_data_list_2d)):
            if self.stop:
                break

            self.ack_success = False

            while not self.ack_success:
                print(f"Frame: {index + 1}")
                encoded_frame = self.encoded_bit_list[index]

                self.frame_sequence_util.set_frame_number(index)
                self.channel.transmit_data(self.frame_sequence_util.append_sequence_number(encoded_frame))

                acknowledgement_encoded = self.channel.receive_data()
                self.acknowledgement_decoded = None

                match self.ack_coding_type:

                    case EncodingTypeEnum.EncodingType.ParityBit:
                        self.acknowledgement_decoded = Decoder.decode_parity_bit_encoded_frame(acknowledgement_encoded)

                        # checking if acknowledgement is stop message
                        if index > 1:
                            if self.check_for_stop_msg():
                                self.stop = True
                                break
                        elif index == 1:
                            self.regular_acknowledgement_length = len(self.acknowledgement_decoded)
                        # checking done

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

                        # checking if acknowledgement is stop message
                        if index > 1:
                            if self.check_for_stop_msg():
                                self.stop = True
                                break
                        elif index == 1:
                            self.regular_acknowledgement_length = len(self.acknowledgement_decoded)
                        # checking done

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

                        # checking if acknowledgement is stop message
                        if index > 1:
                            if self.check_for_stop_msg():
                                self.stop = True
                                break
                        elif index == 1:
                            self.regular_acknowledgement_length = len(self.acknowledgement_decoded)
                        # checking done

                        if Decoder.check_for_error_crc8(self.acknowledgement_decoded, crc8_checksum):
                            self.ack_match = True
                        else:
                            self.ack_success = False
                            self.ack_match = False

                    case _:
                        print("Invalid ack coding type")

                if self.ack_match:
                    # encoding matches
                    self.ack_success = True
                    one_count = 0
                    for bit in range(len(self.acknowledgement_decoded)):
                        if self.acknowledgement_decoded[bit] == 1:
                            one_count += 1
                    if one_count < len(self.acknowledgement_decoded):
                        self.ack_success = False

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
