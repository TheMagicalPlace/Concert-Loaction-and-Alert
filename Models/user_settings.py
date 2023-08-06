import json
import os
from json import JSONDecodeError


class UserSettings:
    def __init__(self, populate_empty = False):
        if(populate_empty):
            self.user_location = [None, None]
            self.bands = []
            self.spotify_id = None
            self.last_checked = None
            self.concert_notification_time_to_display = 2
            self.removed_bands = []


    def __new__(cls):
        print(f'Creating a new {cls.__name__} object...')
        obj = cls.load_from_default_location()
        return obj

    def save_to_file(self):
        with open(os.path.join('userdata','user_settings'),'w') as settings:
            json.dump(self.__dict__,settings)
    @classmethod
    def load_from_default_location(cls):
        try:
            with open(os.path.join('userdata','user_settings'),'r') as settings:
                try:
                    data = json.load(settings)
                except JSONDecodeError:
                    data = {}
                return cls.load_to_model(data)

        except FileNotFoundError:
            pass
    @classmethod
    def load_to_model(cls,json_dict):
        model = super().__new__(cls)
        model.__init__(True)
        properties = [attr for attr in model.__dict__ if not attr.startswith("__")]
        for p in properties:
            if p in json_dict.keys():
                model.__setattr__(p,json_dict[p])
        return model
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__,
            sort_keys=True, indent=4)

    # def save_data(self):
    #     "Saves user data to a JSON file"
    #     data = { 'user_location':self.user_location,
    #              'bands':list(set(self.user_settings.bands)),
    #             'spotify_id':self.spotify_id,
    #             'last_checked':self.user_settings.last_checked,
    #             'concert_notification_time_to_display':self.concert_notification_time_to_display,# weeks, default time until concert to present notifications
    #             'removed_bands':self.removed_bands}
    #     with open(os.path.join('userdata','user_settings'),'w') as settings:
    #         json.dump(data,settings)