#
# GuiTest.py
#
# A short demonstration of the use of the TK GUI under Python
# Malevol3nt
#
 
def console_msg(*msg):
    RPR_ShowConsoleMsg(str(msg) + '\n' + '\n')
 
import sys
sys.argv=["Main"]
 
 
import tkinter
 
class Application(tkinter.Frame):
    def AddEnv(self):
        pass
 
    def createWidgets(self):
        self.QUIT = tkinter.Button(self)
        self.QUIT["text"] = "Hello!"
        self.QUIT["command"] =  self.displayMessage1
        self.QUIT.pack({"side": "left"})
 
        self.hi_there = tkinter.Button(self)
        self.hi_there["text"] = "Click Me!"
        self.hi_there["command"] = self.displayMessage2
        self.hi_there.pack({"side": "left"})
 
    def __init__(self, master=None):
        tkinter.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
 
    def displayMessage1(self):
        console_msg("Hello World!")
 
    def displayMessage2(self):
        console_msg("You clicked a button!") 
 
root = tkinter.Tk()
app = Application(master=root)
app.mainloop()
