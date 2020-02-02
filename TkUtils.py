from tkinter import *
from tkinter.ttk import *
from typing import List

class TextFrame:



    def __init__(self,master,text,no_of_buttons=1,labelstyle : str =None, framestyle : str = None):
        fstyle,lstyle = self._setup_styles(framestyle,labelstyle)
        self.main = Frame(master=master,width=600,style=fstyle)
        self.labelframe = Frame(master=self.main,width=580,height=360,style=lstyle)
        self.label = Label(master=self.labelframe,text=text, style=lstyle)
        Frame(self.main,height=20).grid(row=0) # spacer



        sp1 = Frame(self.main,width=10)
        sp1.grid(row=1,column=0)
        sp1.propagate(False)
        self.labelframe.grid(row=1)



        self.label.pack()


        Frame(self.main, height=10).grid(row=2)  # spacer
        self.labelframe.propagate(False)
        #self.main.propagate(False)
        self._setup_buttons(no_of_buttons)
        self.main.pack()

    def _setup_styles(self,framestyle,labelstyle):
        """sets up the styles used for the generic frames if specified, or defaults to the presets here"""
        if framestyle is None:
            Style().configure('default.TFrame',)
            fstyle = 'default.TFrame'
        else:
            fstyle = framestyle
        if labelstyle is None:
            Style().configure('default.TLabel',wraplength=500,font='arial 11', background='white',border=5,relief=SOLID)
            lstyle = 'default.TLabel'
        else:
            lstyle = labelstyle
        return fstyle,lstyle

    def _setup_buttons(self,no):
        self.buttons = []
        r = 0
        c = 0
        buttonframe = Frame(self.main)
        for i in range(no):
            print(r,(i+1)%5,i)

            self.buttons.append(Button(buttonframe,text='yeet').grid(column=c,row=r))
            if not (i+1)%8:
                r +=1
                c = 0
            else:
                c+=1
        buttonframe.grid(row=3)

if __name__=='__main__':
    root = Tk()
    TextFrame(root,'text',no_of_buttons=3)
    root.mainloop()
    pass