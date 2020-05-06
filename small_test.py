
a = {1: [3]}
try:
    print(a[1][1])
except KeyError or IndexError:
    print("error")