from datetime import datetime 

import vk_api

from config import acces_token
from repository import ViewedProfilesRepository

from constants import *

class VkTools():

    def __init__(self, acces_token, repository: ViewedProfilesRepository):
       self.api = vk_api.VkApi(token=acces_token)
       self.repository = repository

    def get_user_profile(self, user_id):
        try:
            user, = self.api.method('users.get', {'user_id': user_id, 'fields': 'city,bdate,sex,relation,home_town'})
            return { 'name': self.get_property(user, 'first_name', "") + ' ' + self.get_property(user, 'last_name', ""),
                    'id':  user['id'],
                    'bdate': self.get_property(user, 'bdate', '01.01.1990'),
                    'home_town': self.get_property(user, 'home_town'),
                    'sex': self.get_property(user, 'sex', 1),
                    'city': user['city']['id'] if 'city' in user else None
                }
        except KeyError:
            return None
   
    def get_property(self, object, propertyName, defaultValue = None):
        return object[propertyName] if propertyName in object else defaultValue

    def search_user_profiles(self, params):
        res = []
        try:
            offset = 0
            search_attempts = 0
            while len(res) < MAX_USER_PROFILES_TO_SHOW and search_attempts < MAX_VK_USERS_SEARCH_ATTEMPS:
                profiles = self.search_more_user_profiles(params, offset)
                for profile in profiles:
                    if profile['is_closed'] == False and not self.repository.was_profile_viewed(params['id'], profile['id']):
                        res.append({'id' : profile['id'], 'name': profile['first_name'] + ' ' + profile['last_name']})        
                offset += 20
                search_attempts += 1
        except KeyError:
            pass
        return res

    def search_more_user_profiles(self, params, offset):
        sex = 1 if params['sex'] == 2 else 2
        city = params['city']
        curent_year = datetime.now().year
        user_year = self.get_user_year(params['bdate'])
        age = curent_year - user_year
        age_from = age - 5
        age_to = age + 5        
        return self.api.method('users.search', {'count': 20, 'offset': offset, 'age_from': age_from, 'age_to': age_to, 'sex': sex, 'city': city, 'status': 6, 'is_closed': False})['items']

    def get_user_year(self, birthday):
        try:
            return int(birthday.split('.')[2])
        except IndexError:
            return DEFAULT_USER_YEAR

    def get_user_profile_photos(self, user_id):
        res = []
        try:
            photos = self.api.method('photos.get', {'user_id': user_id, 'album_id': 'profile', 'extended': 1})["items"]
            for photo in photos:
                res.append({'owner_id': photo['owner_id'], 'id': photo['id'], 'likes': photo['likes']['count'], 'comments': photo['comments']['count']})            

            res.sort(key=lambda x: x['likes'] + x['comments'] * 10, reverse=True)
        except KeyError:
            pass
        return res
