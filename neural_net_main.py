from neural_net import *
from neural_net_impl import *
import sys
import random
import matplotlib.pyplot as plt
import pickle

class Image:
  def __init__(self, label):
    self.pixels = []
    self.label = label


def print_pixels(image, x, y):
  for j in range(y):
    print image[j*y:(j+1)*y]

def chain2square(image, x, y):
  square = []
  for j in range(y):
    square.append(list(image[j*y:(j+1)*y]))
  return square

def imagify(img, label):
  image = Image(label-2)

  image_array = [img]
  image.pixels.append(list(img))
  return image



def main():

  # Load pickle file
  f = open('image_map_startlife=100.txt', 'r')
  d = pickle.load(f)
  f.close()


  # Parse images into an array to be processed
  images = []
  for k in d:
    image = Image(d[k]-2)
    # print '# ' + str(d[k]) + '\n'
    # print k
    image_array = [k]
    image.pixels.append(list(k))
    images.append(image)

  print len(images)

  # Initialize a one layer hidden network
  num_hidden = 16

  network = SimpleNetwork()
  # network = HiddenNetwork(num_hidden)
  # network = CustomNetwork()

  # Hooks user-implemented functions to network
  network.FeedForwardFn = FeedForward
  if not network.TrainFn:
    network.TrainFn = Train

  # Initialize network weights
  network.InitializeWeights()
  

  # Displays information

  # Divide images into training, validation and test
  n = len(images)

  
  train_len = 8 * n / 10
  validation_len = n / 10
  train = images[0:train_len]
  validation = images[train_len:train_len+validation_len]
  test = images[train_len+validation_len:]

  print('Training datset size: %d' % train_len)
  print('Validation datset size: %d' % validation_len)
  print('Test dataset size: %d\n' % (n - train_len - validation_len))

  # Train the network.
  rate = 0.01
  epochs = 50
  perf_log = network.Train(images, validation, test, rate, epochs)

  f = open('trained_network_startlife=100_simple', 'w')
  pickle.dump(network, f)
  f.close()

  training_errors, validation_errors, test_errors = [], [], []
  for (perf_train, perf_validate, perf_test) in perf_log:
    training_errors.append(1.0 - perf_train)
    validation_errors.append(1.0 - perf_validate)
    test_errors.append(1.0 - perf_test)

  num_iterations = len(test_errors)
  optimal_epochs = len(validation_errors)
  epoch_list = range(0, optimal_epochs)

  results = plt.figure(figsize=(10,7))
  plt.plot(epoch_list[1:], training_errors[1:], "-r", epoch_list[1:], validation_errors[1:], "-b", epoch_list[1:], test_errors[1:], "-g")
  plt.ylabel("Errors")
  plt.xlabel("Epochs")
  plt.legend(["Training Error", "Validation Error", "Testing Error"], loc=1) # legend at lower right

  plot_name = "Plot of error vs epochs - " + "alpha=" + str(rate) + ", epochs=" + str(optimal_epochs)
  plt.title(plot_name)
  
  file_name = "error_plot_" + "_alpha=" + str(rate) + "_epochs=" + str(optimal_epochs)
  results.savefig(file_name + ".eps", dpi=600)

  plt.show()

  # f = open(file_name + ".dat", "w")
  # for (train, validate, test) in zip(training_errors, validation_errors, test_errors):
  #   f.write(str(train) + "\t")
  #   f.write(str(validate) + "\t")
  #   f.write(str(test) + "\n")
  # f.close()


if __name__ == "__main__":
  main()
