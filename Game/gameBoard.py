# import the pygame module, so you can use it
import pygame
import block2
from block2 import block
from gravity2 import gravity
from cells import cells
import Global
import pickle
from Soundmanager import *

class gameBoard():
    def __init__(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("Comic Sans MS",32)
        self.fontBig = pygame.font.SysFont("Comic Sans MS",64)

        self.col = 10
        self.row = 20
        self.sS = 32
        self.timer = 0
        self.timer2 = 0
        self.timer3 = -1
        self.clock2 = pygame.time.Clock()
        self.pressed = False
        self.grid = cells(self.col,self.row)
        self.opponentGrid = cells(self.col,self.row)
        self.current = self.grid.next.moveIn()
        self.grid.nextBlocks(self.current)
        self.quit = False
        self.prevPos = []
        '''
        self.playerName = self.font.render(Global.player.getName(), 1, (255,255,255))
        self.opponentName = self.font.render(Global.opponent.getName(), 1, (255,255,255))
        self.playerNameWidth = self.playerName.get_rect().width
        self.opponentNameWidth = self.opponentName.get_rect().width
        '''
        self.playerName = self.font.render('Wax Chug the Gwad', 1, (255,255,255))
        self.opponentName = self.font.render(('name'), 1, (255,255,255))
        self.playerNameWidth = self.playerName.get_rect().width
        self.opponentNameWidth = self.opponentName.get_rect().width

        self.pressedClock = pygame.time.Clock()
        self.clock = pygame.time.Clock()
        self.clock3 = pygame.time.Clock()
        self.number_count=0
        # initialize the pygame module
        pygame.init()

        # initialize soundmanager
        Global.SoundManager = soundmanager()

        # load and set the logo
        pygame.display.set_caption("TetrisBuddies")
        # create a surface on screen that has the size of 240 x 180
        self.shakeScreen = pygame.display.set_mode(((self.col*2+6)*self.sS,self.row*self.sS))
        self.screen = self.shakeScreen.copy()
        # define a variable to control the main loop
        self.running = True
        self.keys = [False, False, False, False,False, False,False,False]
        # main loop
        self.grav = gravity(1000,5)
        self.saved = None

    def getPrevBlocks(self,blk):
        if len(self.prevPos) < 8:
            self.prevPos.append(blk.clone())
        else:
            del(self.prevPos[0])
            self.prevPos.append(blk.clone())

    def getGrid(self): return self.grid

    def setOpponentGrid(self, newGrid): self.opponentGrid = newGrid

    def update(self):
        background = pygame.image.load("background.png")
        self.screen.blit(background, (0,0))

        gridLines = pygame.image.load("grid.png")
        self.screen.blit(gridLines, (0,0))

        bkg =pygame.image.load("MaxFaggotry.png")
        self.screen.blit(bkg,(self.col*self.sS-64,0))
        for b in self.prevPos:
            self.fadeInBlock(b,50)
        self.drawBlock(self.current) #draws current block
        self.drawGhost(self.current)
        self.drawBlock(self.grid.next)
        self.drawBlock(self.grid.next0)
        self.screen.blit(self.playerName, (5*self.sS - 0.5*self.playerNameWidth,self.sS-6))
        self.screen.blit(self.opponentName, (21*self.sS - 0.5*self.opponentNameWidth,self.sS-6))
        
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
        
        boobs = pygame.image.load("boobs.png")
        self.screen.blit(boobs, (self.col*self.sS-64,0))
        
    def drawBlock(self,blk):
        image = pygame.image.load(blk.image)
        image.set_alpha(255)
        for x in range(0,4):
            for y in range(0,4):
                if blk.array[x][y]:
                    self.screen.blit(image,((x+blk.x)*self.sS,(y+blk.y)*self.sS))
    def fadeInBlock(self,blk,time):
        image = pygame.image.load(blk.image)
        image.convert_alpha()
        image.set_alpha(time/500 * 255)
        for x in range(0,4):
                for y in range(0,4):
                    if blk.array[x][y]:
                        self.screen.blit(image,((x+blk.x)*self.sS,(y+blk.y)*self.sS))
    def drawGhost(self,blk):
        image = pygame.image.load(blk.image)
        ghostBlock = blk.clone()
        image.convert_alpha()
        image.set_alpha(120)
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
                    image = pygame.image.load(grid.image[x][y])
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
                    if self.grid.filled[side+blk.x+a][blk.y+b]:
                        return True
        return False
    def flipNudge(self,blk, LR):
        if(blk._arrangement == block2.block_Sq):
            return False
        temp = blk.clone()
        temp.rotate(LR)
        if self.sideCol(temp,-1) == True and self.sideCol(temp,1) == True:
            return False
        while temp.x < 0:
            temp.x+=1
            blk.x+=1
        while (temp.right() == 3 and temp.x >6):
            blk.x -= 1
            temp.x -= 1
        for x in range(4):
            if temp.array[x]:
                if temp.x + x>self.col:
                    blk.x -= 1
                    temp.x -= 1
                    if temp.x +x> self.col:
                        blk.x
                        temp.x -= 1
                    if temp._arrangement == block2.block_S:
                        temp.x -= 1
        if self.sideCol(temp,0) == True:
            for x in range(4):
                for y in range(4):
                    if temp.array[x][y]:
                        if self.grid.filled[temp.x+x][temp.y+y]:
                            if x>1:
                                blk.x-=1
                            else:
                                blk.x+=1
        for a in range (4):
            for b in temp.bottom():
                if temp.array[a][b]:
                    if self.grid.filled[temp.x+a][temp.y + b]:
                        blk.y -= 1
                        break
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

        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            if(self.number_count>4000):
                if event.type == pygame.KEYDOWN:
                    if event.key==pygame.K_t or event.key==pygame.K_z:
                        self.keys[0]=True
                    elif event.key==pygame.K_w or event.key==pygame.K_UP:
                        self.keys[4]=True
                    if event.key==pygame.K_s or event.key==pygame.K_DOWN:
                        self.keys[1]=True
                    if event.key==pygame.K_SPACE:
                        self.keys[6]=True
                    if event.key==pygame.K_a or event.key==pygame.K_LEFT:
                        self.keys[2]=True
                    elif event.key==pygame.K_d or event.key==pygame.K_RIGHT:
                        self.keys[3]=True
                    if event.key==pygame.K_c or event.key==pygame.K_LSHIFT:
                        self.keys[7]=True
                    if event.key==pygame.K_r:
                        self.keys[5]=True
                if event.type == pygame.KEYUP:
                    self.pressed_time = 0 
                    if event.key==pygame.K_t or event.key==pygame.K_z:
                        self.keys[0]=False
                    elif event.key==pygame.K_w or event.key==pygame.K_UP:
                        self.keys[4]=False
                    if event.key==pygame.K_s or event.key==pygame.K_DOWN:
                        self.keys[1]=False
                    if event.key==pygame.K_SPACE:
                        self.keys[6]=False
                    if event.key==pygame.K_a or event.key==pygame.K_LEFT:
                        self.keys[2]=False
                    elif event.key==pygame.K_d or event.key==pygame.K_RIGHT:
                        self.keys[3]=False
                    if event.key==pygame.K_c or event.key==pygame.K_LSHIFT:
                        self.keys[7]=False
                    if event.key==pygame.K_r:
                        self.keys[5]=False
                # only do something if the event is of type QUIT
                if event.type == pygame.QUIT:
                    # change the value to False, to exit the main loop
                    running = False

        # Either flip right or left
        if self.keys[0]:
            if self.flipNudge(self.current,"R") != False:
                self.current.rotate('R')
            self.keys[0]=False
        elif self.keys[4]:
            if self.flipNudge(self.current,"L") != False:
                self.current.rotate('L')
            self.keys[4]=False

        if self.pressedClock.tick() > 50:
            if self.keys[1]:
                if self.grid.checkCol(self.current)==False:
                    self.current.y+=1
                else:
                    self.grid.swapped = False
                    self.current = self.grid.place(self.current)
                    self.timer = 0
            if self.keys[2]:
                if (self.current.x+self.current.left()>0
                    and self.sideCol(self.current, -1)==False):
                    self.current.x-=1
            elif self.keys[3]:
                if (self.current.x+self.current.right()+1<self.col
                    and self.sideCol(self.current, 1)==False):
                    self.current.x+=1
        if self.keys[5]:
            self.current = self.grid.next.moveIn()
            self.grid.next = block()
            self.grid.addLines(1)
            pygame.quit()
            self.quit=True
            return
            self.keys[5] = False

        # Space
        if self.keys[6]:
            self.current = self.hardDrop(self.current)
            self.grid.swapped = False
            self.keys[6]=False

        if self.keys[7]:
            if self.saved == None:
                self.saved = self.current.save()
                self.current = self.grid.next.moveIn()
                self.grid.next = block()
                self.grid.swapped = True
                Global.SoundManager.playsound('switch')
                self.timer2 = 0
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
                self.quit = True
                pygame.quit()
                Global.Game.setState('Result')
                response = ['PlayingLose']
                packet = pickle.dumps(response)
                Global.NetworkManager.getSocket().sendto(bytes(packet), (Global.opponent.getAddr(), 6969))
                
                print('You lost!')
                print()
                print('Switched state to Result')
                print('Instructions:')
                if Global.Game.getIsHost():
                    print("'Esc' to leave as host")
                else:
                    print("'c' to challenge host")
                    print("'l' to leave to lobby")
                return
        self.shakeScreen.fill((0,0,0))
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
    while True:
        g.run()

