''' authored by abs_saurabh on 14th August 2016
 this module is part of PT_automation project
 
This module contains user prompts
'''

import Tkinter
import tkMessageBox
import tkFileDialog
root = Tkinter.Tk()
root.withdraw()

options = {}

options['initialdir'] = '/home/kickass/Documents/LiClipseWorkspace/PT_automation'
options['mustexist'] = 'True'
options['parent'] = root


def prompt_at_end(message):
    tkMessageBox.showinfo("PT Automation", message)

def prompt_at_start():
    tkMessageBox.showinfo("PT Automation", "Let's get down to logic replacement")
    
# prompt the user for auto directory    
def prompt_for_auto():
    options['title'] = 'Choose directory for auto generated checks'
    auto_dir =  tkFileDialog.askdirectory(**options)
    return auto_dir
 
#ask the users for manual checks directory
def prompt_for_manual():
    options['title']="Choose directory for manual checks"
    manual_dir = tkFileDialog.askdirectory(**options)
    return manual_dir