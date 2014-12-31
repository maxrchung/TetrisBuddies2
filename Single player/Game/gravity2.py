import pygame

class gravity:
    def __init__(self,acc):
        self._time = pygame.time.get_ticks()
        self._startTime = acc
        self._dropTime = self._startTime
        self._landing = False

    def increase(self,clears):
        if clears < 100:
            self._dropTime = self._startTime - (clears * 10)
        
    def fall(self,block,cells,timer):
        if (pygame.time.get_ticks() - self._time > self._dropTime
            and self._landing == False):
            self._time = pygame.time.get_ticks()
            if(cells.checkCol(block)==False):
                block.y += 1
            else:
                self._landing = True
        elif (self._landing == True and pygame.time.get_ticks() -
              self._time > 500) :
            timer = 0
            self._landing = False
            if cells.checkCol(block) != False:
                block = cells.place(block)
            self._time = pygame.time.get_ticks()
        return block
