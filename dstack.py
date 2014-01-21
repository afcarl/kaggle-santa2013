"""
current ideas:

subdividing a layer into smaller bins seems to introduce more error than simple
stacking along x then shifting up by max y until done. this couls still work,
but needs better free space determination.

another idea is to sort a bundle by area, then stack either in 'shelves' like
 the previous version, or radially from the corner.
"""
import numpy as np
import multiprocessing as mp
from sleigh import Sleigh
from shelf import Shelf

#BUNDLES = 5484  # w500
BUNDLES = 4889  # w400
#BUNDLES = 4508  # w300
#BUNDLES = 4375  # w250
#BUNDLES = 2

def stack(bid):
    if bid % 100 == 0:
        print 'bundle', bid+1
    presents = np.load('data/w300/bundle%04d.npz' % (bid+1))['presents']
    ysort = np.argsort(presents[:, 2])[::-1]
    presents = presents[ysort]

    sleigh = Sleigh(bid, len(presents))
    x, y, z = 1, 1, 1
    skip = list()
    znext = 0
    i = 0
    while i < len(presents) - 1:
        shelf = Shelf(sleigh, presents[i, 2], x, y, z)
        i, skip = shelf.fill(presents[i:], i, skip)
        if shelf.zmax > znext:
            znext = shelf.zmax
        if i >= len(presents) - 1:
            break
        if y + shelf.height - 1 > 1000:
            print 'new layer'
            z = znext
            y = 1
        else:
            y += shelf.height
    return sleigh


def merge(s1, s2):
    s1.merge(s2)
    return s1


if __name__ == '__main__':
    pool = mp.Pool(processes=16)
    print 'packing'
    sleighs = pool.map(stack, [3])#range(BUNDLES))

    print 'merging'
    while len(sleighs) > 1:
        print len(sleighs)
        s = len(sleighs) / 2
        temp = list()
        results = list()
        for i in range(s):
            r = pool.apply_async(merge, (sleighs[i*2], sleighs[i*2+1]))
            results.append(r)
        for r in results:
            temp.append(r.get())
        temp = sorted(temp, cmp=lambda a, b: cmp(a.id, b.id))
        if len(sleighs) % 2 == 1:
            temp.append(sleighs[-1])
        sleighs = temp
    print 'scoring'
    print sleighs[0].score()

    #print 'saving'
    #sleighs[0].save(invert=True)
    #print 'plotting'
    sleighs[0].plot(layer=1)