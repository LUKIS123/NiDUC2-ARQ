import DataGenerator
import Decoder
import Encoder
import EncodingTypeEnum


class Receiver:
    output_bit_data_list_2d = []
    channel = None
    frame_coding_type = None
    ack_coding_type = None
    stop_msg = None

    def __init__(self, channel, frame_coding_type, ack_coding_type):
        self.channel = channel
        self.frame_coding_type = frame_coding_type
        self.ack_coding_type = ack_coding_type

    def threaded_receiver_function(self, frame_count, acknowledgement_bit_length):
        self.stop_msg = Encoder.encode_frame(DataGenerator.generate_stop_msg(2 * acknowledgement_bit_length),
                                             self.ack_coding_type)
        frame_index = 0
        while frame_index < frame_count:
            success = False

            while not success:
                encoded_frame = self.channel.receive_data()
                decoded_frame = None
                ack_encoded = None

                match self.ack_coding_type:

                    case EncodingTypeEnum.EncodingType.ParityBit:
                        decoded_frame = Decoder.decode_parity_bit_encoded_frame(encoded_frame)
                        if Decoder.check_for_error_parity_bit(encoded_frame, decoded_frame):
                            ack_list = DataGenerator.generate_ack(acknowledgement_bit_length, True)
                            ack_encoded = Encoder.encode_frame(ack_list, EncodingTypeEnum.EncodingType.ParityBit)
                            success = True
                        else:
                            ack_list = DataGenerator.generate_ack(acknowledgement_bit_length, False)
                            ack_encoded = Encoder.encode_frame(ack_list, EncodingTypeEnum.EncodingType.ParityBit)

                    case _:
                        print("Invalid ack coding type")
                if success:
                    # appending decoded frame if success
                    if not self.check_if_recurrence(decoded_frame, frame_index):
                        self.output_bit_data_list_2d.append(decoded_frame)
                        frame_index += 1
                # transmitting back acknowledgment
                self.channel.transmit_data(ack_encoded)

        print("\nPrinting received data...")
        print(self.output_bit_data_list_2d)
        self.channel.send_stop_msg(self.stop_msg)

        # acknowledge the receiver to stop receiving

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

# do przemyslenia => frame count zastapic jakims framem oznaczajacym koniec transmisji
