import pygame

class gravity:
    def __init__(self,acc,inc):
        self._time = pygame.time.get_ticks()
        self._dropTime = acc
        self._increment = inc
        
    def fall(self,block,cells):
        if pygame.time.get_ticks() - self._time > self._dropTime:
            if(cells.checkCol(block)==False):
                block.y += 1
            else:
                block=cells.place(block)
            self._time = pygame.time.get_ticks()
            if self._dropTime > 300 :
                self._dropTime -= self._increment
        return block   