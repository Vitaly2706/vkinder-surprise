
from operator import attrgetter
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import community_token, acces_token
from repository import ViewedProfilesRepository
from vk_tools import VkTools

from constants import MAX_USER_PROFILES_TO_SHOW, MAX_USER_PHOTOS_TO_SHOW

class VkinderSurprise():

    def __init__(self, community_token, acces_token):
        self.api = vk_api.VkApi(token=community_token)
        self.repository = ViewedProfilesRepository()
        self.vk_tools = VkTools(acces_token, self.repository)
        self.user_profile = None
        self.input_user_data_mode = False

    def start_listening(self):
        longpoll = VkLongPoll(self.api)                
        for event in longpoll.listen():
            try:
                if event.type == VkEventType.MESSAGE_NEW and event.to_me:                
                    if self.input_user_data_mode:                    
                        self.handle_user_data_input(event.user_id, event.text)
                    else:
                        self.handle_user_command(event.user_id, event.text.lower())
            except vk_api.exceptions.ApiError:
                print(f"No permissions to send messages to user_id={event.user_id}")
                pass

    def handle_user_command(self, user_id, command):
        match command:
            case 'привет':
                self.user_profile = self.vk_tools.get_user_profile(user_id)                
                if self.user_profile == None:
                    self.send_message(user_id, f'Привет! К сожалению, не получилось прочитать Ваш профиль.')
                    return
                
                missing_data = self.user_profile.get_missing_data_if_any()
                if missing_data:
                    self.send_message(user_id, f"Не удалось прочитать из Вашего профиля некоторые данные, необходимы для поиска наиболее пододящих пар. Если Вы не хотите предоставить информацию, то введите символ '-' в ответ на любой из вопросов.")
                    self.send_message(user_id, f"Ваш {missing_data.value.lower()}:")
                    self.input_user_data_mode = True
                else:
                    print(self.user_profile)
                    self.send_message(user_id, f'Привет, {self.user_profile.name}!')
            case 'поиск':
                if self.user_profile != None: 
                    profiles = self.vk_tools.search_user_profiles(self.user_profile)
                    if len(profiles) == 0:
                        self.send_message(user_id, f'К сожалению, не смог найти ни одной пары.')
                        return
                    for profile in profiles[:MAX_USER_PROFILES_TO_SHOW]:
                        self.send_user_photos(profile)
                        self.repository.add_viewed_profile(user_id, profile["id"])
                else:
                    self.send_message(user_id, f'Для начала поиска пар нужно вначале прочитать Ваш профиль, выполнив команду "привет".')
            case _:
                self.send_message(user_id, 'Неизвестная команда. Вначале напишине "привет", чтобы чат-бот прочитал Ваш профиль. Далее для поиска анкет выполните команду "поиск".')
    
    def handle_user_data_input(self, user_id, input):
        if input.strip() == '-':
            self.send_message(user_id, f'Вы отказались вводить свои данные, поэтому я не смогу продолжить и рекомендовать Вам пару. До свидания!')
            self.user_profile = None
            self.input_user_data_mode = False
            return                                

        self.user_profile.add_user_data(input.strip())
        missing_data = self.user_profile.get_missing_data_if_any()
        if missing_data:
            self.send_message(user_id, f"Ваш {missing_data.value.lower()}:")
        else:
            self.send_message(user_id, f'Отлично, теперь есть все необходимые данные, чтобы начать поиск пары. Для этого введите команду "поиск".')
            self.input_user_data_mode = False

    def send_message(self, user_id, message, attachment=None):
        self.api.method('messages.send', {'user_id': user_id, 'message': message, 'attachment': attachment, 'random_id': get_random_id()})
        
    def send_user_photos(self, user):
        user_id = user["id"]
        photos = self.vk_tools.get_user_profile_photos(user_id)
        self.send_message(self.user_profile.id, f'Встречайте {user["name"]} (https://vk.com/id{user_id})', attachment=self.photos_to_attachement(photos[:MAX_USER_PHOTOS_TO_SHOW]))

    def photos_to_attachement(self, photos):
        return ",".join(
            map(lambda photo: f'photo{photo["owner_id"]}_{photo["id"]}', photos)
        )

if __name__ == '__main__':
    bot = VkinderSurprise(community_token, acces_token)
    bot.start_listening()
