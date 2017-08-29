
import subprocess;

case = input('Choose a type of comparison (1, 2, or 3):\n \
              1: Vary 1st metastatic site \n \
              2: Vary 2nd metastatic site \n \
              3: Vary 1st and 2nd metastatic sites \n')

print 'You have chosen Option', case, '\n'

def varyFirst():
    print 'Vary 1st metastatic site \n'
    subprocess.check_call(['python2.7','/Users/Confetti/Documents/testprog2.py'])
def varySecond():
    print 'Vary 2nd metastatic site \n'
    os.system('/Users/Confetti/Documents/testprog3.py')
def varyBoth():
    print 'Vary 1st and 2nd metastatic sites \n'
    os.system('/Users/Confetti/Documents/testprog4.py')
    
options = {1 : varyFirst, 
            2 : varySecond, 
            3: varyBoth,
}

try: options[case]()
except KeyError:
    print 'This option is not available.\n'
    pass

