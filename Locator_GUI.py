
from time import sleep
from tkinter import *
import threading
import queue
from os import getcwd

from ConcertScraper import ConcertFinder as CFinder
from scheduler_setup import *
from Notifier import *
import Spotify_API_Integration as spot
from ModifyUserSettings import LocatorSetup,LocatorMain

stop_all_threads = False



class TkinterEventSubprocess(threading.Thread):
    """class used to spawn threads in the Tkinter widgets (hopefully) without breaking anything"""

    def __init__(self, queue,callable_instance,name=None,args=None):
        super().__init__()
        if name is not None: #
            self.name = name
        self.queue = queue
        self.threaded_func = callable_instance

    def run(self):
        funcgen = self.threaded_func()
        thread_func_gen = funcgen()
        try:
            while True:
                # yield is used in the scraper so that stop_all_threads can be checked after each lookup,
                # enabling termination of the thread quickly and without risking data corruption
                next(thread_func_gen)
                if stop_all_threads:
                    print('thread ended due to shutdown')
                    break
        except GeneratorExit:
            self.queue.put('Done')

class FirstTimeStartup:
    """
    This class contains all of the GUI states needed for the first time startup of the app (i.e. getting user location.
    setting up launch on boot & launch delays, setting up spotify integration), all of which are run through sequentially
    upon , with 'message1' being called by __init__. Since the class methods aren't listed entirely in sequential order,
    there is an outline of the decision tree below.

    message1
      ﹀
      ﹀
    message2
      ﹀
      ﹀
    spotify int > (yes) > spotify_setup_user_input
      ﹀                          ﹀
      (no)                       ﹀
      ﹀                  spotify_select_playlists
    manual_band_input            ﹀
      ﹀                         ﹀
      ﹀                         ﹀
    concert_lookup < < < < spotify_select artists
      ﹀
      ﹀
      ﹀
    add_to_startup > > > (yes-use_default) > > > (yes-set custom values)
      ﹀                    ﹀                             ﹀
      ﹀                    ﹀                             ﹀
      (no)                 add_to_startup_default     add_to_startup_custom
      ﹀                    ﹀                             ﹀
      ﹀                    ﹀                             ﹀
    launch_main < < < < < < < < < < < < < < < < < < < < < < <

    Notably, if the concert lookup (concert_lookup, the actual lookup is done by ConcertScraper.py) is launched
    during setup, a seperate thread is spawned while proceeding. If the GUI is exited this thread will continue to run,
    the only programmed way to kill it is by continuing on to Main_GUI (i.e. selecting 'Now' in launch_main), or by
    killing is using a task manager.





    """

    spotifyapp = None
    """Runs through the first time setup GUI"""

    def __init__(self,parent):
        """Initializes the parameters used across methods and then runs the instance"""
        self.spotifyapp = None
        self.root = parent
        self.user_data_setup = LocatorSetup() #
        self.user_data_setup = self.user_data_setup()
        self.queue = queue.Queue()
        self()

    def __call__(self, *args, **kwargs):
        """Attempts to prime the user_data_setup coroutine, if it returns a StopIteration user data is already present
        and the initial setup code is not run (outside instancing the class). Really, this should never be an issue since
        FirstTimeStartup is never called unless the user_settings file is nonexistant """
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
        """Notes down user location and sends it to the LocatorSetup (from ModifyUserSettings.py"""
        def message2_button(event):
            val = location_input.get()
            print(val)
            self.user_data_setup.send(val)
            frame2.destroy()
            self.spotify_int()
            return val

        frame2 = Frame(self.root)
        message2text = ' In order to only keep track of nearby concerts, your location is requred. Please input ' \
                       'the location you would like to track from in the form City,State. Note that this application is ' \
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
        """
        Allows the user to select enable spotify integration or only manually input bands

        """
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
        bfrm = Frame(master=spotint)
        spotint_yes = Button(bfrm,text='Yes')
        spotint_no = Button(bfrm,text='No')

        spotint_yes.bind('<Button-1>',spotint_yes_button)
        spotint_no.bind('<Button-1>', spotint_no_button)
        spotint_yes.grid(row=0, colunm=0), spotint_no.grid(row=0, colunm=1)
        spotint_text.pack(),
        bfrm.pack()
        spotint.pack()

    def spotify_setup_user_input(self):
        """Gets the users spotify ID and attempts to validate credentials"""
        def spotint_send_button(event):

            user_id = spot_usrsetup_field.get()
            self.user_data_setup.send(user_id)
            spot_usrsetup.destroy()
            f = Label(master=self.root,text='Getting Playlist Data - Please Wait')
            f.pack()
            self.root.update()
            self.spotifyapp = spot.SpotifyIntegration('playlist-read-private',user_id) # playlist-read-private is the only scope needed, so this is hardcoded
            self.spotifyapp = self.spotifyapp()
            playlists = next(self.spotifyapp)
            f.destroy()
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
        """Gets a list of playlists from the users Spotify account and sends the selected playlists foreward"""

        def spot_selplay_continue_button(event,playlists=playlists):
            selection = [spot_selplay_choices.get(i) for i in spot_selplay_choices.curselection()]
            playlists = {name:data for name,data in playlists.items() if name in selection}
            spot_selplay.destroy()
            f = Label(master=self.root, text='Gathering Band Data - Please Wait')
            f.pack()
            self.root.update()

            artists = self.spotifyapp.send(playlists)
            f.destroy()
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
        """Allows the user to optionally do the concert lookup while the rest of the setup is run.
        This spawns a seperate thread to run the web scraper"""
        def lookup_yes_action():
            lookup.destroy()
            self.search_thread =TkinterEventSubprocess(self.queue,CFinder,'concert-lookup-thread').start()
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
        """Used for modification of the startup settings"""
        top = self.root # this code is mostly taken from main GUI
        self.scheduler = initialize_scheduler()

        def default_button():
            frm.destroy()
            self.add_to_startup_default(top)

        def custom_button():
            frm.destroy()
            self.add_to_startup_custom(top)

        def disable_button():
            frm.destroy()
            self.scheduler.enabledisable(False)
            self.launch_main()

        frm = Frame(self.root)

        user_os = sys.platform

        if user_os != 'win32':
            Label(master=frm, text='This application is designed to make use of the cron scheduler to '
                                   'automatically perform most of it\'s functions. While you *should* have'
                                   'no issues with just manually updating as you go, for sake of ease I would recommend '
                                   'enabling it and setting the delay as desired. The default settings are a 30 minute'
                                   'delay from startup before concert data is updated from the web, and a one hour delay'
                                   'before the window with the upcoming concerts is displayed',
                  wraplength=500).pack()
        else:

            windows_text = f'''Unless you know for certain that you will never want to have this program automatically
                              run it is recommended that you follow these steps. With this method, toggling automatic 
                              execution can be easily modified though this program. If you do not wish to do this now or
                              have no intent of using this feature, click disable below, otherwise follow these instructions.

                              In the start menu search for \'Task Scheduler\' and click it. In the 'Actions' panel select
                              'Create Basic Task...'. From there, name it anything you would like and click Next in the window.
                              From there you can configure the task settings, I recommend setting it to either 'When the computer starts'
                              or 'When I log on' as further time delay can be configured later. From there hit Next, select 'Start a Program'
                              and hit Next again. You should see an input box with 'Program/script:' above it. Copy the file path
                              shown below into this box and hit next. To complete the setup hit Finish. 
                              
                              File Path = {getcwd()+'/concerttracker.bat'}
                              
                              Once you have done that, select how you would like to proceed.'''
            Label(master=frm,text=windows_text,wraolength=500).pack()
        bfrm = Frame(master=frm)
        b1 = Button(master=bfrm, text='Use Default Settings', command=default_button)
        b2 = Button(master=bfrm, text='Custom Settings', command=custom_button)
        b3 = Button(master=bfrm, text='Disable Automatic Startup', command=disable_button)
        b1.grid(row=0, column=0), b2.grid(row=0, column=1), b3.grid(row=0, column=2)
        bfrm.pack()
        frm.pack()


    def add_to_startup_default(self, parent=None):
        """Creates a cron job with the default settings (30 mins after startup for the scraper to launch,
        an hour after startup for the main GUI to launch"""

        def cont_button():
            usr = ent.get()
            self.scheduler.enabledisable(True)
            self.scheduler.activation_delay()
            if sys.platform != 'win32':
                self.scheduler.cron_setup(usr)
            cronfrm_default.destroy()
            self.launch_main()

        cronfrm_default = Frame(parent)

        Label(master=parent,
              text='If you are on linux or macOS, enter your linux username, i.e. usr in home/usr, otherwise'
                   'just hit Continue').pack()
        ent = Entry(master=cronfrm_default)
        ent.delete(0, END)
        ent.insert(0, str(self.scheduler.user))
        ent.pack()
        Button(master=cronfrm_default, text='Continue', command=cont_button).pack()
        cronfrm_default.pack()

    def add_to_startup_custom(self, parent=None):
        """Creates a cron job with user specified delays for the web scraper and GUI"""

        def cont_button_custom():
            self.scheduler.cron_enable(True)
            usr = entusr.get()
            scraper_delay = entdelay1.get()
            gui_delay = entdelay2.get()
            if sys.platform != 'win32':
                self.scheduler.cron_setup(usr)
            cronfrm_custom.destroy()
            self.scheduler.activation_delay(int(scraper_delay), int(gui_delay))
            self.launch_main()

        cronfrm_custom = Frame(parent)
        cronfrm_custom.pack()
        Label(master=cronfrm_custom, text='''If you are on linux or macOS, enter your linux username, i.e. usr 
        in home/usr, otherwise leave this blank.''').pack()
        entusr = Entry(master=cronfrm_custom)
        entusr.delete(0, END)
        entusr.insert(0, self.scheduler.user)
        entusr.pack()
        Label(master=cronfrm_custom, text='Enter the delay from startup (in minutes) you would like'
                                          'before the application updates concert data from the internet').pack()
        entdelay1 = Entry(master=cronfrm_custom)
        entdelay1.delete(0, END)
        entdelay1.insert(0, str(self.scheduler.web_scraper_delay))
        entdelay1.pack()
        Label(master=cronfrm_custom, text='Enter the delay from startup (in minutes) you would like'
                                          'before the window containing upcoming concert data is opened').pack()
        entdelay2 = Entry(master=cronfrm_custom)
        entdelay2.delete(0, END)
        entdelay2.insert(0, str(self.scheduler.gui_launch_delay))
        entdelay2.pack()
        Button(master=cronfrm_custom, text='Submit', command=cont_button_custom).pack()

    # Launches the main GUI

    def launch_main(self):
        """Allows the user to launch the main GUI immediatly, after the concert scraper is complete (if it was started)
        or just close the application. If the application is closed here the web scraper will run until complete"""
        def now_button():
            self.root.destroy()
            master = Tk()
            main_gui = Main_GUI(master)
            main_gui()
        def later_button():
            self.root.destroy()
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


        frm = Frame(master=self.root)
        frm.pack()
        Label(master=frm,text='Would you like to launch the application now or after the concert data has been collected? If not'
                              'you can hit exit, however if you selected to download the concert data that will continue in the backround').pack()
        b1 = Button(master=frm,text='Now',command=now_button)
        b2 = Button(master=frm, text='When Ready', command=later_button)
        print(threading.active_count())
        print(threading.activeCount(),[ thr.name for thr in threading.enumerate()])
        thread_ids = [ thr.name for thr in threading.enumerate()]
        if 'concert-lookup-thread' not in thread_ids:
            b2.configure(state= 'disabled')

        b3 = Button(master=frm,text='Exit',command=self.root.destroy)
        b1.pack(),b2.pack(),b3.pack()

class Main_GUI:
    """The main GUI window for the program, this class is only responsible for the appearance
    of the application, with all of the actual heavy lifting offloaded to the other files. I've tried to comment where
    this happens such that it should hopefully be clear when the other files are being called"""

    def __init__(self,parent):
        """Initializes the variables used across class methods, of note is that UpdateSettings is an instance of
        LocatorMain, and is used to update the user_settings file whenever changes are made. Those changes are then reflected
        by the GUI where applicable"""
        """Initializes all the important stuff used in the window. Notable things initialized here include the
        'IOsetter' which is an instance that is used to modify and update the 'user_settings' file based on manual input.
        The class for this instance can be found in ModifyUserSettings.py as LocatorMain"""
        self.UpdateSettings = LocatorMain()
        self.root = parent # a Tk() instance
        self.queue = queue.Queue()
        self.concert_database = sqlite.connect('concert_db.db')
        self.update_GUI_variables()
        # This is a reverse of what is done elsewhere, where the database friendly band names are converted back to normal
        self.banddb = {band:str("_".join(band.split(' '))) for band in self.bands}
        self.banddb = {re.sub(r'[\[|\-*/<>\'\"&+%,.=~!^()\]]', '', self.banddb[band]):band for band in self.bands}
        self.scheduler = initialize_scheduler() # creates an instance of the appropriate scheduler and returns it


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
        menu.add_cascade(label='Search and Notification',menu=self.concmenu)
        self.concmenu.add_command(label='Search for upcoming concerts',command=self.concert_update)
        self.concmenu.add_command(label='Change how far in advance to display concert information',
                                  command=self.concert_time_to_update)
        # Menu for addition/removal of bands manually
        manmenu = Menu(menu)
        menu.add_cascade(label='Add/Remove Artists',menu=manmenu)
        manmenu.add_command(label='Add Artists',command=self.add_artists)
        manmenu.add_command(label='Remove Artists',command=self.remove_artists)
        manmenu.add_command(label='Resume tracking of Removed Artists', command=self.add_removed_artist)

        setupmenu = Menu(menu)
        menu.add_cascade(label='Startup Settings',menu=setupmenu)
        setupmenu.add_command(label='Modify Startup Settings',command=self.add_to_startup)
        setupmenu.add_command(label='View Startup Settings',command=self.view_startup_settings)

        exitmenu = Menu(menu)
        menu.add_cascade(label='Exit',menu=exitmenu)
        exitmenu.add_command(label='Exit GUI',command=self.root.destroy) # doesn't kill seperate threads (i.e the scraper)
        exitmenu.add_command(label='Exit all processes (incl. concert search)', command=self.exit_all)

        # Getting and formatting the upcoming concert info from the database
        self.concert_frame = Frame(self.root,width=768, height=576,borderwidth=5,relief=RIDGE,pady=20)
        self.concert_frame.pack()
        up,framedimensions = Notifications().notify_user_()
        self.displaybar(self.concert_frame,up,framedimensions)



        thread_ids = [ thr.name for thr in threading.enumerate()]

        # if the lookup thread (from the setup or launch on reboot) is running the web scraper can not be launched
        if 'concert-lookup-thread' in thread_ids:
            self.concmenu.entryconfig(1, state=DISABLED)
            self.queue_check()

        self.root.mainloop()



    def update_GUI_variables(self):
        """updates the instance variables after user_settings is changed"""
        with open('user_settings','r') as settings:
            data = json.load(settings)
            for key,value in data.items():
                if key == 'last_checked':
                    self.last_checked = value
                else:
                    exec(f'self.{key} = {value}')

    def displaybar(self,parent,iter_data,framedimensions):
        """This is used to display & format the concert data in a (sort of) aesthetic format"""

        dbframe = Frame(master=parent)
        dbframe.pack()
        scrollbar = Scrollbar(dbframe)
        innerholder = Canvas(master=dbframe,height=600,width=970,yscrollcommand=scrollbar.set)

        scrollbar.pack(side=RIGHT, fill=Y)
        n = Frame(master=innerholder)


        innerholder.pack(side='left')
        innerholder.create_window(0, 0, window=n,anchor=NW)
        for row in iter_data:
            r = iter_data.index(row)
            if r == 0: Label(n,borderwidth=0,relief=SUNKEN,pady=1,width=sum(framedimensions)+2*len(row)).grid(row=1,columnspan=len(row),pady=0)
            else: r+=1
            for val in row:
                if row.index(val) == 0:
                    try:
                        value = self.banddb[val]
                    except KeyError:
                        print(val)
                        value = val
                else: value = val
                Label(n,text=value,borderwidth=1,width=framedimensions[row.index(val)],relief=RAISED).grid(row=r, column=row.index(val), pady=1)
        scrollbar.config(command=innerholder.yview)

    def spotify_update(self):
        """Initializes and calls an instance of the SpotifyUpdate class from Spotify_API_Integration"""
        top = Toplevel()
        SpotifyUpdate(top, self.UpdateSettings.removed_bands)

    def concert_update(self):
        """Initializes and calls an instance of ConcertFinder (shortened to CFinder here) from ConcertScraper.py"""
        self.conc_find = TkinterEventSubprocess(self.queue,CFinder,name='concert-lookup-thread')
        self.conc_find.start()
        self.concmenu.entryconfig(1,state=DISABLED)
        self.queue_check()

    def queue_check(self):
        """Tracks if the web scraper thread is still alive"""
        thread_ids = [thr.name for thr in threading.enumerate()]
        if 'concert-lookup-thread'  in thread_ids:
            print('waiting')
            self.root.after(10000,self.queue_check)
        else:
            print('done!')
            self.concmenu.entryconfig(1,state=ACTIVE)

    def add_artists(self):
        """Manual addition of artists to user_settings using the IOsetter mentioned in the __init__ docstring"""
        top = Toplevel()

        def message2_button(event,parent):
            bands = band_input.get()
            print(bands)
            self.UpdateSettings.add_bands(bands)
            self.update_GUI_variables()
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
        """Manual removal of artists to user_settings using the UpdateSettings mentioned in the __init__ docstring"""
        top = Toplevel()

        def button_event_listbox(bands=self.bands):
            removed = sorted([list_choices.get(i) for i in list_choices.curselection()])
            if removed:
                removed_bands = removed
                self.UpdateSettings.remove_bands(removed_bands)

            band_in_frame.destroy()
            self.update_GUI_variables()
            top.destroy()

        band_in_frame = Frame(top)
        frame_description = Label(band_in_frame,text='Select which bands you would stop tracking')
        list_choices = Listbox(band_in_frame,selectmode=MULTIPLE)
        frame_button_1 = Button(band_in_frame,text='Done',command=button_event_listbox)

        frame_description.pack(),list_choices.pack(),frame_button_1.pack()
        band_in_frame.pack()

        for band in sorted(self.bands):
            list_choices.insert(END,band)

    def add_removed_artist(self):
        """Re-adding tracking  of artists removed via self.remove_artist to user_settings using the IOsetter mentioned in the __init__ docstring"""
        top = Toplevel()

        def button_event_listbox(bands=self.bands):
            removed = [list_choices.get(i) for i in list_choices.curselection()]
            if removed:
                removed_bands = removed
                self.UpdateSettings.add_removed_bands(removed_bands)

            band_in_frame.destroy()
            wait = Label(self.root,text='Saving - Please Wait')
            self.update_GUI_variables()
            top.destroy()



        band_in_frame = Frame(top)
        frame_description = Label(band_in_frame,text='Select which bands you would stop tracking')
        list_choices = Listbox(band_in_frame,selectmode=MULTIPLE)
        frame_button_1 = Button(band_in_frame,text='Done',command=button_event_listbox)

        frame_description.pack(),list_choices.pack(),frame_button_1.pack()
        band_in_frame.pack()

        for band in self.removed_bands:
            list_choices.insert(END,band)

    def update_location(self):
        """updates the location from which the user tracks from"""
        top = Toplevel()
        def button_event():
            location = location_input.get()
            self.UpdateSettings.update_user_location(location)
            top.destroy()

        location_frame = Frame(top)
        frame_input_text = 'Input the location you would like to track from.'
        message2 = Label(location_frame, text=frame_input_text,wraplength=500)
        location_input = Entry(location_frame)
        location_input_button = Button(location_frame,command=button_event)
        message2.pack(),location_input.pack(), location_input_button.pack()
        location_frame.pack()

    def add_to_startup(self):
        """Used for modification of the startup settings"""
        top = Toplevel()
        self.scheduler = initialize_scheduler()

        def default_button():
            frm.destroy()
            self.add_to_startup_default(top)

        def custom_button():
            frm.destroy()
            self.add_to_startup_custom(top)

        def disable_button():
            frm.destroy()
            self.scheduler.enabledisable(False)
            top.destroy()


        frm = Frame(top)

        user_os = sys.platform
        if user_os != 'win32':
            Label(master=frm, text='This application is designed to make use of the cron scheduler to '
                                   'automatically perform most of it\'s functions. While you *should* have'
                                   'no issues with just manually updating as you go, for sake of ease I would reccomend '
                                   'enabling it and setting the delay as desired. The default settings are a 30 minute'
                                   'delay from startup before concert data is updated from the web, and a one hour delay'
                                   'before the window with the upcoming concerts is displayed'
                                   '',wraplength=500).pack()

        else:
            Label(master=frm,text='The default settings are a 30 minute ' \
                           'delay from startup before concert data is updated from the web, and a one hour delay ' \
                           'before the window with the upcoming concerts is displayed',wraplength=500).pack()
        bfrm = Frame(master=frm)
        b1 = Button(master=bfrm, text='Use Default Settings', command=default_button)
        b2 = Button(master=bfrm, text='Custom Settings', command=custom_button)
        b3 = Button(master=bfrm, text='Disable Automatic Startup', command=disable_button)
        b1.grid(row=0,column=0), b2.grid(row=0,column=1), b3.grid(row=0,column=2)
        bfrm.pack()
        frm.pack()

    def add_to_startup_default(self,parent=None):
        """Creates a cron job with the default settings (30 mins after startup for the scraper to launch,
        an hour after startup for the main GUI to launch"""

        def cont_button():
            usr = ent.get()
            self.scheduler.enabledisable(True)
            self.scheduler.activation_delay()
            if sys.platform != 'win32':
                self.scheduler.cron_setup(usr)
            parent.destroy()

        cronfrm_default = Frame(parent)

        Label(master=parent, text='If you are on linux or macOS, enter your linux username, i.e. usr in home/usr, otherwise'
                                  'just hit Continue').pack()
        ent = Entry(master=cronfrm_default )
        ent.delete(0,END)
        ent.insert(0,str(self.scheduler.user))
        ent.pack()
        Button(master=cronfrm_default, text='Continue', command=cont_button).pack()
        cronfrm_default.pack()

    def add_to_startup_custom(self,parent=None):
        """Creates a cron job with user specified delays for the web scraper and GUI"""
        def cont_button_custom():
            self.scheduler.cron_enable(True)
            usr = entusr.get()
            scraper_delay = entdelay1.get()
            gui_delay = entdelay2.get()
            if sys.platform != 'win32':
                self.scheduler.cron_setup(usr)
            self.scheduler.activation_delay(int(scraper_delay), int(gui_delay))
            parent.destroy()

        cronfrm_custom = Frame(parent)
        cronfrm_custom.pack()
        Label(master=cronfrm_custom, text='''If you are on linux or macOS, enter your linux username, i.e. usr 
        in home/usr, otherwise leave this blank.''').pack()
        entusr = Entry(master=cronfrm_custom)
        entusr.delete(0,END)
        entusr.insert(0,self.scheduler.user)
        entusr.pack()
        Label(master=cronfrm_custom, text='Enter the delay from startup (in minutes) you would like'
                                          'before the application updates concert data from the internet').pack()
        entdelay1 = Entry(master=cronfrm_custom)
        entdelay1.delete(0,END)
        entdelay1.insert(0,str(self.scheduler.web_scraper_delay))
        entdelay1.pack()
        Label(master=cronfrm_custom, text='Enter the delay from startup (in minutes) you would like'
                                          'before the window containing upcoming concert data is opened').pack()
        entdelay2 = Entry(master=cronfrm_custom)
        entdelay2.delete(0,END)
        entdelay2.insert(0,str(self.scheduler.gui_launch_delay))
        entdelay2.pack()

        Button(master=cronfrm_custom, text='Submit', command=cont_button_custom).pack()

    def view_startup_settings(self):
        top = Toplevel()
        main_frame = Frame(top)
        if self.scheduler.init_on_startup:

            Label(master=main_frame,text=f'Launch on startup: Enabled').pack()
            Label(master=main_frame,text=f'Web Scraper offset : {self.scheduler.web_scraper_delay} Minutes after startup').pack()
            Label(master=main_frame,text=f'GUI Window offset: {self.scheduler.gui_launch_delay} Minutes after startup').pack()
        else:
            Label(master=main_frame,text='Launch on startup: Disabled').pack()
            Label(master=main_frame,
                  text=f'Web Scraper offset : Disabled').pack()
            Label(master=main_frame,
                  text=f'GUI Window offset: Disabled').pack()
        Button(master=main_frame,text='Done',command=top.destroy).pack()
        main_frame.pack()

    def exit_all(self):
        '''kills any seperate threads and exits the application'''
        global stop_all_threads
        stop_all_threads = True
        self.root.destroy()
        sleep(5)
        print([thread.name for thread in threading.enumerate()])

    def concert_time_to_update(self):
        """Updates the time range to display upcoming cocncerts in the GUI"""

        top = Toplevel()
        def button_event():
            time_to_display = int(float(location_input.get()))
            self.UpdateSettings.change_time_to_display(time_to_display)
            Notifications().check_dates()
            top.destroy()
            self.concert_frame.destroy()
            self.concert_frame = Frame(self.root, width=768, height=576, borderwidth=5, relief=RIDGE,pady=20)
            self.concert_frame.pack()
            up, framedimensions = Notifications().notify_user_()
            self.displaybar(self.concert_frame, up, framedimensions)

        location_frame = Frame(top)
        frame_input_text = 'Input how many weeks in advance you would like concert information to be displayed.'
        message2 = Label(location_frame, text=frame_input_text,wraplength=500)
        location_input = Entry(location_frame)
        location_input_button = Button(location_frame,command=button_event)
        message2.pack(),location_input.pack(), location_input_button.pack()
        location_frame.pack()

class SpotifyUpdate:
    """GUI class for running through artist selection via spotify, this is essentially the same as the
    related methods found in the FirstTimeStartup class, but slightly modified to be able to run independently of
    the sequential order used in FirstTimeStartup"""
    def __init__(self,parent,removed=None):
        self.root = parent
        with open('user_settings','r') as settings:
            data = json.load(settings)
            user_id = data['spotify_id']
        fr = Label(self.root,text='Updating Playlists - Please Wait')
        fr.pack()
        self.root.update()
        self.spotifyapp = spot.SpotifyIntegration('playlist-read-private',user_id)
        self.spotifyapp = self.spotifyapp()
        playlists = next(self.spotifyapp)
        fr.destroy()
        self.spotify_select_playlists(playlists,removed)

    def spotify_select_playlists(self,playlists,removed=None):
        """Gets a list of artists from the playlist"""

        def spot_selplay_continue_button(event,playlists=playlists):
            selection = [spot_selplay_choices.get(i) for i in spot_selplay_choices.curselection()]
            playlists = {name:data for name,data in playlists.items() if name in selection}
            spot_selplay.destroy()
            self.root.update()
            artists = self.spotifyapp.send(playlists)
            self.spotify_select_artists(artists,removed)

        spot_selplay = Frame(self.root)
        spot_selplay_desc = Label(spot_selplay,text = 'Select which playlists you would like to track artists from',wraplength=500)
        spot_selplay_choices =Listbox(spot_selplay,selectmode=MULTIPLE)
        spot_selplay_button =Button(spot_selplay,text='Continue')
        spot_selplay_button.bind('<Button-1>',spot_selplay_continue_button)

        spot_selplay_desc.pack(),spot_selplay_choices.pack(),spot_selplay_button.pack()
        spot_selplay.pack()

        for key,_ in playlists.items():
            spot_selplay_choices.insert(END,key)

    def spotify_select_artists(self,artists,removed=None):
        """Select which artists are to be tracked"""
        if removed is not None:
            artists = [band for band in artists if band not in removed]
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

    uid = '1214002279'


if __name__ == '__main__':
    app = Tk()
    #FirstTimeStartup(app).concert_lookup()

    main_test = Main_GUI(app)
    main_test()


