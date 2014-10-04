"""
computes the learning rate according to the current iteration
and the total number of iterations
"""

def learning_rate(iter_no, iter_count):
	
    MAX_VALUE = 0.75
    MIN_VALUE = 0.1
    lr = 0.0 

    lr = MAX_VALUE - (float(iter_no) / iter_count) * 0.65

    return lr