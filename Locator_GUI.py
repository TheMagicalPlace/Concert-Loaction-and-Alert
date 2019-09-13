
from time import sleep
import Spotify_API_Integration as spot
from InitialSetup import LocatorSetup,LocatorMain
from ConcertScraper import ConcertFinder as CFinder
from tkinter import *
import sqlite3 as sqlite
import json
from copy import copy
import threading
import sys
import queue
from scheduler_setup import *

class TkinterEventSubprocess(threading.Thread):
    def __init__(self, queue,name=None):
        super().__init__()
        if name is not None:
            self.name = name
        self.queue = queue
    def run(self):
        concert_finder = CFinder()
        concert_finder()
        self.queue.put('Done')


class FirstTimeStartup:

    spotifyapp = None
    """Runs through the first time setup GUI"""

    def __init__(self,parent):
        self.spotifyapp = None
        self.root = parent
        self.user_data_setup = LocatorSetup()
        self.user_data_setup = self.user_data_setup()
        self.queue = queue.Queue()

    def __call__(self, *args, **kwargs):
        # Attempts to prime the user_data_setup coroutine, if it returns a StopIteration user data is already present
        # and the initial setup code is not run (outside instancing the class)
        try:
            next(self.user_data_setup)
        except StopIteration:
            self.root.destroy()
            return
        else:
            self.message1()
            self.root.mainloop()

    def message1(self):
        """This does nothing other than note that the program has been started"""
        def message1_terminate(event):
            self.root.update()
            sleep(1)
            frame1.destroy()
            self.message2()
        frame1 = Frame(self.root)
        message1 = Label(frame1, text='Performing First Time Startup')
        message1.pack()
        message1.bind('<Visibility>', message1_terminate)
        frame1.pack()

    def message2(self):
        """Notes down user location"""
        def message2_button(event):
            val = location_input.get()
            print(val)
            self.user_data_setup.send(val)
            frame2.destroy()
            self.spotify_int()
            return val

        frame2 = Frame(self.root)
        message2text = ' In order to only keep track of nearby concerts, your location is requred. Please input' \
                       'the location you would like to track from in the form City,State. Note that this application is' \
                       'currently limited to only United States residents'
        message2 = Label(frame2, text=message2text,wraplength=500)
        location_input = Entry(frame2)
        location_input_button = Button(frame2)
        location_input_button.bind('<Button-1>', message2_button)
        self.root.update()
        message2.pack(), location_input.pack(), location_input_button.pack()
        frame2.pack()

    # These methods are run sequentially if spotify integration is selected

    def spotify_int(self):

        def spotint_yes_button(event):
            print('yes registered')
            spotint.destroy()
            self.root.update()
            self.spotify_setup_user_input()
            pass
        def spotint_no_button(event):
            print('no registered')
            spotint.destroy()
            self.manual_band_input()
            pass

        spotint = Frame(self.root)
        spotint_text = Label(spotint,text='Would you like to use one (or more) of your spotify playlists in order to '
                                          'determine what bands to track?',wraplength=500)
        spotint_yes = Button(spotint,text='Yes')
        spotint_no = Button(spotint,text='No')
        spotint_yes.bind('<Button-1>',spotint_yes_button)
        spotint_no.bind('<Button-1>', spotint_no_button)
        spotint_text.pack(),spotint_yes.pack(),spotint_no.pack()
        spotint.pack()

    def spotify_setup_user_input(self):
        def spotint_send_button(event):

            user_id = spot_usrsetup_field.get()
            user_id = '1214002279'
            self.user_data_setup.send(user_id)
            spot_usrsetup.destroy()
            self.root.update()
            print('user id recieved')

            self.spotifyapp = spot.SpotifyIntegration(user_id)
            self.spotifyapp = self.spotifyapp()
            playlists = next(self.spotifyapp)
            self.spotify_select_playlists(playlists)


        spot_usrsetup = Frame(self.root)
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
            print(bands, type(bands))
            tracked = [spot_selbands_choices.get(i) for i in spot_selbands_choices.curselection()]
            if tracked:
                tracked_bands = [name for name in bands if name in tracked]
            else:
                tracked_bands = [name for name in list(bands)]

            self.user_data_setup.send(tracked_bands)
            spot_selbands.destroy()
            wait = Label(self.root,text='Saving - Please Wait')
            wait.pack()
            self.root.update()
            try:
                next(self.user_data_setup)
            except StopIteration:
                pass
            wait.destroy()
            self.concert_lookup()


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

    #Only this method is run for manual input

    def manual_band_input(self):
        """For manual entry of bands to track, YMMV. Also this is just a copy of message 2 in terms of code"""
        def message2_button(event):
            val = band_input.get()
            print(val)
            self.user_data_setup.send('Not Given')
            self.user_data_setup.send(val)
            band_in_frame.destroy()
            self.concert_lookup()

        band_in_frame = Frame(self.root)
        man_imput_2text = 'Input each band you would like to track, seperated by commas'
        message2 = Label(band_in_frame, text=man_imput_2text,wraplength=500)
        band_input = Entry(band_in_frame)
        band_input_button = Button(band_in_frame)
        band_input_button.bind('<Button-1>', message2_button)
        self.root.update()
        message2.pack(), band_input.pack(), band_input_button.pack()
        band_in_frame.pack()

    def concert_lookup(self):

        def lookup_yes_action():
            lookup.destroy()
            self.search_thread =TkinterEventSubprocess(self.queue,'yote').start()
            self.add_to_startup()

        def lookup_no_action():
            lookup.destroy()
            self.add_to_startup()

        lookup = Frame(self.root)
        lookup_text = Label(lookup,text='Would you like to find concert dates now? Note that this obviously required'
                                        'an internet connection, and may take a while in cases where a large'
                                        'number of bands are tracked')
        lookup_button_yes=Button(lookup,text='Yes',command=lookup_yes_action)
        lookup_button_no = Button(lookup,text='No',command=lookup_no_action)
        lookup_text.pack(),lookup_button_yes.pack(),lookup_button_no.pack()
        lookup.pack()

    #The following three methods are involved in setup and customization of startup settings

    def add_to_startup(self):

        def default_button():
            frm.destroy()
            self.add_to_startup_default()

        def custom_button():
            frm.destroy()
            self.add_to_startup_custom()

        def disable_button():
            frm.destroy()
            schdl = SchedulerLinux()
            schdl.cron_enable(False)
            self.launch_main()

        frm = Frame(self.root)

        user_os = sys.platform
        if user_os == 'linux':
            Label(master=frm,text='This application is designed to make use of the cron scheduler to '
                                  'automatically perform most of it\'s functions. While you *should* have'
                                  'no issues with just manually updating as you go, for sake of ease I would reccomend '
                                  'enabling it and setting the delay as desired. The default settings are a 30 minute'
                                  'delay from startup before concert data is updated from the web, and a one hour delay'
                                  'before the window with the upcoming concerts is displayed' ).pack()
            b1 = Button(master=frm,text='Use Default Settings',command=default_button)
            b2 = Button(master=frm,text='Custom Settings',command=custom_button)
            b3 = Button(master=frm,text='Disable Automatic Startup',command=disable_button)
            b1.pack(),b2.pack(),b3.pack()
            frm.pack()

    def add_to_startup_default(self):

        def cont_button():
            usr = ent.get()
            schdl = SchedulerLinux()
            schdl.cron_setup(usr)
            cronfrm_default.destroy()
            self.launch_main()

        cronfrm_default = Frame(self.root)

        Label(master=cronfrm_default,text='Enter your linux username, i.e. usr in home/usr').pack()
        ent = Entry(master=cronfrm_default,)
        ent.pack()
        Button(master=cronfrm_default,text='Continue',command=cont_button).pack()
        cronfrm_default.pack()

    def add_to_startup_custom(self):

        def cont_button_custom():
            usr = entusr.get()
            scraper_delay = entdelay1.get()
            gui_delay = entdelay2.get()
            schdl = SchedulerLinux()
            schdl.cron_setup(usr,int(scraper_delay),int(gui_delay))
            cronfrm_custom.destroy()
            self.launch_main()

        cronfrm_custom = Frame(self.root)
        cronfrm_custom.pack()
        Label(master=cronfrm_custom,text='Enter your linux username, i.e. usr in home/usr').pack()
        entusr =Entry(master=cronfrm_custom)
        entusr.pack()
        Label(master=cronfrm_custom, text='Enter the delay from startup (in seconds) you would like'
                                                      'before the application updates concert data from the internet').pack()
        entdelay1 = Entry(master=cronfrm_custom)
        entdelay1.pack()
        Label(master=cronfrm_custom, text='Enter the delay from startup (in seconds) you would like'
                                                      'before the window containing upcoming concert data is opened').pack()
        entdelay2 = Entry(master=cronfrm_custom)
        entdelay2.pack()
        Button(master=cronfrm_custom,text='Submit',command=cont_button_custom).pack()

    # Launches the main GUI

    def launch_main(self):

        def now_button():
            self.root.destroy()
            master = Tk()
            main_gui = Main_GUI(master)
            main_gui()
        def later_button():

            def process_queue():
                try:
                    self.queue.get()
                except queue.Empty:
                    print('waiting...')
                    self.root.after(10000, process_queue)
                else:
                    self.root.destroy()
                    master = Tk()
                    main_gui = Main_GUI(master)
                    main_gui()
            process_queue()
            self.root.withdraw()

        frm = Frame(master=self.root)
        frm.pack()
        Label(master=frm,text='Would you like to launch the application now or after the concert data has been collected? If not'
                              'you can hit exit, however if you selected to download the concert data that will continue in the backround').pack()
        b1 = Button(master=frm,text='Now',command=now_button)
        b2 = Button(master=frm, text='When Ready', command=later_button)
        print(threading.active_count())
        print(threading.activeCount(),[ thr.name for thr in threading.enumerate()])
        thread_ids = [ thr.name for thr in threading.enumerate()]
        if 'yote' not in thread_ids:
            b2.configure(state= 'disabled')

        b3 = Button(master=frm,text='Exit',command=self.root.destroy)
        b1.pack(),b2.pack(),b3.pack()

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
        self.queue = queue.Queue()
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
        self.concmenu = Menu(menu)
        menu.add_cascade(label='Concert Search',menu=self.concmenu)
        self.concmenu.add_command(label='Search for upcoming concerts',command=self.concert_update)

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

        self.root.mainloop()

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

    # TODO disable this button when the concert search from the initial setup is still running
    def concert_update(self):
        """Initializes and calls an instance of ConcertFinder (shortened to CFinder here) from ConcertScraper.py"""
        finder = CFinder()
        self.conc_find = TkinterEventSubprocess(self.queue,'concert-lookup-thread')
        self.conc_find.start()
        self.concmenu.entryconfig(1,state=DISABLED)
        self.queue_check()

    def queue_check(self):
        if self.conc_find.is_alive():
            print('waiting')
            self.root.after(100,self.queue_check)
        else:
            print('done!')
            self.concmenu.entryconfig(1,state=ACTIVE)

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
    #FirstTimeStartup(app).concert_lookup()



    main_test = Main_GUI(app)
    main_test()
    app.mainloop()
