import pickle
from neural_net_main import *
from neural_net import *

def classify(img):


	f = open('trained_network', 'r')
	network = pickle.load(f)
	f.close()

	image = imagify(img, 0)

	return network.Classify(image)

# images = []
# for i in imgs:
# 	image = imagify(i, imgs[i])
# 	print image
# 	images.append(image)

# print images[0]

# n = 1

# for image in images:
# 	label = network.Classify(image)
# 	print 'Classified: ' + str(label)

