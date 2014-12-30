import threading
import Global
import pickle # pickle is used to package objects to be sent through sockets
import _thread
from collections import deque
from socket import *

'''
PACKET

data[0] = command
    PlayingUpdate - Tells the receiver the sending player's gameboard info
    PlayingLine - Tells the receiver to add a line to gameboard
    PlayingLose - Tells the receiver that the sender lost

    HostingInfo - Gives the receiver the sender's username info

    LobbyRequest - Tells the host receiver to give the sender info
    LobbyChallenge - Tells the host receiver that the sender is attempting to join

    HostingAccept - Tells the joining receiver that the host accepted challenge
    HostingReject - Tells the joining receiver that the host rejected challenge

    ResultChallenge - Tells the host receiver that the sender is attempting to challenge again
    ResultAccept - Tells the challenging receiver that the host accepted challenge
    ResultReject - Tells the challenging receiver that the host rejected challenge
'''

# Handles basically all the networking things
class NetworkManager:

    # Constructor
    def __init__(self):
        # Socket for sending and receiving data
        self.socket = socket(AF_INET, SOCK_DGRAM)

        # Gets the IP address of person running this program
        self.host = gethostbyname(gethostname())

        # Setting some more specific socket options so that
        # we can broadcast messages to all celients in the LAN
        self.socket.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

        # Allows us to reuse an address, not entirely sure if needed
        # but probably safer to do so then not
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        # bind() tells the socket to receive messages on port 6969
        self.socket.bind((self.host, 6969))

        # The socket will receive messages and put them into this queue
        # The queue will then be popped off and the messages will be
        # responded to one by one
        self.messageQueue = deque()

        # Used for locking the messageQueuing so there are no synchronization
        # issues between threads
        self.messageLock = threading.Lock()

        # Starts the message thread
        # The parameter is target= because we are skipping the first argument
        # of the thread constructor and setting the second one directly
        self.messageThread = threading.Thread(target=self.checkForMessages)
        # Daemon tells the thread that it should stop if the main program stops
        self.messageThread.daemon = True
        self.messageThread.start()

    def getSocket(self): return self.socket
    def getMessageQueue(self): return self.messageQueue
    def getMessageLock(self): return self.messageLock

    # Disconnect networking elements
    def disconnect(self):
        # Send a disconnect packet to yourself
        response = ['Disconnect']
        packet = pickle.dumps(response)
        self.socket.sendto(bytes(packet), (self.host, 6969))

        # Wait until the messageThread is finished
        self.messageThread.join()

    # Receives packets(messages) and puts them into queue
    def checkForMessages(self):
        while Global.Game.getIsRunning():
            # recvfrom() will block the application until it receives a packet
            # The 4096 indicates that the socket will receive up to 4096 bytes
            # data is what the socket received
            # addr is where the information came from
            pickledData, addr = self.socket.recvfrom(4096)
            data = pickle.loads(pickledData)

            command = data[0]

            if command == 'Disconnect':
                self.socket.shutdown(SHUT_RDWR)
                self.socket.close()

            # Skip over packets if we have the same addresses
            if self.host == addr[0]:
                continue

            # Enable this line for debugging info on received packets
            # Be careful though, as because this is ran on a different 
            # thread, information could be printed out of nowhere and mess
            # up your current console input/display
            # print('Received packet:', data, addr)

            # Remember to lock so that we don't run into conflict accessing it
            self.messageLock.acquire()

            # These need to be check within the checkForMessages() thread because
            # they need to be responded immediately. If we put these sections in
            # the main thread they may get blocked when the Game() update() is waiting 
            # for input                
            # If new hosting info comes in
            if command == 'HostingInfo':
                # If the current player is waiting in the Lobby
                if Global.Game.getState() == 'Lobby':
                    # Add username to the list of rooms
                    Global.Game.getRoomList().append((data[1], addr[0]))

            # If he gets a request for information then send it
            elif command == 'LobbyRequest':
                # If the current player is hosting
                if Global.Game.getState() == 'Hosting':
                    response = ['HostingInfo', Global.player.getName()]
                    packet = pickle.dumps(response)
                    self.socket.sendto(bytes(packet), addr)
                    # print('Sent packet:', response, addr)

            # If he gets a join request, then move to challenge
            elif command == 'LobbyChallenge':
                # If the current player is hosting
                if Global.Game.getState() == 'Hosting':
                    self.messageQueue.append((data, addr))
                    _thread.interrupt_main()

            # If he gets a join request, then move to challenge
            elif command == 'ResultChallenge':
                # If the current player is hosting
                if Global.Game.getState() == 'Result':
                    self.messageQueue.append((data, addr))
                    _thread.interrupt_main()

            # If a gameboard update comes in
            elif command == 'PlayingUpdate':
                # If the current player is playing
                if Global.Game.getState() == 'Playing':
                    # Reset the connectionTTL
                    Global.Game.connectionTTL = 0
                    # Make sure that the gameboard is not None
                    if Global.GameBoard:
                        # TODO: Update the gameboard info
                        Global.GameBoard.setOpponentGrid(data[1])

            # If the player gets sent a line
            elif command == 'PlayingLine':
                # If the current player is playing
                if Global.Game.getState() == 'Playing':
                    # TODO: Update the gameboard
                    Global.GameBoard.getGrid().addLines(data[1])
                    print('Received packet:', data, addr)

            # Else we put it onto the messageQueue            
            else:
                self.messageQueue.append((data, addr))

            self.messageLock.release()
