#!/usr/bin/env python3

import sys, subprocess, time, json
sys.path.insert(1, "/home/pi/weather-display/lib") # add lib folder in currect directory to sys
import epd2in13
from PIL import Image, ImageDraw, ImageFont

# Initialize the Screen:

epd = epd2in13.EPD()		# get the display
epd.init(epd.FULL_UPDATE)	# initialize the display
print("Clear...")			# prints to console, not the display (for debugging)
epd.Clear(0xFF)				# clears the display (color is req. argument but irrelevant otherwise)

def printToDisplay(string, x, y):
	image = Image.new('1', (epd2in13.EPD_HEIGHT, epd2in13.EPD_WIDTH), 255)
	draw = ImageDraw.Draw(image)
	fontLarge = ImageFont.truetype('/home/pi/weather-display/lib/fonts/SourceCodePro-Semibold.ttf', 24)
	fontMedium = ImageFont.truetype('/home/pi/weather-display/lib/fonts/slkscr.ttf', 24)
	fontSmall = ImageFont.truetype('/home/pi/weather-display/lib/fonts/slkscr.ttf', 16)
	now = time.localtime()
	current_time = time.strftime("%H%M", now)

	draw.text((x, y), string, font = fontMedium, fill = 0)
	draw.text((204, 106), current_time, font = fontSmall, fill = 0)

	epd.display(epd.getbuffer(image.rotate(180))) # send image to screen after rotating it 180 degrees

def parseWeather():
	# read and parse file
	try :
		with open('/home/pi/weather-display/current-weather.json', 'r') as weather_file:
			current_weather = json.load(weather_file)
	except :
		printToDisplay("Weather Service\nDown", 0, 0)
		sys.exit("Wttr.in Service Unavailable and/or Returned Bad Data")

	# show values
	print("Current conditions: " + current_weather['current_condition'][0]['weatherDesc'][0]['value'])
	print("Temperature: " + current_weather['current_condition'][0]['temp_F'] + "° (feels " + current_weather['current_condition'][0]['FeelsLikeF'] + "°)")

	# convert wind speed to Beaufort Scale description and show value
	wind_speed = int(current_weather['current_condition'][0]['windspeedMiles'])
	if wind_speed < 1 :
		wind_desc = "Calm"
	elif wind_speed <= 3 :
		wind_desc = "Light air"
	elif wind_speed <= 7 :
		wind_desc = "Light breeze"
	elif wind_speed <= 12 :
		wind_desc = "Gentle breeze"
	elif wind_speed <= 18 :
		wind_desc = "Moderate breeze"
	elif wind_speed <= 24 :
		wind_desc = "Fresh breeze"
	elif wind_speed <= 31 :
		wind_desc = "Strong breeze"
	elif wind_speed <= 38 :
		wind_desc = "Moderate gale"
	elif wind_speed <= 46 :
		wind_desc = "Gale"
	elif wind_speed <= 54 :
		wind_desc = "Severe gale"
	elif wind_speed <= 63 :
		wind_desc = "Storm"
	elif wind_speed <= 72 :
		wind_desc = "Violent storm"
	else :
		wind_desc = "Hurricane force"

	print("Wind: " + wind_desc + ", " + current_weather['current_condition'][0]['winddir16Point'])

	# convert precipitation from mm to inches and show
	#precip_mm = float(current_weather['current_condition'][0]['precipMM'])
	#precip_in = round(precip_mm/25.4, 2)
	#print ("Precipitation: " + str(precip_in) + "in")

	# Get UV Index and generate risk level
	uv_index = int(current_weather['current_condition'][0]['uvIndex'])
	if uv_index <= 2 :
		uv_risk = "Low risk"
	elif uv_index <= 5 :
		uv_risk = "Moderate risk"
	elif uv_index <= 7 :
		uv_risk = "High risk"
	elif uv_index <= 10 :
		uv_risk = "Very high risk"
	else :
		uv_risk = "Extreme risk"

	print("UV Index: " + str(uv_index) + " (" + uv_risk + ")")

	weather_report = current_weather['current_condition'][0]['weatherDesc'][0]['value'] + "\n" + current_weather['current_condition'][0]['temp_F'] + "° (feels " + current_weather['current_condition'][0]['FeelsLikeF'] + "°)\n" + wind_desc + "\nUV: " + uv_risk

	return weather_report

subprocess.run(["/home/pi/weather-display/getWeather.sh"]) # runs script to collect weather data and save in local json file
clean_weather_report = parseWeather() # parses json and returns string to be displayed on eInk screen
printToDisplay(clean_weather_report, 0, 0) # prints weather data on the eInk screen at position 0, 0

