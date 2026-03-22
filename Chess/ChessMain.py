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
    animte = False #flag to detemnine when to animate a move
    loadImages()
    running = True
    sqSelected = ()  #no square selected initally
    clicks = [] #keep track of player clicks
    gameOver = False
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
                            if validMoves[i].isPawnPromotion:
                                choice = ""
                                while choice not in ['Q', 'R', 'B', 'N']:
                                    print("What do you want to promote to? Type Q for Queen, R for Rook, N for Knight, B for Bishop")
                                    choice = input().upper()
                                    if choice not in ['Q', 'R', 'B', 'N']:
                                        print("Please enter a valid promotion option!")
                                        
                                validMoves[i].promotionChosen = choice
                            gameState.makeMove(validMoves[i])                         
                            moveMade = True
                            animte = True
                            sqSelected = () #reset user clicks
                            clicks = []

                            break
                    if not moveMade:
                        clicks = [sqSelected]

            elif event.type == p.KEYDOWN:
                if event.key == p.K_z:
                    gameState.undoMove()
                    moveMade = True
                    animte = False
                if event.key == p.K_r:
                    gameState = ChessEngine.GameState()
                    validMoves = gameState.getValidMoves()
                    clicks = []
                    sqSelected = ()
                    moveMade = False
                    animte = False

        #generate moves only when a valid move is made     
        if moveMade:
            if animte:
                animateMove(gameState.moveLog[-1], screen, gameState.board, clock)
            validMoves = gameState.getValidMoves()
            moveMade = False
            animte = False    

        draw(screen, gameState, validMoves, sqSelected)

        if gameState.checkmate:
            gameOver = True
            if gameState.whiteToMove:
                drawText(screen, 'Black wins by Checkmate')
            else:
                drawText(screen, 'White wins by Checkmate')
        elif gameState.stalemate:
            drawText(screen, 'Stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()


def highlightSquares(screen, gameState, validMoves, sqSelected):
    if sqSelected != () :
        r, c = sqSelected
        if gameState.board [r][c][0] == ('w' if gameState.whiteToMove else 'b'):
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color('blue'))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))

            #highlight moves from the piece on the square
            s.fill(p.Color('red'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (SQ_SIZE * move.endCol, SQ_SIZE * move.endRow))

def draw(screen , gameState, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gameState, validMoves, sqSelected)
    drawPieces(screen, gameState.board)

def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("dark green")]
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

def animateMove(move, screen, board, clock):
    global colors
    R = move.endRow - move.startRow
    C = move.endCol - move.startCol
    framesPerSquare = 10  #frames to move one square
    frameCount = (abs(R) + abs(C)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + R * frame / frameCount, move.startCol + C * frame / frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece 
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObj = font.render(text, 0, p.Color('Gray'))
    textLoc = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - textObj.get_width() / 2, HEIGHT / 2 - textObj.get_height() / 2)
    screen.blit(textObj, textLoc)
    textObj = font.render(text, 0, p.Color("Black"))
    screen.blit(textObj, textLoc.move(2,2))


if __name__ == "__main__":
    main()