Welcome to Suduko Party! created by Aidan Greenaway

Introduction/About the App:

This project is a fun, colorful app that allows the user to play sudoku games with 
various additional features. The app will self-solve boards and check the user's 
progress mid-game, as well as giving the user legal values and three types of hints. 
The app also supports user-imported boards (entered graphically or with text files) 
as well as the ability to save boards mid-game and complete them at another time!

How to Run/File Details:

To run the app please install cmu_graphics and its subrequisite packages.
Here are the basic details and functions of each of the included files/folders:

sudokuAppFxns.py --> the main build of the app, run this to play the game!
helpersAndClasses.py --> includes helper functions and custom classes
pipCommand.py --> use this to install libraries if needed (especially cmu_graphics!)
removingExtraFiles.py --> use this to remove extra DS files stored in boards folder (on Mac)
readme.txt --> what you are reading now!
images --> folder of gif and jpegs used throughout the project 
           (images cited when implemented in sudokuAppFxns.py)
boards --> folder of txt files that contain the game's boards, users can save 
           boards non-included or partially-solved here to then play them!

Shortcuts to examine extra features:

In the 'enter a board' screen, load the text file 'demoHintThree'
The first available hint is a doublet tuplet hint, but the next hint is 
and example of the app's additional third 'locked candidate' hint, explained here:

https://www.stolaf.edu/people/hansonr/sudoku/explain.htm

