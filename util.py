
import sys, os, re

import gi
gi.require_version('Wnck', '3.0') 
from gi.repository import GLib, Wnck, Gtk  

# find a window with given title. Returns window object or None
def check_window(title):
    # If I dont do this get_windows each time, will return always the same thing
    # This will always return immediatly
    Gtk.main_iteration_do(False)
    
    screen = Wnck.Screen.get_default()
    screen.force_update()

    # https://lazka.github.io/pgi-docs/#Wnck-3.0/classes/Window.html#Wnck.Window.close
    wins = screen.get_windows()

    for win in wins:
        if win.get_name() == title:
            return win
    return None

def error(msg):
    sys.stderr.write(msg + "\n")
    sys.exit(0)


# Convert logdir paths to absolute. Don't change urls
# Support multiple dirs like
# --logdir=name1:/path/to/logs/1,name2:relpath2,name3:gs://mybucket/ola`
def logdir_to_abs(logdir):
    def _conv_url(u):
        if re.match(r'^\w+://.*', u):
            # is a url
            return u
        else:
            return os.path.abspath(u)

    newels = []
    for el in re.split(",", logdir):
        m = re.match("(\w+):(.*)", el)
        if m:
            newels.append(m.group(1)+":"+_conv_url(m.group(2)))
        else:
            newels.append(_conv_url(el))

    return ",".join(newels)

# This helps to parse some args and leave the others intact (that will be the params to tensorboard).
# Maybe could use this? Is it possible to use argparse to capture an arbitrary set of optional arguments? - https://stackoverflow.com/questions/37367331/is-it-possible-to-use-argparse-to-capture-an-arbitrary-set-of-optional-arguments
class Params:
    def __init__(self):
        self.args = sys.argv[1:]
        if self.args == ["-h"]:
            error("Use: %s --logdir=<logdir> <other tensorboard options...>" % os.path.basename(sys.argv[0]))

    def getparam(self, name):
        for a, arg in enumerate(self.args):
            if arg == "--%s" % name and a + 1 < len(self.args):
                return self.args[a + 1]
            elif arg.startswith("--%s=" % name):
                return arg[len("--%s=" % name):]
        return None

    def add(self, newparams):
        self.args.extend(newparams)

