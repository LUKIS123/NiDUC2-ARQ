from collections import deque
from threading import *

import ChannelNoise
import NoiseTypeEnum


class Channel:
    # single frame is being stored in the channel
    q = deque(maxlen=1)
    condition_object = Condition()
    probability_1 = 2
    probability_2 = 10
    probability_3 = 20
    probability_4 = 10

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
        if len(self.q) == 1:
            self.condition_object.wait()

        match self.noise_type:
            case NoiseTypeEnum.NoiseType.bsc_channel:
                self.q.append(ChannelNoise.bsc_channel_single(bit_list_1d, self.probability_1))
            case NoiseTypeEnum.NoiseType.gilbert_elliot:
                self.q.append(
                    ChannelNoise.gilbert_elliot_channel_single(bit_list_1d, self.probability_1, self.probability_2,
                                                               self.probability_3, self.probability_4))
            case _:
                print("Noise type invalid")
        # printing transmitted data
        print(self.q[0])
        print("\n")

        self.condition_object.notify()
        self.condition_object.wait()
        self.condition_object.release()

    def receive_data(self):
        self.condition_object.acquire()
        if len(self.q) == 0:
            self.condition_object.wait()
        result = self.q.pop()
        self.condition_object.notify()
        self.condition_object.release()
        return result

    def send_stop_msg(self, msg):
        self.condition_object.acquire()
        if len(self.q) == 1:
            self.q.pop()
        match self.noise_type:
            case NoiseTypeEnum.NoiseType.bsc_channel:
                self.q.append(ChannelNoise.bsc_channel_single(msg, self.probability_1))
            case NoiseTypeEnum.NoiseType.gilbert_elliot:
                self.q.append(
                    ChannelNoise.gilbert_elliot_channel_single(msg, self.probability_1, self.probability_2,
                                                               self.probability_3, self.probability_4))
            case _:
                print("Noise type invalid")
        self.condition_object.notify()
        self.condition_object.release()
