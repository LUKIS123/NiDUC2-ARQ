import EncodingTypeEnum
import ParityBitCoding


def encode_frame(bit_list, encoding_type):
    match encoding_type:
        case EncodingTypeEnum.EncodingType.ParityBit:
            return ParityBitCoding.parity_bit_encode(bit_list)
        case _:
            # returning parity bit if invalid type
            return ParityBitCoding.parity_bit_encode(bit_list)
