import player1.player
import player2.player
import game_interface
import random
import signal
import sys
import time
import traceback
from optparse import OptionParser
import pdb
import pickle

class TimeoutException(Exception):
  def __init__(self):
    pass

def get_move(view, cmd, options, player_id):
  def timeout_handler(signum, frame):
    raise TimeoutException()
  signal.signal(signal.SIGALRM, timeout_handler)
  signal.alarm(1)
  try: 
    (mv, eat) = cmd(view)
    # Clear the alarm.
    signal.alarm(0)
  except TimeoutException:
    # Return a random value
    # Should probably log this to the interface
    (mv, eat) = (random.randint(0, 4), False)
    error_str = 'Error in move selection (%d).' % view.GetRound()
    if options.display:
      game_interface.curses_debug(player_id, error_str)
    else:
      print error_str
  return (mv, eat)

def run(options):
  game = game_interface.GameInterface(options.plant_bonus,
                                      options.plant_penalty,
                                      options.observation_cost,
                                      options.starting_life,
                                      options.life_per_turn)
  player1_view = game.GetPlayer1View()
  player2_view = game.GetPlayer2View()

  if options.display:
    if game_interface.curses_init() < 0:
      return
    game_interface.curses_draw_board(game)

  d = {}
  img = {}
  
  # Keep running until one player runs out of life.
  while True:
    (mv1, eat1) = get_move(player1_view, player1.player.get_move, options, 1)
    (mv2, eat2) = get_move(player2_view, player2.player.get_move, options, 2)

# ---------------------------------
# Experiment Code

    # Get the coordinates of each run
    player1_coords = (player1_view.GetXPos(), player1_view.GetYPos())
    player2_coords = (player2_view.GetXPos(), player2_view.GetYPos()) 

    
    d[player1_coords] = player1_view.GetPlantInfo()
    status = player1_view.GetPlantInfo()
    d[player2_coords] = status

    # if (status == game_interface.STATUS_NUTRITIOUS_PLANT) | (status == game_interface.STATUS_POISONOUS_PLANT):
    #   img[player1_view.GetImage()] = status

# ----------------------------------

    game.ExecuteMoves(mv1, eat1, mv2, eat2)
    if options.display:
      game_interface.curses_draw_board(game)
      game_interface.curses_init_round(game)
    else:
      print mv1, eat1, mv2, eat2
      print player1_view.GetLife(), player2_view.GetLife()
    # Check whether someone's life is negative.
    l1 = player1_view.GetLife()
    l2 = player2_view.GetLife()
  
    if l1 <= 0 or l2 <= 0:
      if options.display:
        winner = 0
        if l1 < l2:
          winner = 2
        else:
          winner = 1
        game_interface.curses_declare_winner(winner)
      else:
        if l1 == l2:
          print 'Tie, remaining life: %d v. %d' % (l1, l2)
        elif l1 < l2:
          print 'Player 2 wins: %d v. %d' % (l1, l2)
        else:
          print 'Player 1 wins: %d v. %d' % (l1, l2)
      # Wait for input
      sys.stdin.read(1)
      if options.display:
        game_interface.curses_close()
      break

  distri_file = open('plant_distribution_100x100_06.txt', 'w')
  # image_map_file = open('image_map_huge.txt', 'w')
  # print img
  pickle.dump(d, distri_file)
  # pickle.dump(img, image_map_file)
  distri_file.close()
  # image_map_file.close()

def main(argv):
  parser = OptionParser()
  parser.add_option("-d", action="store", dest="display", default=1, type=int,
                    help="whether to display the GUI board")
  parser.add_option("--plant_bonus", dest="plant_bonus", default=20,
                    help="bonus for eating a nutritious plant",type=int)
  parser.add_option("--plant_penalty", dest="plant_penalty", default=10,
                    help="penalty for eating a poisonous plant",type=int)
  parser.add_option("--observation_cost", dest="observation_cost", default=1,
                    help="cost for getting an image for a plant",type=int)
  parser.add_option("--starting_life", dest="starting_life", default=100,
                    help="starting life",type=int)
  parser.add_option("--life_per_turn", dest="life_per_turn", default=1,
                    help="life spent per turn",type=int)
  (options, args) = parser.parse_args()

  try:
    run(options)
  except KeyboardInterrupt:
    if options.display:
      game_interface.curses_close()
  except:
    game_interface.curses_close()
    traceback.print_exc(file=sys.stdout)

if __name__ == '__main__':
  main(sys.argv)
