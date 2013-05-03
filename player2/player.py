import common
import random
import pdb
import game_interface as g
import time

initial_energy = 0
history_length = 3

class State:
    def __init__(self, past_outcomes):
        self.past_outcomes = past_outcomes

    def __eq__(self, other):
        return self.past_outcomes == other.past_outcomes

class Action:
    def __init__(self, direction, observe):
        self.direction = direction
        self.observe = observe

def get_states():
    #for i in range(history_length):
        #outcomes = [g.STATUS_UNKNOWN_PLANT]*i
        #for j in range(history_length - i):
            #k = history_length - i - j
            #outcomes += [g.STATUS_POISONOUS_PLANT]*j
            #outcomes += [g.STATUS_NUTRITIOUS_PLANT]*k
    plant_states = [g.STATUS_NO_PLANT, g.STATUS_UNKNOWN_PLANT, g.STATUS_NUTRITIOUS_PLANT, g.STATUS_POISONOUS_PLANT]
    outcomes = list(itertools.product(plant_states, repeat=history_length))
    states = [State(list(tup)) for tup in outcomes]
    return states

def get_actions():
    actions = []
    for i in range(4):
        actions.append(Action(i, True))
        actions.append(Action(i, False))
    return actions

def get_move(view):
    return common.get_move(view)

    states = get_states()
    actions = get_actions()
    
    first_round = view.GetRound() == 0

    # initialize if first move
    if not hasattr(view, 'points_visited'):
        view.points_visited = []
    if not hasattr(view, 'T'):
        T = {}
        for s in range(len(states)):
            T[s] = {}
            for a in range(len(actions)):
                T[s][a] = {}
                for s_prime in range(len(states)):
                    T[s][a][s] = 0. #should this be non-zero?
        view.T = T
    if not hasattr(view, 'R'):
        R = {}
        for s in range(len(states)):
            R[s] = {}
            for a in range(len(actions)):
                R[s][a] = 0.
        view.R = R
    if not hasattr(view, 'V'):
        V = {}
        for s in range(len(states)):
            V[s] = 0.
        view.V = V
    if not hasattr(view, 'num_sa'):
        num_sa = {}
        for s in range(len(states)):
            num_sa[s] = {}
            for a in range(len(actions)):
                num_sa[s][a] = 0
        view.num_sa = num_sa
    if not hasattr(view, 'num_sas'):
        num_sas = {}
        for s in range(len(states)):
            num_sas[s] = {}
            for a in range(len(actions)):
                num_sas[s][a] = {}
                for s_prime in range(len(states)):
                    num_sas[s][a][s] = 0
        view.num_sas = num_sas
    if not hasattr(view, 'total_R'):
        total_R = {}
        for s in range(len(states)):
            total_R[s] = {}
            for a in range(len(actions)):
                total_R[s][a] = 0.
        view.total_R = total_R
    if not hasattr(view, 'prev_life'):
        view.prev_life = view.GetLife()
    if not hasattr(view, 'no_plant'):
        view.no_plant = True

    # remember points visited
    x = view.GetXPos()
    y = view.GetYPos()
    view.points_visited.append(x, y)

    life = view.GetLife()
    if first_round:
        plant_states = [g.STATUS_UNKNOWN_PLANT]*history_length
        view.state = State(history)
    if not first_round:
        # determine r based on energy difference
        r = view.prev_life - life
        # determine s, s', and a
        most_recent = g.STATUS_UNKNOWN_PLANT
        if r > 0:
            most_recent = g.STATUS_NUTRITIOUS_PLANT
        elif r < -1:
            most_recent = g.STATUS_POISONOUS_PLANT
        elif no_plant:
            most_recent = g.STATUS_NO_PLANT
        history = view.state.history
        history.pop(0)
        history.append(most_recent)
        state_prime = State(history)
        s = states.index(view.state)
        s_prime = states.index(state_prime)
        a = actions.index(view.action)
    # update reward and transition models based on counts
    # perform value update step
    # use epsilon-greedy to decide whether to explore or exploit
    # explore: pick a direction leading to an unexplored coordinate
    # OR pick the action that has been taken the least?
    # exploit: use formula in notes
    # if chosen action has observe set to True, use classifier to determine whether to eat
    # QUESTION: should we take energy into account somehow besides the reward?
    # QUESTION: should we take the "wobble" into account?

