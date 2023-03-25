import threading
from time import sleep
import Encoder
import Decoder
import EncodingTypeEnum


class Sender:
    bit_data_list_2d = None
    encoded_bit_list = None
    timeout = 0.0001
    channel = None
    frame_coding_type = None
    ack_coding_type = None

    def __init__(self, bit_list_2d, channel, frame_coding_type, ack_coding_type):
        self.bit_data_list_2d = bit_list_2d
        self.channel = channel
        self.frame_coding_type = frame_coding_type
        self.ack_coding_type = ack_coding_type
        # encoded 2D data list
        self.encoded_bit_list = Encoder.encode_frame(bit_list_2d, self.frame_coding_type)

    def threaded_sender_function(self):
        for i in range(len(self.bit_data_list_2d)):
            self.channel.transmit_data(self.bit_data_list_2d)
            acknowledgement_encoded = self.channel.receive_data()
            acknowledgement_decoded = None
            match self.ack_coding_type:
                case EncodingTypeEnum.EncodingType.ParityBit:
                    acknowledgement_encoded = Decoder.decode_parity_bit_encoded_frame(acknowledgement_encoded)
                case _:
                    print("Invalid ack coding type")
            if Decoder.check_for_error(acknowledgement_encoded, acknowledgement_decoded):
                print()
                # encoding matches
