# Run tensorboard as if it was a desktop application

I created this small script to make more easy to run tensorboard. Before, I had to launch tensorboard 
from the command line, copy the url and open it in a browser tab. And to terminate I had to go to
both places also.

With this script it is much simpler.

Use:
`tensorboard_viewer.sh --logdir=/tmp/mycheckpoints <other tensorboard options...>`

This will launch tensorboard, and open a Google Chrome app mode window (with no toolbars) connected to the tensorboard url.

There are two ways to terminate it: 
- Close the chrome window and tensorboard will also be killed.
- Or interrupt the command line with Ctrl+C and the chrome window will close.

Requirements:
Google chrome, Python3, Gtk, Wnck...

Only tested in Linux (Ubuntu)!

TODO: support other browsers like Firefox if it supports app windows?
