
from time import sleep
import datetime
import re
import Spotify_API_Integration as spot
from InitialSetup import LocatorSetup,LocatorMain
from ConcertScraper import ConcertFinder as CFinder
from tkinter import *
import sqlite3 as sqlite
import json
from copy import copy
import threading

class FirstTimeStartup:
    spotifyapp = None
    """Runs through the first time setup GUI"""
    def __init__(self,parent):
        self.spotifyapp = None
        self.root = parent
        self.user_data_setup = LocatorSetup()
        self.user_data_setup = self.user_data_setup()

        # Attempts to prime the user_data_setup coroutine, if it returns a StopIteration user data is already present
        # and the initial setup code is not run (outside instancing the class)
        try:
            next(self.user_data_setup)
        except StopIteration:
            parent.destroy()
            return
        else:
            self.message1(parent)
            parent.mainloop()

    # TODO - the 'startup' Tk() instance is a global variable and really, really does not need to be explicitly sent to each function
    def message1(self,startup):
        """This does nothing other than note that the program has been started"""
        def message1_terminate(event):
            startup.update()
            sleep(1)
            frame1.destroy()
            self.message2(startup)
        frame1 = Frame(startup)
        message1 = Label(frame1, text='Performing First Time Startup')
        message1.pack()
        message1.bind('<Visibility>', message1_terminate)
        frame1.pack()

    def message2(self,startup):
        """Notes down user location"""
        def message2_button(event):
            val = location_input.get()
            print(val)
            self.user_data_setup.send(val)
            frame2.destroy()
            self.spotify_int(startup)
            return val

        frame2 = Frame(startup)
        message2text = ' In order to only keep track of nearby concerts, your location is requred. Please input' \
                       'the location you would like to track from in the form City,State. Note that this application is' \
                       'currently limited to only United States residents'
        message2 = Label(frame2, text=message2text,wraplength=500)
        location_input = Entry(frame2)
        location_input_button = Button(frame2)
        location_input_button.bind('<Button-1>', message2_button)
        startup.update()
        message2.pack(), location_input.pack(), location_input_button.pack()
        frame2.pack()

    # These methods are run sequentially if spotify integration is selected

    def spotify_int(self,startup):

        def spotint_yes_button(event):
            print('yes registered')
            spotint.destroy()
            startup.update()
            self.spotify_setup_user_input(startup)
            pass
        def spotint_no_button(event):
            print('no registered')
            spotint.destroy()
            self.manual_band_input(startup)
            pass

        spotint = Frame(startup)
        spotint_text = Label(spotint,text='Would you like to use one (or more) of your spotify playlists in order to '
                                          'determine what bands to track?',wraplength=500)
        spotint_yes = Button(spotint,text='Yes')
        spotint_no = Button(spotint,text='No')
        spotint_yes.bind('<Button-1>',spotint_yes_button)
        spotint_no.bind('<Button-1>', spotint_no_button)
        spotint_text.pack(),spotint_yes.pack(),spotint_no.pack()
        spotint.pack()

    def spotify_setup_user_input(self,startup):
        def spotint_send_button(event):

            user_id = spot_usrsetup_field.get()
            user_id = '1214002279'
            self.user_data_setup.send(user_id)
            spot_usrsetup.destroy()
            startup.update()
            print('user id recieved')

            self.spotifyapp = spot.SpotifyIntegration(user_id)
            self.spotifyapp = self.spotifyapp()
            playlists = next(self.spotifyapp)
            self.spotify_select_playlists(startup,playlists)


        spot_usrsetup = Frame(startup)
        spot_usrsetup_dist = Label(spot_usrsetup,text = 'Note: in order to impliment spotify integration your spotify ID '
                                                        'is required. In most cases this is not the same as your spotify '
                                                        'login information. In order to find your spotify ID go to '
                                                        'https://www.spotify.com/us/account/overview/ and click on the '
                                                        '\'Change Password\' tab and copy the device username to the field below',wraplength=500)
        spot_usrsetup_field = Entry(spot_usrsetup)
        spot_usrsetup_button = Button(spot_usrsetup,text='Enter')
        spot_usrsetup_button.bind('<Button-1>',spotint_send_button)
        spot_usrsetup_dist.pack(),spot_usrsetup_button.pack(),spot_usrsetup_field.pack()
        spot_usrsetup.pack()

    def spotify_select_playlists(self,startup,playlists):
        """Gets a list of artists from the playlist"""

        def spot_selplay_continue_button(event,playlists=playlists):
            selection = [spot_selplay_choices.get(i) for i in spot_selplay_choices.curselection()]
            playlists = {name:data for name,data in playlists.items() if name in selection}
            spot_selplay.destroy()
            startup.update()
            artists = self.spotifyapp.send(playlists)
            self.spotify_select_artists(startup,artists)

        spot_selplay = Frame(startup)
        spot_selplay_desc = Label(spot_selplay,text = 'Select which playlists you would like to track artists from',wraplength=500)
        spot_selplay_choices =Listbox(spot_selplay,selectmode=MULTIPLE)
        spot_selplay_button =Button(spot_selplay,text='Continue')
        spot_selplay_button.bind('<Button-1>',spot_selplay_continue_button)

        spot_selplay_desc.pack(),spot_selplay_choices.pack(),spot_selplay_button.pack()
        spot_selplay.pack()

        for key,_ in playlists.items():
            spot_selplay_choices.insert(END,key)

    def spotify_select_artists(self,startup,artists):
        """Select which artists are to be tracked"""
        def spot_selbands_continue_button(event,bands=artists):
            print(bands, type(bands))
            tracked = [spot_selbands_choices.get(i) for i in spot_selbands_choices.curselection()]
            if tracked:
                tracked_bands = [name for name in bands if name in tracked]
            else:
                tracked_bands = [name for name in list(bands)]

            self.user_data_setup.send(tracked_bands)
            spot_selbands.destroy()
            wait = Label(startup,text='Saving - Please Wait')
            wait.pack()
            startup.update()
            try:
                next(self.user_data_setup)
            except StopIteration:
                pass
            wait.destroy()
            self.concert_lookup(startup)



        spot_selbands = Frame(startup)
        spot_selbands_desc = Label(spot_selbands,text='Select which bands you would like to follow or just press Done '
                                                      'to track all listed bands')
        spot_selbands_choices = Listbox(spot_selbands,selectmode=MULTIPLE)
        spot_selbands_button = Button(spot_selbands,text='Done')
        spot_selbands_button.bind('<Button-1>',spot_selbands_continue_button)
        spot_selbands_desc.pack(),spot_selbands_choices.pack(),spot_selbands_button.pack()
        spot_selbands.pack()
        for band in artists:
            spot_selbands_choices.insert(END,band)

    #Only this method is run for manual input

    def manual_band_input(self,startup):
        """For manual entry of bands to track, YMMV. Also this is just a copy of message 2 in terms of code"""
        def message2_button(event):
            val = band_input.get()
            print(val)
            self.user_data_setup.send('Not Given')
            self.user_data_setup.send(val)
            band_in_frame.destroy()
            self.concert_lookup(startup)

        band_in_frame = Frame(startup)
        man_imput_2text = 'Input each band you would like to track, seperated by commas'
        message2 = Label(band_in_frame, text=man_imput_2text,wraplength=500)
        band_input = Entry(band_in_frame)
        band_input_button = Button(band_in_frame)
        band_input_button.bind('<Button-1>', message2_button)
        startup.update()
        message2.pack(), band_input.pack(), band_input_button.pack()
        band_in_frame.pack()

    def concert_lookup(self,startup):

        def lookup_yes_action():
            lookup.destroy()
            concert_finder = CFinder()
            concert_finder()
            print('Done!')

        def lookup_no_action():
            pass
            startup.destroy()

        lookup = Frame(startup)
        lookup_text = Label(lookup,text='Would you like to find concert dates now? Note that this obviously required'
                                        'an internet connection, and may take a while in cases where a large'
                                        'number of bands are tracked')
        lookup_button_yes=Button(lookup,text='Yes',command=lookup_yes_action)
        lookup_button_no = Button(lookup,text='No',command=lookup_no_action)
        lookup_text.pack(),lookup_button_yes.pack(),lookup_button_no.pack()
        lookup.pack()

class Main_GUI:
    """The main GUI window for the program, this class is only responsible for the appearance
    of the application, with all of the actual heavy lifting offloaded to the other files. I've tried to comment where
    this happens such that it should hopefully be clear when the other files are being called"""

    def __init__(self,parent):
        """Initializes all the important stuff used in the window. Notable things initialized here include the
        'IOsetter' which is an instance that is used to modify and update the 'user_settings' file based on manual input.
        The class for this instance can be found in InitialSetup.py as LocatorMain"""
        self.IOsetter = LocatorMain()
        self.root = parent
        self.concert_database = sqlite.connect('concert_db.db')
        with open('user_settings','r') as settings:
            data = json.load(settings)
            self.bands = data['bands']

        # This is a reverse of what is done elsewhere, where the database friendly band names are converted back to normal
        self.banddb = {band:str("_".join(band.split(' '))) for band in self.bands}
        self.banddb = {re.sub(r'[\[|\-*/<>\'\"&+%,.=~!^()\]]', '', self.banddb[band]):band for band in self.bands}

    def __call__(self):
        """Initializes the main window, which includes the menu as well as the information for the upcoming concerts"""
        menu = Menu(self.root)
        self.root.config(menu=menu)

        # Spotify setting menu bar
        spotmenu = Menu(menu)
        menu.add_cascade(label='Spotify Settings',menu=spotmenu)
        spotmenu.add_command(label='Update Tracked Artists',command=self.spotify_update)

        # Manual initiation of concert lookup
        concmenu = Menu(menu)
        menu.add_cascade(label='Concert Search',menu=concmenu)
        concmenu.add_command(label='Search for upcoming concerts',command=self.concert_update)

        # Menu for addition/removal of bands manually
        manmenu = Menu(menu)
        menu.add_cascade(label='Add/Remove Artists',menu=manmenu)
        manmenu.add_command(label='Add Artists',command=self.add_artists)

        # Getting and formatting the upcoming concert info from the database
        space_frame = Frame(self.root,width=768,height=20)
        concert_frame = Frame(self.root,width=768, height=576,borderwidth=5,relief=RIDGE)
        space_frame.pack()
        concert_frame.pack()
        Frame(self.root,width=768,height=20).pack()
        with self.concert_database as cdb:
            cur = cdb.cursor()
            up = list(cur.execute('SELECT * FROM Upcoming ORDER BY Date'))
            up.insert(0, ['Band', 'Location', 'Time', 'Date', 'Days until concert'])
            framedimensions = [max([len(j) for j in i]) for i in list(zip(*copy(up)))]
            up = list(up)
        self.displaybar(concert_frame,up,framedimensions)

    def displaybar(self,parent,iter_data,framedimensions):
        """This is used to display & format the concert data in a (sort of) aesthetic format"""
        for row in iter_data:
            r = iter_data.index(row)
            if r == 0: Label(parent,borderwidth=0,relief=SUNKEN,pady=1,width=sum(framedimensions)+2*len(row)).grid(row=1,columnspan=len(row),pady=0)
            else: r+=1
            for val in row:
                if row.index(val) == 0:
                    try:
                        value = self.banddb[val]
                    except KeyError:
                        print(val)
                        value = val
                else: value = val
                Label(parent,text=value,borderwidth=1,width=framedimensions[row.index(val)],relief=RAISED).grid(row=r, column=row.index(val), pady=1)

    def spotify_update(self):
        """Initializes and calls an instance of the SpotifyUpdate class from Spotify_API_Integration"""
        top = Toplevel()
        SpotifyUpdate(top)

    def concert_update(self):
        """Initializes and calls an instance of ConcertFinder (shortened to CFinder here) from ConcertScraper.py"""
        finder = CFinder()
        find = threading.Thread(target=finder())
        find.start()

    def add_artists(self):
        """Manual addition of artists to user_settings using the IOsetter mentioned in the __init__ docstring"""
        top = Toplevel()

        def message2_button(event,parent):
            bands = band_input.get()
            print(bands)
            self.IOsetter.add_bands(bands)
            top.destroy()


        band_in_frame = Frame(top)
        man_imput_2text = 'Input each band you would like to track, seperated by commas'
        message2 = Label(band_in_frame, text=man_imput_2text,wraplength=500)
        band_input = Entry(band_in_frame)
        band_input_button = Button(band_in_frame)
        band_input_button.bind('<Button-1>', message2_button)
        top.update()
        message2.pack(), band_input.pack(), band_input_button.pack()
        band_in_frame.pack()

    def remove_artists(self):
        pass

    def update_location(self):
        pass

class SpotifyUpdate:
    """GUI class for running through artist selection via spotify, this is essentially the same as the
    related methods found in the FirstTimeStartup class, but slightly modified to be able to run independently of
    the sequential order used in FirstTimeStartup"""
    def __init__(self,parent):
        self.root = parent
        with open('user_settings','r') as settings:
            data = json.load(settings)
            user_id = data['spotify_id']
        fr = Label(self.root,text='Updating Playlists - Please Wait')
        fr.pack()
        self.root.update()
        self.spotifyapp = spot.SpotifyIntegration(user_id)
        self.spotifyapp = self.spotifyapp()
        playlists = next(self.spotifyapp)
        fr.destroy()
        self.spotify_select_playlists(playlists)

    def spotify_select_playlists(self,playlists):
        """Gets a list of artists from the playlist"""

        def spot_selplay_continue_button(event,playlists=playlists):
            selection = [spot_selplay_choices.get(i) for i in spot_selplay_choices.curselection()]
            playlists = {name:data for name,data in playlists.items() if name in selection}
            spot_selplay.destroy()
            self.root.update()
            artists = self.spotifyapp.send(playlists)
            self.spotify_select_artists(artists)

        spot_selplay = Frame(self.root)
        spot_selplay_desc = Label(spot_selplay,text = 'Select which playlists you would like to track artists from',wraplength=500)
        spot_selplay_choices =Listbox(spot_selplay,selectmode=MULTIPLE)
        spot_selplay_button =Button(spot_selplay,text='Continue')
        spot_selplay_button.bind('<Button-1>',spot_selplay_continue_button)

        spot_selplay_desc.pack(),spot_selplay_choices.pack(),spot_selplay_button.pack()
        spot_selplay.pack()

        for key,_ in playlists.items():
            spot_selplay_choices.insert(END,key)

    def spotify_select_artists(self,artists):
        """Select which artists are to be tracked"""
        def spot_selbands_continue_button(event,bands=artists):
            tracked = [spot_selbands_choices.get(i) for i in spot_selbands_choices.curselection()]
            if tracked:
                tracked_bands = [name for name in bands if name in tracked]
            else:
                tracked_bands = [name for name in list(bands)]
            spot_selbands.destroy()
            wait = Label(self.root,text='Saving - Please Wait')
            wait.pack()
            self.root.update()
            self.root.destroy()

        spot_selbands = Frame(self.root)
        spot_selbands_desc = Label(spot_selbands,text='Select which bands you would like to follow or just press Done '
                                                      'to track all listed bands')
        spot_selbands_choices = Listbox(spot_selbands,selectmode=MULTIPLE)
        spot_selbands_button = Button(spot_selbands,text='Done')
        spot_selbands_button.bind('<Button-1>',spot_selbands_continue_button)
        spot_selbands_desc.pack(),spot_selbands_choices.pack(),spot_selbands_button.pack()
        spot_selbands.pack()
        for band in artists:
            spot_selbands_choices.insert(END,band)





    #test.first_time_startup_events(s)
    uid = '1214002279'

    #FirstTimeStartup.concert_lookup(FirstTimeStartup,s)
    #FirstTimeStartup.spotify_setup_user_input(FirstTimeStartup,s)


if __name__ == '__main__':
    app = Tk()
    main_test = Main_GUI(app)
    main_test()
    app.mainloop()
