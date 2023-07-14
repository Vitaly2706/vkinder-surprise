from datetime import datetime 

import vk_api

from config import acces_token
from repository import ViewedProfilesRepository
from user_profile import UserProfile

from constants import MAX_USER_PROFILES_TO_SHOW, MAX_VK_USERS_SEARCH_ATTEMPS, DEFAULT_USER_YEAR

class VkTools():

    def __init__(self, acces_token, repository: ViewedProfilesRepository):
       self.api = vk_api.VkApi(token=acces_token)
       self.repository = repository

    def get_user_profile(self, user_id):
        try:
            user, = self.api.method('users.get', {'user_id': user_id, 'fields': 'city,bdate,sex,relation,home_town'})
            return UserProfile(
                user_id,
                self.get_property(user, 'first_name', "") + ' ' + self.get_property(user, 'last_name', ""),
                self.get_property(user, 'sex'),
                self.get_user_year(user),
                user['city']['id'] if 'city' in user else None
            )
        except KeyError:
            return None
   
    def get_property(self, object, propertyName, defaultValue = None):
        return object[propertyName] if propertyName in object else defaultValue

    def search_user_profiles(self, user_profile: UserProfile):
        res = []
        try:
            offset = 0
            search_attempts = 0
            while len(res) < MAX_USER_PROFILES_TO_SHOW and search_attempts < MAX_VK_USERS_SEARCH_ATTEMPS:
                profiles = self.search_more_user_profiles(user_profile, offset)
                for profile in profiles:
                    if profile['is_closed'] == False and not self.repository.was_profile_viewed(user_profile.id, profile['id']):
                        res.append({'id' : profile['id'], 'name': profile['first_name'] + ' ' + profile['last_name']})        
                offset += 20
                search_attempts += 1
        except KeyError:
            pass
        return res

    def search_more_user_profiles(self, user_profile: UserProfile, offset):
        sex = 1 if user_profile.sex == 2 else 2
        curent_year = datetime.now().year
        age = curent_year - user_profile.birth_year
        age_from = age - 5
        age_to = age + 5        
        return self.api.method('users.search', {'count': 20, 'offset': offset, 'age_from': age_from, 'age_to': age_to, 'sex': sex,
         'city': user_profile.city, 'hometown': user_profile.hometown, 'status': 6, 'is_closed': False})['items']

    def get_user_year(self, params):
        birthday = self.get_property(params, 'bdate')
        if birthday == None:
            return None
        try:
            return int(birthday.split('.')[2])
        except IndexError:
            return None        

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
