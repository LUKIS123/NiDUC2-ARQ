class FrameSequencing:
    frame_number = 0
    heading_len = None

    def __init__(self, heading_len):
        self.heading_len = heading_len

    # Numerowanie ramek od 0
    def append_sequence_number(self, list_1d):
        tmp_num = self.frame_number
        binary_seq = [int(i) for i in bin(tmp_num)[2:]]
        addendum_len = self.heading_len - len(binary_seq)
        if addendum_len < 0:
            # Jesli ilosc ramek w zapisie binarnym przekroczy rozmiar nastepuje reset
            self.frame_number = 0
            binary_seq = [0]

        for i in range(addendum_len):
            binary_seq.insert(0, 0)

        # self.frame_number += 1
        return [*binary_seq, *list_1d]

    def split_sequence_from_frame(self, list_1d):
        # list[0] dostep do naglowka
        # list[1] dostep do ramki
        return list_1d[:self.heading_len], list_1d[self.heading_len:]

    @staticmethod
    def get_int_from_heading(heading_list):
        weight = 0
        result = 0
        for i in range(len(heading_list) - 1, -1, -1):
            result += heading_list[i] * pow(2, weight)
            weight += 1
        return result

    def set_frame_number(self, number):
        self.frame_number = number

# seq = FrameSequencingUtils.FrameSequencing(16)
# t = seq.append_sequence_number([1, 1, 1, 1, 1, 1])
# split = seq.split_sequence_from_frame(t)
# seq.get_int_from_heading(split[0])
