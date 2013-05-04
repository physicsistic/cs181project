import common
import random
import pdb
import game_interface as g
import time
import itertools
import classify

history_length = 5
GAMMA = 0.5

FORWARD = 0
BACKWARD = 1
LEFT = 2
RIGHT = 3

class State:
    def __init__(self, history):
        self.history = history

    def __eq__(self, other):
        return self.history == other.history

class Action:
    def __init__(self, direction, observe):
        self.direction = direction
        self.observe = observe
    
    def __eq__(self, other):
        return self.direction == other.direction \
                and self.observe == other.observe

# state: how many plants in recent history have been nutritious
def get_states():
    states = range(history_length + 1)
    #plant_states = [g.STATUS_NO_PLANT, g.STATUS_UNKNOWN_PLANT, g.STATUS_NUTRITIOUS_PLANT, g.STATUS_POISONOUS_PLANT]
    #outcomes = list(itertools.product(plant_states, repeat=history_length))
    #states = [State(list(tup)) for tup in outcomes]
    return states

def get_actions():
    actions = []
    # FORWARD, BACKWARD, LEFT, RIGHT
    for i in range(4):
        actions.append(Action(i, True))
        actions.append(Action(i, False))
    return actions

# TODO change this?
def pick_direction(points_visited, x, y):
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
        if proposal not in points_visited:
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

def relative_movement(direction1, direction2):
    if direction1 == direction2:
        return FORWARD
    elif (direction1 == g.UP and direction2 == g.DOWN) \
            or (direction1 == g.DOWN and direction2 == g.UP) \
            or (direction1 == g.RIGHT and direction2 == g.LEFT) \
            or (direction1 == g.LEFT and direction2 == g.RIGHT):
                return BACKWARD
    elif (direction1 == g.UP and direction2 == g.RIGHT) \
            or (direction1 == g.RIGHT and direction2 == g.DOWN) \
            or (direction1 == g.DOWN and direction2 == g.LEFT) \
            or (direction1 == g.LEFT and direction2 == g.UP):
                return RIGHT
    else:
        return LEFT

# Determines what direction get_move should return given a
# previous direction and intended relative direction
def absolute_movement(prev_direction, relative):
    if relative == FORWARD:
        return prev_direction
    elif relative == BACKWARD:
        if prev_direction == g.UP:
            return g.DOWN
        elif prev_direction == g.DOWN:
            return g.UP
        elif prev_direction == g.RIGHT:
            return g.LEFT
        else:
            return g.RIGHT
    elif relative == RIGHT:
        if prev_direction == g.UP:
            return g.RIGHT
        elif prev_direction == g.RIGHT:
            return g.DOWN
        elif prev_direction == g.DOWN:
            return g.LEFT
        else:
            return g.UP
    else:
        if prev_direction == g.UP:
            return g.LEFT
        elif prev_direction == g.LEFT:
            return g.DOWN
        elif prev_direction == g.DOWN:
            return g.RIGHT
        else:
            return g.UP

    

def observe_img(image):
    return True
    poisonous = classify.classify(image)
    if poisonous == 0:
        print "EAT IT!"
    return poisonous == 0
    #return True

def get_move(view):
    #return common.get_move(view)

    # Attributes added to view:
    # points_visited
    # T, R, V, num_sa, num_sas, total_R
    # prev_life (int)
    # state, action, status, eaten, history

    states = get_states()
    actions = get_actions()
    
    first_round = view.GetRound() == 0

    # initialize if first move
    if first_round:
        view.points_visited = []

        T = {}
        for s in range(len(states)):
            T[s] = {}
            reachable_states = []
            for s_prime in range(len(states)):
                reachable = True
                for i in range(history_length - 1):
                    #if states[s].history[i + 1] != states[s_prime].history[i]:
                    if abs(states[s] - states[s_prime]) != 1:
                        reachable = False
                if reachable:
                    reachable_states.append(s_prime)
            reachable_prob = 1. / len(reachable_states)
            for a in range(len(actions)):
                T[s][a] = {}
                for s_prime in range(len(states)):
                    T[s][a][s_prime] = 0.
                #for s_2prime in reachable_states:
                    #T[s][a][s_2prime] = reachable_prob

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

    # remember points visited
    x = view.GetXPos()
    y = view.GetYPos()
    view.points_visited.append((x, y))

    life = view.GetLife()
    if first_round:
        view.history = [g.STATUS_UNKNOWN_PLANT] * history_length
        view.state = 0
        #view.state = State(history)
        direction_traveled = random.randint(0, 3)
    else:
        # determine r based on energy difference
        r = life - view.prev_life
        print "Reward: " + str(r)
        # determine s, s', and a based on r
        most_recent = g.STATUS_UNKNOWN_PLANT
        if view.eaten:
            if r > 0:
                most_recent = g.STATUS_NUTRITIOUS_PLANT
            else:
                most_recent = g.STATUS_POISONOUS_PLANT
        else:
            most_recent = view.status
        
        least_recent = view.history.pop(0)
        view.history.append(most_recent)
        state_prime = view.state
        if least_recent == g.STATUS_NUTRITIOUS_PLANT:
            state_prime -= 1
        if most_recent == g.STATUS_NUTRITIOUS_PLANT:
            print "NUTRITIOUS"
            state_prime += 1
        #state_prime = State(history)
        s = states.index(view.state)
        s_prime = states.index(state_prime)
        a = actions.index(view.action)
        
        prev_coord = view.points_visited[len(view.points_visited) - 2]
        direction_traveled = g.UP
        if prev_coord[0] < x:
            direction_traveled = g.RIGHT
        elif prev_coord[0] > x:
            direction_traveled = g.LEFT
        elif prev_coord[1] > y:
            direction_traveled = g.DOWN

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
        print "state: " +str(view.state)
        print "status: " + str(view.status)
    
    # use epsilon-greedy to decide whether to explore or exploit
    explore = True
    #if not first_round and view.state != 0:
    if not first_round:
        explore = e_greedy(view.GetRound())
    # explore: pick a direction leading to an unexplored coordinate
    if explore:
        raw_direction = pick_direction(view.points_visited, x, y)
        rel_direction = relative_movement(direction_traveled, raw_direction)
        observe = True
        if random.random() < 0.01:
            observe = False
        action = Action(rel_direction, observe)
        # OR pick the action that has been taken the least?
    # exploit: use formula in notes
    else:
        max_value = 0.
        a_star = 0
        print "EXPLOIT"
        for a_prime in range(len(actions)):
            future_val = 0.
            for s_2prime in range(len(states)):
                p = view.T[s][a_prime][s_2prime]
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
    if view.GetPlantInfo() == g.STATUS_UNKNOWN_PLANT and action.observe:
        eat = observe_img(view.GetImage())
    # update view attributes for next round
    view.eaten = eat
    view.action = action
    view.status = view.GetPlantInfo()
    view.prev_life = life

    abs_direction = absolute_movement(direction_traveled, action.direction)
    print "Direction: " + str(action.direction)
    print "eat? " + str(eat)
    return (abs_direction, eat)
    # QUESTION: should we take energy into account somehow besides the reward?
    # QUESTION: should we take the "wobble" into account?

