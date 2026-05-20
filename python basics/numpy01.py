import numpy as np
import matplotlib.pyplot as plt


arr =np.array([1,2,3,4,5,6,7,8])
print(arr.dtype)
print(type(arr))
arr[0]=0
print(arr)
arr[0]=1
print (arr)
print(arr[1::2])
print(arr.size)
print(arr.ndim)
print(arr.shape)
print(arr.mean())
print(arr.max())
print(arr.min())
print(arr.std())
a=np.array([1,2,3])
b=np.array([2,4,6])
print(np.add(a,b))
print(np.subtract(a,b))
print(np.multiply(a,b))
print(np.divide(a,b))
print(np.dot(a,b))
print(a+1)
np.pi
c=np.array([0,np.pi/4,np.pi/2,3*np.pi/4,np.pi])
d=np.sin(c)
print(d)
x=np.linspace(0,np.pi/2,100)
y=np.sin(x)
plt.plot(x,y)