import numpy as np
import pylab as plt


class Sleigh():
    """
    Represents the Santa's sleigh. Keeps track of presents placed in it and
    scores the result based on the compactness and orderliness metric.

    Presents in the sleigh are defined by two corner vertices (x, y, z, i)
    """
    def __init__(self, id, count, length=1000, width=1000):
        self.id = id
        self.length = length
        self.width = width
        self.height = 0
        self.count = count
        self.presents = np.zeros((count, 2, 3))
        self.present_ids = np.zeros(count)
        self.cursor = 0
        self.present_layers = dict()

    def place_present(self, id, vertices, xy=False, invert=False):
        """
        Attempt to place the present defined be the two vertices into the
        sleigh. Returns an error if the placement is invalid.

        vertices has shape (2,3) corresponding to lower and upper x, y, and z
        coordinates i.e. vertices[0] < vertices[1] is true for all elements

        When a present is placed, the collision surface should be updated
        accordingly and the present id added to the appropriate z layer
        counter.
        """
        # place present in layer
        if xy:
            ok = self.check_layer_collision(vertices)
        else:
            ok = self.check_collision(vertices)

        if ok:
            self.presents[self.cursor] = vertices
            self.present_ids[self.cursor] = id
            self.cursor += 1

            if invert:
                layer = vertices[0, 2]
            else:
                layer = vertices[1, 2]

            if vertices[1, 2] > self.height:
                self.height = vertices[1, 2]

            if layer in self.present_layers.keys():
                self.present_layers[layer].add(id)
            else:
                self.present_layers[layer] = set([id])
            return True
        else:
            return False

    def score(self):
        """
        A metric based on compactness and orderliness of the present stack.
        """
        order = list()
        for key in sorted(self.present_layers.keys(), reverse=False):
            order.extend(sorted(self.present_layers[key]))
            #print key, len(self.present_layers[key])
        #print order
        sigma = 0
        offset = np.min(order) - 1
        for i, pid in enumerate(order):
            sigma += np.abs((i+1) - (pid-offset))

        #print '---'
        #print self.height, sigma
        return 2 * self.height + sigma

    def check_collision(self, vertices):
        """
        Determine if the present vertices fall inside the current collision
        surface.
        """
        if vertices[0, 0] < 1 or vertices[1, 0] > 1000 or \
           vertices[0, 1] < 1 or vertices[1, 1] > 1000 or \
           vertices[0, 2] < 1 or vertices[1, 2] < 1:
            return False

        for p in self.presents:
            collisions = 0
            if not (vertices[1, 0] < p[0, 0] or vertices[0, 0] > p[1, 0]):
                collisions += 1

            if not (vertices[1, 1] < p[0, 1] or vertices[0, 1] > p[1, 1]):
                collisions += 1

            if not (vertices[1, 2] < p[0, 2] or vertices[0, 2] > p[1, 2]):
                collisions += 1

            if collisions == 3:
                return False

        return True

    def check_layer_collision(self, vertices, full=False):
        """
        Determine if the present xy vertices fall inside the current collision
        surface of the specified area
        """
        if vertices[0, 0] < 1 or vertices[1, 0] > 1000 or \
           vertices[0, 1] < 1 or vertices[1, 1] > 1000 or \
           vertices[0, 2] < 1 or vertices[1, 2] < 1:
            return False

        if full:
            idz = np.where(self.presents[:, ::2, 2] == vertices[0, 2])
            presents = self.presents[idz[0]]
            for p in presents:
                collisions = 0
                if not (vertices[1, 0] < p[0, 0] or vertices[0, 0] > p[1, 0]):
                    collisions += 1

                if not (vertices[1, 1] < p[0, 1] or vertices[0, 1] > p[1, 1]):
                    collisions += 1

                if collisions == 2:
                    print 'collision'
                    return False

        return True

    def save(self, invert=False):
        if invert:
            self.presents[:, :, 2] = (self.height + 1) - self.presents[:, :, 2]
        header = ('PresentId',
                  'x1', 'y1', 'z1', 'x2', 'y2', 'z2', 'x3', 'y3', 'z3',
                  'x4', 'y4', 'z4', 'x5', 'y5', 'z5', 'x6', 'y6', 'z6',
                  'x7', 'y7', 'z7', 'x8', 'y8', 'z8')
        fh = open('submission.csv', 'w')
        fh.write(','.join(header)+'\n')
        sort = np.argsort(self.present_ids)
        for i, p in enumerate(self.presents[sort]):
            entry = (i + 1,
                     p[0, 0], p[0, 1], p[0, 2], p[1, 0], p[0, 1], p[0, 2],
                     p[0, 0], p[1, 1], p[0, 2], p[1, 0], p[1, 1], p[0, 2],
                     p[0, 0], p[0, 1], p[1, 2], p[1, 0], p[0, 1], p[1, 2],
                     p[0, 0], p[1, 1], p[1, 2], p[1, 0], p[1, 1], p[1, 2])
            fh.write(','.join(map(str,map(int,entry)))+'\n')
        fh.close()

    def merge(self, sleigh):
        """
        Merge two sleigh packings together.
        """
        for key, val in sleigh.present_layers.iteritems():
            self.present_layers[key + self.height] = val
        sleigh.presents[:, :, 2] += self.height
        self.presents = np.concatenate((self.presents, sleigh.presents))
        self.present_ids = np.concatenate((self.present_ids, sleigh.present_ids))
        self.height += sleigh.height
        self.count = len(self.presents)
        self.cursor = self.count - 1

    def plot(self, layer=1):
        """
        Plot the 2d layout of the layer
        """
        img = np.zeros((1000, 1000))
        color = 1
        n_colors = 7
        pids = self.present_layers[layer]
        for i, pid in enumerate(pids):
            idx = np.where(self.present_ids == pid)[0][0]
            p = self.presents[idx]
            x = np.arange(p[0, 0]-1, p[1, 0], dtype=np.uint32)
            y = np.arange(p[0, 1]-1, p[1, 1], dtype=np.uint32)
            for j in y:
                img[j, x] = p[1, 2]
            color += 1
            if color > n_colors:
                color = 1
        plt.imshow(img, aspect='auto', interpolation='nearest',
                   origin='lower', cmap=plt.get_cmap('spectral'))
        #plt.colorbar()
        plt.show()
