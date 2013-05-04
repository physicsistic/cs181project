import game_interface
import random
import time
import common

def get_move(view):
    return common.get_move(view)

    hasPlant = view.GetPlantInfo() != game_interface.STATUS_NO_PLANT
    if hasPlant:
        #f = open('training_points2.txt', 'a')
        #f.write(str(view.GetXPos()) + " " + str(view.GetYPos()) + "\n")
        #f.close()
        if view.GetPlantInfo() == game_interface.STATUS_NUTRITIOUS_PLANT:
            f = open("nutritious_points.txt", 'a')
            f.write(str(view.GetXPos()) + " " + str(view.GetYPos()) + "\n")
            f.close()
        elif view.GetPlantInfo() == game_interface.STATUS_POISONOUS_PLANT:
            f = open("poisonous_points.txt", 'a')
            f.write(str(view.GetXPos()) + " " + str(view.GetYPos()) + "\n")
            f.close()
    else:
        f = open("empty_points.txt", 'a')
        f.write(str(view.GetXPos()) + " " + str(view.GetYPos()) + "\n")
        f.close()

    #if view.GetPlantInfo() == game_interface.STATUS_NUTRITIOUS_PLANT:
        #image = view.GetImage()

    time.sleep(0.1)

    return(random.randint(0, 4), hasPlant)
