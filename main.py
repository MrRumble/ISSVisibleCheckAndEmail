import smtplib
import requests
from datetime import datetime
import os
from dotenv import load_dotenv
import time

#------------------------------------- API REQUESTS -----------------------------------------#

load_dotenv()
MY_LAT = float(os.getenv("MY_LAT"))
MY_LONG = float(os.getenv("MY_LONG"))

response = requests.get(url="http://api.open-notify.org/iss-now.json")
response.raise_for_status()
data = response.json()

iss_latitude = float(data["iss_position"]["latitude"])
iss_longitude = float(data["iss_position"]["longitude"])

#Your position is within +5 or -5 degrees of the ISS position.

parameters = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0,
}

response = requests.get("https://api.sunrise-sunset.org/json", params=parameters)
response.raise_for_status()
data = response.json()
sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])

time_now = datetime.now()

iss_current_position = (iss_latitude, iss_longitude)


#------------------------------------- FUNCTIONS -----------------------------------------#

def is_iss_near_my_location(iss_lat, iss_long, my_lat, my_long):
    return abs(iss_lat - my_lat) < 5 and abs((iss_long - my_long)) < 5
    
def is_currently_dark(current_time, sunrise, sunset):
    return sunrise > current_time > sunset 

def is_iss_visible(iss_lat, iss_long, my_lat, my_long, current_time, sunrise, sunset):
    near_location = is_iss_near_my_location(iss_lat, iss_long, my_lat, my_long)
    dark_time = is_currently_dark(current_time, sunrise, sunset)
    return near_location and dark_time

is_visible = is_iss_visible(iss_latitude, iss_longitude, MY_LAT, MY_LONG, time_now.hour, sunrise, sunset)

#------------------------------------- EMAIL IF VISIBLE -----------------------------------------#

def send_email_if_visible():
    if is_visible:
        email = os.getenv("MY_EMAIL")
        password = os.getenv("MY_PASSWORD")
        email_reciever = "" # <- enter the email of recipient. 

        connection = smtplib.SMTP("smtp.gmail.com")   # <- May need adjusting per personal email provider.
        connection.starttls()
        connection.login(user=email, password=password)
        connection.sendmail(
            from_addr=email,
            to_addr=email_reciever,
            msg = "Subject:Look up now!\n\nIt is dark and the ISS station is near you!"
            )
        connection.close


# Main loop to run every 60 seconds
if __name__ == "__main__":
    while True:
        send_email_if_visible()
        time.sleep(60)  




