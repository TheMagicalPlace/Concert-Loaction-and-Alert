from tkinter import *

from InitialSetup import setup_data





class StartupInterface(Frame):
    """Initializes required user data on first time use"""
    def __init__(self,master=None):
        super().__init__(master)
        try:
            with open('user_settings', 'r') as settings:
                pass
        except FileNotFoundError:
            self.top_interface = Tk()
            self.top_interface.mainloop()
        else:
            self.top_interface = Tk()
            self.top_interface.mainloop()



    def main_menu(self):
        self.interface.addLabel('opening','First time setup.')
        self.interface.setLabelBg("opening", "red")
        self.interface.addLabel('location_info','Since this is your first time using this app, some startup information'
                                                'is required.')
        self.interface.addLabel('location','Please enter your location in the following format: City, State, Country')
        self.interface.addLabelEntry("Location (City, State, Country)")
        self.interface.addLabel('band_desc', 'Please the bands you would like to track in the following format: Band1,Band2,...')
        self.interface.addLabelEntry("Bands")
        self.interface.addNamedButton('YEEEEEEEEEEET','YEEEEEEEEEEET',self.press)
        self.interface.go()

    def press(self,button):
        if button == "Cancel":
            self.interface.stop()
        else:
            location = self.interface.getEntry("Location (City, State, Country)")
            bands = self.interface.getEntry("Bands")
            bands = [band.lstrip().rstrip() for band in bands.split(',')]
            setup = setup_data()
            setup(location,bands)
            print("location:", location, "Bands", bands)



if __name__ == '__main__':
    test = StartupInterface()
    #test.main_menu()
