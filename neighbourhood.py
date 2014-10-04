import sys
import math

"""
build a mask with values in [0, 1] for weights updating
"""

def neighbourhood(y, x, radius, height, width):
    x -= 1
    y -= 1
    mask = [[0 for j in range(width)] for i in range(height)]

    xmin = x - int(radius)
    if xmin < 0:
        xmin = 0

    xmax = x + int(radius) + 1
    if xmax > width:
        xmax = width

    ymin = y - int(radius)
    if ymin < 0:
        ymin = 0

    ymax = y + int(radius) + 1
    if ymax > height:
        ymax = height

    for i in range(ymin, ymax):
        for j in range(xmin, xmax):
            dist = math.sqrt((y - i)**2 + (x - j)**2)
            if dist <= radius:
                mask[i][j] = 1

    return mask

if __name__ == "__main__":
    m = neighbourhood(int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]),
                      int(sys.argv[4]), int(sys.argv[5]))