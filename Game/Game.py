import Global
import pygame
import pickle
import msvcrt
from Player import *
from NetworkManager import NetworkManager
from gameBoard import *

'''
STATES
    NameSelection - Decide a name
    Lobby - Looking for available games
    Hosting - Hosting a room that is available for play
    Playing - Playing a game
    Results - After playing a game, wait in the room
'''

class Game:
    isHost = False
    isRunning = True
    roomList = []

    # Constructor
    def __init__(self):
        # Start off by looking for a game
        self.state = 'NameSelection'

    # initialize() is ran after the constructor because we may
    # need access to member variables that aren't constructed yet
    def initialize(self):
        Global.NetworkManager = NetworkManager()
        Global.player = Player()
        Global.opponent = Player()
        pygame.init()
        self.clock = pygame.time.Clock()
        self.connectionClock = pygame.time.Clock()

        # connectionTTL is a TTL timer
        # If it passes some limit without a response from the opponent
        # then it will kick the player out to Hosting or Lobby
        self.connectionTTL = 0

    # Accessors
    def getRoomList(self): return self.roomList
    def getState(self): return self.state
    def getIsRunning(self): return self.isRunning
    def getIsHost(self): return self.isHost

    # Setters
    def setState(self, newState): self.state = newState

    # Lets Game handle everything here
    def run(self):
        # Force game to run roughly at 60FPS
        self.clock.tick(60)

        while self.isRunning:
            self.update()
        
    def update(self):
        # Separation text
        print()
        print('---------------------------------------------------------------')
        print()

        # The first thing to do is give yourself a name
        if self.state == 'NameSelection':
            print('Welcome to TetrisBuddies!')
            name = input('To get started, enter a name: ')

            # Looks for available hosts
            response = ['LobbyRequest']
            packet = pickle.dumps(response)
            Global.NetworkManager.getSocket().sendto(bytes(packet), ('<broadcast>', 6969))


            Global.player.setName(name)
            print('Hello ' + Global.player.getName() + '!')
            print()
            print("Changed state to Lobby")
            print("Instructions:")
            print("'h' to host a room")
            print("'v' to view available rooms")
            print("'0', '1', '2', ... to join a room")
            
            self.state = 'Lobby'

        # If in lobby, then browse for games or become a host
        elif self.state == 'Lobby':
            key = input("Enter a command: ")
            print()
            
            # Become a host
            if key == 'h':
                self.state = 'Hosting'
                self.isHost = True

                print('You are now hosting a game')
                print()
                print("Changed state to Hosting")
                print("Instructions:")
                print("'Esc' to leave as host")

            # Look for rooms
            elif key == 'v':
                print('Rooms:')
                for roomIndex in range(len(self.roomList)):
                    print('Room', str(roomIndex), '-', self.roomList[roomIndex][0], '-', self.roomList[roomIndex][1])
                print()

                # Reset room list so we remove duplicates and offline players
                self.roomList = []

                response = ['LobbyRequest']
                packet = pickle.dumps(response)
                Global.NetworkManager.getSocket().sendto(bytes(packet), ('<broadcast>', 6969))
                # print('Broadcasted packet', response)

            # Else display instructions
            else:
                # Checks if the key is a number
                try:
                    roomIndex = int(key)
                except ValueError:
                    print("Invalid command")
                    print()
                    print("Instructions:")
                    print("'h' to host a room") 
                    print("'v' to view available rooms")
                    print("'0', '1', '2', ... to join a room number")
                    return

                # If it is then check if it is within range of the roomList
                if roomIndex in range(len(self.roomList)):
                    # room[0] returns the username of the host
                    # room[1] returns the Network IP address of the room
                    room = self.roomList[roomIndex]
                    Global.opponent.setName(room[0])
                    Global.opponent.setAddr(room[1])

                    # Block and wait for other side to respond
                    self.clock.tick()
                    timer = 0

                    response = ['LobbyChallenge', Global.player.getName()]
                    packet = pickle.dumps(response)

                    # Send a join request
                    Global.NetworkManager.getSocket().sendto(bytes(packet), (Global.opponent.getAddr(), 6969))
                    # print('Sent packet', response, Global.opponent.getAddr())

                    # Will poll for a message back, with a TTL of 5 seconds (5000 milliseconds)
                    while timer <= 10000:
                        timer += self.clock.tick()
                        while Global.NetworkManager.getMessageQueue():
                            Global.NetworkManager.getMessageLock().acquire()
                            data, addr = Global.NetworkManager.getMessageQueue().popleft()
                            Global.NetworkManager.getMessageLock().release()

                            command = data[0]

                            # If host rejects, then we just return to normal lobby activity
                            if command == 'HostingReject':
                                print('The host rejected your challenge')
                                print()
                                return
                            # Else we start playing the game
                            elif command == 'HostingAccept':
                                print('The host accepted your challenge')
                                print()

                                self.connectionClock.tick()
                                self.connectionTTL = 0
                                self.state = 'Playing'
                                Global.GameBoard = gameBoard()
                                return
                            else:
                                continue
                    
                    print('Challenge request timed out')

                else:
                    print('Invalid room number')

        # If hosting
        elif self.state == 'Hosting':
            print("Waiting for challenger... 'Esc' to leave")

            # Block until we retetceive a challengeRequest
            # The message thread will spit out an exception here that we
            # will then catch
            try:
                while True:
                    if msvcrt.kbhit():
                        ascii = ord(msvcrt.getch())

                        # Escape key
                        if ascii == 27:
                            self.state = 'Lobby'
                            self.isHost = False
                                    
                            print('You left as host')
                            print()
                            print("Changed state to Lobby")
                            print("Instructions:")
                            print("'h' to host a room")
                            print("'v' to view available rooms")
                            print("'0', '1', '2', ... to join a room number")
                            return

            except KeyboardInterrupt:
                validInput = False

                data = None
                addr = None

                # Block until we get the right message in the queue
                while Global.NetworkManager.getMessageQueue():
                    Global.NetworkManager.getMessageLock().acquire()
                    data, addr = Global.NetworkManager.getMessageQueue().popleft()
                    Global.NetworkManager.getMessageLock().release()

                    command = data[0]

                    if not command == 'LobbyChallenge':
                        continue
                    else:
                        break

                while not validInput:
                    response = input('Accept challenge by ' + data[1] + ' (y/n)? ')
                    if response == 'y':
                        validInput = True
                        response = ['HostingAccept']
                        packet = pickle.dumps(response)
                        Global.NetworkManager.getSocket().sendto(bytes(packet), addr)
                        # print('Sent packet', response, addr[0])

                        self.connectionClock.tick()
                        self.connectionTTL = 0
                        self.state = 'Playing'
                        Global.GameBoard = gameBoard()
                        Global.opponent.setName(data[1])
                        Global.opponent.setAddr(addr[0])

                    elif response == 'n':
                        validInput = True
                        response = ['HostingReject']
                        packet = pickle.dumps(response)
                        Global.NetworkManager.getSocket().sendto(bytes(packet), addr)
                        # print('Sent packet', response, addr[0])

        elif self.state == 'Playing':
            # Every loop we check and see if we are still in communication with opponent
            self.connectionTTL += self.connectionClock.tick()

            # If we aren't, then change our state after 10 seconds depending if we are a host
            if self.connectionTTL >= 5000:
                self.connectionTTL = 0
                if self.isHost:
                    pygame.quit()
                    self.state = 'Hosting'
                    print('Lost connection with challenger')
                    print()
                    print('Changed state to Hosting')
                    print("Instructions:")
                    print("'Esc' to leave as host")
                else:
                    pygame.quit()
                    self.state = 'Lobby'
                    print('Lost connection with host')
                    print()
                    print('Changed state to Lobby')
                    print("Instructions:")
                    print("'h' to host a room")
                    print("'v' to view available rooms")
                    print("'0', '1', '2', ... to join a room number")

            # If playing, continuously send information to other person
            # TODO: Send gameboard
            response = ['PlayingUpdate', Global.GameBoard.getGrid()]
            packet = pickle.dumps(response)
            Global.NetworkManager.getSocket().sendto(bytes(packet), (Global.opponent.getAddr(), 6969))
            # print('Sent packet', response, Global.opponent.getAddr())

            Global.GameBoard.run()

            # If we have a PlayingWin or PlayingLose message, then we deal with it here
            while Global.NetworkManager.getMessageQueue():
                Global.NetworkManager.getMessageLock().acquire()
                data, addr = Global.NetworkManager.getMessageQueue().popleft()
                Global.NetworkManager.getMessageLock().release()

                command = data[0]

                # TODO: Within the game code, set Game.state = "Result"

                if command == 'PlayingLose':
                    pygame.quit()
                    self.state = 'Result'
                    print('You won!')
                    print()
                    print('Switched state to Result')
                    print('Instructions:')
                    if self.isHost:
                        print("'Esc' to leave as host")
                    else:
                        print("'c' to challenge host")
                        print("'l' to leave to lobby")
                    return

        elif self.state == 'Result':
            if self.isHost:
                print("Waiting for challenger... 'Esc' to leave")

                # Block until we receive a challengeRequest
                # The message thread will spit out an exception here that we
                # will then catch
                try:
                    while True:
                        if msvcrt.kbhit():
                            ascii = ord(msvcrt.getch())

                            # Escape key
                            if ascii == 27:
                                self.state = 'Lobby'
                                self.isHost = False
                                    
                                print('You left as host')
                                print()
                                print("Changed state to Lobby")
                                print("Instructions:")
                                print("'h' to host a room")
                                print("'v' to view available rooms")
                                print("'0', '1', '2', ... to join a room number")

                                return

                except KeyboardInterrupt:
                    validInput = False

                    data = None
                    addr = None

                    # Block until we get the right message in the queue
                    while Global.NetworkManager.getMessageQueue():
                        Global.NetworkManager.getMessageLock().acquire()
                        data, addr = Global.NetworkManager.getMessageQueue().popleft()
                        Global.NetworkManager.getMessageLock().release()

                        command = data[0]

                        if not command == 'ResultChallenge':
                            continue
                        else:
                            break

                    while not validInput:
                        response = input('Accept challenge by ' + data[1] + ' (y/n)? ')
                        if response == 'y':
                            validInput = True
                            response = ['ResultAccept']
                            packet = pickle.dumps(response)
                            Global.NetworkManager.getSocket().sendto(bytes(packet), addr)
                            # print('Sent packet', response, addr[0])

                            self.connectionClock.tick()
                            self.connectionTTL = 0
                            self.state = 'Playing'
                            Global.GameBoard = gameBoard()
                            Global.opponent.setName(data[1])
                            Global.opponent.setAddr(addr[0])

                        elif response == 'n':
                            validInput = True
                            response = ['ResultReject']
                            packet = pickle.dumps(response)
                            Global.NetworkManager.getSocket().sendto(bytes(packet), addr)
                            # print('Sent packet', response, addr[0])

            else:
                key = input("Enter a command: ")
                print()
                
                # Challenge host
                if key == 'c':
                    # Block and wait for other side to respond
                    self.clock.tick()
                    timer = 0

                    response = ['ResultChallenge', Global.player.getName()]
                    packet = pickle.dumps(response)
                    Global.NetworkManager.getSocket().sendto(bytes(packet), (Global.opponent.getAddr(), 6969))
                    # print('Sent packet', response, Global.opponent.getAddr())

                    # Will poll for a message back, with a TTL of 5 seconds (5000 milliseconds)
                    while timer <= 5000:
                        timer += self.clock.tick()
                        while Global.NetworkManager.getMessageQueue():
                            Global.NetworkManager.getMessageLock().acquire()
                            data, addr = Global.NetworkManager.getMessageQueue().popleft()
                            Global.NetworkManager.getMessageLock().release()

                            command = data[0]

                            # If host rejects
                            if command == 'ResultReject':
                                print('The host rejected your challenge')
                                print()
                                return
                            # Else we start playing the game
                            elif command == 'ResultAccept':
                                print('The host accepted your challenge')
                                print()

                                self.connectionClock.tick()
                                self.connectionTTL = 0
                                self.state = 'Playing'
                                Global.GameBoard = gameBoard()
                                return
                            else:
                                continue

                    print('Challenge request timed out')
               
                elif key == 'l':
                    self.state = 'Lobby'
                    
                    print('You left the room')
                    print()
                    print('Changed state to Lobby')
                    print("Instructions:")
                    print("'h' to host a room")
                    print("'v' to view available rooms")
                    print("'0', '1', '2', ... to join a room number")

                else:
                    print('Invalid command')
                    print()
                    print("Instructions:")
                    print("'c' to challenge host")
                    print("'l' to leave to lobby")
