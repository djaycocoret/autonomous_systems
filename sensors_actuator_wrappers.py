import random
import threading

from gpiozero import DigitalOutputDevice, DistanceSensor, PWMOutputDevice

from helper_functions import check_speed, play_wav


class Audio_processing:
    """A class representing the audio making module of the robot

    Attributes
    __________
    barks : List[str]
        A list containing the path at which the various audio samples of barks reside
    growl : List[str]
        A list containing the path at which the various audio samples of barks reside"""

    def __init__(self, barks, growls):
        self.barks = list(barks)
        self.growls = list(growls)
        # The lock ensures only one audio thread runs at a time
        self.audio_lock = threading.Lock()

    def _audio_worker(self, path):
        """
        The logic running inside the thread.
        It plays the sound and then releases the lock when finished.
        """
        try:
            play_wav(path)
        finally:
            # Always release the lock, even if play_wav crashes
            self.audio_lock.release()

    def _request_playback(self, audio_list):
        """
        Internal logic to check the lock and spawn a thread.
        If the lock is busy, it simply skips.
        """
        if not audio_list:
            return

        # Attempt to acquire the lock without waiting (non-blocking)
        if self.audio_lock.acquire(blocking=False):
            path = random.choice(audio_list)
            thread = threading.Thread(
                target=self._audio_worker, args=(path,), daemon=True
            )
            thread.start()
        else:
            print("Audio system busy. Skipping sound.")

    def bark(self):
        """Plays a random bark if the audio device is free."""
        self._request_playback(self.barks)

    def growl(self):
        """Plays a random growl if the audio device is free."""
        self._request_playback(self.growls)


class Distance_sensor:
    def __init__(self, trigger_pin, echo_pin):
        self.sensor = DistanceSensor(trigger_pin, echo_pin)

    def safe_distance(self, safe_distance: float):
        print(self.sensor.distance)
        return self.sensor.distance > safe_distance


class Motor:
    """A class representing a motor

    Attributes
    __________
    PWM : PWMOutputDevice
        The pin number connected to the Pulse Width Modulation connection on the L293D chip.
        This pin changes the speed of the motor.
    forward_pin : DigitalOutputDevice
        The pin number connected to the forward connection on the L293D chip
    backward_pin : DigitalOutputDevice
        The pin number connected to the backward connection on the L293D chip
    """

    def __init__(self, forward_pin, backward_pin, pwm_pin):
        """Initialise the motor class

        Parameters
        __________
        pwm_pin : int
            The pin connected to the Pulse Width Modulation connection on the L293D chip.
            This pin changes the speed of the motor.
        forward_pin : int
            The pin connected to the forward connection on the L293D chip
        backward_pin : int
            The pin connected to the backward connection on the L293D chip
        speed : float
            current speed
        """
        self.PWM = PWMOutputDevice(pwm_pin)
        self.forward_pin = DigitalOutputDevice(forward_pin)
        self.backward_pin = DigitalOutputDevice(backward_pin)
        self.speed = 0

    def __repr__(self):
        return f"Motor object: forward pin: {self.forward_pin}, backward pin: {self.backward_pin}, PWM: {self.PWM}, speed: {self.PWM.value}"

    def forward(self, speed=1.0):
        """Makes the motor move in the direction such that the agent moves forward

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the motor moves
        """
        self.speed = check_speed(speed)
        self.PWM.value = self.speed
        self.backward_pin.off()
        self.forward_pin.on()

    def stop(self):
        """Makes the motor stop"""
        self.speed = 0
        self.backward_pin.off()
        self.forward_pin.off()

    def backward(self, speed=1):
        """Makes the motor move in the direction such that the agent moves backward

        Parameters
        __________
        speed : float [0, 1]
            The speed at which the motor moves
        """
        self.speed = check_speed(speed)
        self.PWM.value = self.speed
        self.forward_pin.off()
        self.backward_pin.on()
