import pygame

class gravity:
    def __init__(self,acc,inc):
        self._time = pygame.time.get_ticks()
        self._dropTime = acc
        self._increment = inc
        self._landing = False
        
    def fall(self,block,cells,timer):
        if (pygame.time.get_ticks() - self._time > self._dropTime
            and self._landing == False):
            self._time = pygame.time.get_ticks()
            if(cells.checkCol(block)==False):
                block.y += 1
            else:
                self._landing = True
            if self._dropTime > 100 :
                self._dropTime -= self._increment
        elif (self._landing == True and pygame.time.get_ticks() -
              self._time > 300) :
            timer = 0
            self._landing = False
            if cells.checkCol(block) != False:
                block = cells.place(block)
            self._time = pygame.time.get_ticks()
        return block
