from tkinter import *
from time import sleep
import Spotify_API_Integration as spot
from InitialSetup import setup_data





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
        self.message1(parent)

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
            frame2.destroy()
            self.spotify_int(startup)
            return val

        frame2 = Frame(startup)
        message2text = ' In order to only keep track of nearby concerts, your location is requred. Please input' \
                       'the location you would like to track from in the form City,State. Note that this application is' \
                       'currently limited to only United States residents'
        message2 = Label(frame2, text=message2text)
        location_input = Entry(frame2)
        location_input_button = Button(frame2)
        location_input_button.bind('<Button-1>', message2_button)
        startup.update()
        message2.pack(), location_input.pack(), location_input_button.pack()
        frame2.pack()

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
                                          'determine what bands to track?')
        spotint_yes = Button(spotint,text='Yes')
        spotint_no = Button(spotint,text='No')
        spotint_yes.bind('<Button-1>',spotint_yes_button)
        spotint_no.bind('<Button-1>', spotint_no_button)
        spotint_text.pack(),spotint_yes.pack(),spotint_no.pack()
        spotint.pack()

    def spotify_setup_user_input(self,startup):
        def spotint_send_button(event):

            user_id = spot_usrsetup_field.get()
            spot_usrsetup.destroy()
            startup.update()
            print('user id recieved')

            spotifyapp = spot.SpotifyIntegration(user_id)
            spotifyapp = spotifyapp()
            playlists = next(spotifyapp)
            self.spotify_select_playlists(startup,playlists,spotifyapp)


        spot_usrsetup = Frame(startup)
        spot_usrsetup_dist = Label(spot_usrsetup,text = 'Note: in order to impliment spotify integration your spotify ID '
                                                        'is required. In most cases this is not the same as your spotify '
                                                        'login information. In order to find your spotify ID go to '
                                                        'https://www.spotify.com/us/account/overview/ and click on the '
                                                        '\'Change Password\' tab and copy the device username to the field below')
        spot_usrsetup_field = Entry(spot_usrsetup)
        spot_usrsetup_button = Button(spot_usrsetup,text='Enter')
        spot_usrsetup_button.bind('<Button-1>',spotint_send_button)
        spot_usrsetup_dist.pack(),spot_usrsetup_button.pack(),spot_usrsetup_field.pack()
        spot_usrsetup.pack()

    def spotify_select_playlists(self,startup,playlists,spotifyapp):
        """Gets a list of artists from the playlist"""
        self.spotifyapp = spotifyapp

        def spot_selplay_continue_button(event,playlists=playlists):
            playlists = {name:data for name,data in playlists.items() if name in spot_selplay_choices.get(ACTIVE)}
            spot_selplay.destroy()
            startup.update()
            artists = self.spotifyapp.send(playlists)

        spot_selplay = Frame(startup)
        spot_selplay_desc = Label(spot_selplay,text = 'Select which playlists you would like to track artists from')
        spot_selplay_choices =Listbox(spot_selplay,selectmode=MULTIPLE)
        spot_selplay_button =Button(spot_selplay,text='Continue')
        spot_selplay_button.bind('<Button-1>',spot_selplay_continue_button)

        spot_selplay_desc.pack(),spot_selplay_choices.pack(),spot_selplay_button.pack()
        spot_selplay.pack()

        for key,_ in playlists.items():
            spot_selplay_choices.insert(END,key)

    def spotify_select_artists(self,startup,artists):
        """Select which artists are to be tracked"""
        spot_selbands = Frame(startup)
        spot_selbands_desc = Label(spot_selbands,text='Select which bands you would like to follow or just press Continue '
                                                      'to track all listed')
        spot_selbands_choices = Listbox(spot_selbands,selectmode=MULTIPLE)
        spot_selbands_button = Button(spot_selbands,text='Done')
        for band in artists:
            spot_selbands_choices.insert(END,band)

if __name__ == '__main__':


    test = StartupInterface()
    s = Tk()

    #test.first_time_startup_events(s)
    uid = '1214002279'
    FirstTimeStartup(s)
    mainloop()

    #test.main_menu(root_gui)

