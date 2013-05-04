import game_interface
import random
import time
import pdb

direction = game_interface.UP


def get_move(view):
  # Choose a random direction.
  # If there is a plant in this location, then try and eat it.
  hasPlant = view.GetPlantInfo() == game_interface.STATUS_UNKNOWN_PLANT

  
  # Choose a random direction
  # if hasPlant:
  #   for i in xrange(5):
  #     print view.GetImage()
  # time.sleep(0.1)
  return (random.randint(0, 4), hasPlant)


def scan(view):
	x = view.GetXPos()
	y = view.GetYPos()
	pass


def observe(view):
	# Save the image files of plants
  f = open('observations.txt', 'a')
  side = 100
  x = view.GetXPos()
  y = view.GetYPos()

  global direction
  # print x, y, direction

  if y > side:
  	direction = game_interface.DOWN
  elif y < (-side):
    direction = game_interface.UP
  elif x < (-side):
  	direction = game_interface.RIGHT
  elif x > side:
    direction = game_interface.LEFT
  else:
  	direction = random.randint(0, 4)

  print direction

  status = view.GetPlantInfo()
  coord = (x, y)
  image = view.GetImage()
  text_line = str(coord) + '\n' + str(image) + '\n' + str(status) + '\n'
  f.write(text_line)
  f.close()
  return (direction, True)

