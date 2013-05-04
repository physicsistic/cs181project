import common
import random
import pdb
import game_interface as g
import time
import itertools
import sys
import classify

GAMMA = 0.5

class Action:
    def __init__(self, direction, observe):
        self.direction = direction
        self.observe = observe
    
    def __eq__(self, other):
        return self.direction == other.direction \
                and self.observe == other.observe

# state: a tuple of the plant statuses surrounding the agent
def get_states():
    #probs = [0, 0.25, 0.5, 0.75]
    #pairs = list(itertools.product(probs, repeat=2))
    #return pairs
    plant_states = [g.STATUS_NO_PLANT, g.STATUS_UNKNOWN_PLANT, g.STATUS_NUTRITIOUS_PLANT, g.STATUS_POISONOUS_PLANT]
    states = list(itertools.product(plant_states, repeat=4))
    return states
    #states = [State(list(tup)) for tup in outcomes]

def get_actions():
    actions = []
    for i in range(4):
        actions.append(Action(i, True))
        actions.append(Action(i, False))
    return actions

# TODO change this?
def pick_direction(points_dict, x, y):
    directions = range(4)
    direction = random.choice(directions)
    random.shuffle(directions)
    for d in directions:
        if d == g.UP:
            proposal = x, y + 1
        elif d == g.DOWN:
            proposal = x, y - 1
        elif d == g.RIGHT:
            proposal = x + 1, y
        else:
            proposal = x - 1, y
        if proposal not in points_dict:
            direction = d
            break
    return direction

def e_greedy(t):
    c = 10.
    epsilon = c / t
    r = random.random()
    if (r < epsilon):
        return True
    return False

def observe_img(view):
    #return True
    #poisonous = classify.classify(image)
    #if poisonous == 0:
        #print "EAT IT!"
    #return poisonous == 0
    image = view.GetImage()
    probs = classify.regression(image)
    if probs[0] > 0.8:
        return True
    elif probs[0] < 0.5:
        return False
    else:
        image2 = view.GetImage()
        probs2 = classify.regression(image2)
        return probs2[0] > 0.5



def get_move(view):
    #return common.get_move(view)

    # Attributes added to view:
    # points_visited
    # T, R, V, num_sa, num_sas, total_R
    # prev_life (int)
    # state, action, status, eaten

    states = get_states()
    actions = get_actions()
    
    first_round = view.GetRound() == 0

    # initialize if first move
    if first_round:
        view.points_to_statuses = {}

        T = {}
        for s in range(len(states)):
            T[s] = {}
            for a in range(len(actions)):
                T[s][a] = {}
                for s_prime in range(len(states)):
                    T[s][a][s_prime] = 0.

        view.T = T

        R = {}
        for s in range(len(states)):
            R[s] = {}
            for a in range(len(actions)):
                R[s][a] = 0.
        view.R = R

        V = {}
        for s in range(len(states)):
            V[s] = 0.
        view.V = V
        
        num_sa = {}
        for s in range(len(states)):
            num_sa[s] = {}
            for a in range(len(actions)):
                num_sa[s][a] = 0.
        view.num_sa = num_sa
        
        num_sas = {}
        for s in range(len(states)):
            num_sas[s] = {}
            for a in range(len(actions)):
                num_sas[s][a] = {}
                for s_prime in range(len(states)):
                    num_sas[s][a][s_prime] = 0.
        view.num_sas = num_sas
    
        total_R = {}
        for s in range(len(states)):
            total_R[s] = {}
            for a in range(len(actions)):
                total_R[s][a] = 0.
        view.total_R = total_R

    # remember point visited
    x = view.GetXPos()
    y = view.GetYPos()
    current_pos = (x, y)
    status = view.GetPlantInfo()
    view.points_to_statuses[(x, y)] = status

    life = view.GetLife()

    if first_round:
        view.state = (g.STATUS_UNKNOWN_PLANT, g.STATUS_UNKNOWN_PLANT, g.STATUS_UNKNOWN_PLANT, g.STATUS_UNKNOWN_PLANT)
        print "ORDER: " + str(g.UP) + " " + str(g.DOWN) + " " + str(g.LEFT) + " " + str(g.RIGHT)
    else:
        # determine r based on energy difference
        r = life - view.prev_life
        #print "Reward: " + str(r)
        # determine s, s', and a based on r
        if view.eaten:
        # update points_to_statuses if we just found more info about neighboring plant
            if r > 0:
                view.points_to_statuses[view.prev_pos] = g.STATUS_NUTRITIOUS_PLANT
            else:
                view.points_to_statuses[view.prev_pos] = g.STATUS_POISONOUS_PLANT
        # determine status of neighbors, if known
        neighbor_up = g.STATUS_UNKNOWN_PLANT
        neighbor_down = g.STATUS_UNKNOWN_PLANT
        neighbor_left = g.STATUS_UNKNOWN_PLANT
        neighbor_right = g.STATUS_UNKNOWN_PLANT
        if (x, y+1) in view.points_to_statuses:
            neighbor_up = view.points_to_statuses[(x, y+1)]
        if (x, y-1) in view.points_to_statuses:
            neighbor_down = view.points_to_statuses[(x, y-1)]
        if (x-1, y) in view.points_to_statuses:
            neighbor_left = view.points_to_statuses[(x-1, y)]
        if (x+1, y) in view.points_to_statuses:
            neighbor_right = view.points_to_statuses[(x+1, y)]
        state_prime = (neighbor_up, neighbor_down, neighbor_left, neighbor_right)

        s = states.index(view.state)
        s_prime = states.index(state_prime)
        a = actions.index(view.action)
        
        # update reward and transition models based on counts
        view.num_sa[s][a] += 1.
        view.num_sas[s][a][s_prime] += 1.
        view.total_R[s][a] += r
        view.T[s][a][s_prime] = float(view.num_sas[s][a][s_prime]) / view.num_sa[s][a]
        view.R[s][a] = float(view.total_R[s][a]) / view.num_sa[s][a]
    
        # perform value update step
        old_Vs = view.V[s]
        if view.num_sa[s][a] == 0:
            alpha = 1.
        else:
            alpha = 1. / view.num_sa[s][a]
        view.V[s] = old_Vs + alpha * ((r + GAMMA * view.V[s_prime]) - old_Vs)
        s = s_prime
        view.state = states[s]
        #print "state: " +str(view.state)
        #print "status: " + str(view.status)
    
    # use epsilon-greedy to decide whether to explore or exploit
    explore = True
    if not first_round:
        explore = e_greedy(view.GetRound())
    # explore: pick a direction leading to an unexplored coordinate
    if explore:
        #direction = pick_direction(view.points_to_statuses, x, y)
        #observe = True
        #if random.random() < 0.2:
            #observe = False
        #action = Action(direction, observe)
        # OR pick the action that has been taken the least?
        min_times = sys.maxint
        a_star = random.randint(0, len(actions) - 1)
        for a_prime in range(len(actions)):
            if view.num_sa[s][a_prime] < min_times:
                a_star = a_prime
        action = actions[a_star]
        action.observe = True
    # exploit: use formula in notes
    else:
        max_value = 0.
        a_star = random.randint(0, len(actions) - 1)
        #print "EXPLOIT"
        for a_prime in range(len(actions)):
            future_val = 0.
            for s_2prime in range(len(states)):
                #if (p > 0.):
                    #print "probability: " + str(p)
                #print "value: " + str(view.V[s_2prime])
                future_val += view.T[s][a_prime][s_2prime] * view.V[s_2prime]
            value = view.R[s][a_prime] + future_val
            if value > max_value:
                max_value = value
                a_star = a_prime
        action = actions[a_star]

    # if chosen action has observe set to True, use classifier to determine whether to eat
    eat = False
    if status == g.STATUS_UNKNOWN_PLANT and action.observe:
        eat = observe_img(view)
    # update view attributes for next round
    view.eaten = eat
    view.action = action
    view.status = status
    view.prev_life = life
    view.prev_pos = current_pos

    print "Direction: " + str(action.direction)
    print "eat? " + str(eat)
    return (action.direction, eat)
    # QUESTION: should we take energy into account somehow besides the reward?
    # QUESTION: should we take the "wobble" into account?

