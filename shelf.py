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
        self.yoffset = y
        self.x = x
        self.y = y
        self.z = z
        self.zmax = 1
        #print 'new shelf at (%d, %d, %d)' % (x, y, z)

    def add(self, p, invert=False):
        #print self.x, self.y, p
        #print 'adding', int(p[0])
        if int(p[0]) in self.sleigh.present_ids:
            #print np.sort(self.sleigh.present_ids)
            raise Exception('duplicate present! %d' % p[0])
        if invert:
            vertices = np.array(
                [[self.x-p[1]+1, self.y-p[2]+1, self.z],
                 [self.x, self.y, self.z+p[3]-1]])
        else:
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
                self.fill_right(presents, i, offset, skip)
                self.full = True

            if self.full:
                break
        return i + offset, skip

    def fill_up(self, presents, i, offset, skip):
        """
        Fill the final column left-to-right, bottom-to-top using the largest
        available boxes.

        If the first fill box is significantly taller than the next, we
        introduce another gap. Check is the height of a placed fill piece is
        significantly shorter than the one before it (e.g. under 75%), if so
        create a new column until the fill catches up.
        """
        if i >= len(presents) - 1:
            return

        x_col = 1001 - self.x
        y_col = self.height  # + 1 - self.y

        if x_col <= 0 or y_col <= 0:
            return
        stop = 0
        remain = np.array([x_col, y_col])
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


    def fill_right(self, presents, i, offset, skip):
        """
        Starting above and on the left edge of the last order placed box,
        fill top-to-bottom, right-to-left.

        we need to test when x, y are flipped.
        """
        if i >= len(presents) - 1:
            return

        for placed in self.presents[::-1]:
            self.x = placed[1, 0]
            self.y = self.yoffset + self.height - 1

            x_col = placed[1, 0] - placed[0, 0] + 1
            y_col = self.height - (placed[1, 1] - placed[0, 1] + 1)

            if x_col <= 0 or y_col <= 0:
                continue

            stop = 0
            remain = np.array([x_col, y_col])
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

                    ok = self.add(p, invert=True)

                    if not ok:
                        print 'fill up placement error'
                        return
                    else:
                        skip.append(p[0])
                        self.x -= p[1]
                        if self.z + p[3] > self.zmax:
                            self.zmax = self.z + p[3]
                        remain[0] -= p[1]
                        if p[2] > y_shift:
                            y_shift = p[2]
                if stop >= 2:
                    break
                remain[1] -= y_shift
                self.x = placed[1, 0]
                self.y -= y_shift