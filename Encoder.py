from Enums import EncodingTypeEnum
from Coding import ParityBitCoding
from Coding import CRC32Coding
from Coding import CRC8Coding


def encode_frame(bit_list, encoding_type):
    match encoding_type:
        case EncodingTypeEnum.EncodingType.ParityBit:
            if isinstance(bit_list[0], list):
                return ParityBitCoding.parity_bit_encode(bit_list)
            else:
                return ParityBitCoding.parity_bit_encode_single(bit_list)
        case EncodingTypeEnum.EncodingType.CRC_32:
            if isinstance(bit_list[0], list):
                return CRC32Coding.encode_list2d_crc_32(bit_list)
            else:
                return CRC32Coding.encode_list1d_crc_32_get(bit_list)
        case EncodingTypeEnum.EncodingType.CRC_8:
            if isinstance(bit_list[0], list):
                return CRC8Coding.encode_list2d_crc_8(bit_list)
            else:
                return CRC8Coding.encode_list1d_crc_8(bit_list)
        case _:
            # returning parity bit if invalid type
            return ParityBitCoding.parity_bit_encode(bit_list)
