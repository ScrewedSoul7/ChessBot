'''
Stores current state of the game
'''

class GameState():
    def __init__(self):

        #board is a 2D list, with elements having 2 characters
        #First letter represents the color of the piece b = black and w = white 
        #Second letter represents type of the piece according to standard notations
        #"--" represent  empty space on the chessboard with no piece
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],                        
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],            
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]            
            ]

        self.whiteToMove = True
        self.moveLog = []
        self.moveFunctions = {'P': self.getPawnMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves,
                              'R': self.getRookMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        
        #Keeping track of King's location for detemining checks and castling 
        self.whiteKingLoc = (7, 4)
        self.blackKingLoc = (0, 4)
        self.checkMate = False
        self.staleMate = False

    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  #To display game history
        self.whiteToMove = not self.whiteToMove 

        #update Kings location if its moved 
        if move.pieceMoved == 'wK':
            self.whiteKingLoc = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLoc = (move.endRow, move.endCol)


    #Undo the last move
    def undoMove(self):
        if len(self.moveLog) != 0:
            lastMove = self.moveLog.pop()
            self.board[lastMove.startRow][lastMove.startCol] = lastMove.pieceMoved        
            self.board[lastMove.endRow][lastMove.endCol] = lastMove.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            #Update king's position if needed
            if lastMove.pieceMoved == 'wK':
                self.whiteKingLoc = (lastMove.startRow, lastMove.startCol)
            elif lastMove.pieceMoved == 'bK':
                self.blackKingLoc = (lastMove.startRow, lastMove.startCol)                        

            
    def getValidMoves(self):

        #Generate all possible moves
        moves = self.getAllPossibleMoves()

        for i in range(len(moves) - 1, -1, -1):  #When removing and iterating from list go backwards 
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove  #Swap turns back because makeMoves swaps the turn to opponent but we want to run inCheck for the current player and not opponent.
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove #Swap turns back
            self.undoMove()
            if len(moves) == 0:
                if self.inCheck():
                    self.checkMate = True
                    print("Checkmate")
                else:
                    self.staleMate = True
            else:
                self.checkMate = False
                self.staleMate = False
        return moves
    
    def inCheck(self):
        if self.whiteToMove:
            return self.SquareUnderAttack(self.whiteKingLoc[0], self.whiteKingLoc[1])
        else:
            return self.SquareUnderAttack(self.blackKingLoc[0], self.blackKingLoc[1])

    def SquareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove  #Switch turn back
        for move in oppMoves:
            if  move.endRow == r and move.endCol == c: #Square is under attack
                return True
        return False    

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):           #no. of rows
            for c in range(len(self.board[r])):    #no. of cols 
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]    #piece type
                    self.moveFunctions[piece] (r, c, moves)  #calls respective move function
        return moves    

    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r - 1, c), self.board)) 
                if self.board[r - 2][c] == "--" and r == 6:
                    moves.append(Move((r, c), (r-2, c), self.board)) 
            
            #Left capture logic for white pawn
            if (c >= 1) and (self.board[r - 1][c - 1][0] == 'b') :
                moves.append(Move((r, c), (r - 1, c - 1), self.board))
            
            #Right capture logic for white pawn
            if (c < 7) and (self.board[r - 1][c + 1][0] == 'b') :
                moves.append(Move((r, c), (r - 1, c + 1), self.board))

        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board)) 
                if self.board[r + 2][c] == "--" and r == 1:
                    moves.append(Move((r, c), (r + 2, c), self.board))  

            #Left capture logic for black pawn
            if (c >= 1) and (self.board[r + 1][c - 1][0] == 'w') :
                moves.append(Move((r, c), (r + 1, c - 1), self.board))                           
            
            #Right capture logic for black pawn
            if (c < 7) and (self.board[r + 1][c + 1][0] == 'w') :
                moves.append(Move((r, c), (r + 1, c + 1), self.board))             

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (+2, -1), (+2, +1), (-2, +1),
                      (+1, -2), (+1, +2), (-1, -2), (-1, +2))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for direction in knightMoves:
                endRow = r + direction[0] 
                endCol = c + direction[1]
                if 0 <= endRow < 8 and 0 <= endCol < 8:  #On board
                    endSq = self.board [endRow] [endCol]
                    if endSq == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board)) 
                    elif endSq[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board)) 

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for direction in directions:
            for i in range(1, 8):
                endRow = r + direction[0] * i
                endCol = c + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  #On board
                    endSq = self.board [endRow] [endCol]
                    if endSq == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board)) 
                    elif endSq[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board)) 
                        break
                    else:                               #Friendly piece    
                        break                                           
                else:                                   #Off board 
                    break  

    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (1, 0), (0, -1), (0, 1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for direction in directions:
            for i in range(1, 8):
                endRow = r + direction[0] * i
                endCol = c + direction[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:  #On board
                    endSq = self.board [endRow] [endCol]
                    if endSq == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board)) 
                    elif endSq[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board)) 
                        break
                    else:                               #Friendly piece    
                        break                                           
                else:                                   #Off board 
                    break        
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r ,c , moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (+1, -1), (+1, +1), (-1, +1),
                      (1, 0), (0, 1), (-1, 0), (0, -1))
        enemyColor = 'b' if self.whiteToMove else 'w'
        for direction in kingMoves:
                endRow = r + direction[0] 
                endCol = c + direction[1]
                if 0 <= endRow < 8 and 0 <= endCol < 8:  #On board
                    endSq = self.board [endRow] [endCol]
                    if endSq == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board)) 
                    elif endSq[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board)) 

class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0 }    
    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, 
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self, startSq, endSq, board):
        self.startRow = startSq[0]      #Stores row of the first click as a number   
        self.startCol  = startSq[1]     #Stores col of the first click as a number   
        self.endRow = endSq[0]          #Stores row of the second click as a number                
        self.endCol = endSq[1]          #Stores col of the second click as a number
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = False
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  #get the coordinates for a piece

    # Overriding __equals__ method to establish equality between moves variable in ChessMain and moves in the valid moves list
    # Doing this wont be necessary if we parse the moves as
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getRankAndFile(self, row, col):
        return self.colsToFiles[col] + self.rowsToRanks[row]
    
    def getChessNotation(self):
        pieceName = self.pieceMoved[1]
        isCaptured = self.pieceCaptured != "--"

        if pieceName == 'P':
            if isCaptured:
                return self.colsToFiles[self.startCol] + "x" + self.getRankAndFile(self.endRow, self.endCol)
            return self.getRankAndFile(self.endRow, self.endCol)
        else:
            if isCaptured:
                return pieceName + "x" + self.getRankAndFile(self.endRow, self.endCol)            
            return pieceName + self.getRankAndFile(self.endRow, self.endCol)

        