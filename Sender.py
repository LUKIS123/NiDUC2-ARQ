import Decoder
import Encoder
from Enums import EncodingTypeEnum


class Sender:
    bit_data_list_2d = None
    encoded_bit_list = None
    channel = None
    frame_coding_type = None
    ack_coding_type = None
    ack_error_toleration = None
    ack_success = None
    acknowledgement_decoded = None
    regular_acknowledgement_length = None
    stop = False

    def __init__(self, bit_list_2d, channel, frame_coding_type, ack_coding_type, ack_error_toleration_percentage):
        self.bit_data_list_2d = bit_list_2d
        self.channel = channel
        self.frame_coding_type = frame_coding_type
        self.ack_coding_type = ack_coding_type
        self.ack_error_toleration = ack_error_toleration_percentage
        # encoded 2D data list
        self.encoded_bit_list = Encoder.encode_frame(bit_list_2d, self.frame_coding_type)

    def threaded_sender_function(self):
        for index in range(len(self.bit_data_list_2d)):
            if self.stop:
                break

            self.ack_success = False

            while not self.ack_success:
                print(f"Frame: {index + 1}")
                self.channel.transmit_data(self.encoded_bit_list[index])

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
                            # encoding matches
                            self.ack_success = True
                            zero_count = 0
                            for bit in range(len(self.acknowledgement_decoded)):
                                if self.acknowledgement_decoded[bit] == 0:
                                    zero_count += 1
                            if zero_count >= self.ack_error_toleration * len(self.acknowledgement_decoded):
                                self.ack_success = False
                        else:
                            self.ack_success = False

                    case _:
                        print("Invalid ack coding type")

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
