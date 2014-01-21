import numpy as np


class Shelf():
    """
    Shelf packing strategies
     1) fill boxes in descending y-value order along shelf from left-to-right
        until the next largest can't fit
     2) find the next largest boxes to fill the remaining space until we are
        as close to the edge as we can get
     3) fill upwards as in (2) until the top of the shelf is met
     4) fill backwards along shelf like in (2) until initial box is met

     i.e. fill left, fill up, fill right

     in order to perform 3 and 4, we need to keep track of the presents on the
     shelf instead of just current x position and next y
    """
    def __init__(self, sleigh, height, x, y, z):
        self.sleigh = sleigh
        self.height = height
        self.presents = list()
        self.full = False
        self.x = x
        self.y = y
        self.z = z
        self.zmax = 1
        #print 'new shelf at (%d, %d, %d)' % (x, y, z)

    def add(self, p):
        #print self.x, self.y, p
        #print 'adding', int(p[0])
        if int(p[0]) in self.sleigh.present_ids:
            #print np.sort(self.sleigh.present_ids)
            raise Exception('duplicate present! %d' % p[0])
        vertices = np.array(
            [[self.x, self.y, self.z],
             [self.x+p[1]-1, self.y+p[2]-1, self.z+p[3]-1]])

        ok = self.sleigh.place_present(int(p[0]), vertices, xy=True,
                                         invert=True)
        #if not ok:
        #    print 'failed'
        return ok

    def fill(self, presents, offset, skip):
        """
        Given the current remaining list of presents, fill the shelf
        """
        i = 0
        for i, p in enumerate(presents):
            #print i + offset, self.sleigh.cursor
            if p[0] in skip:
                continue

            ok = self.add(p)

            if ok:
                self.presents.append(self.sleigh.presents[self.sleigh.cursor-1])
                self.x += p[1]
                if self.z + p[3] > self.zmax:
                    self.zmax = self.z + p[3]
            else:
                self.fill_up(presents, i, offset, skip)
                self.fill_right(presents, i, skip)
                self.full = True

            if self.full:
                break
        return i + offset, skip

    def fill_up(self, presents, i, offset, skip):
        """
        Fill the final column left-to-right, bottom-to-top using the largest
        available boxes.
        """
        if i >= len(presents) - 1:
            return

        x_col = 1001 - self.x
        y_col = self.height  # + 1 - self.y

        if x_col <= 0 or y_col <= 0:
            return
        stop = 0
        remain = np.array([x_col, y_col])
        added = 0
        while remain[1] > 0:
            remain[0] = x_col
            y_shift = 0
            while remain[0] > 0:
                #print remain
                test = remain >= presents[i+1:, 1:3]
                options = np.logical_and(test[:, 0], test[:, 1])
                if not options.any():
                    stop += 1
                    break
                else:
                    stop = 0

                idx = np.nonzero(options)[0] + i + 1
                best = np.argsort(presents[idx, 1])[::-1]
                pids = idx[best]
                pid = pids[0]
                p = presents[pid]
                j = 0
                while p[0] in skip:
                    j += 1
                    if j >= len(pids):
                        stop = 2
                        break
                    pid = pids[j]
                    p = presents[pid]
                if stop > 0:
                    break

                ok = self.add(p)

                if not ok:
                    print 'fill up placement error'
                    return
                else:
                    added += 1
                    skip.append(p[0])
                    self.x += p[1]
                    if self.z + p[3] > self.zmax:
                        self.zmax = self.z + p[3]
                    remain[0] -= p[1]
                    if p[2] > y_shift:
                        y_shift = p[2]
            if stop >= 2:
                break
            remain[1] -= y_shift
            self.x = 1001 - x_col
            self.y += y_shift

        return added

    def fill_right(self, present, i, skip):
        pass