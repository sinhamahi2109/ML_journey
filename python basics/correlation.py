import matplotlib.pyplot as plt

# Sample data
x = [1, 2, 3, 4, 5]
y = [10, 24, 36, 45, 52]

plt.plot(x, y)

# Restrict the y-axis to look closely at values between 20 and 40
plt.ylim(20, 40)

plt.show()