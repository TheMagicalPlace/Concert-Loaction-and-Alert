from tkinter import *
from time import sleep
import Spotify_API_Integration as spot
from InitialSetup import LocatorSetup




class StartupInterface():
    """Initializes required user data on first time use"""
    def __init__(self):
        self.spotifyapp = None

        try:
            with open('user_settings', 'r') as settings:
                pass
        except FileNotFoundError:
            print('File Not Found')

class FirstTimeStartup:
    spotifyapp = None
    """Runs through the first time setup GUI"""
    def __init__(self,parent):
        self.spotifyapp = None
        self.user_data_setup = LocatorSetup()
        self.user_data_setup = self.user_data_setup()

        # Attempts to prime the user_data_setup coroutine, if it returns a StopIteration user data is already present
        # and the initial setup code is not run (outside instancing the class)
        try:
            next(self.user_data_setup)
        except StopIteration:
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



if __name__ == '__main__':


    test = StartupInterface()
    s = Tk()

    #test.first_time_startup_events(s)
    uid = '1214002279'
    FirstTimeStartup(s)
