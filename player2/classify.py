import pickle
from neural_net_main import *
from neural_net import *
from neural_net_impl import *

def classify(img):


	f = open('trained_network', 'r')
	network = pickle.load(f)
	f.close()

	image = imagify(img, 0)

	return network.Classify(image)

def regression(img):
	f = open('trained_network_startlife=100', 'r')
	network = pickle.load(f)
	f.close()

	image = imagify(img, 0)
	return network.Regression(image)

#f = open('image_map_startlife=100.txt', 'r')
#imgs = pickle.load(f)
#f.close()

#f = open('trained_network_startlife=100', 'r')
#network = pickle.load(f)
#f.close()

#images, probs = [], []
#for i in imgs:
	#image = imagify(i, imgs[i])
	#images.append(image)

## print images[0]

#n = 0
#n_correct = 0

#for image in images:
	#print n
	#n += 1
	#label = network.Classify(image)
	#prob = network.Regression(image)
	#print 'Classified: ' + str(label)
	#print 'Actual: ' + str(image.label)
	#print 'Probs: ' + str(prob)
	#if label == image.label:
		#n_correct += 1

#print 'Accuracy = ' + str(float(n_correct)/float(n))


