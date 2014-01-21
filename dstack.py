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
#BUNDLES = 1024

def stack(bid):
    if bid % 100 == 0:
        print 'bundle', bid+1
    presents = np.load('data/w400/bundle%04d.npz' % (bid+1))['presents']
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
        if y + shelf.height - 1 > 1000:
            print 'new layer'
            z = znext
            y = 1
        else:
            y += shelf.height
    return sleigh



# def stack(bid):
#     if bid % 100 == 0:
#         print 'bundle', bid+1
#     presents = np.load('data/w250/bundle%04d.npz' % (bid+1))['presents']
#     ysort = np.argsort(presents[:, 2])[::-1]
#     presents = presents[ysort]
#
#     sleigh = Sleigh(bid, len(presents))
#     #print "[%d - count] %d" % (bid, sleigh.count)
#     x, y, z = 1, 1, 1
#     skip = list()
#     ynext = 0
#     znext = 0
#     shelf = list()
#     for i, p in enumerate(presents):
#         if i in skip:
#             continue
#         while True:
#             # 1) fill ordered
#             placed = sleigh.place_present(int(p[0]), np.array([[x, y, z],
#                                           [x+p[1]-1, y+p[2]-1, z+p[3]-1]]),
#                                           xy=True, invert=True)
#             if placed:
#                 # increment x, bump up shelf as needed
#                 x += p[1]
#                 if y+p[2] > ynext:
#                     ynext = y + p[2]
#                 if z+p[3] > znext:
#                     znext = z + p[3]
#                 shelf.append(sleigh.presents[sleigh.cursor-1])
#                 break
#             elif y+p[2] - 1 > 1000:
#                 # for current strategy, this means we can't fit all pieces
#                 # into the layer, so we terminate
#                 print 'bad fit', bid, znext
#                 x, y, z = 1, 1, znext
#                 ynext = 0
#                 shelf = list()
#             else:
#                 # 2) fill left
#                 remain = 1001 - x
#                 xshelf = remain
#                 yshelf = y
#                 yremain = ynext - yshelf
#                 while yremain > 0:
#                     yns = 0
#                     while (i < sleigh.count - 1 and
#                            remain > np.min(presents[i+1:, 1])):
#                         options = np.nonzero(np.logical_and(
#                             presents[i+1:, 1] <= remain,
#                             presents[i+1:, 2] <= yremain))[0]+i+1
#                         best = np.argsort(presents[options, 1])[::-1]
#                         boxes = options[best]
#                         box = boxes[0]
#                         j = 0
#                         while box in skip:
#                             j += 1
#                             box = boxes[j]
#                         b = presents[box]
#                         placed = sleigh.place_present(
#                             int(b[0]), np.array([[x, y, z],
#                             [x+b[1]-1, y+b[2]-1, z+b[3]-1]]),
#                             xy=True, invert=True)
#                         if not placed:
#                             print bid, 'placement error'
#                             return
#                         skip.append(box)
#                         x += b[1]
#                         if b[2] > yns:
#                             yns = b[2]
#                         if z+b[3] > znext:
#                             znext = z + b[3]
#                         remain = 1001 - x
#                     yshelf += yns
#                     yremain = ynext - yshelf
#
#                 x, y = 1, ynext
#                 shelf = list()
#     return sleigh




def merge(s1, s2):
    s1.merge(s2)
    return s1


if __name__ == '__main__':
    pool = mp.Pool(processes=4)
    print 'packing'
    sleighs = pool.map(stack, range(BUNDLES))

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

    print 'saving'
    sleighs[0].save(invert=True)

    # print 'plotting'
    # sleighs[0].plot(layer=1)
