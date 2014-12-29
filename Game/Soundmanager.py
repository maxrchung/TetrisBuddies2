import pygame

class soundmanager():
    def __init__(self):
        # Not sure if needed, but guides recommended it
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)

        # 200 MB of music is too much to work with, so I limited it to
        # 1 background track. Chose madoka since it's the smallest file...
        # and probably the most relevant
        madoka = pygame.mixer.music.load('pinkpanther.wav')
        # -1 to indicate repeat forever
        pygame.mixer.music.play(-1)

    def playsound(self, soundname):
        if soundname=='singleline':
            sound = pygame.mixer.Sound('linecomplete.wav')
            sound.play()
        elif soundname=='switch':
            sound = pygame.mixer.Sound('switch.wav')
            sound.play()
        elif soundname=='placed':
            sound = pygame.mixer.Sound('placed.wav')
            sound.play()
        elif soundname=='fourline':
            sound = pygame.mixer.Sound('tetriscomplete.wav')
            sound.play()
        elif soundname=='youfail':
            sound = pygame.mixer.Sound('youfail.wav')
            sound.play()
        else:
            print("WHAT THE FUCK I CAN'T FIND THE SOUND FILE HELP!!!!")
