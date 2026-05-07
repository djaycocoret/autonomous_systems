import subprocess
from pathlib import Path

import numpy as np


def softmax(scores):
    """
    A function that returns the input list as a probability distribution (softmax).

    Parameters
    __________
    scores : list[float]
        list that will be turned into a pdf

    Returns
    _______
    pd : list[float]
        The probability distribution
    """
    x = np.array(scores)
    e_x = np.exp(x - np.max(x))
    return (e_x / e_x.sum()).tolist()


def check_speed(speed):
    """
    A function that return a value between 0 and 1, which has predictable behaviour for the motor class

    Parameters
    __________

    speed : float
        The input speed

    Returns
    _______
    float
        The output speed, which is limited to a range of [0, 1]
    """

    return max(0, min(1, speed))


def play_wav(path):
    """
    A function that plays the .wav file of the specified path

    Parameters
    __________
    path : string
        The path of the .wav file which is supposed to be played
    """
    subprocess.run(["aplay", path])


def get_wav_files(directory_path):
    """
    A function that returns all the .wav files in a certain directory

    Parameters
    __________
    directory_path : string
        The directory where the .wav files are

    Returns
    _______
    wav_files : list[string]
        A list containing all the .wav files in the directory
    """
    path = Path(directory_path)
    wav_files = [str(file) for file in path.glob("*.wav")]
    return wav_files
