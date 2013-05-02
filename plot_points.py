import matplotlib.pyplot as plt

f = open("nutritious_points.txt", "r")
xs_n = []
ys_n = []
for line in f:
    p = line.split()
    xs_n.append(float(p[0]))
    ys_n.append(float(p[1]))
f.close()

f = open("poisonous_points.txt", "r")
xs_p = []
ys_p = []
for line in f:
    p = line.split()
    xs_p.append(float(p[0]))
    ys_p.append(float(p[1]))
f.close()

f = open("empty_points.txt", "r")
xs_e = []
ys_e = []
for line in f:
    p = line.split()
    xs_e.append(float(p[0]))
    ys_e.append(float(p[1]))
f.close()

results = plt.figure(figsize=(10,7))
plt.scatter(xs_n, ys_n, c="green")
plt.scatter(xs_p, ys_p, c="red")
plt.scatter(xs_e, ys_e, c="skyblue")
results.savefig("training_plot3.png", dpi=600)
