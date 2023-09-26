from cmu_graphics import *
from helpersAndClasses import *
from PIL import Image
import random

#BOARD SCREEN
def board_onScreenStart(app):
    app.goHome = Button(350, 380, 75, 25, color = 'lightGreen', 
                        label = 'Home (esc)', labelSize = 12)
    app.toggleLegals = Button(60, 380, 95, 25, color = 'lightBlue',
                        label = 'Show Legals (L)', labelSize = 12)
    app.options = Button(260, 380, 78, 25, color = 'orange',
                              label = 'Options (o)', labelSize = 12)
    app.hint = Button(165, 380, 80, 25, color = 'aquamarine',
                      label = 'Show Hint (h)', labelSize = 12)
    app.playHint = Button(230, 420, 78, 25, color = 'lemonChiffon',
                      label = 'Play Hint (H)', labelSize = 12)
    app.undoButton = Button(44, 420, 53, 25, color = 'mediumAquamarine', 
                      label = 'Undo (u)', labelSize = 12)
    app.redoButton = Button(100, 420, 53, 25, color = 'thistle', 
                      label = 'Redo (r)', labelSize = 12)
    app.save = Button(156, 420, 53, 25, color = 'hotPink', 
                      label = 'Save (p)', labelSize = 12)
    app.singleton = Button(330, 410, 107, 16, color = 'pink', 
                           label = 'Play Singleton (s)', labelSize = 12)
    app.allSingletons = Button(330, 430, 107, 16, color = 'darkTurquoise', 
                           label = 'All Singletons (S)', labelSize = 12)
    
    #from image-demos.zip on https://www.cs.cmu.edu/~112-3/notes/term-project.html
    #gif from https://media.tenor.com/sZhit3b59H8AAAAM/dancing.gif
    app.wonSprites = loadAnimatedGif('images/youWonGif.gif')
    app.wonSpriteCounter = 0
    app.stepsPerSecond = 5

    app.boardButtons = [app.goHome, app.toggleLegals, app.options, app.hint, app.undoButton, app.redoButton, app.playHint, app.save]
    app.mouseOnlyButtons = loadMouseModeButtons()
    app.puzzleDict = splitPuzzlesByDifficulty()
    
    app.rows = app.cols = 9
    app.boardLeft = 37.5
    app.boardTop = 22.5
    app.boardWidth = 325
    app.boardHeight = 325
    app.cellBorderWidth = 1.5
    app.regionCells = set()
    app.prevKey = None
    app.gameOver = app.keyboardMode = app.mouseMode =  False

#from image-demos.zip on https://www.cs.cmu.edu/~112-3/notes/term-project.html
def board_onStep(app):
    app.wonSpriteCounter = (1 + app.wonSpriteCounter) % len(app.wonSprites)

def board_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.backColor, opacity = 60)
    drawBoard(app)
    drawBoardBlocks(app)
    if app.showLegals:
        drawLegals(app)
    if app.gameOver:
        drawRect(75, 100, 250, 250, fill = 'violet')
        drawLabel('Game Over! You won.', 200, 125, size = 18, bold = True)
        sprite = app.wonSprites[app.wonSpriteCounter]
        drawImage(sprite, 200, 225, align='center')
        app.goHome.centerX = 200
        app.goHome.centerY = 320
    else: 
        app.goHome.centerX = 350
        app.goHome.centerY = 380
    for button in app.boardButtons:
        button.drawButton()

def board_onMousePress(app, mouseX, mouseY):
    app.hintCells = []

    #general gameplay
    if not (app.gameOver or app.keyboardMode):
        #selecting cells with mouse
        selectedCell = getCell(app, mouseX, mouseY)
        if selectedCell != None:
            app.selectedCell = selectedCell
            row, col = app.selectedCell
            app.regionCells = State.getAllRegions(row, col)
            app.selectedValue = app.puzzle.board[row][col]

        #showing/not showing legals
        if app.toggleLegals.checkMouseCollision(mouseX, mouseY):
                if not app.showLegals:
                    app.toggleLegals.color = 'salmon'
                    app.toggleLegals.label = 'Hide Legals (L)'
                else:
                    app.toggleLegals.color = 'lightBlue'
                    app.toggleLegals.label = 'Show Legals (L)'
                app.showLegals = not app.showLegals
    
        #undo and redo buttons
        elif app.undoButton.checkMouseCollision(mouseX, mouseY):
            undone = app.puzzle.undo(app.undoList, app.redoList)
            if undone != None:
                app.puzzle = undone
        elif app.redoButton.checkMouseCollision(mouseX, mouseY):
            redone = app.puzzle.redo(app.undoList, app.redoList)
            if redone != None:
                app.puzzle = redone
        
        #playing or showing hints
        elif app.hint.checkMouseCollision(mouseX, mouseY):
            showHints(app)
        elif app.playHint.checkMouseCollision(mouseX, mouseY):
            playHints(app)
        
         #playing Singletons if difficulty is not easy
        if app.puzzle.diff != 'easy':
            if app.singleton.checkMouseCollision(mouseX, mouseY):
                playedSingleton = app.puzzle.playHintOne()
                if playedSingleton != None:
                    app.selectedCell = playedSingleton
                    newRow, newCol = app.selectedCell
                    app.regionCells = State.getAllRegions(newRow, newCol)
                    app.selectedValue = app.puzzle.board[newRow][newCol]
            elif app.allSingletons.checkMouseCollision(mouseX, mouseY):
                app.puzzle.playAllHintOnes()
        
    #mouse-only gameplay (setting and banning values buttons)
    if app.mouseMode:
        for setButton in app.mouseOnlyButtons[:10]:
            if (setButton.checkMouseCollision(mouseX, mouseY) and app.selectedCell != None):
                value = 0 if setButton.label == 'X' else int(setButton.label)
                row, col = app.selectedCell
                if (row, col) not in app.givenValues:
                    app.puzzle.set(row, col, value)
        for banButton in app.mouseOnlyButtons[10:]:
            if (banButton.checkMouseCollision(mouseX, mouseY) and app.selectedCell != None):
                value = int(banButton.label)
                row, col = app.selectedCell
                if (row, col) in app.puzzle.legals and (row, col) not in app.givenValues: 
                    if value in app.puzzle.legals[(row, col)]:
                        app.puzzle.ban(row, col, value)
                    else:
                        app.puzzle.unban(row, col, value)

    #screen buttons
    if app.goHome.checkMouseCollision(mouseX, mouseY):
        setActiveScreen('start')
    elif app.options.checkMouseCollision(mouseX, mouseY):
        setActiveScreen('help')
    elif app.save.checkMouseCollision(mouseX, mouseY):
        handleSaveAttempt(app)
        
    #ending the game is puzzle is complete
    if app.puzzle.board == app.puzzle.solvedBoard:
        app.gameOver = True

def board_onKeyPress(app, key):
    app.hintCells = []

    #key presses that change screens
    if key == 'o':
        setActiveScreen('help')
    elif key == 'escape':
        setActiveScreen('start')

    #key presses that play the game
    if not (app.mouseMode or app.gameOver):

        #banning/unbanning legals (press enter then 1-9)
        if key == 'enter':
            app.prevKey = key
            return
        elif (app.prevKey == 'enter' and app.selectedCell != None and
              key.isdigit()):
                row, col = app.selectedCell
                if (row, col) in app.puzzle.legals:
                    if int(key) in app.puzzle.legals[(row, col)]:
                        app.puzzle.ban(row, col, int(key), ownAction = True)
                    else:
                        app.puzzle.unban(row, col, int(key), ownAction = True)
                        
                app.prevKey = None
                return

        #toggling the display of legals
        elif key == 'L':
            if not app.showLegals:
                    app.toggleLegals.color = 'salmon'
                    app.toggleLegals.label = 'Hide Legals (L)'
            else:
                app.toggleLegals.color = 'lightBlue'
                app.toggleLegals.label = 'Show Legals (L)'
            app.showLegals = not app.showLegals

        # undo or redoing moves
        elif key == 'u':
            undone = app.puzzle.undo(app.undoList, app.redoList)
            if undone != None:
                app.puzzle = undone
        elif key == 'r':
            redone = app.puzzle.redo(app.undoList, app.redoList)
            if redone != None:
                app.puzzle = redone

        #saving the board
        elif key == 'p':
            handleSaveAttempt(app)

        #changing selected cell with arrow keys
        elif key in ['left', 'right', 'up', 'down']:
            if app.selectedCell == None:
                app.selectedCell = (0, 0)
                newRow, newCol = app.selectedCell
                app.regionCells = State.getAllRegions(newRow, newCol)
                app.selectedValue = app.puzzle.board[newRow][newCol]
            else:
                moveSelectedCellWithKeys(app, key)
                newRow, newCol = app.selectedCell
                app.regionCells = State.getAllRegions(newRow, newCol)
                app.selectedValue = app.puzzle.board[newRow][newCol]
        
        # 'h' for showing hints, 'H' for playing hints (only Hint 1 as of now)
        elif key == 'h':
           showHints(app)
        elif key == 'H':
            playHints(app)

        # 's' for playing a singleton, 'S' for playing all singletons
        if app.puzzle.diff != 'easy':
            if key == 's':
                playedSingleton = app.puzzle.playHintOne()
                if playedSingleton != None:
                    app.selectedCell = playedSingleton
                    newRow, newCol = app.selectedCell
                    app.regionCells = State.getAllRegions(newRow, newCol)
                    app.selectedValue = app.puzzle.board[newRow][newCol]
                else:
                    app.moreSingletons = False
            elif key == 'S':
                app.puzzle.playAllHintOnes() 
        
        #setting a value in a selected cell
        if app.selectedCell != None:
            row, col = app.selectedCell
            if ((row, col) not in app.givenValues and
                key.isdigit()):
                app.puzzle.set(row, col, key)
    
    #ending the game is puzzle is complete
    if app.puzzle.board == app.puzzle.solvedBoard:
        app.gameOver = True
    

#STARTER SCREEN
def start_onScreenStart(app):
    #image from https://img-9gag-fun.9cache.com/photo/aYgX4qq_700bwp.webp
    app.image = Image.open('images/catimage.jpeg')
    
    app.image = CMUImage(app.image)
    app.backColor = gradient('red', 'orange', 'yellow', 'green', 'blue', 'purple', start='top')
    app.rainbow = ['royalBlue', 'yellow', 'orchid']
    app.easy = Button(100, 350, 80, 40, label='easy mode', color = 'lightGreen',
                      labelSize = 14, labelColors = app.rainbow)
    app.medium = Button(200, 350, 110, 40, label='medium mode', color = 'lightBlue',
                       labelSize = 14, labelColors = app.rainbow)
    app.hard = Button(300, 350, 80, 40, label='hard mode', color = 'lemonChiffon',
                      labelSize = 14, labelColors = app.rainbow)
    app.expert = Button(50, 400, 95, 40, label='expert mode', color = 'violet',
                        labelSize = 14, labelColors = app.rainbow)
    app.evil = Button(150, 400, 95, 40, label='evil mode', color = 'pink',
                      labelSize = 14, labelColors = app.rainbow)
    app.manual = Button(250, 400, 95, 40, label='enter a board', color ='orange',
                        labelSize = 14, labelColors = app.rainbow)
    app.instructions = Button(350, 400, 90, 40, label='instructions', color='aquamarine',
                        labelSize = 14, labelColors = app.rainbow)
    app.startButtons = [app.easy, app.medium, app.hard, app.expert, app.evil, 
                        app.instructions, app.manual]
    
    app.manualMode = False

def start_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.backColor, opacity=60)
    Button.makeLabelPretty('Sudoku Party!', 200, 50, 40, app.rainbow[::-1])
    Button.makeLabelPretty('Created by Aidan Greenaway', 200, 85, 15, app.rainbow[::-1])
    drawImage(app.image, 200, 210, align = 'center', width = 200, height = 200)
    for button in app.startButtons:
        button.drawButton()

def start_onMousePress(app, mouseX, mouseY):
    if app.easy.checkMouseCollision(mouseX, mouseY):
        loadNewPuzzle(app, difficulty='easy')
    elif app.medium.checkMouseCollision(mouseX, mouseY):
        loadNewPuzzle(app, difficulty='medium')
    elif app.hard.checkMouseCollision(mouseX, mouseY):
        loadNewPuzzle(app, difficulty='hard')
    elif app.expert.checkMouseCollision(mouseX, mouseY):
        loadNewPuzzle(app, difficulty='expert')
    elif app.evil.checkMouseCollision(mouseX, mouseY):
        loadNewPuzzle(app, difficulty='evil')
    elif app.instructions.checkMouseCollision(mouseX, mouseY):
        setActiveScreen('instructions')
    elif app.manual.checkMouseCollision(mouseX, mouseY):
        loadNewPuzzle(app, manual = 'empty')
        app.manualMode = True
        setActiveScreen('manual')


#INSTRUCTION SCREEN
def instructions_onScreenStart(app):
    app.goHome4 = Button(200, 400, 75, 30, label ='Home (esc)', color= 'lightGreen', 
                         labelSize = 12)
    app.instructionButtons = [app.goHome4]

    app.instructionKeys = ['arrow keys', '1-9', '0', 'enter + 1-9', 's', 'S', 'h', 'H']
    app.instructionActions = ['change selected cell:', 'insert value:',
                              'clear a non-given cell:', 'ban/unban value:', '**play one singleton', 
                              '**play all singletons', 'show hint', 'play hint']
    app.mouseOnlyInstructions = ['In Mouse-Only Mode:', 'Click on cells to select them',
    '*Left column buttons (purple) insert values', '*Right column buttons (blue) ban/uban values']
    
def instructions_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.backColor, opacity = 60)
    drawRect(60, 50, 280, 325, fill = 'lightGray')
    drawLabel('INSTRUCTIONS', 200, 65, size = 20, bold = True)
    drawLabel('In Key-Only Mode:', 200, 90, size = 15)
    #key instructions
    labelY = 110
    instructionX = 200
    actionX = 80
    for i in range(len(app.instructionKeys)):
        instruction = app.instructionKeys[i]
        action = app.instructionActions[i]
        drawLabel(instruction, instructionX, labelY, size = 12, align = 'left')
        drawLabel(action, actionX, labelY, size = 12, align= 'left')
        labelY += 15
    #mouse instructions
    labelY = 260
    labelX = 80
    drawLabel('In Mouse-Only Mode:', 200, 235, size = 15)
    for i in range(1, len(app.mouseOnlyInstructions)):
        line = app.mouseOnlyInstructions[i]
        drawLabel(line, labelX, labelY, size = 12, align = 'left')
        labelY += 20
    drawLabel('* - not availabile in default gameplay', 80, 330, size = 12, align='left')
    drawLabel('** - not available for easy level boards', 80, 350, size = 12, align = 'left')

    for button in app.instructionButtons:
        button.drawButton()

def instructions_onMousePress(app, mouseX, mouseY):
    if app.goHome4.checkMouseCollision(mouseX, mouseY):
        setActiveScreen('start')

def instructions_onKeyPress(app, key):
    if key == 'escape':
        setActiveScreen('start')

#HELP SCREEN
def help_onScreenStart(app):
    app.goHome2 = Button(100, 425, 110, 25, color = 'lightGreen', 
                        label = 'Exit to Home (esc)', labelSize = 12)
    app.backToBoard = Button(300, 425, 75, 25, color = 'orange',
                        label = 'Back (b)', labelSize = 12)
    app.helpButtons = [app.goHome2, app.backToBoard]

def help_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.backColor, opacity = 60)
    #displaying selected game mode
    autoLegals = 'on' if app.puzzle.autoLegals else 'off'
    keyMode = 'on' if app.keyboardMode else 'off'
    mouseMode = 'on' if app.mouseMode else 'off'
    labels = [f'Updating Legals (press l to toggle): {autoLegals}', 
              f'Keyboard-only Mode (press k to toggle): {keyMode}', 
              f'Mouse-only Mode (press m to toggle): {mouseMode}']
    drawRect(75, 35, 250, 150, fill = 'lightGray')
    drawRect(70, 200, 260, 200, fill = 'lightGray')
    drawLabel('OPTIONS', 200, 60, size = 20, bold=True)
    labelX = 80
    labelY = 100
    for label in labels:
        drawLabel(label, labelX, labelY, size = 12, align = 'left')
        labelY += 30
    #drawing instructions for given game-mode
    drawLabel('INSTRUCTIONS', 200, 225, size = 20, bold = True)
    labelX, labelY = 80, 270
    if app.keyboardMode: 
        drawLabel('In Key-Only Mode:', 200, 250, size = 14)
        instructionX = 200
        for i in range(len(app.instructionKeys)):
            instruction = app.instructionKeys[i]
            action = app.instructionActions[i]
            drawLabel(instruction, instructionX, labelY, size = 12, align = 'left')
            drawLabel(action, labelX, labelY, size = 12, align= 'left')
            labelY += 15
        drawLabel('** - not available for easy level boards', labelX, 390, size = 11, align = 'left')
    elif app.mouseMode:
        drawLabel('In Mouse-Only Mode:', 200, 250, size = 14)
        for i in range(1, len(app.mouseOnlyInstructions)):
            line = app.mouseOnlyInstructions[i] if i < 2 else app.mouseOnlyInstructions[i][1:]
            drawLabel(line, labelX, labelY, size = 12, align = 'left')
            labelY += 20
    else:
        drawLabel('Default Instructions:', 200, 250, size = 14)
        instructionX = 200
        for i in range(len(app.instructionKeys)):
            instruction = app.instructionKeys[i]
            if i == 0: instruction = instruction + '/mouse click'
            action = app.instructionActions[i]
            drawLabel(instruction, instructionX, labelY, size = 12, align = 'left')
            drawLabel(action, labelX, labelY, size = 12, align= 'left')
            labelY += 15
        drawLabel('** - not available for easy level boards', labelX, 390, size = 11, align = 'left')

    for button in app.helpButtons:
        button.drawButton()

def help_onMousePress(app, mouseX, mouseY):
    if app.goHome2.checkMouseCollision(mouseX, mouseY):
        setActiveScreen('start')
    if app.backToBoard.checkMouseCollision(mouseX, mouseY):
        setActiveScreen('board')

def help_onKeyPress(app, key):
    if key == 'escape':
        setActiveScreen('start')
    elif key == 'b':
        setActiveScreen('board')
    elif key == 'l':
        app.puzzle.autoLegals = not app.puzzle.autoLegals
    elif key == 'k':
        app.keyboardMode = not app.keyboardMode
        if app.keyboardMode and app.mouseMode:
            app.mouseMode = False
        showMouseOnlyButtons(app)
    elif key == 'm':
        app.mouseMode = not app.mouseMode
        if app.keyboardMode and app.mouseMode:
            app.keyboardMode = False
        showMouseOnlyButtons(app)


#MANUAL BOARD ENTRY SCREEN
def manual_onScreenStart(app):
    app.playBoard = Button(100, 390, 115, 30, color = 'pink', 
                           label = 'Play this board! (p)', labelSize = 12)
    app.fileInput = Button(300, 390, 115, 30, color = 'orange', 
                           label = 'Input a text file! (f)', labelSize = 12)
    app.goHome3 = Button(200, 390, 75, 30, color = 'lightGreen', 
                        label = 'Home (esc)', labelSize = 12)
    app.manualButtons = [app.goHome3, app.playBoard, app.fileInput]
    app.manualLoadingError = False
    #from image-demos.zip on https://www.cs.cmu.edu/~112-3/notes/term-project.html
    #gif from https://tenor.com/view/oops-facepalm-shimi-pawsonify-silly-cat-gif-17969153
    app.errorSprites = loadAnimatedGif('images/errorLoadingBoardGIF.gif')
    app.errorSpriteCounter = 0

#from image-demos.zip on https://www.cs.cmu.edu/~112-3/notes/term-project.html
def manual_onStep(app):
    app.errorSpriteCounter = (1 + app.errorSpriteCounter) % len(app.errorSprites)

def manual_redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill=app.backColor, opacity = 60)
    for button in app.manualButtons:
        button.drawButton()
    drawBoard(app)
    drawBoardBlocks(app)
    if app.manualLoadingError:
        drawRect (200, 200, 350, 200, align= 'center', fill = 'lightBlue')
        drawLabel('There was an error loading your puzzle!', 200, 125, size = 15, bold = True)
        drawLabel('Make sure to follow the manual input instructions!', 200, 270, size = 15)
        drawLabel('(Press any key or click to continue)', 200, 285, size = 10)
        sprite = app.errorSprites[app.errorSpriteCounter]
        pilImage = sprite.image
        drawImage(sprite, 200, 200, align = 'center', width = pilImage.width//4, 
                  height = pilImage.height//4)

def manual_onMousePress(app, mouseX, mouseY):
    if app.manualLoadingError: app.manualLoadingError = False
    selectedCell = getCell(app, mouseX, mouseY)
    if selectedCell != None:
        app.selectedCell = selectedCell
    elif app.goHome3.checkMouseCollision(mouseX, mouseY):
        setActiveScreen('start')
    elif app.playBoard.checkMouseCollision(mouseX, mouseY):
        loadNewPuzzle(app, manual = 'ready')
    elif app.fileInput.checkMouseCollision(mouseX, mouseY):
        filename = app.getTextInput("Enter the exact filename of your board. Ensure the board is placed in the 'board' folder!")
        pathToFile = f'boards/{filename}'
        loadNewPuzzle(app, manual = 'file', manualFile = pathToFile)

def manual_onKeyPress(app, key):
    if app.manualLoadingError: app.manualLoadingError = False
    if app.selectedCell != None:
        row, col = app.selectedCell
        if key.isdigit():
            app.puzzle.set(row, col, key)
            app.givenValues.append((row, col))
    if key in ['left', 'right', 'up', 'down']:
            if app.selectedCell == None:
                app.selectedCell = (0, 0)
            else:
                moveSelectedCellWithKeys(app, key)
    elif key == 'f':
        filename = app.getTextInput("Enter the exact filename of your board. Ensure the board is placed in the 'board' folder!")
        pathToFile = f'boards/{filename}'
        loadNewPuzzle(app, manual = 'file', manualFile = pathToFile)
    elif key == 'escape':
        setActiveScreen('start')

        
#HELPERS FOR LOADING BOARD PAGE BASED ON MODE/DIFFICULTY, SAVING BOARD
def loadNewPuzzle(app, difficulty= None, manual = None, manualFile = None):
    if manual == 'empty': #preparing an empty app.puzzle for manual input
        board = [[0]*9 for _ in range(9)]
        app.puzzle = State(board, None)
        app.givenValues = []
    else:
        if manual == None: #loading an app.puzzle from stored txt files
            filename = random.choice(app.puzzleDict[difficulty])
            board = fileToBoard(filename)
            app.puzzle = State(board, difficulty)

        elif manual == 'ready': #app.puzzle is already created by manual input
            app.puzzle = State(app.puzzle.board, 'unknown difficulty')

        elif manual == 'file': #user tries to use a txt file as input
            try:
                board = fileToBoard(manualFile)
                app.puzzle = State(board, 'unknown difficulty') 
                app.manualLoadingError = False
            except: 
                app.manualLoadingError = True
                return

        app.givenValues = getInitialValues(app.puzzle.board) # {(row, col) ....}

    app.gameOver = False
    app.selectedCell = app.selectedValue = None
    app.regionCells = []
    app.currRow = app.currCol = app.currBlock = None
    app.hintCells = []
    app.lastShowedHint2 = app.lastPlayedHint2 = None
    app.wrongCells = []
    app.undoList = [] #State copies oldest --> newest
    app.redoList = [] #State copies oldest --> newest
    
    app.showLegals = False
    app.toggleLegals.color = 'lightBlue'
    app.toggleLegals.label = 'Show Legals (L)'
    
    setButtonsForDifficulty(app, difficulty)
    setActiveScreen('board')

def setButtonsForDifficulty(app, difficulty):
    if difficulty != 'easy':
        app.boardButtons.extend([app.singleton, app.allSingletons])
    else:
        while app.singleton in app.boardButtons:
            app.boardButtons.remove(app.singleton)
        while app.allSingletons in app.boardButtons:
            app.boardButtons.remove(app.allSingletons)

def handleSaveAttempt(app):
    filename = app.getTextInput("Save board to 'boards' folder as?")
    try:
        path = f"boards/{filename}"
        string = listIntoString(app.puzzle.board)
        writeFile(path, string)
    except: 
        return

#tries hints in successive order 
def showHints(app):
    hint1 = app.puzzle.showHintOne()
    if hint1 != None:
        app.hintCells = [hint1]
        return
    hint2 = app.puzzle.showHintTwo()
    # hint 2 may become repitive, this allows hint 3 to be tried before a
    # repeat of hint 2 comes up.
    if (hint2 != None) and (hint2 != app.lastShowedHint2):
        app.hintCells = hint2[0]
        app.lastShowedHint2 = hint2
        return
    hint3 = app.puzzle.lookForHintThree()
    if (app.puzzle.diff != 'easy') and (hint3 != None):
        app.hintCells = hint3[0]
        return
    #if hint 2 exists, was already shown and not played, show hint 2 again
    if (hint2 != None) and (hint2 != app.lastPlayedHint2):
        app.hintCells = hint2[0]
        app.lastHint2 = hint2
    return

#plays hints in successive order
def playHints(app):
    #singleton hint
    hint1 = app.puzzle.playHintOne()
    if hint1 != None:
        app.selectedCell = hint1
        newRow, newCol = app.selectedCell
        app.regionCells = State.getAllRegions(newRow, newCol)
        app.selectedValue = app.puzzle.board[newRow][newCol]
        return
    #tuples hint
    hint2 = app.puzzle.showHintTwo()
    #attempts to circumvent repetitive hint 2's if possible
    if (hint2 != None) and (hint2 != app.lastPlayedHint2):
        cells, legals = hint2
        app.hintCells = cells
        app.lastPlayedHint2 = hint2
        app.puzzle.playHintTwo(cells, legals)
        return
    #'locked' candidate hint from https://www.stolaf.edu/people/hansonr/sudoku/explain.htm
    hint3 = app.puzzle.lookForHintThree()
    if hint3 != None:
        app.hintCells = hint3[0]
        moveList = hint3[1]

        for i in range(len(moveList)):
            row, col, value = moveList[i]
            ownAction = True if i == 0 else False
            app.puzzle.ban(row, col, value, ownAction = ownAction)
    return

#from image-demos.zip on https://www.cs.cmu.edu/~112-3/notes/term-project.html
def loadAnimatedGif(path):
    pilImages = Image.open(path)
    if pilImages.format != 'GIF':
        raise Exception(f'{path} is not an animated image!')
    if not pilImages.is_animated:
        raise Exception(f'{path} is not an animated image!')
    cmuImages = [ ]
    for frame in range(pilImages.n_frames):
        pilImages.seek(frame)
        pilImage = pilImages.copy()
        cmuImages.append(CMUImage(pilImage))
    return cmuImages

def main():
    app = runAppWithScreens(initialScreen = 'start', height = 450)

main() 
