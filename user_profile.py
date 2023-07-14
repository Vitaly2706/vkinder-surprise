from dataclasses import dataclass
from enum import Enum

class UserInfo(Enum):
    CITY = "Город"
    BIRTH_YEAR = "Год рождения"
    SEX = "Пол (м/ж)"

@dataclass
class UserProfile:
    id: str
    name: str
    sex: int = None
    birth_year: int = None
    city: int = None
    hometown: str = None

    def is_all_personal_data_available(self):
        return self.get_missing_data_if_any != None

    def get_missing_data_if_any(self):
        if self.city == None and self.hometown == None:
            return UserInfo.CITY
        elif self.birth_year == None:
            return UserInfo.BIRTH_YEAR
        elif self.sex == None:
            return UserInfo.SEX
        else:
            return None

    def add_user_data(self, value):        
        match self.get_missing_data_if_any():
            case UserInfo.CITY:
                self.hometown = value
            case UserInfo.SEX:
                if value == 'м':
                    self.sex = 2
                elif value == 'ж':
                    self.sex = 1
            case UserInfo.BIRTH_YEAR:
                try:
                    self.birth_year = int(value)
                except ValueError:
                    pass
        
