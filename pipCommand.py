import sys, os

#from https://www.cs.cmu.edu/~112-3/notes/term-project.html
def runPipCommand(pipCommand, pipPackage=None):
    # get quoted executable path
    quote = '"' if 'win' in sys.platform else "'"
    executablePath = f'{quote}{sys.executable}{quote}'
    # first upgrade pip:
    command = f'{executablePath} -m pip -q install --upgrade pip'
    os.system(command)
    # input the package from the user if it's not supplied in the call:
    if pipPackage == None:
        pipPackage = input(f'Enter the pip package for {pipCommand} --> ')
    # then run pip command:
    command = f'{executablePath} -m pip {pipCommand} {pipPackage}'
    os.system(command)

#runPipCommand('install', 'cmu_graphics') # <-- uncomment and run here if needed!