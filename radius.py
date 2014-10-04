"""
compute the learning radius according to the current iteration,
the total number of iterations and the size of the network
"""

def radius(iter_no, iter_count, height, width):
    maximum = 0.0

    if height > width:
    	maximum = height
    else:
    	maximum = width

    maximum = maximum / 8.0

    r = maximum - maximum * (float(iter_no) / iter_count)

    return r