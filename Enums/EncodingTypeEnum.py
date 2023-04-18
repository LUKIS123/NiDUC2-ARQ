from enum import Enum


class EncodingType(Enum):
    ParityBit = 1
    Hamming = 2
    CRC_8 = 3
    CRC_32 = 4
