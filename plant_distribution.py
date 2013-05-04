import pickle
import game_interface
import matplotlib.pyplot as plt

f = open('plant_distribution_100x100_03.txt', 'r')
d = pickle.load(f)
f.close()
Nx, Ny, Px, Py, Ux, Uy, Ex, Ey = [], [], [], [], [], [], [], []


for k in d:
	(x, y) = k
	v = d[k]
	# Unknown Plant - 0
	if v == game_interface.STATUS_UNKNOWN_PLANT:
		Ux.append(x)
		Uy.append(y)
	elif v == game_interface.STATUS_NO_PLANT:
		Ex.append(x)
		Ey.append(y)
	elif v == game_interface.STATUS_NUTRITIOUS_PLANT:
		Nx.append(x)
		Ny.append(y)
	elif v == game_interface.STATUS_POISONOUS_PLANT:
		Px.append(x)
		Py.append(y)

fig = plt.figure(1, figsize=(20, 20))

plt.plot(Nx, Ny, 'sg', markersize=4, markeredgecolor = 'none')
plt.plot(Px, Py, 'sr', markersize=4, markeredgecolor = 'none')
plt.plot(Ux, Uy, 'sb', markersize=4, markeredgecolor = 'none')
plt.plot(Ex, Ey, 'sw', markersize=4, markeredgecolor = 'none')
plt.axis('equal')
plt.grid(False)

plt.show()

