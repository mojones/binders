import sys
#import IPython
import copy
import re
import inspect
import os
import colorama
from colorama import Fore, Back, Style
import builtins


backup_open = builtins.open

#backup_showtraceback = IPython.core.interactiveshell.InteractiveShell.showtraceback

# list of variable names that we don't want to suggest to the user
variable_name_blacklist = []

# things that are part of the tool itself
variable_name_blacklist.extend('my_excepthook handle_error backup variable_name_blacklist levenshteinDistance Fore Back Style format_message'.split(' '))

# things that are part of ipython
variable_name_blacklist.extend('exit get_ipython quit In Out'.split(' '))

def levenshteinDistance(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def format_message(message, traceback_follows = True):
    parts = message.split('`')
    result = Style.RESET_ALL + Fore.BLUE
    for i, part in enumerate(parts):
        if i ==0:
            result += part
        elif i % 2 == 1:
            result += Fore.RED + part + Fore.BLUE
        else:
            result += part
    if traceback_follows:
        result += '\nThe real Python error message follows...'
    result += Style.RESET_ALL
    return result


def handle_error(type, myerror, traceback):
    #print('handling error', type, myerror, traceback)
    #print(traceback.tb_frame.f_globals.keys())

    # for e.g. 4 + 'foo'
    if type == TypeError and myerror.args[0] == "unsupported operand type(s) for +: 'int' and 'str'":
        message = """
Error: you have tried to use plus to add together a number and a string.
You probably need to either turn the number into a string using `str()`, or turn the string into a number using `int()` or `float()`."""
        print(format_message(message))
        return None

    # for typos
    if type == NameError:
        # see if if looks like a typo
        typo_match = re.search("name '(.+)' is not defined", myerror.args[0])
        if typo_match:
            wrong_name = typo_match.group(1)

            # get a list of things that we think the user meant to type
            # starting with a global list of variables
            candidates = [name for (name, value) in traceback.tb_frame.f_globals.items()
                          if name[0] !='_'  # exclude variable names starting with _
                          and name not in variable_name_blacklist   # exclude things that we know are going to show up
                          and not inspect.ismodule(value) # exclude things that are names of imported modules
                         ]

            # sort the suggested names so that the most likely typos are first
            candidates.sort(key = lambda x : levenshteinDistance(x, wrong_name))
            #candidates = ['a', 'b']
            message = """
I didn't recognize the word `{}`. If this is a variable or function name, check the spelling and capitalization.
Here are the variables that are currently defined - maybe you meant one of these:

`{}`

Or maybe it's supposed to be a string, in which case you need to surround it with quotes like this:

`"{}"`
""".format( wrong_name,
         '\n'.join(candidates),
          wrong_name)

            print(format_message(message))
            return None
        else:
            print('some other kind of NameError, check it out')

    # handle wrong file path
    if type(myerror) == FileNotFoundError and myerror.strerror == 'No such file or directory':
        message = """
Error: I can't find the file called `{}`. The working directory is
    `{}`
so the full path you're trying to open is
    `{}`
""".format(
        myerror.filename,
            os.getcwd(),
            os.path.join(os.getcwd(), myerror.filename)
            )

        print(format_message(message))
        return None

    # handle trying to call method on wrong object
    if type == AttributeError:
        attribute_match = re.search("'(.+)' object has no attribute '(.+)'", myerror.args[0])
        if attribute_match:
            wrong_type = attribute_match.group(1)
            trying_to_run = attribute_match.group(2)


            candidates = [name for (name, value) in traceback.tb_frame.f_globals.items()
                          if name[0] !='_'  # exclude variable names starting with _
                          and name not in variable_name_blacklist   # exclude things that we know are going to show up
                          and not inspect.ismodule(value) # exclude things that are names of imported modules
                          and hasattr(value, trying_to_run)
                         ]
            message = """
Error: you have tried to run the `{}` function on the wrong type of object.
Here is a list of the variables that you can run `{}` on:

`{}`

""".format(
                trying_to_run,
            trying_to_run,
            '\n'.join(candidates))

            print(format_message(message))



def my_excepthook(type, value, traceback):
    #print("hooking")
    myerror = sys.exc_info()[1]
    #print(sys.exc_info()[2].tb_frame.f_locals.keys())
    handle_error(type, value, traceback)
    #print('done handling error')
    backup_showtraceback(type, value, traceback)

class HelpfulFile(object):
    """
    Wrapper round inputwrapper which delegates everything, but intercepts some method calls to print helpful messages
    """

    def __init__(self, real_file):
        self.real_file = real_file
        self.times_read = 0
        #print('initialized!')

    def __getitem__(self, item):
       result = self.real_file[item]
       return result

    def __getattr__(self, item):
       result = getattr(self.real_file, item)
       return result

    def __repr__(self):
       return repr(self.real_file)

    def __str__(self):
        message = "Warning: you are printing the file object for `{}`, not the contents of the file.".format(self.real_file.name)
        print(format_message(message))
        return self.real_file.__str__()

    def check_if_exhausted(self):
        if self.times_read > 0:
            message = """Warning: you have read the contents of the file `{}` multiple times (either by calling `read()` or by using it in a loop). After the first time, the file will always appear to be empty since Python is already at the end.

Try re-opening the file, or (better) store the contents with `readlines()`""".format(self.real_file.name)
            print(format_message(message), traceback_follows=False)
        self.times_read += 1

    def read(self, *args):
        self.check_if_exhausted()
        return self.real_file.read(*args)

    def __iter__(self):
        self.check_if_exhausted()
        return iter(self.real_file)

def my_open(*args):
    #print('opening!')
    real_file = backup_open(*args)
    hf = HelpfulFile(real_file)
    return hf


#def start_working():
    #IPython.core.interactiveshell.InteractiveShell.showtraceback = my_excepthook
    #builtins.open = my_open
    #print(vars().keys())

def stop_working():
    #IPython.core.interactiveshell.InteractiveShell.showtraceback = backup_showtraceback
    builtins.open = backup_open

backup_showtraceback = sys.excepthook
builtins.open = my_open
sys.excepthook = my_excepthook
print("Easy help module runining; don't use this in production code!")
