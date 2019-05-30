#!/usr/bin/python3

# 201904

# corre o tensorboard e abre uma janela chrome em modo app.
# Quando o user fechar a janela, mata o tensorboard
# Se user interromper com Control+C, termina o tensorboard e fecha a janela do chrome.

import subprocess, re, io, time, sys, os, signal
from threading import Thread

from util import *

# this will be called when user presses control C
def interrupted(*args):
    print("Interrupted with sigint!")

    print("killing tensorboard")
    tensorboard_proc.kill()

    chrome_kill()
    
    print("Exiting")
    sys.exit(1)

# open chrome window, wait until it is closed by user, then kill tensorboard process and exit
def chrome_window():
    # Now I can launch the chrome window as an app. That means it will have its own window.
    # This command will return immediatly
    cmd = ["google-chrome", "--app="+ URL]
    print("Launching Chrome", str(cmd))
    subprocess.Popen(cmd)

    DELTATIME = 0.1
    # First wait until the window is visible
    while not check_window(TITLE):
        time.sleep(DELTATIME)

    print("Window opened")

    # Now wait until it is closed
    while check_window(TITLE):
        #print("test")
        time.sleep(DELTATIME)

    print("Chrome window closed")
    
    # This is one of the ways to end this script. The other is when
    # user presses control+C or tensorboard subprocess exists
    print("killing tensorboard")
    tensorboard_proc.kill()

    # No need to call sys.exit(0) ?
    # if I do it here, will get this error
    # Exception ignored in: <module 'threading' from '/usr/lib/python3.7/threading.py'>

# closes chrome window, if exists
def chrome_kill():
    win = check_window(TITLE)
    if win:
        print("Closing chrome window")
        win.close(time.time())

# captures control-C
signal.signal(signal.SIGINT, interrupted)

# Parse command line. I'm interested in logdir and window_title options.
# All others are passed as is to tensorboard command

LOGDIR=None
TITLE=None

#args = sys.argv[1:]

params = Params()

LOGDIR = params.getparam("logdir")
if LOGDIR is None:
    error("Logdir required\n")

print("LOGDIR", LOGDIR)

#print("NEWLOGDIR", logdir_to_abs(LOGDIR))
#sys.exit(1)

# title is important because it is how we locate the browser window
TITLE = params.getparam("title")
if TITLE is None:
    # I need the title, so create the option

    # The user may have multiple terminals in difeferent folders and
    # use --logdir=. in all of then. If we don't convert "." to abspath,
    # it will all have the same name
    TITLE = "TensorBoard %s" % logdir_to_abs(LOGDIR)
    params.add(["--window_title", TITLE])

# title must be unique!
test = check_window(TITLE)
if test is not None:
    error("There is another window with the title '%s'" % TITLE)

PORT = params.getparam("port")
if PORT is None:
    # this will make tensorboard to use an available port.
    # Makes sense to set this as default, because user doesn't need to care about the port, since
    # the browser will automatically open the page for him
    params.add(["--port=0"])

if "--firefox" in params.args:
    error("firefox not supported")

if "--chrome" in params.args:
    # don't send this param to tensorboard
    params.args.remove("--chrome")
else:
    import webbrowser
    default_browser = webbrowser.get()
    if default_browser.name != 'google-chrome':
        error("Default browser %s not suported. Please use --chrome" % default_browser.name)

# If tensorboard is not on the PATH, this will throw an exception.
# If there is an tensorboard error... or logdir doens't exist...

# TODO verificar se deu erro. Pode ser que nao tenha o ambiente do TF instalado
cmd = ["tensorboard"] + params.args
print("Launching tensorboard", str(cmd))
try:
    tensorboard_proc = subprocess.Popen(cmd, stderr=subprocess.PIPE)
except:
    error("Can't run tensorboard")

# Now I have to parse the tensorboard stderr until I find the url
stderr = io.TextIOWrapper(tensorboard_proc.stderr, encoding='utf8')

URL = None

while True:
    # line includes newline at end
    line = stderr.readline()

    if line == "":
        # EOF. tensorboard exited
        poll = tensorboard_proc.poll()
        if poll != None:
            error("tensorboard error %i" % poll)

        chrome_kill()

        sys.exit(0)
        
    # echos to mystderr
    sys.stderr.write(line)
    
    # Find a line like
    # TensorBoard 1.13.1 at http://freixo:6006 (Press CTRL+C to quit)
    # it is the url we need to open the chrome window
    m = re.match(r'TensorBoard.*at.*(http://[a-zA-Z0-9]+:[0-9]+)', line)
    if m and not URL:
        URL = m.group(1)
        print("URL", URL)

        # need a separate thread
        Thread(target=chrome_window).start()
        




