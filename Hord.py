import csv
from typing import Any, Dict, List, Optional, Union

import pyowm

# Создание объекта OWM с уникальным API ключом.
owm = pyowm.OWM(API_key='e8105e17092b41b8c9eb198d7692a4f2', version='2.5')

# Список для хранения прогнозов погоды в виде словарей
forecasts: List[Dict[str, Any]] = []

# Эти словари позволяют изменять значения в одном месте и использовать их везде по программе.
menu_options: Dict[str, str] = {'city': '1', 'postal': '2', 'coords': '3'}
saved_data_fields: Dict[str, str] = {'loc':      'Location',
                                     'time':     'Time (UTC)',
                                     'desc':     'Description',
                                     'temp_min': 'Minimum Temperature (°C)',
                                     'temp_max': 'Maximum Temperature (°C)',
                                     'wind':     'Wind Speed (m/s)',
                                     'rain':     'Rain Accumulation (cm)',
                                     'snow':     'Snow Accumulation (cm)'}

def print_prompt() -> None:
# Выбор по городу, почтовому индексу или координатам
    ansi_bold: str = '\033[1m'
    ansi_reset: str = '\033[0m'

    print("Menu options:")
    print(f"\tEnter {ansi_bold}{menu_options['city']}{ansi_reset}: "
          f"\t\tsearch by city name and country code")
    print(f"\tEnter {ansi_bold}{menu_options['postal']}{ansi_reset}: "
          f"\t\tsearch by postal code and country code")
    print(f"\tEnter {ansi_bold}{menu_options['coords']}{ansi_reset}: "
          f"\t\tsearch by coordinates")
    print(f"\tEnter {ansi_bold}exit{ansi_reset}: \tquit")

def input_loop() -> None:

    while True:
        # Выводим меню
        print_prompt()
        user_input: str = input("\nEnter menu option: ")

        # Прерывание цикла, если введено "EXIT"
        if user_input.upper() == 'EXIT':
            break
        elif user_input == menu_options['city']:
            forecaster: Optional['Forecaster'] = get_forecaster_from_name()
        elif user_input == menu_options['postal']:
            forecaster: Optional['Forecaster'] = get_forecaster_from_postal()
        elif user_input == menu_options['coords']:
            forecaster: Optional['Forecaster'] = get_forecaster_from_coordinates()
        else:
            print('Invalid input. Try again.\n')
            continue

        # ВЫвод None, если будет исключение
        if not forecaster:
            print_forecast(forecaster)

    # Сохранение данных в файл после выхода из цикла
    dump_forecasts()

def get_forecaster_from_name() -> Optional['Forecaster']:

    city: str = input("Enter the city name: ")
    country_code: str = input("Enter the country code: ")
    lookup: str = city + ',' + country_code

    # Создание объекта forecaster на основе введенных данных
    try:
        forecaster: Optional['Forecaster'] = owm.three_hours_forecast(lookup)
        return forecaster
    except pyowm.exceptions.api_response_error.NotFoundError:
        # Ошибка, если данные некорректны
        print('\nThere was an error using the parameters entered. Try again.\n')

def get_forecaster_from_postal() -> Optional['Forecaster']:

    zip_code: str = input("Enter the postal code: ")
    country_code: str = input("Enter the country code: ")
    lookup: str = zip_code + ',' + country_code

    # Создание объекта forecaster на основе введенных данных
    try:
        forecaster: Optional['Forecaster'] = owm.three_hours_forecast(lookup)
        return forecaster
    except pyowm.exceptions.api_response_error.NotFoundError:
        print('\nThere was an error using the parameters entered. Try again.\n')

def get_forecaster_from_coordinates() -> Optional['Forecaster']:
    lat: Union[str, float] = input("Enter the latitude: ")
    long: Union[str, float] = input("Enter the longitude ")

    # Проверка, являются ли введенные значения числами
    if is_number(lat) and is_number(long):
        lat = float(lat)
        long = float(long)
    else:
        print("\nThe parameters entered are invalid. Try again.\n")
        return

    # Находятся ли координаты в допустимом диапазоне
    if -90 <= lat <= 90 and -180 <= long <= 180:
        try:
            # Попытка создать объект Forecaster на основе координат
            forecaster: Optional['Forecaster'] = owm.three_hours_forecast_at_coords(lat, long)
            return forecaster
        except pyowm.exceptions.api_response_error.NotFoundError:
            print('\nThere was an error using the parameters entered. Try again.\n')
    else:
        print("\nThe parameters entered are invalid. Try again.\n")

def is_number(string: str) -> bool:

    # Функция для проверки, можно ли строку преобразовать в число.

    try:
        float(string)
        return True
    except ValueError:
        return False

def print_forecast(forecaster: 'Forecaster') -> None:

    # Вывод прогноза погоды для заданного местоположения.
    # Также сохраняет данные прогноза в список forecasts для последующего экспорта.

    forecast: 'Forecast' = forecaster.get_forecast()
    location = forecast.get_location()
    ansi_bold: str = '\033[1m'
    ansi_yellow: str = '\033[33m'
    ansi_reset: str = '\033[0m'

    # Итерация по прогнозам на следующие 5 дней
    for weather in forecast:
        # Получение количества осадков (дождь и снег) для каждого временного интервала
        rain_length, rainfall = len(weather.get_rain()), '0'
        snow_length, snowfall = len(weather.get_snow()), '0'

        if rain_length > 0:
            rainfall = weather.get_rain()['3h']
        if snow_length > 0:
            snowfall = weather.get_snow()['3h']

        temp_min = weather.get_temperature(unit='celsius')['temp_min']
        temp_max = weather.get_temperature(unit='celsius')['temp_max']

        # Логика для отображения диапазона температур, если минимальное и максимальное значения различаются
        temperature = temp_min if temp_min == temp_max else "{} - {}".format(temp_min, temp_max)

        # Вывод прогноза
        print(f"\n{ansi_bold}{location.get_name()} at "
              f"{weather.get_reference_time('iso')}{ansi_reset}"
              f"\n\tDescription:\t\t{ansi_yellow}{weather.get_detailed_status()}{ansi_reset}"
              f"\n\tTemperature (°C):\t{ansi_yellow}{temperature}{ansi_reset}"
              f"\n\tWind Speed (m/s):\t{ansi_yellow}{weather.get_wind()['speed']}{ansi_reset}"
              f"\n\tRainfall (cm):\t\t{ansi_yellow}{rainfall}{ansi_reset}"
              f"\n\tSnowfall (cm):\t\t{ansi_yellow}{snowfall}{ansi_reset}")

        # Добавление данных прогноза в список forecasts
        forecasts.append({saved_data_fields['loc']:      location.get_name(),
                          saved_data_fields['time']:     weather.get_reference_time('iso'),
                          saved_data_fields['desc']:     weather.get_detailed_status(),
                          saved_data_fields['temp_min']: weather.get_temperature(unit='celsius')[
                                                             'temp_min'],
                          saved_data_fields['temp_max']: weather.get_temperature(unit='celsius')[
                                                             'temp_max'],
                          saved_data_fields['wind']:     weather.get_wind()['speed'],
                          saved_data_fields['rain']:     rainfall,
                          saved_data_fields['snow']:     snowfall})

    print(f'\n{ansi_bold}========================================{ansi_reset}\n')

def dump_forecasts() -> None:

    # Сохраняет все данные, напечатанные в консоли за сессию, в файл forecasts.csv

    try:
        # Открываеn CSV файл для записи
        with open('forecasts.csv', 'w') as data_dump:
            # Используеn заранее определенные поля для заголовка и поиска в словарях
            writer = csv.DictWriter(data_dump, fieldnames=(saved_data_fields['loc'],
                                                           saved_data_fields['time'],
                                                           saved_data_fields['desc'],
                                                           saved_data_fields['temp_min'],
                                                           saved_data_fields['temp_max'],
                                                           saved_data_fields['wind'],
                                                           saved_data_fields['rain'],
                                                           saved_data_fields['snow']))
            writer.writeheader()
            # Записываеn каждый прогноз в CSV файл
            for data in forecasts:
                writer.writerow(data)
    except IOError:
        print('I/O error')

input_loop()
