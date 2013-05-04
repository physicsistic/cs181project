from neural_net import NeuralNetwork, NetworkFramework
from neural_net import Node, Target, Input
import random
import pdb
import math


# <--- Problem 3, Question 1 --->

def FeedForward(network, input):
  """
  Arguments:
  ---------
  network : a NeuralNetwork instance
  input   : an Input instance

  Returns:
  --------
  Nothing

  Description:
  -----------
  This function propagates the inputs through the network. That is,
  it modifies the *raw_value* and *transformed_value* attributes of the
  nodes in the network, starting from the input nodes.

  Notes:
  -----
  The *input* arguments is an instance of Input, and contains just one
  attribute, *values*, which is a list of pixel values. The list is the
  same length as the number of input nodes in the network.

  i.e: len(input.values) == len(network.inputs)

  This is a distributed input encoding (see lecture notes 7 for more
  informations on encoding)

  In particular, you should initialize the input nodes using these input
  values:

  network.inputs[i].raw_value = input[i]
  """
  network.CheckComplete()
  # 1) Assign input values to input nodes
  for i in range(0, len(input.values)):
      network.inputs[i].raw_value = input.values[i]
      network.inputs[i].transformed_value = input.values[i]
  # 2) Propagates to hidden layer
  for node in network.hidden_nodes:
      node.raw_value = NeuralNetwork.ComputeRawValue(node)
      node.transformed_value = NeuralNetwork.Sigmoid(node.raw_value)
  # 3) Propagates to the output layer
  for node in network.outputs:
      node.raw_value = NeuralNetwork.ComputeRawValue(node)
      node.transformed_value = NeuralNetwork.Sigmoid(node.raw_value)

#< --- Problem 3, Question 2

def Backprop(network, input, target, learning_rate):
  """
  Arguments:
  ---------
  network       : a NeuralNetwork instance
  input         : an Input instance
  target        : a target instance
  learning_rate : the learning rate (a float)

  Returns:
  -------
  Nothing

  Description:
  -----------
  The function first propagates the inputs through the network
  using the Feedforward function, then backtracks and update the
  weights.

  Notes:
  ------
  The remarks made for *FeedForward* hold here too.

  The *target* argument is an instance of the class *Target* and
  has one attribute, *values*, which has the same length as the
  number of output nodes in the network.

  i.e: len(target.values) == len(network.outputs)

  In the distributed output encoding scenario, the target.values
  list has 10 elements.

  When computing the error of the output node, you should consider
  that for each output node, the target (that is, the true output)
  is target[i], and the predicted output is network.outputs[i].transformed_value.
  In particular, the error should be a function of:

  target[i] - network.outputs[i].transformed_value
  
  """
  network.CheckComplete()
  # 1) We first propagate the input through the network
  FeedForward(network, input)
  # 2) Then we compute the errors and update the weights starting with the last layer
  for i in range(len(network.outputs)):
      node = network.outputs[i]
      a = node.transformed_value
      error = target.values[i] - a 
      delta = error * a * (1 - a)
      # save delta value for calculating parent's error
      node.delta = delta
      for j in range(len(node.weights)):
          node.weights[j].value += learning_rate * delta * node.inputs[j].transformed_value

  # 3) We now propagate the errors to the hidden layer, and update the weights there too
  hidden = len(network.hidden_nodes)
  for i in range(hidden):
      # iterate through hidden nodes in reverse topological order
      m = hidden - i - 1
      node = network.hidden_nodes[m]
      a = node.transformed_value
      error = 0
      for j in range(len(node.forward_neighbors)):
          error += node.forward_weights[j].value * node.forward_neighbors[j].delta
      delta = error * a * (1 - a)
      node.delta = delta
      for j in range(len(node.weights)):
          node.weights[j].value += learning_rate * delta * node.inputs[j].transformed_value

# <--- Problem 3, Question 3 --->

def Train(network, inputs, targets, learning_rate, epochs):
  """
  Arguments:
  ---------
  network       : a NeuralNetwork instance
  inputs        : a list of Input instances
  targets       : a list of Target instances
  learning_rate : a learning_rate (a float)
  epochs        : a number of epochs (an integer)

  Returns:
  -------
  Nothing

  Description:
  -----------
  This function should train the network for a given number of epochs. That is,
  run the *Backprop* over the training set *epochs*-times
  """
  network.CheckComplete()
  test_arr = [0] * 2
  for i in range(epochs):
      assert len(inputs) == len(targets), ('Different number of inputs than targets')
      for j in range(len(inputs)):
          Backprop(network, inputs[j], targets[j], learning_rate)

def CustomTrain(network, inputs, targets, learning_decay_constant, epochs):
  """
  Arguments:
  ---------
  network                : a NeuralNetwork instance
  inputs                 : a list of Input instances
  targets                : a list of Target instances
  learning_decay_consant : a constant for use in the learning_rate decay formula
  epochs                 : a number of epochs (an integer)

  Returns:
  -------
  Nothing

  Description:
  -----------
  This function should train the network for a given number of epochs using stochastic
  gradient descent and a decaying learning rate. The number of inputs per epoch can be
  set below, while the constant for learning decay can be passed in as an argument.
  """
  network.CheckComplete()
  subset_size = 1 
  iterations = 100000

  print "Custom training function"

  for i in range(iterations):
    subset = random.sample(xrange(len(inputs)), subset_size)
    learning_rate = learning_decay_constant / (learning_decay_constant + i)
    for j in subset:
        Backprop(network, inputs[j], targets[j], learning_rate)

# <--- Problem 3, Question 4 --->

class EncodedNetworkFramework(NetworkFramework):
  def __init__(self):
    """
    Initializatio.
    YOU DO NOT NEED TO MODIFY THIS __init__ method
    """
    super(EncodedNetworkFramework, self).__init__() # < Don't remove this line >
    
  # <--- Fill in the methods below --->

  def EncodeLabel(self, label):
    """
    Arguments:
    ---------
    label: a number between 0 and 9

    Returns:
    ---------
    a list of length 10 representing the distributed
    encoding of the output.
    ### NOTE: Actual returns a Target instance, in accordance with
    the rest of the pset

    Description:
    -----------
    Computes the distributed encoding of a given label.

    Example:
    -------
    0 => [1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    3 => [0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

    Notes:
    ----
    Make sure that the elements of the encoding are floats.
    
    """
    target = Target()
    encoding = [0.0] * 2
    encoding[label] = 1.0
    target.values = encoding
    return target

  def GetNetworkLabel(self):
    """
    Arguments:
    ---------
    Nothing

    Returns:
    -------
    the 'best matching' label corresponding to the current output encoding

    Description:
    -----------
    The function looks for the transformed_value of each output, then decides 
    which label to attribute to this list of outputs. The idea is to 'line up'
    the outputs, and consider that the label is the index of the output with the
    highest *transformed_value* attribute

    Example:
    -------

    # Imagine that we have:
    map(lambda node: node.transformed_value, self.network.outputs) => [0.2, 0.1, 0.01, 0.7, 0.23, 0.31, 0, 0, 0, 0.1, 0]

    # Then the returned value (i.e, the label) should be the index of the item 0.7,
    # which is 3
    
    """
    output_encoding = map(lambda node: node.transformed_value, self.network.outputs)

    return output_encoding.index(max(output_encoding))

  def Convert(self, image):
    """
    Arguments:
    ---------
    image: an Image instance

    Returns:
    -------
    an instance of Input

    Description:
    -----------
    The *image* arguments has 2 attributes: *label* which indicates
    the digit represented by the image, and *pixels* a matrix 14 x 14
    represented by a list (first list is the first row, second list the
    second row, ... ), containing numbers whose values are comprised
    between 0 and 256.0. The function transforms this into a unique list
    of 14 x 14 items, with normalized values (that is, the maximum possible
    value should be 1).
    
    """
    input = Input()
    values = []
    for row in image.pixels:
        values += map(lambda value: float(value), row)


    input.values = values
    return input

  def InitializeWeights(self):
    """
    Arguments:
    ---------
    Nothing

    Returns:
    -------
    Nothing

    Description:
    -----------
    Initializes the weights with random values between [-0.01, 0.01].

    Hint:
    -----
    Consider the *random* module. You may use the the *weights* attribute
    of self.network.
    
    """
    for weight in self.network.weights:
        weight.value = (random.random() - 0.5) / 50



#<--- Problem 3, Question 6 --->

class SimpleNetwork(EncodedNetworkFramework):
  def __init__(self):
    """
    Arguments:
    ---------
    Nothing

    Returns:
    -------
    Nothing

    Description:
    -----------
    Initializes a simple network, with 196 input nodes,
    10 output nodes, and NO hidden nodes. Each input node
    should be connected to every output node.
    """
    super(SimpleNetwork, self).__init__() # < Don't remove this line >
    
    # 1) Adds an input node for each pixel.    
    num_inputs = 36
    inputs = []
    outputs = []
    for i in range(num_inputs):
        new_node = Node()
        inputs.append(new_node)
        self.network.AddNode(new_node, self.network.INPUT)
    # 2) Add an output node for each possible digit label.
    for i in range(2):
        new_node = Node()
        outputs.append(new_node)
        self.network.AddNode(new_node, self.network.OUTPUT)

    for output in outputs:
        for input in inputs:
            output.AddInput(input, 0, self.network)


#<---- Problem 3, Question 7 --->

class HiddenNetwork(EncodedNetworkFramework):
  def __init__(self, number_of_hidden_nodes=15):
    """
    Arguments:
    ---------
    number_of_hidden_nodes : the number of hidden nodes to create (an integer)

    Returns:
    -------
    Nothing

    Description:
    -----------
    Initializes a network with a hidden layer. The network
    should have 196 input nodes, the specified number of
    hidden nodes, and 10 output nodes. The network should be,
    again, fully connected. That is, each input node is connected
    to every hidden node, and each hidden_node is connected to
    every output node.
    """
    super(HiddenNetwork, self).__init__() # < Don't remove this line >

    num_inputs = 36
    num_outputs = 2
    inputs = []
    outputs = []
    hidden_nodes = []
    # 1) Adds an input node for each pixel
    for i in range(num_inputs):
        new_node = Node()
        inputs.append(new_node)
        self.network.AddNode(new_node, self.network.INPUT)
    # 2) Adds the hidden layer
    for i in range(number_of_hidden_nodes):
        new_node = Node()
        hidden_nodes.append(new_node)
        self.network.AddNode(new_node, self.network.HIDDEN)
    # 3) Adds an output node for each possible digit label.
    for i in range(num_outputs):
        new_node = Node()
        outputs.append(new_node)
        self.network.AddNode(new_node, self.network.OUTPUT)

    for node in hidden_nodes:
        for input in inputs:
            node.AddInput(input, 0, self.network)
    for output in outputs:
        for node in hidden_nodes:
            output.AddInput(node, 0, self.network)



#<--- Problem 3, Question 8 ---> 


def find_nth_square(total_size, square_size, n):
    """
    Helper function for CustomNetwork.
    Arguments:
    ---------
    total_size: the size of the image
    square_size: the size of each subset
    n: which subset we wish to extract

    Returns:
    --------
    A list of length square_size, containing the indices in
    [0, square_size) that comprise the nth square

    Description:
    --------
    Calculates the indices of a list that will allow us to
    consider only pixels located within the nth section of
    an image.
    Example: With an image of total_size 196, getting the 0th
    square of size 4 will yield [0,1,14,15].
    """
    square_indices = []
    side = int(math.sqrt(square_size))
    total_side = int(math.sqrt(total_size))
    #x_start = (n * side) % total_side
    #y_start = ((n * side) / total_side) * side
    #start = y_start * total_side + x_start
    offset = side - 1
    total_side_adj = total_side - offset
    row = n / total_side_adj
    start = n + row * offset
    for i in range(side):
        for j in range(side):
            square_indices.append(start + i * total_side + j)

    print str(n) + ": " + str(square_indices)

    return square_indices

class CustomNetwork(EncodedNetworkFramework):
  def __init__(self, number_of_hidden_nodes=49):
    """
    Arguments:
    ---------
    None.

    Returns:
    --------
    None.

    Description:
    -----------
    Builds a network with 196 input nodes, 3 layers of hidden 
    nodes, and 10 output nodes. The network is no longer fully connected: 
    Sets the train function to CustomTrain, which uses stochastic 
    gradient descent and a decaying learning rate.
    """
    super(CustomNetwork, self).__init__() # <Don't remove this line>
    
    num_inputs = 36
    num_outputs = 2
    inputs = []
    hidden_nodes = []
    outputs = []
    square_size = 16 
    num_hidden_nodes = int((math.sqrt(num_inputs) - (math.sqrt(square_size) - 1))**2)
    #hidden_nodes = [[],[],[]]
    #square_sizes = [4, 9, 16]
    #hidden_node_nums = [169, 121, 64]
    # 1) Adds an input node for each pixel
    for i in range(num_inputs):
        new_node = Node()
        inputs.append(new_node)
        self.network.AddNode(new_node, self.network.INPUT)
    # 2) Adds the hidden layers
    #for i in range(3):
        #for j in range(hidden_node_nums[i]):
            #new_node = Node()
            #hidden_nodes[i].append(new_node)
            #self.network.AddNode(new_node, self.network.HIDDEN)
    for i in range(num_hidden_nodes):
        new_node = Node()
        hidden_nodes.append(new_node)
        self.network.AddNode(new_node, self.network.HIDDEN)
    # 3) Adds an output node for each possible digit label.
    for i in range(num_outputs):
        new_node = Node()
        outputs.append(new_node)
        self.network.AddNode(new_node, self.network.OUTPUT)
    
    #previous_layers = [inputs, hidden_nodes[0], hidden_nodes[1]]
    #for i in range(3):
        #for j in range(hidden_node_nums[i]):
            #input_indices = find_nth_square(len(previous_layers[i]), square_sizes[i], j)
            #for k in input_indices:
                #hidden_nodes[i][j].AddInput(previous_layers[i][k], 0, self.network)

    for i in range(num_hidden_nodes):
        input_indices = find_nth_square(num_inputs, square_size, i)
        for j in input_indices:
            hidden_nodes[i].AddInput(inputs[j], 0, self.network)

    for output in outputs:
        for node in hidden_nodes:
            output.AddInput(node, 0, self.network)

    #self.RegisterTrainFunction(CustomTrain)