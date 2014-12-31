import pygame
import random
from block2 import block
import Global

class cells:
    def __init__(self,col,row):
        self.score = 0
        self.col = col
        self.row = row
        self.lose = False
        self.next = block()
        self.next0 = None
        self.next1 = None
        self.swapped = False
        image = 7
        self.default = image
        self.filled = [[0 for x in range(row+1)] for x in range(col+1)]
        self.image = [[image for x in range(row +1)]for x in range(col+1)]
        self.shake = False
        for x in range(col+1):
            self.filled[x][row]=1
    def rowFilled(self):
        lines_cleared = 0
        for y in range (self.row):
            clear = True
            for x in range(self.col):
                if self.filled[x][y]!=1:
                    clear = False
                if x == self.col-1 and clear:
                    self.score+=1337
                    self.clear(y)
                    lines_cleared+=1
        
        # Play sound if cleared lines
        if lines_cleared >= 4: # I mean... better safe than sorry
            Global.SoundManager.playsound('fourline')
        elif lines_cleared >= 1:
            Global.SoundManager.playsound('singleline')

    def addLines(self,n):
        for a in range(n):
            r = random.randint(0,self.col-1)
            for b in range (self.row):
                for x in range(self.col):
                    self.filled[x][b]=self.filled[x][b+1]
                    self.image[x][b]=self.image[x][b+1]
                    if b == self.row-1:
                        self.image[x][b]=self.default
                    if b == self.row-1 and x == r:
                        self.filled[x][b] = 0
        self.shake = True
        # Play sound
        Global.SoundManager.playsound('youfail')
    
    def nextBlocks(self,blk):
        if self.next == None:
                self.next = block()
                while self.next._arrangement == blk._arrangement:
                    self.next = block()
        else:
            self.next = self.next0
        self.next.x = 11
        self.next.y = 1
        if self.next0 == None:
                self.next0 = block()
                while self.next0._arrangement == self.next._arrangement:
                    self.next0 = block()
        else:
            self.next0 = self.next1
        self.next0.x = 11
        self.next0.y = 6
        self.next1 = block()
        while self.next1._arrangement == self.next0._arrangement:
            self.next1 = block()
        self.next1.x = 11
        self.next1.y = 11
                        
    def place(self,blk):
        Global.SoundManager.playsound('placed')
        self.swapped = False
        for x in range(0,4):
            for y in range(0,4):
                if blk.array[x][y]:
                    self.filled[blk.x+x][blk.y+y]=1
                    self.image[blk.x+x][blk.y+y]=blk.image
        self.rowFilled()
        blk = self.next.moveIn()
        self.nextBlocks(blk)

        for x in range (self.col):
            if(self.filled[x][1]):
                self.lose = True
        return blk
    def checkCol(self,blk):
        for y in range(self.row+1):
            for x in range(4):
                if blk.bottom()[x]!=-1:
                    try:
                        if self.filled[blk.x+x][blk.y+blk.bottom()[x]+1]:
                            return True
                    except(IndexError):
                        return True
        return False     
    def clear(self,y):
        for x in range(self.col+1):
            self.filled[x][y] = 0
            self.image[x][y] = self.default
        for b in range (y,0,-1):
            for x in range(self.col+1):
                self.filled[x][b]=self.filled[x][b-1]
                self.image[x][b]=self.image[x][b-1]
                    
