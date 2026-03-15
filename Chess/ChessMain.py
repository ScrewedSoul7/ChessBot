import pygame as p
import ChessEngine

WIDTH = HEIGHT = 512 #piece dimentions
DIMENTION = 8 #chessboard has a dimention of 8 x 8
SQ_SIZE = HEIGHT // DIMENTION
MAX_FPS = 15
IMAGES = {}

'''
Load images through a global dictionary

'''

def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bP", "wR", "wN", "wB", "wQ", "wK", "wP"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("Pieces/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

'''
Handle user input and graphics in main.

'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gameState = ChessEngine.GameState()
    validMoves = gameState.getValidMoves()
    moveMade = False #flag for when a move is made
    loadImages()
    running = True
    sqSelected = ()  #no square selected initally
    clicks = [] #keep track of player clicks
    while running:
        for event in p.event.get():
            if event.type == p.QUIT:
                running = False
            elif event.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  #location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col):
                    sqSelected = ()
                    clicks = []  #clear the player clicks
                else:
                    sqSelected = (row, col)
                    clicks.append(sqSelected)  #append first and second clicks
                if len(clicks) == 2:
                    move = ChessEngine.Move(clicks[0], clicks[1], gameState.board)
                    print(move.getChessNotation())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gameState.makeMove(validMoves[i])                         
                            moveMade = True
                            sqSelected = () #reset user clicks
                            clicks = []
                    if not moveMade:
                        clicks = [sqSelected]

            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gameState.undoMove()
                    moveMade = True

        #generate moves only when a valid move is made     
        if moveMade:
            validMoves = gameState.getValidMoves()
            moveMade = False    

        draw(screen, gameState)
        clock.tick(MAX_FPS)
        p.display.flip()

def draw(screen , gameState):
    drawBoard(screen)
    drawPieces(screen, gameState.board)

def drawBoard(screen):
    for i in range(DIMENTION):
        for j in range(DIMENTION):
            if ((i + j) % 2 == 0):
                p.draw.rect(screen,"white",(i * SQ_SIZE, j * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen,"dark green",(i * SQ_SIZE, j * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawPieces(screen, board):
    for row in range(DIMENTION):
        for col in range(DIMENTION):
            piece = board [row] [col]
            if piece !="--":
                screen.blit(IMAGES[piece], (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

if __name__ == "__main__":
    main()