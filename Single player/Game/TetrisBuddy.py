# import the pygame module, so you can use it
import pygame
import block2
from block2 import block
from gravity2 import gravity
from cells import cells
from Soundmanager import *
from random import randint
import Global

class gameBoard():
    def __init__(self):
        # initialize the pygame module
        pygame.init()

        pygame.font.init()
        self.font = pygame.font.SysFont("Comic Sans MS",32)
        self.fontBig = pygame.font.SysFont("Comic Sans MS",64)

        self.running = True

        self.col = 10
        self.row = 20
        self.sS = 32
        self.timer = 0
        self.timer2 = 0
        self.timer3 = -1
        self.clock2 = pygame.time.Clock()
        self.grid = cells(self.col,self.row)
        self.opponentGrid = cells(self.col,self.row)
        self.current = self.grid.next.moveIn()
        self.grid.next = None
        self.grid.nextBlocks(self.current)
        self.quit = False
        self.prevPos = []
        

        self.playerName = self.font.render('You', 1, (255,255,255))
        self.opponentName = self.font.render((''), 1, (255,255,255))
        self.playerNameWidth = self.playerName.get_rect().width
        self.opponentNameWidth = self.opponentName.get_rect().width

        self.clock = pygame.time.Clock()
        self.clock3 = pygame.time.Clock()
        self.number_count=0

        # Limiting how fast press can go
        self.pressedTimer = 0
        self.pressedClock = pygame.time.Clock()

        # initialize soundmanager
        Global.SoundManager = soundmanager()

        # load and set the logo
        pygame.display.set_caption("TetrisBuddy")
        # create a surface on screen that has the size of 240 x 180
        self.shakeScreen = pygame.display.set_mode(((self.col+6)*self.sS,self.row*self.sS))
        self.screen = self.shakeScreen.copy()
        # define a variable to control the main loop
        self.running = True
        self.keys = [False, False, False, False,False, False,False,False]
        # main loop
        self.grav = gravity(1050)
        self.saved = None

        self.background = pygame.image.load('background.png')
        self.gridLines = pygame.image.load("grid.png")
        self.bkg =pygame.image.load("MaxFaggotry.png")
        self.boobs = pygame.image.load("boobs.png")

        self.blockImages = []
        for x in range(8):
            self.blockImages.append(pygame.image.load('block'+str(x)+'.png'))

    def getPrevBlocks(self,blk):
        if len(self.prevPos) < 8:
            self.prevPos.append(blk.clone())
        else:
            del(self.prevPos[0])
            self.prevPos.append(blk.clone())

    def getGrid(self): return self.grid

    def setOpponentGrid(self, newGrid): self.opponentGrid = newGrid

    def update(self):
        self.screen.blit(self.background, (0,0))
        self.screen.blit(self.gridLines, (0,0))
        self.screen.blit(self.bkg,(self.col*self.sS-64,0))
        for b in self.prevPos:
            self.fadeInBlock(b,50)
        self.drawBlock(self.current) #draws current block
        self.drawGhost(self.current)
        self.drawBlock(self.grid.next)
        self.drawBlock(self.grid.next0)
        self.screen.blit(self.playerName, (5*self.sS - 0.5*self.playerNameWidth,self.sS-8))
        self.screen.blit(self.opponentName, (21*self.sS - 0.5*self.opponentNameWidth,self.sS-8))
        
        score = self.font.render(str(self.grid.getScore()), 1, (255,255,255))
        self.screen.blit(score, (5*self.sS - score.get_rect().width/2, 2*self.sS))

        if(self.timer < 500):
            self.timer += self.clock.tick()
            self.fadeInBlock(self.grid.next1, self.timer)
        else:
            self.drawBlock(self.grid.next1)
        if self.saved != None:
            if(self.timer2 < 500):
                self.timer2 += self.clock2.tick()
                self.fadeInBlock(self.saved, self.timer2)
            else:
                self.drawBlock(self.saved)
        self.clock.tick()
        self.clock2.tick()
        self.drawgrid(self.grid, 0)
        self.drawgrid(self.opponentGrid, 1)

        self.screen.blit(self.boobs, (self.col*self.sS-64,0))
        
    def drawBlock(self,blk):
        image = self.blockImages[blk.image]
        image.set_alpha(255)
        for x in range(0,4):
            for y in range(0,4):
                if blk.array[x][y]:
                    self.screen.blit(image,((x+blk.x)*self.sS,(y+blk.y)*self.sS))
    def fadeInBlock(self,blk,time):
        image = self.blockImages[blk.image]
        image.convert_alpha()
        image.set_alpha(time/500 * 255)
        for x in range(0,4):
                for y in range(0,4):
                    if blk.array[x][y]:
                        self.screen.blit(image,((x+blk.x)*self.sS,(y+blk.y)*self.sS))
    def drawGhost(self,blk):
        image = self.blockImages[blk.image]
        ghostBlock = blk.clone()
        image.convert_alpha()
        image.set_alpha(80)
        while 1:
            if self.grid.checkCol(ghostBlock):
                break
            else:
                ghostBlock.y += 1
        for x in range(0,4):
            for y in range(0,4):
                if ghostBlock.array[x][y]:
                    self.screen.blit(image,((x+ghostBlock.x)*self.sS,(ghostBlock.y+y)*self.sS))
    def drawgrid(self,grid,isOpponent):
        for x in range (self.col):
            for y in range(self.row+1):
                if grid.filled[x][y]:
                    image = self.blockImages[grid.image[x][y]]
                    image.set_alpha(255)
                    if isOpponent:
                        self.screen.blit((image),((x+self.col+6)*self.sS,y*self.sS))
                    else:
                        self.screen.blit((image),(x*self.sS,y*self.sS))
    def hardDrop(self,blk):
        while 1:
            if(self.grid.checkCol(blk)):
                blk = self.grid.place(blk)
                self.timer = 0
                return blk
            blk.y+=1
    def sideCol(self,blk,side):
        for a in range (4):
            for b in range (4):
                if blk.array[a][b]:
                    try:
                        if self.grid.filled[side+blk.x+a][blk.y+b]:
                            return True
                    except(IndexError):
                        return True
        return False
    def flipNudge(self,blk, LR):
        if(blk._arrangement == block2.block_Sq):
            return False
        nudgex = 0
        temp = blk.clone()
        temp.rotate(LR)
        if self.sideCol(temp,-1) == True and self.sideCol(temp,1) == True:
            return False
        while temp.x < 0:
            temp.x+=1
            nudgex+=1
        while (temp.right() == 3 and temp.x >6):
            nudgex -= 1
            temp.x -= 1
        for x in range(4):
            if temp.array[x]:
                if temp.x + x>self.col:
                    nudgex -= 1
                    temp.x -= 1
                    if temp.x +x> self.col:
                        nudgex -= 1
                        temp.x -= 1
                    if temp._arrangement == block2.block_S:
                        temp.x -= 1
        if self.sideCol(temp,0) == True:
            for x in range(4):
                for y in range(4):
                    if temp.array[x][y]:
                        if self.grid.filled[temp.x+x][temp.y+y]:
                            if x>1:
                                nudgex-=1
                                temp.x-=1
                            else:
                                nudgex+=1
                                temp.x+=1
        for a in range (4):
            for b in temp.bottom():
                if temp.array[a][b]:
                    if self.grid.filled[temp.x+a][temp.y + b]:
                        blk.y -= 1
                        break
        if self.sideCol(temp,-1) == True and self.sideCol(temp,1) == True:
            return False
        for x in range(4):
            for y in range(4):
                if temp.array[x][y]:
                    if temp.x+x < 0:
                        return False
                    if temp.x+x > self.col:
                        return False
                    try:
                        if self.grid.filled[temp.x+x][temp.y+y]:
                            pass
                    except(IndexError):
                        return False
        blk.x += nudgex
        return True

    def drawNumber(self,n):
        # print("dolan")
        if(n == 0):
            go = self.fontBig.render('GO!', 1, (255,255,255))
            self.screen.blit(go,(5*self.sS - go.get_rect().width/2,10*self.sS-go.get_rect().height/2 - 1))
            return
        countdown = self.fontBig.render(str(n), 1, (255,255,255))
        self.screen.blit(countdown,(5*self.sS - countdown.get_rect().width/2,10*self.sS-countdown.get_rect().height/2 - 1))
    def run(self):
        if self.quit:
            return

        self.grav.increase(self.grid.clears)

        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            if(self.number_count>4000):
                if event.type == pygame.KEYDOWN:
                    self.pressedTimer = 96
                    if event.key==pygame.K_t or event.key==pygame.K_z:
                        self.keys[0]=True
                    elif event.key==pygame.K_w or event.key==pygame.K_UP:
                        self.keys[4]=True
                    elif event.key==pygame.K_s or event.key==pygame.K_DOWN:
                        self.keys[1]=True
                    elif event.key==pygame.K_SPACE:
                        self.keys[6]=True
                    elif event.key==pygame.K_a or event.key==pygame.K_LEFT:
                        self.keys[2]=True
                    elif event.key==pygame.K_d or event.key==pygame.K_RIGHT:
                        print()
                        self.keys[3]=True
                    elif event.key==pygame.K_c or event.key==pygame.K_LSHIFT:
                        self.keys[7]=True
                elif event.type == pygame.KEYUP:
                    self.pressedTimer = 96
                    if event.key==pygame.K_t or event.key==pygame.K_z:
                        self.keys[0]=False
                    elif event.key==pygame.K_w or event.key==pygame.K_UP:
                        self.keys[4]=False
                    elif event.key==pygame.K_s or event.key==pygame.K_DOWN:
                        self.keys[1]=False
                    elif event.key==pygame.K_SPACE:
                        self.keys[6]=False
                    elif event.key==pygame.K_a or event.key==pygame.K_LEFT:
                        self.keys[2]=False
                    elif event.key==pygame.K_d or event.key==pygame.K_RIGHT:
                        self.keys[3]=False
                    elif event.key==pygame.K_c or event.key==pygame.K_LSHIFT:
                        self.keys[7]=False
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                self.running = False

        # Either flip right or left
        if self.keys[0]:
            if self.flipNudge(self.current,"R") != False:
                self.current.rotate('R')
                self.keys[0]=False
        elif self.keys[4]:
            if self.flipNudge(self.current,"L") != False:
                self.current.rotate('L')
                self.keys[4]=False

        self.pressedTimer += self.pressedClock.tick()
        if self.pressedTimer >= 69:
            if self.keys[1]:
                if self.grid.checkCol(self.current)==False:
                    self.current.y+=1
                    self.pressedTimer = 0
                else:
                    #self.grid.swapped = False
                    #self.current = self.grid.place(self.current)
                    #self.timer = 0
                    self.current = self.grav.fall(self.current,self.grid,self.timer)
                    self.pressedTimer = 0
            if self.keys[2]:
                if self.current.x+self.current.left()>0 and self.sideCol(self.current, -1)==False:
                    self.current.x-=1
                    self.pressedTimer = 0
            elif self.keys[3]:
                if self.current.x+self.current.right()+1<self.col and self.sideCol(self.current, 1)==False:
                    self.current.x+=1
                    self.pressedTimer = 0

        # Space
        if self.keys[6]:
            self.current = self.hardDrop(self.current)
            self.grid.swapped = False
            self.keys[6]=False

        if self.keys[7]:
            if self.saved == None:
                self.saved = self.current.save()
                self.current = self.grid.next.moveIn()
                self.grid.nextBlocks(self.current)
                self.grid.swapped = True
                Global.SoundManager.playsound('switch')
                self.timer2 = 0
                self.keys[7]=False
            elif self.grid.swapped==False:
                temp = self.current
                self.current = self.saved.moveIn()
                self.current.x = 1
                self.current.y = 1
                self.saved = temp.save()
                self.grid.swapped = True
                Global.SoundManager.playsound('switch')
                self.timer2 = 0
                self.keys[7]=False
        self.number_count += self.clock3.tick()

        # print(self.number_count)
        if(self.number_count<4000):
            # print('dolan')
            self.update()
            self.font = pygame.font.SysFont("Comic Sans MS",51)
            self.drawNumber(3-int(self.number_count/1000))
            self.font = pygame.font.SysFont("Comic Sans MS",21)
            
        else:
            self.current = self.grav.fall(self.current,self.grid,self.timer)
            self.getPrevBlocks(self.current)
            self.update()
        
    
            if self.grid.lose:
                self.__init__()
        if self.grid.shake == True:
            if self.timer3 == -1:
                self.timer3 = 4
            elif self.timer3 > 1:
                self.timer3 -= 1
            else:
                self.timer3 = -1
                self.grid.shake = False
            self.shakeScreen.blit(self.screen, (randint(-20,20),randint(-20,20)))
        else:
             self.shakeScreen.blit(self.screen, (0,0))
        pygame.display.flip() #updates self.screen


if __name__ == '__main__':    
    g = gameBoard()
    while g.running:
        g.run()

