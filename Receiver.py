import DataGenerator
import Decoder
import Encoder
import EncodingTypeEnum


class Receiver:
    output_bit_data_list_2d = []
    timeout = 0.0001
    channel = None
    frame_coding_type = None
    ack_coding_type = None

    def __init__(self, channel, frame_coding_type, ack_coding_type):
        self.channel = channel
        self.frame_coding_type = frame_coding_type
        self.ack_coding_type = ack_coding_type

    # do poprawy -> frame count zastapic jakims framem oznaczajacym koniec transmisji
    def threaded_receiver_function(self, frame_count, acknowledgement_bit_length):
        for i in range(frame_count):
            success = False
            while not success:
                encoded_frame = self.channel.receive_data()
                decoded_frame = None

                match self.ack_coding_type:
                    case EncodingTypeEnum.EncodingType.ParityBit:
                        decoded_frame = Decoder.decode_parity_bit_encoded_frame(encoded_frame)
                    case _:
                        print("Invalid ack coding type")

                ack_list = None
                if Decoder.check_for_error_parity_bit(encoded_frame, decoded_frame):
                    # appending decoded frame
                    self.output_bit_data_list_2d.append(decoded_frame)
                    # ack
                    ack_list = DataGenerator.generate_ack(acknowledgement_bit_length, True)
                    ack_encoded = Encoder.encode_frame(ack_list, EncodingTypeEnum.EncodingType.ParityBit)
                    self.channel.transmit_data(ack_encoded)
                    success = True
                else:
                    ack_list = DataGenerator.generate_ack(acknowledgement_bit_length, False)
                    ack_encoded = Encoder.encode_frame(ack_list, EncodingTypeEnum.EncodingType.ParityBit)
                    self.channel.transmit_data(ack_encoded)
        print("Printing received data...")
        print(self.output_bit_data_list_2d)

# Problem jest nastepujacy -> nalezy zmienic format wiadomosci ack poniewaz
# jesli uzywamy samych jedynek jako perawda to wedy latwo dochodzi do przeklaman przez kodowanie bitem parzystosci
# przez to jeli zostanie przeklamana jedna jedynka, receiver potraktuje to jako fałsz
# przetla nie przechodzi i idzie jedna ramka przez cały czas
# wszytsko sie psuje
