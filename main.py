import numpy as np

import matplotlib.pyplot as plt


file = open("F:\\result.txt")

a = []
while 1:
    line = file.readline()
    if not line:
        break
    a.append(line)

plt.xlabel('times')
plt.ylabel('func')
plt.plot(a)
plt.show()