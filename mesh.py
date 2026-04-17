import pygame
import time, os, meshtastic.serial_interface, meshtastic, math
from pubsub import pub
from meshtastic.util import findPorts
import threading
import util

letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]


status = ""
target = ""
interface = 0

devices = []
started = False

done = False

gameStarted = False

turn = False

winner = 0

gotResponseAttack = False
gotResponseMissHit = False
gotResponseWin = False

enemy = [[]]
player = []
guesses = [[-1, -1]]


def attack(x, y):
    global turn
    global guesses
    turn = False
    guesses.append([x, y])
    sendPacket(0, x, y)
    

def repeat(i, x=0, y=0):
    if i == 0 and not gotResponseAttack:
        print("try " + str(i))
        sendPacket(i, x, y)
    elif (i == 1 or i == 2) and not gotResponseMissHit:
        print("try " + str(i))
        sendPacket(i, x, y)
    elif i == -3 and not gotResponseWin:
        print("try " + str(i))
        sendPacket(i, x, y)

        
        

def sendPacket(i, x=0, y=0):
    global status
    global gameStarted
    global turn
    global winner
    global gotResponseAttack
    global gotResponseMissHit
    global gotResponseWin
    if i == 0:
        interface.sendText(("attack " + str(x) + " " + str(y)), channelIndex=1, wantAck=True)
        status = "attacking " + letters[y] + str(x+1)
        threading.Timer(10, repeat, [i, x, y]).start()
    elif i == 1:
        interface.sendText(("hit " + str(x) + " " + str(y)), channelIndex=1, wantAck=True)
        status = "the enemy has hit your boat at " + letters[y] + str(x+1)
        threading.Timer(10, repeat, [i, x, y]).start()
    elif i == 2:
        interface.sendText(("miss " + str(x) + " " + str(y)), channelIndex=1, wantAck=True)
        status = "the enemy has missed at " + letters[y] + str(x+1)
        threading.Timer(10, repeat, [i, x, y]).start()
                

    elif i == 3:
        interface.sendText(("ok hit " + str(x) + " " + str(y)), channelIndex=1, wantAck=True)
        
        
    elif i == 4:
        interface.sendText(("ok miss " + str(x) + " " + str(y)), channelIndex=1, wantAck=True)

        
    elif i == -1:
        interface.sendText("start game", channelIndex=1, wantAck=True)
        status = "init game"
    elif i == -2:
        interface.sendText("ok start game", channelIndex=1, wantAck=True)
        status = "game started"
        gameStarted = True
    elif i == -3:
        time.sleep(2)
        interface.sendText("you win", channelIndex=1, wantAck=True)
        status = "you lose. All your ships have been destroyed."
        winner = 2
        threading.Timer(10, repeat, [i, x, y]).start()
        
    elif i == -4:
        interface.sendText("ok you win", channelIndex=1, wantAck=True)
        turn = False
        
        

def onReceive(packet, interface, screen):
    global turn
    global target
    global status
    global gameStarted
    global winner
    global gotResponseAttack
    global gotResponseMissHit
    global gotResponseWin
    if len(packet.get('decoded' , "")):
            if len(packet['decoded'].get('payload' , "")):
                #print(packet['decoded']['payload'])
                if packet['decoded']['payload'] == b'start game':
                    target = packet['from']
                    sendPacket(-2)
                    turn = False
                if packet['decoded']['payload'] == b'ok start game':
                    status = "starting game"
                    gameStarted = True
                    turn = True
                if packet['decoded']['payload'][:7] == b'you win':
                    status = "you win. All the enemy's ships have been destroyed."
                    winner = 1
                    sendPacket(-4)
                if packet['decoded']['payload'][:10] == b'ok you win':
                    gotResponseWin = True
                if packet['from'] == target and packet['decoded']['payload'][:3] == b'hit':
                    x = int(packet['decoded']['payload'].decode('utf-8').split(" ")[1])
                    y = int(packet['decoded']['payload'].decode('utf-8').split(" ")[2])
                    enemy[0].append([x, y, False])
                    print(enemy)
                    status = "hit " + letters[y] + str(x+1)
                    gotResponseAttack = True
                    print(gotResponseAttack)
                    sendPacket(3, x, y)
                if packet['from'] == target and packet['decoded']['payload'][:4] == b'miss':
                    x = int(packet['decoded']['payload'].decode('utf-8').split(" ")[1])
                    y = int(packet['decoded']['payload'].decode('utf-8').split(" ")[2])
                    status = "miss " + letters[y] + str(x+1)
                    gotResponseAttack = True
                    print(gotResponseAttack)
                    sendPacket(4, x, y)
                if packet['from'] == target and packet['decoded']['payload'][:6] == b'ok hit':
                    x = int(packet['decoded']['payload'].decode('utf-8').split(" ")[2])
                    y = int(packet['decoded']['payload'].decode('utf-8').split(" ")[3])
                    gotResponseMissHit = True
                    turn = True
                    gotResponseAttack = False
                if packet['from'] == target and packet['decoded']['payload'][:7] == b'ok miss':
                    x = int(packet['decoded']['payload'].decode('utf-8').split(" ")[2])
                    y = int(packet['decoded']['payload'].decode('utf-8').split(" ")[3])
                    gotResponseMissHit = True
                    turn = True
                    gotResponseAttack = False
                    print(gotResponseAttack)
                if packet['from'] == target and packet['decoded']['payload'][:6] == b'attack':
                    x = int(packet['decoded']['payload'].decode('utf-8').split(" ")[1])
                    y = int(packet['decoded']['payload'].decode('utf-8').split(" ")[2])
                    b = util.getShip(player, y, x)
                    print (str(x) + ", " + str(y))
                    print(b)
                    if b == 1:
                        sendPacket(1, x, y)
                        win = True
                        for r in range(len(player)):
                            for s in range(len(player[r])):
                                if player[r][s][0] == x and player[r][s][1] == y:
                                    player[r][s][2] = False
                                if player[r][s][2]:
                                    win = False
                        if win:
                            sendPacket(-3)
                            turn = False
                    if b == 0:
                        sendPacket(2, x, y)

                    



def onConnection(interface, topic=pub.AUTO_TOPIC):
    global status
    status = "connected to " + interface.getLongName()
    sendPacket(-1)



def findDevices():
    global done
    global started
    global devices

    
    started = True
    for i in findPorts():
        try:
            iface = meshtastic.serial_interface.SerialInterface(devPath=i)
            devices.append([i, iface.getLongName()])
            iface.close()
        except meshtastic.serial.serialutil.SerialException:
            print("deal")
            break
        except meshtastic.mesh_interface.MeshInterface.MeshInterfaceError:
            print("deal")
            break
    done = True

def setupMesh(dev, screen):
    global interface
    interface = meshtastic.serial_interface.SerialInterface(devPath=dev)
    pub.subscribe(onReceive, "meshtastic.receive", screen=screen)
    pub.subscribe(onConnection, "meshtastic.connection.established")
    