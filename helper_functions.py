import subprocess
from pathlib import Path


def check_speed(speed):
    """A function that return a value between 0 and 1, which has predictable behaviour for the motor class

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
    subprocess.run(["aplay", path])


def get_wav_files(directory_path):
    path = Path(directory_path)
    wav_files = [str(file) for file in path.glob("*.wav")]
    return wav_files
