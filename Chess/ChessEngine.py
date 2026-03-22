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
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()  #Square where an enpassant capture is possible
        self.currentCastelingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastelingRights.wks, self.currentCastelingRights.wqs,
                                             self.currentCastelingRights.bks, self.currentCastelingRights.bqs)]
 
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

        #pawn promotion
        if move.isPawnPromotion:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + move.promotionChosen

        #enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--'  #pawn captured 
        
        #update enpassantPossible
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enpassantPossible = ()

        #update castling rights 
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastelingRights.wks, self.currentCastelingRights.wqs,
                                             self.currentCastelingRights.bks, self.currentCastelingRights.bqs))


        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:   #King side castle
                self.board[move.endRow] [move.endCol - 1] = self.board[move.endRow] [move.endCol + 1]  #moves the rook
                self.board[move.endRow] [move.endCol + 1] = '--' #erase old square
            else:
                #Queen side castle
                self.board[move.endRow] [move.endCol + 1] = self.board[move.endRow] [move.endCol - 2]
                self.board[move.endRow] [move.endCol - 2] = '--' #erase old square

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

            if lastMove.isEnpassantMove:                 
                self.board[lastMove.endRow][lastMove.endCol] = '--'
                self.board[lastMove.startRow][lastMove.endCol] = lastMove.pieceCaptured
                self.enpassantPossible = (lastMove.endRow, lastMove.endCol)
            
            #Undo 2 square pawn advance
            if lastMove.pieceMoved[1] == 'P' and abs(lastMove.startRow - lastMove.endRow) == 2:
                self.enpassantPossible = ()

            #Undo castling rights
            self.castleRightsLog.pop()
            castleRights = self.castleRightsLog[-1]
            self.currentCastelingRights = CastleRights(castleRights.wks, castleRights.wqs, 
                                                       castleRights.bks, castleRights.bqs)
            #Undo castling move
            if lastMove.isCastleMove:
                if lastMove.endCol - lastMove.startCol == 2:  #kingside
                    self.board [lastMove.endRow] [lastMove.endCol + 1] = self.board [lastMove.endRow] [lastMove.endCol - 1]
                    self.board [lastMove.endRow] [lastMove.endCol - 1] = '--'
                else:
                    self.board [lastMove.endRow] [lastMove.endCol - 2] = self.board [lastMove.endRow] [lastMove.endCol + 1]
                    self.board [lastMove.endRow] [lastMove.endCol + 1] = '--'

    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastelingRights.wks = False
            self.currentCastelingRights.wqs = False   
        elif move.pieceMoved == 'bK':
            self.currentCastelingRights.bks = False
            self.currentCastelingRights.bqs = False            
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:   #Queen side rook
                    self.currentCastelingRights.wqs = False
                elif move.startCol == 7:  #King side rook
                    self.currentCastelingRights.wks = False        

        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:    #Queen side rook
                    self.currentCastelingRights.bqs = False
                elif move.startCol == 7:  #King side rook
                    self.currentCastelingRights.bks = False    


    def getValidMoves(self):

        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastelingRights.wks, self.currentCastelingRights.wqs, 
                                        self.currentCastelingRights.bks, self.currentCastelingRights.bqs)
        
        #Generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLoc[0], self.whiteKingLoc[1], moves)
        else:
            self.getCastleMoves(self.blackKingLoc[0], self.blackKingLoc[1], moves)  

        for i in range(len(moves) - 1, -1, -1):  #When removing and iterating from list go backwards 
            self.makeMove(moves[i])
            self.whiteToMove = not self.whiteToMove  #Swap turns back because makeMoves swaps the turn to opponent but we want to run inCheck for the current player and not opponent.
            if self.inCheck():
                moves.remove(moves[i])
            self.whiteToMove = not self.whiteToMove #Swap turns back
            self.undoMove()
            if len(moves) == 0:
                if self.inCheck():
                    self.checkmate = True
                    print("Checkmate")
                else:
                    self.stalemate = True
            else:
                self.checkmate = False
                self.stalemate = False
        self.enpassantPossible = tempEnpassantPossible
        self.currentCastelingRights = tempCastleRights
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
            if (c >= 1):
                if(self.board[r - 1][c - 1][0] == 'b'):
                    moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.enpassantPossible :
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnpassantMove = True))    

            #Right capture logic for white pawn
            if (c < 7):
                if (self.board[r - 1][c + 1][0] == 'b'):
                    moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.enpassantPossible :
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnpassantMove = True))   
        else:
            if self.board[r + 1][c] == "--":
                moves.append(Move((r, c), (r + 1, c), self.board)) 
                if self.board[r + 2][c] == "--" and r == 1:
                    moves.append(Move((r, c), (r + 2, c), self.board))  

            #Left capture logic for black pawn
            if (c >= 1) :
                if (self.board[r + 1][c - 1][0] == 'w'): 
                    moves.append(Move((r, c), (r + 1, c - 1), self.board))                           
                elif (r + 1, c - 1) == self.enpassantPossible :
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnpassantMove = True)) 

            #Right capture logic for black pawn
            if (c < 7) :
                if (self.board[r + 1][c + 1][0] == 'w'):
                    moves.append(Move((r, c), (r + 1, c + 1), self.board))             
                elif (r + 1, c + 1) == self.enpassantPossible :
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnpassantMove =True)) 

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


    def getCastleMoves(self, r, c, moves):
        if self.inCheck(): 
            return  #Cant castle when in check
        if (self.whiteToMove and self.currentCastelingRights.wks) or (not self.whiteToMove and self.currentCastelingRights.bks):
            if self.board[r][c + 1] == '--' and self.board[r] [c + 2] == '--':
                if not self.SquareUnderAttack(r, c + 1) and not self.SquareUnderAttack(r, c + 2):
                    moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove = True))

        if (self.whiteToMove and self.currentCastelingRights.wqs) or (not self.whiteToMove and self.currentCastelingRights.bqs):
            if self.board[r][c - 1] == '--' and self.board[r] [c - 2] == '--' and self.board [r] [c - 3] == '--':
                if not self.SquareUnderAttack(r, c - 1) and not self.SquareUnderAttack(r, c - 2):
                    moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove = True))

class CastleRights():
    def __init__(self, whiteKingSide, whiteQueenSide, blackKingSide, blackQueenSide):
        self.wks = whiteKingSide
        self.wqs = whiteQueenSide
        self.bks = blackKingSide
        self.bqs = blackQueenSide
 


class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0 }    
    rowsToRanks = {v:k for k,v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, 
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v:k for k,v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove  = False, isCastleMove = False):
        self.startRow = startSq[0]      #Stores row of the first click as a number   
        self.startCol  = startSq[1]     #Stores col of the first click as a number   
        self.endRow = endSq[0]          #Stores row of the second click as a number                
        self.endCol = endSq[1]          #Stores col of the second click as a number
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.isPawnPromotion = (self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7)
        self.promotionChosen = 'Q'  

        #en passant
        self.isEnpassantMove = isEnpassantMove 
        if self.isEnpassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol  #get the coordinates for a piece

        self.isCastleMove = isCastleMove

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


        