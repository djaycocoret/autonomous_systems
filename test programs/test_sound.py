import subprocess
from random import randint
from time import sleep


def play_wav(path):
    subprocess.run(["aplay", path])


class Audio_processing:
    """A class representing the audio making module of the robot

    Attributes
    __________
    barks : List[str]
        A list containing the path at which the various audio samples of barks reside
    growl : List[str]
        A list containing the path at which the various audio samples of barks reside"""

    def __init__(self, bark, growl):
        """Initialses the Audio_processing class

        Parameters
        __________
        bark : List(str)
            A list containing one or several paths of a bark audio sample in wav format
        growl : List(str)
            A list containing one or several paths of a growl audio sample in wav format
        """
        self.bark_ = list()
        self.bark_.extend(bark)

        self.growl_ = list()
        self.growl_.extend(growl)

    def bark(self):
        max = len(self.bark_)
        index = randint(0, max - 1)
        path = self.bark_[index]
        play_wav(path)

    def growl(self):
        max = len(self.growl_)
        index = randint(0, max - 1)
        path = self.growl_[index]
        play_wav(path)


play_wav("files/audio/KSHMR_Animals_13_Dog_Growl.wav")

# ugly test code


audio = Audio_processing(
    ["files/audio/KSHMR_Animals_12_Dog_A.wav"],
    ["files/audio/KSHMR_Animals_13_Dog_Growl.wav"],
)

for i in range(10):
    audio.growl()
    sleep(5)
