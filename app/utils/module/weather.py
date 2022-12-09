from typing import Optional

from pyowm import OWM
from pyowm.utils.config import get_default_config

from decorator.cache import cache


class Weather:
    __emoji_weather = {'пасмурно': '☁',
                       'облачно с прояснениями': '🌥',
                       'переменная облачность': '⛅',
                       'небольшая облачность': '🌤',
                       'ясно': '☀',
                       'сильный дождь': '🌧',
                       'дождь': '🌧',
                       'небольшой дождь': '🌧',
                       'небольшой снег': '🌨',
                       'гроза': '🌩',
                       'туман': '🌫'
                       }

    def __init__(self, token: Optional[str], city: Optional[str], language: Optional[str] = 'en'):
        self.__token = token
        self.__city = city
        self.__language = language

    @property
    def language(self):
        """Get-er"""
        return self.__language

    @language.setter
    def language(self, language: Optional[str]):
        if not isinstance(language, str):
            raise ValueError("Значення повинно бути типу str")

        self.__language = language

    @property
    def city(self):
        """Get-er"""
        return self.__language

    @city.setter
    def city(self, city: Optional[str]):
        if not isinstance(city, str):
            raise ValueError("Значення повинно бути типу str")
        self.__city = city

    def __get_weather(self, language: Optional[str] = None):
        config_dict = get_default_config()
        if language:
            config_dict['language'] = language
        else:
            config_dict['language'] = self.language
        owm = OWM(self.__token, config_dict)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(self.__city)
        return observation.weather

    @cache(60*5)
    def get_detailed_status(self, emoji: Optional[bool] = None) -> Optional[str]:
        """
            Вертає статус погоди

        Args:
            emoji: If True - return emoji

        Returns:

        """

        if emoji:
            detailed_status = self.__get_weather('ru').detailed_status
            return self.__emoji_weather.get(detailed_status)

        return self.__get_weather().detailed_status
