"""
3d array - x,y,z
boxes fill the volume

compactness = max z that contains a non-zero value
ordering

constraints - 1000 x, 1000 y, inf z

1,000,000 boxes

ideas:
 - use evolutionary methods to find best configuration
 - split the task into multiple discrete chunks and then stack together
   i.e. 1000 1000 box sets, 100 10000 box sets
    need to profile speed of different set sizes
 - gpu-based acceleration if possible

first step:
  evaluate the first 10, 50, 100, 500, 1000 box result w/ no gpu


box = 24 points


"""

import numpy as np

print 'loading data'
presents = np.genfromtxt('data/presents.csv', delimiter=',', skip_header=1,
                         usecols=(1, 2, 3), dtype=np.uint32)

print 'bundling'
b = 1
bundle = np.zeros((0, 4))
max_area = 1000*1000 - 400*400
area = 0
for i, p in enumerate(presents):
    box = np.sort(p)
    box_area = box[0] * box[1]
    if area + box_area > max_area:
        if b % 100 == 0:
            print 'saving', i
        np.savez('data/w400/bundle%04d' % b, presents=bundle)
        area = 0
        b += 1
        bundle = np.zeros((0, 4))
    area += box_area
    box = np.r_[i+1, box].reshape((1, 4))
    bundle = np.concatenate((bundle, box))
print 'saving', i
print b, 'bundles'
np.savez('data/w400/bundle%04d' % b, presents=bundle)
