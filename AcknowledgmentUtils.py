import ParityBitCoding
import Decoder


def encode_ack_parity_bit(length, positive):
    output = []
    if positive:
        bit = 1
    else:
        bit = 0
    for i in range(length):
        output.append(bit)
    return ParityBitCoding.parity_bit_decode_single(output)
