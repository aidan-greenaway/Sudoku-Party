from cmu_graphics import *
import os, copy, math, itertools, time

###DRAWING 2D BOARD HELPERS###
#drawBoard through getCell from https://cs3-112-f22.academy.cs.cmu.edu/notes/4187
def drawBoard(app):
    for row in range(app.rows):
        for col in range(app.cols):
            drawCell(app, row, col)

def drawBoardBlocks(app):
    cellWidth, cellHeight = getCellSize(app)
    blockWidth, blockHeight = 3*cellWidth, 3*cellHeight
    blockLeft, blockTop = app.boardLeft, app.boardTop
    for _ in range(3):
        for _ in range(3):
            drawRect(blockLeft, blockTop, blockWidth, blockHeight, fill=None,
                     border='black', borderWidth=2*app.cellBorderWidth)
            blockLeft += blockWidth
        blockTop += blockHeight
        blockLeft = app.boardLeft

def drawCell(app, row, col):
    cellLeft, cellTop = getCellLeftTop(app, row, col)
    cellWidth, cellHeight = getCellSize(app)
    cellColor = getCellColor(app, row, col)
    opacity = 100 if cellColor != 'ghostWhite' else 80
    drawRect(cellLeft, cellTop, cellWidth, cellHeight,
             fill=cellColor, border='black',
             borderWidth=app.cellBorderWidth, opacity = opacity)
    labelX = cellLeft + cellWidth // 2
    labelY = cellTop + cellHeight // 2
    value = app.puzzle.board[row][col]
    if value != 0:
        labelColor = ['black'] if (row, col) in app.givenValues else app.rainbow
        Button.makeLabelPretty(str(value), labelX, labelY, 16, labelColor)

def getCellLeftTop(app, row, col):
    cellWidth, cellHeight = getCellSize(app)
    cellLeft = app.boardLeft + col * cellWidth
    cellTop = app.boardTop + row * cellHeight
    return (cellLeft, cellTop)

def getCellSize(app):
    cellWidth = app.boardWidth / app.cols
    cellHeight = app.boardHeight / app.rows
    return (cellWidth, cellHeight)

def getCell(app, x, y):
    dx = x - app.boardLeft
    dy = y - app.boardTop
    cellWidth, cellHeight = getCellSize(app)
    row = math.floor(dy / cellHeight)
    col = math.floor(dx / cellWidth)
    if (0 <= row < app.rows) and (0 <= col < app.cols):
        return (row, col)
    else:
        return None
 
def drawLegals(app):
    colors = ['red', 'tomato', 'green', 'blue', 'purple']
    i = 0
    for cell in app.puzzle.empties:
            row, col = cell
            cellLeft, cellTop = getCellLeftTop(app, row, col)
            cellWidth, cellHeight = getCellSize(app)
            cellsLegals = app.puzzle.legals[(row, col)]
            labelX = cellLeft + (cellWidth / 4)
            labelY = cellTop + (cellWidth / 4)
            for value in range(1, 10):
                if value in cellsLegals:
                    drawLabel(str(value), labelX, labelY, size = 10, 
                              fill = colors[i%len(colors)], bold= True)
                    i += 1
                if value % 3 == 0: 
                    labelX = cellLeft + (cellWidth / 4)
                    labelY += (cellHeight/4)
                else:
                    labelX += (cellWidth/4)
            i += 1

def getCellColor(app, row, col):
    if (row, col) in app.hintCells:
        return 'paleGreen'
    elif (row, col) in app.puzzle.wrongCells:
        return 'lightCoral'
    elif (row, col) == app.selectedCell:
        return 'aquamarine'
    elif (row, col) in app.regionCells:
        return 'paleTurquoise'
    elif (app.selectedValue != 0 and
          (row, col) in getSameValuePositions(app.puzzle.board, app.selectedValue)):
        return 'lightCyan'
    else: 
        return 'ghostWhite'

def getBlock(row, col):
    blockRow = row // 3
    blockCol = col // 3
    block = (blockRow*3) + blockCol
    return block

def moveSelectedCellWithKeys(app, key):
    row, col = app.selectedCell
    if key == 'left':
        if col != 0:
            app.selectedCell = (row, col-1)
    elif key == 'right':
        if col != 8:
            app.selectedCell = (row, col+1)
    elif key == 'up':
        if row != 0:
            app.selectedCell = (row-1, col)
    elif key == 'down':
        if row != 8:
            app.selectedCell = (row+1, col)

def showMouseOnlyButtons(app):
    if app.mouseMode:
        app.boardButtons.extend(app.mouseOnlyButtons)
    else:
        for button in app.mouseOnlyButtons:
            try:
                app.boardButtons.remove(button)
            except:
                pass

def loadMouseModeButtons():
    mouseModeButtons = []
    #setting buttons
    buttonX = 20
    buttonY = 35
    for i in range(10):
        label = 'X' if i == 0 else str(i)
        button = Button(buttonX, buttonY, 20, 20, label = label, color = 'lavender')
        mouseModeButtons.append(button)
        buttonY += 32
    buttonX = 380
    buttonY = 35
    for i in range(1, 10):
        label = str(i)
        button = Button(buttonX, buttonY, 20, 20, label = label, color = 'lightSteelBlue')
        mouseModeButtons.append(button)
        buttonY += 35
    return mouseModeButtons



###FILE READING AND SORTING PUZZLES BY DIFFICULTY###
def stringInto2DList(string):
    puzzle = []
    for row in string.splitlines():
        rowToAdd = []
        for cell in row.split(' '):
            if cell.isdigit():
                rowToAdd.append(int(cell))
        puzzle.append(rowToAdd)
    return puzzle  

def listIntoString(board):
    string = ''
    for row in board:
        line = ''
        for value in row:
            line += f'{value} '
        line = line.strip()
        string += line + '\n'
    return string.strip()

#from https://www.cs.cmu.edu/~112-3/notes/term-project.html 
def readFile(path):
    f = open(path, "r")
    return f.read()

#from https://www.cs.cmu.edu/~112-3/notes/term-project.html 
def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def fileToBoard(path):
    contents = readFile(path)
    board = stringInto2DList(contents)
    return board

def splitPuzzlesByDifficulty():
    result = dict()
    for filename in os.listdir('boards'):
        if filename.endswith('.txt') and 'solution' not in filename:
            pathToFile = f'boards/{filename}'
            if 'easy' in pathToFile:
                if 'easy' not in result:
                    result['easy'] = [pathToFile]
                else: 
                    result['easy'].append(pathToFile)
            elif 'medium' in pathToFile:
                if 'medium' not in result:
                    result['medium'] = [pathToFile]
                else: 
                    result['medium'].append(pathToFile)
            elif 'hard' in pathToFile:
                if 'hard' not in result:
                    result['hard'] = [pathToFile]
                else: 
                    result['hard'].append(pathToFile)
            elif 'evil' in pathToFile:
                if 'evil' not in result:
                    result['evil'] = [pathToFile]
                else: 
                    result['evil'].append(pathToFile)
            elif 'expert' in pathToFile:
                if 'expert' not in result:
                    result['expert'] = [pathToFile]
                else: 
                    result['expert'].append(pathToFile)
    return result


###SUDOKU PUZZLE OPERATIONS###
def getSameValuePositions(puzzle, targetValue):
    rows, cols = len(puzzle), len(puzzle[0])
    sameValues = [] #(row, col)
    for row in range(rows):
        for col in range(cols):
            if puzzle[row][col] == targetValue:
                sameValues.append((row, col))
    return sameValues

def getInitialValues(puzzle):
    initialValues = set() #(row, col)
    rows, cols = len(puzzle), len(puzzle[0])
    for row in range(rows):
        for col in range(cols):
            if puzzle[row][col] != 0:
                initialValues.add((row, col))
    return initialValues

def getLegals(board, empties):
    legalsDict = dict()
    for row, col in empties:
        bannedValues = set()
        legalValues = set(range(1, 10))
        for otherRow, otherCol in State.getAllRegions(row, col):
            value = board[otherRow][otherCol]
            if value != 0:
                bannedValues.add(value)
        legalsDict[(row, col)] = list(legalValues - bannedValues)
    return legalsDict

def getEmptySpots(board):
    emptySpots = [] #(row, col)
    rows, cols = len(board), len(board[0])
    for row in range(rows):
        for col in range(cols):
            if board[row][col] == 0:
                emptySpots.append((row, col))
    return emptySpots

def unionMultipleSets(L, initialSet):
    if L == []:
        return initialSet
    else:
        initialSet = initialSet | L[0]
        return unionMultipleSets(L[1:], initialSet)

def intersectMultipleSets(L, initialSet):
    if L == []:
        return initialSet
    else:
        initialSet = initialSet & L[0]
        return intersectMultipleSets(L[1:], initialSet)


#from https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html#printing
def repr2dList(L):
    if (L == []): return '[]'
    output = [ ]
    rows = len(L)
    cols = max([len(L[row]) for row in range(rows)])
    M = [['']*cols for row in range(rows)]
    for row in range(rows):
        for col in range(len(L[row])):
            M[row][col] = repr(L[row][col])
    colWidths = [0] * cols
    for col in range(cols):
        colWidths[col] = max([len(M[row][col]) for row in range(rows)])
    output.append('[\n')
    for row in range(rows):
        output.append(' [ ')
        for col in range(cols):
            if (col > 0):
                output.append(', ' if col < len(L[row]) else '  ')
            output.append(M[row][col].rjust(colWidths[col]))
        output.append((' ],' if row < rows-1 else ' ]') + '\n')
    output.append(']')
    return ''.join(output)

def print2dList(L):
    print(repr2dList(L))



###SUDOKU SOLVER W/ BACKTRACKING###
def solveSudoku(board, emptySpots, legalsDict):
    regions = State.getEveryBoardRegion()
    return sudokuSolver(copy.deepcopy(board), copy.deepcopy(emptySpots), copy.deepcopy(legalsDict), regions)

def sudokuSolver(board, emptySpots, legalsDict, regions):
    if emptySpots == []:
        return board
    else:
        nextCellToSolve = findLeastLegalsCell(legalsDict)
        row, col = nextCellToSolve
        cellsLegals = legalsDict[(row, col)]
        for value in set(cellsLegals):
            if canAddToBoard(copy.deepcopy(board), regions, row, col, value):
                board[row][col] = value
                emptySpots.remove((row, col))
                legalsDict.pop((row, col))
                #banning this value in cell's region
                for otherRow, otherCol in State.getAllRegions(row, col):
                    if (otherRow, otherCol) in legalsDict:
                        try: legalsDict[(otherRow, otherCol)].remove(value)
                        except: pass
                #recursive call 
                solution = sudokuSolver(copy.deepcopy(board), copy.deepcopy(emptySpots), copy.deepcopy(legalsDict), regions)
                if solution != None:
                    return solution
                #resetting bc value did not work
                board[row][col] = 0
                emptySpots.append((row, col))
                legalsDict[(row, col)] = getLegalsAtOneCell(board, row, col)
                #unbanning removed value in cell's region
                for otherRow, otherCol in State.getAllRegions(row, col):
                    if ((otherRow, otherCol) in legalsDict and 
                         value not in legalsDict[(otherRow, otherCol)]):
                        legalsDict[(otherRow, otherCol)].append(value)
    return None

def findLeastLegalsCell(legalsDict):
    for numLegals in range(0, 10):
        for cell in legalsDict:
            if len(legalsDict[cell]) == numLegals:
                return cell

def canAddToBoard(board, regions, row, col, value):
    board[row][col] = value
    if isBoardLegal(board, regions):
        return True
    return False

def isBoardLegal(board, regions):
    for region in regions:
        values = list()
        for row, col in region:
            if board[row][col] != 0:
                values.append(board[row][col])
        if len(values) != len(set(values)): 
            return False
    return True

def getLegalsAtOneCell(board, row, col):
    result = list(range(1, 10))
    for otherRow, otherCol in State.getAllRegions(row, col):
        value = board[otherRow][otherCol]
        if value != 0:
            try: result.remove(value)
            except: pass
    return result



###BACKTRACKING TESTER###
#functions from https://www.cs.cmu.edu/~112-3/notes/tp-sudoku-hints.html
def loadBoardPaths(filters):
        boardPaths = [ ]
        for filename in os.listdir(f'boards/'):
            if filename.endswith('.txt'):
                if hasFilters(filename, filters):
                    boardPaths.append(f'boards/{filename}')
        return boardPaths

def hasFilters(filename, filters=None):
    if filters == None: return True
    for filter in filters:
        if filter not in filename:
            return False
    return True

def testBacktracker(filters):
    print(f'\n --------{filters} boards-------- \n')
    time0 = time.time()
    boardPaths = sorted(loadBoardPaths(filters))
    failedPaths = [ ]
    for boardPath in boardPaths:
        board = fileToBoard(boardPath)

        print(boardPath)
        emptySpots = getEmptySpots(board)
        legalsDict = getLegals(board, emptySpots)
        solution = solveSudoku(board, emptySpots, legalsDict)
        if not solution:
            failedPaths.append(boardPath)
    print()
    totalCount = len(boardPaths)
    failedCount = len(failedPaths)
    okCount = totalCount - failedCount
    time1 = time.time()
    if len(failedPaths) > 0:
        print('Failed boards:')
        for path in failedPaths:
            print(f'    {path}')
    percent = rounded(100 * okCount/totalCount)
    print(f'Success rate: {okCount}/{totalCount} = {percent}%')
    print(f'Total time: {rounded(time1-time0)} seconds')

####CLASSES####

class Button:
    def __init__(self, centerX, centerY, width, height, color=None, label=None, 
                labelSize =16, labelColors = ['black']):
        self.centerX = centerX
        self.centerY = centerY
        self.width = width
        self.height = height
        self.color = color
        self.label = label
        self.labelColors = labelColors
        self.labelSize = labelSize

    def checkMouseCollision(self, x, y):
        left = self.centerX - self.width // 2
        top = self.centerY - self.height // 2
        return (left < x < (left + self.width) and 
            top < y < (top + self.height))
    
    def drawButton(self):
        left = self.centerX - self.width // 2
        top = self.centerY - self.height // 2
        drawRect(left, top, self.width, self.height, 
                 fill = self.color, border = 'ghostWhite')
        if self.label != None:
            labelX = left + self.width // 2
            labelY = top + self.height // 2
            Button.makeLabelPretty(self.label, labelX, labelY, self.labelSize, self.labelColors)
            #drawLabel(self.label, labelX, labelY, size=self.labelSize)

    ### COSMETIC DRAWING TEXT ###
    @staticmethod
    def makeLabelPretty(label, startX, startY, size, colors):
        labelX, labelY = startX - len(colors)/2, startY + len(colors)/2
        for i in range(len(colors)):
            drawLabel(label, labelX, labelY, size = size, fill = colors[len(colors) - (i+1)], bold = True,
                      border = 'black', borderWidth = 0)
            labelX += 1
            labelY -= 1

#conceptual idea of class from https://www.cs.cmu.edu/~112-3/notes/tp-sudoku-hints.html
class State:

    def __init__(self, board, difficulty):
        self.board = board
        self.diff = difficulty
        self.empties = getEmptySpots(board)
        self.legals = getLegals(board, self.empties)
        self.solvedBoard = solveSudoku(self.board, self.empties, self.legals)
        self.autoLegals = True if self.diff != 'easy' else False
        self.wrongCells = [] #(row, col)
    
    def set(self, row, col, value):
        lastState = copy.deepcopy(self)
        app.undoList.append(lastState)
        
        value = int(value)
        self.board[row][col] = value

        if self.diff != None:
            if value == 0:
                if (row, col) in self.wrongCells:
                    self.wrongCells.remove((row, col))
                if (row, col) not in self.empties:
                    self.empties.append((row, col))  
                self.legals[(row, col)] = []
            else:
                if value != self.solvedBoard[row][col] and (row, col) not in self.wrongCells:
                    self.wrongCells.append((row, col))
                elif value == self.solvedBoard[row][col] and (row, col) in self.wrongCells:
                    self.wrongCells.remove((row, col))

                if (row, col) in self.empties:
                    self.empties.remove((row, col))
                if (row, col) in self.legals:
                    self.legals.pop((row, col))

            if (self.autoLegals and value != 0):
                for (neighborRow, neighborCol) in State.getAllRegions(row, col):
                    if (neighborRow, neighborCol) in self.legals:
                        self.ban(neighborRow, neighborCol, value)
    
    def ban(self, row, col, value, ownAction=False):
        if ownAction:
            lastState = copy.deepcopy(self)
            app.undoList.append(lastState)
        if (row, col) in self.legals:
            if isinstance(value, list) or isinstance(value, set):
                for eachValue in value:
                    if eachValue in self.legals[(row, col)]:
                        self.legals[(row,col)].remove(eachValue)
                        if (eachValue == self.solvedBoard[row][col] and (row, col) not in self.wrongCells):
                            self.wrongCells.append((row, col))
            elif isinstance(value, int):
                if value in self.legals[(row, col)]:
                        self.legals[(row,col)].remove(value)
                        if (value == self.solvedBoard[row][col] and (row, col) not in self.wrongCells):
                            self.wrongCells.append((row, col))
    
    def unban(self, row, col, value, ownAction=False):
        if ownAction:
            lastState = copy.deepcopy(self)
            app.undoList.append(lastState)
        if (row, col) in self.legals:
            if isinstance(value, list) or isinstance(value, set):
                for eachValue in value:
                    if eachValue not in self.legals[(row, col)]:
                        self.legals[(row, col)].append(eachValue)
                        if (eachValue == self.solvedBoard[row][col] and (row, col) in self.wrongCells):
                            self.wrongCells.remove((row, col))
            elif isinstance(value, int):
                if value not in self.legals[(row, col)]:
                        self.legals[(row, col)].append(value)
                        if (value == self.solvedBoard[row][col] and (row, col) in self.wrongCells):
                            self.wrongCells.remove((row, col))

    def undo(self, undoList, redoList):
        if undoList == []:
            return
        else:
            currState = copy.deepcopy(self)
            undoneState = undoList.pop()
            redoList.append(currState)
            return undoneState

    def redo(self, undoList, redoList):
        if redoList == []:
            return
        else:
            redoneState = copy.deepcopy(self)
            undoList.append(redoneState)
            return redoList.pop()

    @staticmethod
    def getEveryBoardRegion():
        result = []
        for rows in range(9):
            eachRow = State.getRowRegion(rows, None)
            result.append(eachRow)
        for cols in range(9):
            eachCol = State.getColRegion(None, cols)
            result.append(eachCol)
        oneCellInEachBlock = [(0, 0), (0, 3), (0,8), (3, 0), (3, 3), (3, 6), (6, 0), (6, 3), (6, 6)]
        for row, col in oneCellInEachBlock:
            eachBlock = State.getBlockRegion(row, col)
            eachBlock.append((row, col))
            result.append(eachBlock)
        return result

    @staticmethod
    def getAllRegions(row, col):
        return set(State.getRowRegion(row, col) + State.getColRegion(row, col) +
                State.getBlockRegion(row, col))

    @staticmethod
    def getRowRegion(row, col):
        rowRegion = []
        for otherCol in range(9):
            if otherCol != col:
                rowRegion.append((row, otherCol))
        return rowRegion
    
    @staticmethod
    def getColRegion(row, col):
        colRegion = []
        for otherRow in range(9):
            if otherRow != row:
                colRegion.append((otherRow, col))
        return colRegion
    
    @staticmethod
    def getBlockRegion(row, col):
        blockRegion = []

        if row % 3 == 0:
            blockRows = list(range(row, row+3))
        elif row % 3 == 1:
            blockRows = list(range(row-1, row+2))
        elif row % 3 == 2:
            blockRows = list(range(row-2, row+1))

        if col % 3 == 0:
            blockCols = list(range(col, col+3))
        elif col % 3 == 1:
            blockCols = list(range(col-1, col+2))
        elif col % 3 == 2:
            blockCols = list(range(col-2, col+1)) 

        for eachRow in blockRows:
            for eachCol in blockCols:
                if (eachRow != row or eachCol != col):
                    blockRegion.append((eachRow, eachCol))
        return blockRegion
    
    def showHintOne(self):
        for (row, col) in self.legals:
            if len(self.legals[(row, col)]) == 1:
                return (row, col)
        return None

    def playHintOne(self):
        for (row, col) in self.legals:
            if len(self.legals[(row, col)]) == 1:
                value = self.legals[(row, col)][0]
                self.set(row, col, value)
                return (row, col)
        return None
    
    def playAllHintOnes(self):
        while self.playHintOne() != None:
            pass

    #from https://www.cs.cmu.edu/~112-3/notes/tp-sudoku-hints.html
    def showHintTwo(self):
        for region in State.getEveryBoardRegion():
            for n in range(2, 6):
                i = 0
                while i < len(region):
                    if region[i] not in self.empties:
                        region.pop(i)
                    else:
                        i += 1
                result = self.lookForHintTwo(region, n)
                if result != None:
                    return result
        return None
    
    def lookForHintTwo(self, region, n):
        for group in itertools.combinations(region, n):
            if n == len(region): continue
            cellsLegals = [] #list of sets of each cell's legals
            for cell in group:
                row, col = cell
                cellsLegals.append(set(getLegalsAtOneCell(self.board, row, col)))
            combinedSet = unionMultipleSets(cellsLegals, set(cellsLegals[0]))
            if len(combinedSet) == n:
                return group, combinedSet
        return None
    
    def playHintTwo(self, cells, legals):
        for region in State.getEveryBoardRegion():
            sharedRegion = True
            for cell in cells:
                if cell not in region: 
                    sharedRegion = False
            if not sharedRegion:
                continue
            for neighborRow, neighborCol in region:
                if (neighborRow, neighborCol) not in cells:
                    self.ban(neighborRow, neighborCol, legals)
        return

    #extra hint from https://www.stolaf.edu/people/hansonr/sudoku/explain.htm
    #look at the 'locked candidate rule'
    def lookForHintThree(self):
        everyRegion = State.getEveryBoardRegion()
        allRows = everyRegion[:9]
        allCols = everyRegion[9:18]
        #checking every col+block region intersection
        for row in allRows:
            for i in range(0, 9, 3):

                #creating the subregion of empty cells that share a row and block
                subRegion = row[i:i+3]
                subRegionLegals = []
                j = 0
                while j < len(subRegion):
                    subRow, subCol = subRegion[j]
                    if (subRow, subCol) in self.empties:  
                        subRegionLegals.append(set(self.legals[(subRow, subCol)]))
                        j += 1
                    else: subRegion.pop(j)
                if subRegion == []: continue
                mutualLegals = intersectMultipleSets(subRegionLegals, subRegionLegals[0])


                #getting the remainging row/block cells and legals that subregion shares
                firstRow, firstCol = subRegion[0]

                otherBlockCells = list(set(State.getBlockRegion(firstRow, firstCol)) - set(subRegion))
                otherBlockLegals = []
                k = 0
                while k < len(otherBlockCells):
                    bRow, bCol = otherBlockCells[k]
                    if (bRow, bCol) in self.legals:
                        otherBlockLegals.append(set(self.legals[(bRow, bCol)]))
                        k += 1
                    else: otherBlockCells.pop(k)    
                combinedBlockLegals = unionMultipleSets(otherBlockLegals, set())

                
                otherRowCells = list(set(State.getRowRegion(firstRow, firstCol)) - set(subRegion))
                otherRowLegals = []
                k = 0
                while k < len(otherRowCells):
                    rRow, rCol = otherRowCells[k]
                    if (rRow, rCol) in self.legals:
                        otherRowLegals.append(set(self.legals[(rRow, rCol)]))
                        k += 1
                    else: otherRowCells.pop(k)    
                combinedRowLegals = unionMultipleSets(otherRowLegals, set())

                #applying sudoku rule
                for value in mutualLegals:
                    if (value not in combinedBlockLegals) and (value not in combinedRowLegals):
                        continue
                    elif value not in combinedBlockLegals:
                        moveList = []
                        for row, col in otherRowCells:
                            if value in self.legals[(row, col)]:
                                moveList.append((row, col, value))
                        return subRegion, moveList
                    elif value not in combinedRowLegals:
                        moveList = []
                        for row, col in otherBlockCells:
                            if value in self.legals[(row, col)]:
                                moveList.append((row, col, value))
                        return subRegion, moveList

        #checking every row+block region intersection
        for col in allCols:
            for i in range(0, 9, 3):

                #creating the subregion of empty cells that share a row and block
                subRegion = col[i:i+3]
                subRegionLegals = []
                j = 0
                while j < len(subRegion):
                    subRow, subCol = subRegion[j]
                    if (subRow, subCol) in self.empties:  
                        subRegionLegals.append(set(self.legals[(subRow, subCol)]))
                        j += 1
                    else: subRegion.pop(j)
                if subRegion == []: continue
                mutualLegals = intersectMultipleSets(subRegionLegals, subRegionLegals[0])

                #getting the remainging col/block cells and legals that subregion shares
                firstRow, firstCol = subRegion[0]
                otherBlockCells = list(set(State.getBlockRegion(firstRow, firstCol)) - set(subRegion))
                otherBlockLegals = []
                k = 0
                while k < len(otherBlockCells):
                    bRow, bCol = otherBlockCells[k]
                    if (bRow, bCol) in self.legals:
                        otherBlockLegals.append(set(self.legals[(bRow, bCol)]))
                        k += 1
                    else: otherBlockCells.pop(k)    
                combinedBlockLegals = unionMultipleSets(otherBlockLegals, set())
                
                
                otherColCells = list(set(State.getColRegion(firstRow, firstCol)) - set(subRegion))
                otherColLegals = []
                k = 0
                while k < len(otherColCells):
                    cRow, cCol = otherColCells[k]
                    if (cRow, cCol) in self.legals:
                        otherColLegals.append(set(self.legals[(cRow, cCol)]))
                        k += 1
                    else: otherColCells.pop(k)    
                combinedColLegals = unionMultipleSets(otherColLegals, set())
                

                #applying rule
                for value in mutualLegals:
                    if (value not in combinedBlockLegals) and (value not in combinedColLegals):
                        continue
                    elif value not in combinedBlockLegals:
                        moveList = []
                        for row, col in otherColCells:
                            if value in self.legals[(row, col)]:
                                moveList.append((row, col, value))
                        return subRegion, moveList
                    elif value not in combinedColLegals:
                        moveList = []
                        for row, col in otherBlockCells:
                            if value in self.legals[(row, col)]:
                                moveList.append((row, col, value))
                        return subRegion, moveList
        
        return None

def main():
    for filter in ['easy', 'medium', 'hard', 'evil', 'expert']:
        testBacktracker(filters=filter)

###uncomment and run to test backtracker speed###
#main()
