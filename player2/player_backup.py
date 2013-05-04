import common
import random
import pdb
import game_interface as g
import time
import itertools
import classify

history_length = 2
GAMMA = 0.5

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

def get_states():
    #plant_states = [g.STATUS_NO_PLANT, g.STATUS_UNKNOWN_PLANT, g.STATUS_NUTRITIOUS_PLANT, g.STATUS_POISONOUS_PLANT]
    directions = range(4)
    outcomes = list(itertools.product(directions, repeat=history_length))
    states = [State(list(tup)) for tup in outcomes]
    return states

def get_actions():
    actions = []
    for i in range(4):
        actions.append(Action(i, True))
        actions.append(Action(i, False))
    return actions

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

def observe_img(image):
    #poisonous = classify.classify(image)
    #return not poisonous
    return True

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
        view.points_visited = []

        T = {}
        for s in range(len(states)):
            T[s] = {}
            reachable_states = []
            for s_prime in range(len(states)):
                reachable = True
                for i in range(history_length - 1):
                    if states[s].history[i + 1] != states[s_prime].history[i]:
                        reachable = False
                if reachable:
                    reachable_states.append(s_prime)
            reachable_prob = 1. / len(reachable_states)
            for a in range(len(actions)):
                T[s][a] = {}
                for s_prime in range(len(states)):
                    T[s][a][s_prime] = 0.
                for s_2prime in reachable_states:
                    T[s][a][s_2prime] = reachable_prob

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
                    num_sas[s][a][s] = 0.
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
        history = [g.STATUS_UNKNOWN_PLANT] * history_length
        # we don't have a history in the first round, so use random directions
        #history = random.sample(range(4), history_length)
        view.state = State(history)
    else:
        # determine r based on energy difference
        r = view.prev_life - life
        # determine s, s', and a based on r
        most_recent = g.STATUS_UNKNOWN_PLANT
        if view.eaten:
            if r > 0:
                most_recent = g.STATUS_NUTRITIOUS_PLANT
            else:
                most_recent = g.STATUS_POISONOUS_PLANT
        else:
            most_recent = view.status
        #prev_coord = view.points_visited[len(view.points_visited) - 2]
        #most_recent = g.DOWN
        #if prev_coord[0] < x:
            #most_recent = g.RIGHT
        #elif prev_coord[0] > x:
            #most_recent = g.LEFT
        #elif prev_coord[1] < y:
            #most_recent = g.UP
        history = view.state.history
        history.pop(0)
        history.append(most_recent)
        state_prime = State(history)
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
    
    # use epsilon-greedy to decide whether to explore or exploit
    explore = True
    if not first_round:
        explore = e_greedy(view.GetRound())
    # explore: pick a direction leading to an unexplored coordinate
    if explore:
        direction = pick_direction(view.points_visited, x, y)
        observe = True
        if random.random() < 0.5:
            observe = False
        action = Action(direction, observe)
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
                if (p > 0.):
                    print "probability: " + str(p)
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

    print "Direction: " + str(action.direction)
    print "eat? " + str(eat)
    return (action.direction, eat)
    # QUESTION: should we take energy into account somehow besides the reward?
    # QUESTION: should we take the "wobble" into account?

