from brain import Brain

brain = Brain.dummy_config(webcam=True)

if __name__ == "__main__":
    try:
        while True:
            brain.update(verbose=True)

    except KeyboardInterrupt:
        brain.stop()
