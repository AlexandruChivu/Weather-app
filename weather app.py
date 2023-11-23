from tkinter import *
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from datetime import *
import pytz
from PIL import Image, ImageTk
import openmeteo_requests
import requests_cache
from retry_requests import retry


def get_weather():
    city = search_textfield.get()
    geolocator = Nominatim(user_agent="geoapi Exercises")
    location = geolocator.geocode(city)

    obj = TimezoneFinder()
    result = obj.timezone_at(lng=location.longitude, lat=location.latitude)
    result_content = result.split("/")
    continent = result_content[0]
    timezone.config(text=continent + f'/{city.capitalize()}')
    long_lat.config(text=f"{round(location.latitude, 1)}°N,{round(location.longitude, 1)}°E ")

    home = pytz.timezone(result)
    local_time = datetime.now(home)
    current_time = local_time.strftime("%I:%M %p")
    clock.config(text=current_time)

    # Setup the Open-Meteo API client with cache and retry on error
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": location.latitude,
        "longitude": location.longitude,
        "current": ["temperature_2m", "relative_humidity_2m", "surface_pressure", "wind_speed_10m", "weather_code"],
        "hourly": "surface_pressure",
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "wind_speed_10m_max"],
        "timezone": "auto"
    }

    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    weather_codes_interpretation = {
        0: 'Clear sky', 1: 'Mainly Clear', 2: 'Partly cloudy', 3: 'Overcast',
        45: 'Fog', 48: 'Deposing rime fog', 51: 'Light drizzle', 53: 'Moderate drizzle',
        55: 'Dense drizzle', 56: 'Freezing drizzle', 57: 'Dense freezing drizzle',
        61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain', 66: 'Light freezing rain',
        67: 'Heavy freezing rain', 71: 'Slight snow fall', 73: 'Moderate snow fall',
        75: 'Heavy snow fall', 77: 'Snow grains', 80: 'Light rain showers',
        81: 'Moderate rain showers',
        82: 'Violent rain showers', 85: 'Light snow showers', 86: 'Heavy snow showers',
        95: 'Slight thunderstorms',
        96: 'Thunderstorm with rain', 99: 'Thunderstorm with hail'
    }

    def weather_images(weather_code, x=None, y=None):
        if weather_code in [0, 1]:
            icon_file = 'Images/icons/sun.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code == 2:
            icon_file = 'Images/icons/cloudy.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code == 3:
            icon_file = 'Images/icons/cloud.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code in [45, 48]:
            icon_file = 'Images/icons/foog.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code in [51, 61, 80]:
            icon_file = 'Images/icons/cloudy rain.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code in [53, 55, 63, 81]:
            icon_file = 'Images/icons/rain moderate.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code in [56, 71]:
            icon_file = 'Images/icons/snowy.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code in [73, 75, 85, 86]:
            icon_file = 'Images/icons/snow.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code == 65:
            icon_file = 'Images/icons/rainy.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code in [57, 66, 67]:
            icon_file = 'Images/icons/freezing rain.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code == 77:
            icon_file = 'Images/icons/hail.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code == 82:
            icon_file = 'Images/icons/shower.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code == 95:
            icon_file = 'Images/icons/storm.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code == 99:
            icon_file = 'Images/icons/thunderstorm with hail.png'
            photo = ImageTk.PhotoImage(file=icon_file)
        elif weather_code == 96:
            icon_file = 'Images/icons/storm rainy.png'
            photo = ImageTk.PhotoImage(file=icon_file)

        if x or y:
            img = Image.open(icon_file)
            resized_image = img.resize((50, 50))
            photo = ImageTk.PhotoImage(resized_image)

        return photo

    # Current values. The order of variables needs to be the same as requested.
    current = response.Current()
    current_temperature = current.Variables(0).Value()
    current_relative_humidity = current.Variables(1).Value()
    current_surface_pressure = current.Variables(2).Value()
    current_wind_speed = current.Variables(3).Value()
    current_weather_code = current.Variables(4).Value()

    # Process hourly data. The order of variables needs to be the same as requested.
    hourly = response.Hourly()
    hourly_surface_pressure = hourly.Variables(0).ValuesAsNumpy()

    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    weather_codes = daily.Variables(0).ValuesAsNumpy(),
    daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
    daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
    daily_wind_speed_10m_max = daily.Variables(3).ValuesAsNumpy()

    t.config(text=f"{int(current_temperature)}°C")
    h.config(text=f"{int(current_relative_humidity)} %")
    p.config(text=f"{int(current_surface_pressure)} hPa")
    w.config(text=f"{int(current_wind_speed)} Km/h")
    d.config(text=weather_codes_interpretation[current_weather_code])

    # firstcell
    photo1 = weather_images(int(current_weather_code))
    firstimage.config(image=photo1)
    firstimage.image = photo1

    temperature_day1 = int(daily_temperature_2m_max[0])
    temperature_night1 = int(daily_temperature_2m_min[0])

    day1temp.config(text=f"Day / Night\n{temperature_day1}°C / {temperature_night1}°C")

    # secondcell
    photo2 = weather_images(int(weather_codes[0][1]), x=50, y=50)
    secondimage.config(image=photo2)
    secondimage.image = photo2

    temperature_day2 = int(daily_temperature_2m_max[1])
    temperature_night2 = int(daily_temperature_2m_min[1])

    day2temp.config(text=f"Day / Night\n{temperature_day2}°C / {temperature_night2}°C")

    # thirdcell
    photo3 = weather_images(int(weather_codes[0][2]), x=50, y=50)
    thirdimage.config(image=photo3)
    thirdimage.image = photo3

    temperature_day3 = int(daily_temperature_2m_max[2])
    temperature_night3 = int(daily_temperature_2m_min[2])

    day3temp.config(text=f"Day / Night\n{temperature_day3}°C / {temperature_night3}°C")

    # fourthcell
    photo4 = weather_images(int(weather_codes[0][3]), x=50, y=50)
    fourthimage.config(image=photo4)
    fourthimage.image = photo4

    temperature_day4 = int(daily_temperature_2m_max[3])
    temperature_night4 = int(daily_temperature_2m_min[3])

    day4temp.config(text=f"Day / Night\n{temperature_day4}°C / {temperature_night4}°C")

    # fifthcell
    photo5 = weather_images(int(weather_codes[0][4]), x=50, y=50)
    fifthimage.config(image=photo5)
    fifthimage.image = photo5

    temperature_day5 = int(daily_temperature_2m_max[4])
    temperature_night5 = int(daily_temperature_2m_min[4])

    day5temp.config(text=f"Day / Night\n{temperature_day5}°C / {temperature_night5}°C")

    # sixthcell
    photo6 = weather_images(int(weather_codes[0][5]), x=50, y=50)
    sixthimage.config(image=photo6)
    sixthimage.image = photo6

    temperature_day6 = int(daily_temperature_2m_max[5])
    temperature_night6 = int(daily_temperature_2m_min[5])

    day6temp.config(text=f"Day / Night\n{temperature_day6}°C / {temperature_night6}°C")

    # seventhcell
    photo7 = weather_images(int(weather_codes[0][6]), x=50, y=50)
    seventhimage.config(image=photo7)
    seventhimage.image = photo7

    temperature_day7 = int(daily_temperature_2m_max[6])
    temperature_night7 = int(daily_temperature_2m_min[6])

    day7temp.config(text=f"Day / Night\n{temperature_day7}°C / {temperature_night7}°C")

    # days
    first = datetime.now()
    day1.config(text=first.strftime("%A"))

    second = first + timedelta(days=1)
    day2.config(text=second.strftime('%A'))

    third = second + timedelta(days=1)
    day3.config(text=third.strftime('%A'))

    fourth = third + timedelta(days=1)
    day4.config(text=fourth.strftime('%A'))

    fifth = fourth + timedelta(days=1)
    day5.config(text=fifth.strftime('%A'))

    sixth = fifth + timedelta(days=1)
    day6.config(text=sixth.strftime('%A'))

    seventh = sixth + timedelta(days=1)
    day7.config(text=seventh.strftime('%A'))


root = Tk()
root.title("Weather App")
root.geometry("890x470+300+300")
root.configure(bg="#57adff")
root.resizable(False, False)

# Icon
app_icon_file = PhotoImage(file="Images/logo.png")
root.iconphoto(False, app_icon_file)

round_box_file = PhotoImage(file="Images/Rounded Rectangle 1.png")
Label(root, image=round_box_file, bg="#57adff").place(x=30, y=110)

# labels

label1 = Label(root, text="Temperature", font=("Helvetica", 11), fg="White", bg="#213135")
label1.place(x=50, y=115)

label2 = Label(root, text="Humidity", font=("Helvetica", 11), fg="White", bg="#213135")
label2.place(x=50, y=135)

label3 = Label(root, text="Pressure", font=("Helvetica", 11), fg="White", bg="#213135")
label3.place(x=50, y=155)

label4 = Label(root, text="Wind Speed", font=("Helvetica", 11), fg="White", bg="#213135")
label4.place(x=50, y=175)

label5 = Label(root, text="Description", font=("Helvetica", 11), fg="White", bg="#213135")
label5.place(x=50, y=195)

# search_box

search_background_file = PhotoImage(file="Images/Rounded Rectangle 3.png")
search_background = Label(image=search_background_file, bg="#57adff")
search_background.place(x=300, y=110)

search_white_file = PhotoImage(file="Images/Rounded Rectangle 2.png")
search_white = Label(image=search_white_file, bg="#213135")
search_white.place(x=377, y=117)

search_weather_image_file = PhotoImage(file="Images/Layer7.png")
search_weather_image = Label(root, image=search_weather_image_file, bg="#213135")
search_weather_image.place(x=315, y=117)

search_textfield = Entry(root, justify='center', width=24, font=("poppins", 18), bg="#ffffff", border=0, fg="black")
search_textfield.place(x=381, y=121)
search_textfield.focus()

search_icon_file = PhotoImage(file="Images/Layer6.png")
search_icon_button = Button(image=search_icon_file, borderwidth=0, cursor='hand2', bg="#213135", command=get_weather)
search_icon_button.place(x=710, y=123)

# Bind the <Return> key to the getWeather function
root.bind('<Return>', lambda event=None: get_weather())

# bottom boxes

frame = Frame(root, width=900, height=200, bg="#212120")
frame.pack(side=BOTTOM)

firstbox_file = PhotoImage(file="Images/Rounded Rectangle 4.png")
secondbox_file = PhotoImage(file="Images/Rounded Rectangle 5.png")

Label(frame, image=firstbox_file, bg="#212120").place(x=30, y=20)
Label(frame, image=secondbox_file, bg="#212120").place(x=285, y=30)
Label(frame, image=secondbox_file, bg="#212120").place(x=385, y=30)
Label(frame, image=secondbox_file, bg="#212120").place(x=485, y=30)
Label(frame, image=secondbox_file, bg="#212120").place(x=585, y=30)
Label(frame, image=secondbox_file, bg="#212120").place(x=685, y=30)
Label(frame, image=secondbox_file, bg="#212120").place(x=785, y=30)

# clock
clock = Label(root, font=("Helvetica", 30, 'bold'), fg='white', bg='#57adff')
clock.place(x=30, y=20)

# timezone
timezone = Label(root, font=("Helvetica", 20), fg='white', bg='#57adff')
timezone.place(x=650, y=15)

# longitude and latitude
long_lat = Label(root, font=("Helvetica", 20), fg='white', bg='#57adff')
long_lat.place(x=650, y=50)

# temperature label
t = Label(root, font=('Helvetica', 11), fg="white", bg="#213135")
t.place(x=150, y=115)

# humidity label
h = Label(root, font=('Helvetica', 11), fg="white", bg="#213135")
h.place(x=150, y=135)

# pressure label
p = Label(root, font=('Helvetica', 11), fg="white", bg="#213135")
p.place(x=150, y=155)

# wind label
w = Label(root, font=('Helvetica', 11), fg="white", bg="#213135")
w.place(x=150, y=175)

# description label
d = Label(root, font=('Helvetica', 11), fg="white", bg="#213135")
d.place(x=150, y=195)

# first cell
firstframe = Frame(root, width=225, height=141, bg="#292b2b")
firstframe.place(x=37, y=297)

day1 = Label(firstframe, font=(18), bg="#292b2b", fg="#fff")
day1.place(x=110, y=5)

firstimage = Label(firstframe, bg="#292b2b")
firstimage.place(x=5, y=20)

day1temp = Label(firstframe, bg='#292b2b', fg="#57adff", font="arial 15 bold")
day1temp.place(x=115, y=60)

# second cell
secondframe = Frame(root, width=74, height=120, bg="#292b2b")
secondframe.place(x=292, y=307)

day2 = Label(secondframe, bg="#292b2b", fg="#fff")
day2.place(x=0, y=0)

secondimage = Label(secondframe, bg="#292b2b")
secondimage.place(x=7, y=25)

day2temp = Label(secondframe, bg='#292b2b', fg="#57adff", font="arial 9 bold")
day2temp.place(x=2, y=80)

# third cell
thirdframe = Frame(root, width=74, height=120, bg="#292b2b")
thirdframe.place(x=392, y=307)

day3 = Label(thirdframe, bg="#292b2b", fg="#fff")
day3.place(x=0, y=0)

thirdimage = Label(thirdframe, bg="#292b2b")
thirdimage.place(x=7, y=25)

day3temp = Label(thirdframe, bg='#292b2b', fg="#57adff", font="arial 9 bold")
day3temp.place(x=2, y=80)

# fourth cell
fourthframe = Frame(root, width=74, height=120, bg="#292b2b")
fourthframe.place(x=492, y=307)

day4 = Label(fourthframe, bg="#292b2b", fg="#fff")
day4.place(x=0, y=0)

fourthimage = Label(fourthframe, bg="#292b2b")
fourthimage.place(x=7, y=25)

day4temp = Label(fourthframe, bg='#292b2b', fg="#57adff", font="arial 9 bold")
day4temp.place(x=2, y=80)

# fifth cell
fifthframe = Frame(root, width=74, height=120, bg="#292b2b")
fifthframe.place(x=592, y=307)

day5 = Label(fifthframe, bg="#292b2b", fg="#fff")
day5.place(x=0, y=0)

fifthimage = Label(fifthframe, bg="#292b2b")
fifthimage.place(x=7, y=25)

day5temp = Label(fifthframe, bg='#292b2b', fg="#57adff", font="arial 9 bold")
day5temp.place(x=2, y=80)

# sixth cell
sixthframe = Frame(root, width=74, height=120, bg="#292b2b")
sixthframe.place(x=692, y=307)

day6 = Label(sixthframe, bg="#292b2b", fg="#fff")
day6.place(x=0, y=0)

sixthimage = Label(sixthframe, bg="#292b2b")
sixthimage.place(x=7, y=25)

day6temp = Label(sixthframe, bg='#292b2b', fg="#57adff", font="arial 9 bold")
day6temp.place(x=2, y=80)

# seventh cell
seventhframe = Frame(root, width=74, height=120, bg="#292b2b")
seventhframe.place(x=792, y=307)

day7 = Label(seventhframe, bg="#292b2b", fg="#fff")
day7.place(x=0, y=0)

seventhimage = Label(seventhframe, bg="#292b2b")
seventhimage.place(x=7, y=25)

day7temp = Label(seventhframe, bg='#292b2b', fg="#57adff", font="arial 9 bold")
day7temp.place(x=2, y=80)

mainloop()
