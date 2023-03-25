from threading import *
from time import sleep
from collections import deque
import ChannelNoise
import NoiseTypeEnum


class Channel:
    # single frame is being stored in the channel
    q = deque(maxlen=1)
    condition_object = Condition()
    probability_1 = 50
    probability_2 = 50
    probability_3 = 50
    probability_4 = 50

    def __init__(self, channel_type):
        self.noise_type = channel_type

    def set_channel_type(self, channel_type):
        self.noise_type = channel_type

    def set_probability_bsc(self, error_probability):
        self.probability_1 = error_probability

    def set_probabilities_gilbert_elliot(self, error_probability_of_good_state, error_probability_of_bad_state,
                                         switch_to_good_probability, switch_to_bad_probability):
        self.probability_1 = error_probability_of_good_state
        self.probability_2 = error_probability_of_bad_state
        self.probability_3 = switch_to_good_probability
        self.probability_3 = switch_to_bad_probability

    def transmit_data(self, bit_list_1d):
        self.condition_object.acquire()
        match self.noise_type:
            case NoiseTypeEnum.NoiseType.bsc_channel:
                self.q.append(ChannelNoise.bsc_channel_single(bit_list_1d, 0.5))
            case NoiseTypeEnum.NoiseType.gilbert_elliot:
                self.q.append(
                    ChannelNoise.gilbert_elliot_channel_single(bit_list_1d, self.probability_1, self.probability_2,
                                                               self.probability_3, self.probability_4))
            case _:
                print("Noise type invalid")
        self.condition_object.notify()
        self.condition_object.wait()
        self.condition_object.release()

    def receive_data(self):
        self.condition_object.acquire()
        result = self.q.pop()
        self.condition_object.release()
        return result
