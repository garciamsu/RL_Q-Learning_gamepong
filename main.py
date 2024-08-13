import matplotlib.pyplot as plt

figure, axes = plt.subplots()
ball = plt.Circle((0.5, 0.5), 0.3, fill=False)

axes.set_aspect(1)
axes.add_artist(ball)
plt.title("Ball")
plt.show()