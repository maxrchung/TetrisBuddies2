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
        self.font = pygame.font.SysFont("ComicSans",21)
        self.col = 10
        self.row = 20
        self.sS = 32
        self.timer = 0
        self.grid = cells(self.col,self.row)
        self.opponentGrid = cells(self.col,self.row)
        self.current = self.grid.next.moveIn()
        self.grid.nextBlocks(self.current)
        self.quit = False
        self.playerName = self.font.render(Global.player.getName(), 1, (255,255,255))
        self.opponentName = self.font.render(Global.opponent.getName(), 1, (255,255,255))
        self.playernamelength = len(Global.player.getName())
        self.opponentnamelength = len(Global.opponent.getName())
        # initialize the pygame module
        pygame.init()

        # initialize soundmanager
        Global.SoundManager = soundmanager()

        # load and set the logo
        pygame.display.set_caption("TetrisBuddies")
        # create a surface on screen that has the size of 240 x 180
        self.screen = pygame.display.set_mode(((self.col*2+6)*self.sS,self.row*self.sS))
        # define a variable to control the main loop
        self.running = True
        self.keys = [False, False, False, False,False, False,False,False]
        # main loop
        self.grav = gravity(1000,5)
        self.saved = None

    def getGrid(self): return self.grid

    def setOpponentGrid(self, newGrid): self.opponentGrid = newGrid

    def update(self):
        self.timer += pygame.time.get_ticks()
        self.screen.fill((55,55,55)) #clear screen
        self.screen.blit(self.playerName, (5*self.sS - .5*self.playernamelength*7,self.sS))
        self.screen.blit(self.opponentName, (5*self.sS - .5*self.opponentnamelength*7,self.sS))
        bkg =pygame.image.load("MaxFaggotry.png")
        self.screen.blit(bkg,(self.col*self.sS,0))
        self.drawBlock(self.current) #draws current block
        self.drawGhost(self.current)
        self.drawBlock(self.grid.next)
        self.drawBlock(self.grid.next0)
        if(self.timer < 500):
            self.fadeInBlock(self.grid.next1, self.timer)
        else:
            self.drawBlock(self.grid.next1)
        if(self.saved!=None):
            self.drawBlock(self.saved)
        self.drawgrid(self.grid, 0)
        self.drawgrid(self.opponentGrid, 1)
        pygame.display.flip() #updates self.screen
    def drawBlock(self,blk):
        image = pygame.image.load(blk.image)
        image.set_alpha(255)
        for x in range(0,4):
            for y in range(0,4):
                if blk.array[x][y]:
                    self.screen.blit(image,((x+blk.x)*self.sS,(y+blk.y)*self.sS))
    def fadeInBlock(self,blk,time):
        image = pygae.image.load(blk.image)
        image.convert_alpha()
        image.set_alpha(int(time/2))
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
                Global.SoundManager.playsound('placed')
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

    def run(self):
        if self.quit:
            return
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key==pygame.K_t or event.key==pygame.K_z:
                    self.keys[0]=True
                elif event.key==pygame.K_s or event.key==pygame.K_DOWN:
                    self.keys[1]=True
                elif event.key==pygame.K_a or event.key==pygame.K_LEFT:
                    self.keys[2]=True
                elif event.key==pygame.K_d or event.key==pygame.K_RIGHT:
                    self.keys[3]=True
                elif event.key==pygame.K_w or event.key==pygame.K_UP:
                    self.keys[4]=True
                elif event.key==pygame.K_r:
                    self.keys[5]=True
                elif event.key==pygame.K_SPACE:
                    self.keys[6]=True
                elif event.key==pygame.K_c or event.key==pygame.K_LSHIFT:
                    self.keys[7]=True
            # only do something if the event is of type QUIT
            elif event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

        if self.keys[0]:
            if self.flipNudge(self.current,"R") != False:
                self.current.rotate('R')
            self.keys[0]=False
        elif self.keys[1]:
            if self.grid.checkCol(self.current)==False:
                self.current.y+=1
            else:
                self.grid.swapped = False
                self.current = self.grid.place(self.current)
                self.timer = 0
            self.keys[1]=False
        elif self.keys[2]:
            if (self.current.x+self.current.left()>0
                and self.sideCol(self.current, -1)==False):
                self.current.x-=1
            self.keys[2]=False
        elif self.keys[3]:
            if (self.current.x+self.current.right()+1<self.col
                and self.sideCol(self.current, 1)==False):
                self.current.x+=1
            self.keys[3]=False
        elif self.keys[4]:
            if self.flipNudge(self.current,"L") != False:
                self.current.rotate('L')
            self.keys[4]=False
        elif self.keys[5]:
            self.current = self.grid.next.moveIn()
            self.grid.next = block()
            self.grid.addLines(1)
            pygame.quit()
            self.quit=True
            return
            self.keys[5] = False
        elif self.keys[6]:
            self.current = self.hardDrop(self.current)
            self.grid.swapped = False
            self.keys[6]=False
        elif self.keys[7]:
            if self.saved == None:
                self.saved = self.current.save()
                self.current = self.grid.next.moveIn()
                self.grid.next = block()
                self.grid.swapped = True
                Global.SoundManager.playsound('switch')
            elif self.grid.swapped==False:
                temp = self.current
                self.current = self.saved.moveIn()
                self.current.x = 1
                self.current.y = 1
                self.saved = temp.save()
                self.grid.swapped = True
                Global.SoundManager.playsound('switch')
            self.keys[7]=False
        self.current = self.grav.fall(self.current,self.grid)
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


if __name__ == '__main__':    
    g = gameBoard()
    while True:
        g.run()

