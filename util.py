import pygame



def drawGrid(screen: pygame.Surface, x: int, y: int, squareColor: str, lineColor: str, fontColor: str, boats, guesses = []):

    arr = [[], [], [], [], [], [], [], [], [], []]

    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"]

    font = pygame.font.Font('comic.ttf', 40)



    screen.fill(lineColor, pygame.Rect(x+30, y+50, 448, 448))
    for r in range(10):
        text = font.render(letters[r], True, (0, 0, 255))
        screen.blit(text, pygame.Rect(x, (y+(r*45))+40, 43, 43))
        for c in range(10):
            if len(guesses):
                b = getShip(boats, r, c, guesses)
            else:
                b = getShip(boats, r, c)
            rect = pygame.Rect(x+(c*45)+30, y+(r*45)+50, 43, 43)

            if b == 0:
                screen.fill(squareColor, rect)
            elif b == 1:
                screen.fill("dark grey", rect)
            elif b == -1:
                screen.fill("black", rect)
            else:
                screen.fill("red", rect)

            arr[r].append(rect)
            
            if c == 9:
                text = font.render(str(c+1), True, (0, 0, 255))
                screen.blit(text, pygame.Rect(x+(c*45)+30, y, 43, 43))
            else:
                text = font.render(str(c+1), True, (0, 0, 255))
                screen.blit(text, pygame.Rect(x+(c*45)+40, y, 43, 43))
    return arr

def getShip(boats, r, c, guesses = []):
    if len(guesses):
        for i in range(len(guesses)):
            if guesses[i][0] == c and guesses[i][1] == r:
                return getShip(boats, r, c)
        return -1                
    
    else:
        for b in range(len(boats)):
            for i in range(len(boats[b])):
                if boats[b][i][0] == c and boats[b][i][1] == r:
                    if boats[b][i][2]:
                        return 1
                    else:
                        return 2
    return 0
