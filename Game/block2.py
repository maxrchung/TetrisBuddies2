import random
import pygame

class block:
    def __init__(self):
        '''initializes a random block at a specific position x,y,
        randomizes which "block" as well as which rotation state it begins in'''
        self.x = 11
        self.y = 2
        self.state = random.randint(0,3)
        r =  random.randint(0,6)
        if r == 0:
            self._arrangement = block_T
        if r == 1:
            self._arrangement = block_LL
        if r == 2:
            self._arrangement = block_LR
        if r == 3:
            self._arrangement = block_ZL
        if r == 4:
            self._arrangement = block_ZR
        if r == 5:
            self._arrangement = block_S
        if r == 6:
            self._arrangement = block_Sq
        self.image = (r)
        self.array = self._arrangement(self.state)
    def moveIn(self):
        self.x = 3
        self.y = 0
        return self
    def clone(self):
        c = block()
        c.array = self._arrangement(self.state)
        c.x = self.x
        c.y = self.y
        c.image = self.image
        c.state = self.state
        c._arrangement = self._arrangement
        return c
    def save(self):
        self.x = 11
        self.y = 16
        return self
    def rotate(self,LR):
        if LR == 'L':
            if self.state > 0:
                self.state -= 1
                
            else:
                self.state = 3
            self.array = self._arrangement(self.state)
        if LR == 'R':
            if self.state < 3:
                self.state += 1
                
            else:
                self.state = 0
            self.array = self._arrangement(self.state)
    
    def left(self):
        for a in range (0,4):
            for b in range(0,4):
                if self.array[a][b]:
                    return a    
    def right(self):
        a = 3
        while a>-1:
            for b in range(0,4):
                if self.array[a][b]:
                    return a
            a-=1
    def bottom(self):
        bottoms = []
        max = -1
        for a in range(0,4):
            for b in range(0,4):
                if self.array[a][b]:
                    if max < b:
                        max = b
            bottoms.append(max)
            max = -1
        return bottoms
                
        

def block_T(state):
    if state == 0:
        block_T0 = [
         [0,1,0,0]
        ,[0,1,1,0]
        ,[0,1,0,0]
        ,[0,0,0,0]]
        return block_T0
    if state == 1:
        block_T1 = [
         [0,0,0,0]
        ,[1,1,1,0]
        ,[0,1,0,0]
        ,[0,0,0,0]]
        return block_T1
    if state == 2:
        block_T2 = [
         [0,1,0,0]
        ,[1,1,0,0]
        ,[0,1,0,0]
        ,[0,0,0,0]]
        return block_T2
    if state == 3:
        block_T3 = [
         [0,1,0,0]
        ,[1,1,1,0]
        ,[0,0,0,0]
        ,[0,0,0,0]]
        return block_T3
        
def block_LL(state):
    if state == 0:
        block_LL0 = [
         [0,1,0,0]
        ,[0,1,0,0]
        ,[0,1,1,0]
        ,[0,0,0,0]]
        return block_LL0
    if state == 1:
        block_LL1 = [
         [0,0,0,0]
        ,[1,1,1,0]
        ,[1,0,0,0]
        ,[0,0,0,0]]
        return block_LL1
    if state == 2:
        block_LL2 = [
         [1,1,0,0]
        ,[0,1,0,0]
        ,[0,1,0,0]
        ,[0,0,0,0]]
        return block_LL2
    if state == 3:
        block_LL3 = [
         [0,0,1,0]
        ,[1,1,1,0]
        ,[0,0,0,0]
        ,[0,0,0,0]]
        return block_LL3
        
def block_LR(state):
    if state == 0:
        block_LR0 = [
         [0,1,0,0]
        ,[0,1,0,0]
        ,[1,1,0,0]
        ,[0,0,0,0]]
        return block_LR0
    if state == 1:
        block_LR1 = [
         [1,0,0,0]
        ,[1,1,1,0]
        ,[0,0,0,0]
        ,[0,0,0,0]]
        return block_LR1
    if state == 2:
        block_LR2 = [
         [0,1,1,0]
        ,[0,1,0,0]
        ,[0,1,0,0]
        ,[0,0,0,0]]
        return block_LR2
    if state == 3:
        block_LR3 = [
         [0,0,0,0]
        ,[1,1,1,0]
        ,[0,0,1,0]
        ,[0,0,0,0]]
        return block_LR3

def block_ZL(state):
    if state == 0:
        block_ZL0 = [
         [1,1,0,0]
        ,[0,1,1,0]
        ,[0,0,0,0]
        ,[0,0,0,0]]
        return block_ZL0
    if state == 1:
        block_ZL1 = [
         [0,0,1,0]
        ,[0,1,1,0]
        ,[0,1,0,0]
        ,[0,0,0,0]]
        return block_ZL1
    if state == 2:
        block_ZL2 = [
         [0,0,0,0]
        ,[1,1,0,0]
        ,[0,1,1,0]
        ,[0,0,0,0]]
        return block_ZL2
    if state == 3:
        block_ZL3 = [
         [0,1,0,0]
        ,[1,1,0,0]
        ,[1,0,0,0]
        ,[0,0,0,0]]
        return block_ZL3
    
def block_ZR(state):
    if state == 0:
        block_ZR0 = [
         [0,1,1,0]
        ,[1,1,0,0]
        ,[0,0,0,0]
        ,[0,0,0,0]]
        return block_ZR0
    if state == 1:
        block_ZR1 = [
         [0,1,0,0]
        ,[0,1,1,0]
        ,[0,0,1,0]
        ,[0,0,0,0]]
        return block_ZR1
    if state == 2:
        block_ZR2 = [
         [0,0,0,0]
        ,[0,1,1,0]
        ,[1,1,0,0]
        ,[0,0,0,0]]
        return block_ZR2
    if state == 3:
        block_ZR3 = [
         [1,0,0,0]
        ,[1,1,0,0]
        ,[0,1,0,0]
        ,[0,0,0,0]]
        return block_ZR3
    
def block_S(state):
    if state == 0:
        block_S0 = [
         [0,1,0,0]
        ,[0,1,0,0]
        ,[0,1,0,0]
        ,[0,1,0,0]]
        return block_S0
    if state == 1:
        block_S1 = [
         [0,0,0,0]
        ,[1,1,1,1]
        ,[0,0,0,0]
        ,[0,0,0,0]]
        return block_S1
    if state == 2:
        block_S2 = [
         [0,0,1,0]
        ,[0,0,1,0]
        ,[0,0,1,0]
        ,[0,0,1,0]]
        return block_S2
    if state == 3:
        block_S3 = [
         [0,0,0,0]
        ,[0,0,0,0]
        ,[1,1,1,1]
        ,[0,0,0,0]]
        return block_S3

def block_Sq(state):
    block_Sq = [
     [1,1,0,0]
    ,[1,1,0,0]
    ,[0,0,0,0]
    ,[0,0,0,0]]
    return block_Sq
