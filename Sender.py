import Decoder
import Encoder
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
            ack_success = False

            while not ack_success:
                self.channel.transmit_data(self.bit_data_list_2d[i])
                acknowledgement_encoded = self.channel.receive_data()
                acknowledgement_decoded = None

                match self.ack_coding_type:
                    case EncodingTypeEnum.EncodingType.ParityBit:
                        acknowledgement_decoded = Decoder.decode_parity_bit_encoded_frame(acknowledgement_encoded)
                    case _:
                        print("Invalid ack coding type")

                # do poprawy -> jesli bedzie wiecej typow kodowania
                if Decoder.check_for_error_parity_bit(acknowledgement_encoded, acknowledgement_decoded):
                    # encoding matches
                    ack_success = True
                    for bit in range(len(acknowledgement_decoded)):
                        if bit == 0:
                            ack_success = False
                else:
                    ack_success = False
