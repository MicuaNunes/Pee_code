from sense_hat import SenseHat
from time import sleep, strftime


green = (0, 255, 0)
red = (255, 0, 0)
blue = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)


def show_t(sense):
  sense.show_letter("T", back_colour = red)
  sleep(.5)

def show_p(sense):
  sense.show_letter("P", back_colour = green)
  sleep(.5)

def show_h(sense):
  sense.show_letter("H", back_colour = blue)
  sleep(.5)


#
def update_screen(sense, mode, show_letter = False):
  if mode == "temp":
    if show_letter:
      show_t(sense)
    temp = sense.temp
    temp_value = temp / 2.5 + 16
    pixels = [red if i < temp_value else white for i in range(64)]

  elif mode == "pressure":
    if show_letter:
      show_p(sense)
    pressure = sense.pressure
    msg = " Pressure %.0f hPa" % (pressure)
    sense.show_message(msg,scroll_speed=0.01,back_colour=black)
    #pressure_value = pressure / 20
    #pixels = [green if i < pressure_value else white for i in range(64)]

  elif mode == "humidity":
    if show_letter:
      show_h(sense)
    humidity = sense.humidity
    humidity_value = 64 * humidity / 100
    pixels = [blue if i < humidity_value else white for i in range(64)]

  #sense.set_pixels(pixels)
