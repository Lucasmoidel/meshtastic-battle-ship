#!/bin/python
import pygame
import threading

import util, mesh
# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 1080))
#clock = pygame.time.Clock()
running = True

state = 1

#boatlen = [5, 4, 3, 3, 2]
boatlen = [2]
direction = True

rPressed = False
lcPressed = False

textSelected = False

blocked = False




throbber = "finding devices"
throbberNum = 0

font = pygame.font.Font('comic.ttf', 40)

def throb():
    global throbberNum
    global throbber
    if throbberNum == 3:
        throbberNum = 0
    else:
        throbberNum+=1
    throbber = "finding devices" + ("."*throbberNum)
    if state != 0:
        threading.Timer(0.5, throb).start()



while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame

    match state:
        case 1:
            
            text = font.render("place your boats. Press R to rotate and left click to place", True, (103, 234, 148))
            screen.blit(text, pygame.Rect(5, 10, len("place your boats. Press R to rotate and left click to place")*40, 40))

            blocked = False

            grid = util.drawGrid(screen, 0, 60, "blue", "white", "white", mesh.player)

            temp = []
            boat = boatlen[len(mesh.player)]


            for r in range(10):
                for c in range(10):
                    if grid[r][c].collidepoint(pygame.mouse.get_pos()):
                        if direction:
                            if (c + boat-1) < 10:
                                for i in range(boat):
                                    if util.getShip(mesh.player, r, c+i) != 0:
                                        blocked = True
                                if not blocked:
                                    arr = []
                                    for i in range(boat):
                                        arr.append([(c+i), r, True])
                                    temp.append(arr)
                        elif not direction:
                            if (r + boat-1) < 10:
                                for i in range(boat):
                                    if util.getShip(mesh.player, r+i, c) != 0:
                                        blocked = True
                                if not blocked:
                                    arr = []
                                    for i in range(boat):
                                        arr.append([c, (r+i), True])
                                    temp.append(arr)

            if pygame.key.get_pressed()[pygame.K_r]:
                rPressed = True
            if rPressed and not pygame.key.get_pressed()[pygame.K_r]:
                direction = not direction
                rPressed = False


            if pygame.mouse.get_pressed()[0]:
                lcPressed = True
            if lcPressed and not pygame.mouse.get_pressed()[0]:            
                lcPressed = False
                if len(temp) > 0:
                    mesh.player.append(temp[0])

            for i in range(len(mesh.player)):
                temp.append(mesh.player[i])

            grid = util.drawGrid(screen, 0, 60, "blue", "white", "white", temp)


            if len(mesh.player) == len(boatlen):
                state = 2
        case 2:
            screen.fill(pygame.Color(0,0,0))
            if mesh.done:
                text = font.render("select a device", True, (103, 234, 148))
                screen.blit(text, pygame.Rect(40, 10, len("select a device")*40, 40))
                for i in range(len(mesh.devices)):
                    rect = pygame.Rect(40, 60+(i*50), (len(mesh.devices[i][0])+len(mesh.devices[i][1])+len(" at "))*40, 40)
                    if rect.collidepoint(pygame.mouse.get_pos()):
                        text = font.render((mesh.devices[i][1] + " at " + mesh.devices[i][0]), True, pygame.Color(255,255,255), pygame.Color(100,100,100))
                        screen.blit(text, rect)

                        if pygame.mouse.get_pressed()[0]:
                            lcPressed = True
                        if lcPressed and not pygame.mouse.get_pressed()[0]:            
                            lcPressed = False
                            mesh.setupMesh(mesh.devices[i][0], screen)
                            state = 0
                            
                    else:
                        text = font.render((mesh.devices[i][1] + " at " + mesh.devices[i][0]), True, pygame.Color(255,255,255))
                        screen.blit(text, rect)
                
            else:
                
                text = font.render(throbber, True, (103, 234, 148))
                screen.blit(text, pygame.Rect(40, 10, len(throbber)*40, 40))
                
                if not mesh.started:
                    threading.Thread(target=mesh.findDevices).start()
                    threading.Thread(target=throb).start()

        case 0:
            screen.fill(pygame.Color(0,0,0))

            text = font.render(mesh.status, True, (103, 234, 148))
            screen.blit(text, pygame.Rect(40, 10, len(mesh.status)*40, 40))

            top = util.drawGrid(screen, 0, 60, "blue", "white", "white", mesh.enemy, mesh.guesses)
            bottom = util.drawGrid(screen, 0, 570, "blue", "white", "white", mesh.player)
            temp = []
            tempG = []
            if mesh.turn:
                for r in range(10):
                    for c in range(10):
                        if top[r][c].collidepoint(pygame.mouse.get_pos()):
                            if util.getShip(mesh.enemy, r, c, mesh.guesses) == -1:
                                arr = []
                                arr.append([c, r, False])
                                temp.append(arr)
                                tempG.append([c, r])
                                if pygame.mouse.get_pressed()[0]:
                                    lcPressed = True
                                if lcPressed and not pygame.mouse.get_pressed()[0]:            
                                    lcPressed = False
                                    
                                    mesh.attack(c, r)




            for i in range(len(mesh.enemy)):
                temp.append(mesh.enemy[i])

            for i in range(len(mesh.guesses)):
                tempG.append(mesh.guesses[i])

            top = util.drawGrid(screen, 0, 60, "blue", "white", "white", temp, tempG)
    
    pygame.display.flip()

pygame.quit()
