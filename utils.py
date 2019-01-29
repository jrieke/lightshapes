import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt


class Audio(sd.InputStream):

    def __init__(self):
        sd.InputStream.__init__(self)
        self.last_volumes = np.zeros((50, 3))
        self.index_last_volume = 0

    def volume(self, num_frames=1024, normalize_to='average', print_=False):
        """
        Return the volume of the audio input.

        Args:
            num_frames (int): The number of frames from the sound device to average.
            normalize_to (float): If not None (default), normalize the return value to [0, 1], where 1 is equivalent to this number.
            print_ (bool): Print a volume bar to the command line.

        Return:
            Volume (if normalize_to is not None, this is normalized to [0, 1]).
        """

        def print_volume(volume, overshoot=0, end='\n'):
            # Assumes volume to be between 0 and 1.
            bars = int(volume * 20)
            bars_overshoot = min(20, int(overshoot * 20))
            print('|' * bars, end='')
            print('-' * bars_overshoot, end='')
            print(' ' * max(0, 40-bars-bars_overshoot), end=end)

        def normalize(volume, normalize_to):
            normalized_volume = min(1, volume / normalize_to)
            overshoot_volume = volume / normalize_to - normalized_volume
            return normalized_volume, overshoot_volume

        # Read audio input and compute raw volume.
        #num_frames = audio_stream.read_available
        frames = self.read(num_frames)[0]
        frames = frames.mean(axis=1)  # get rid of channel information by averaging

        # Compute raw volume for low and high frequencies via FFT.
        fft = np.fft.fft(frames)
        start = int(len(fft) / 2)
        threshold = int(len(fft) * 3 / 4)
        low = fft[start:threshold]
        high = fft[threshold:]
        volume_low = np.linalg.norm(low) / len(low)
        volume_high = np.linalg.norm(high) / len(high)
        volume = np.linalg.norm(fft) / len(fft)
        #plt.plot(fft)
        #plt.show()

        # Store volumes for averaging.
        self.last_volumes[self.index_last_volume] = (volume, volume_low, volume_high)
        self.index_last_volume += 1
        if self.index_last_volume >= len(self.last_volumes):
            self.index_last_volume = 0
            print('history full')

        if normalize_to == 'average':
            normalize_to = self.last_volumes.mean(axis=0) + 1.5 * self.last_volumes.std(axis=0)
            normalize_to = normalize_to.clip(1e-10)

        if normalize_to is not None:
            volume, overshoot = normalize(volume, normalize_to[0])
            volume_low, overshoot_low = normalize(volume_low, normalize_to[1])
            volume_high, overshoot_high = normalize(volume_high, normalize_to[2])
            if print_:
                print_volume(volume, overshoot, end='     ')
                print_volume(volume_low, overshoot_low, end='     ')
                print_volume(volume_high, overshoot_high)

        return volume, volume_low, volume_high
