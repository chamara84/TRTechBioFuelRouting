#!/usr/bin/python

"""Van Emde Boas queues implementation for Python. See:

http://evanjones.ca/software/van-emde-boas-queue.html

Released into the Public Domain.
"""

__author__ = "Evan Jones <evanj@mit.edu>"

import bisect
import random
import sys
import unittest

def log2(n):
    if n <= 0: raise OverflowError("log2(%d) is undefined" % n)

    i = 0
    v = 1L
    while v < n:
        v <<= 1
        i += 1
    if v != n:
        raise ValueError("%d is not a power of 2" % n)
    return i

    
class Log2Test(unittest.TestCase):
    def testLog0(self):
        self.assertRaises(OverflowError, log2, 0)

    def testLog2(self):
        assert log2(1) == 0
        assert log2(2) == 1
        assert log2(4) == 2
        assert log2(1024) == 10

    def testNotPowerOf2(self):
        self.assertRaises(ValueError, log2, 3)
        self.assertRaises(ValueError, log2, 79)


class VEBQueueSmall(object):
    def __init__(self):
        """Creates a "VEB" queue containing only 2 items."""
        self.values = [False, False]

    def insert(self, x):
        assert 0 <= x and x < 2
        self.values[x] = True

    def delete(self, x):
        assert 0 <= x and x < 2
        self.values[x] = False

    def find(self, x):
        assert 0 <= x and x < 2
        return self.values[x]

    def max(self):
        for i in xrange(1, -1, -1):
            if self.values[i]:
                return i
        return None

    def min(self):
        for i in xrange(2):
            if self.values[i]:
                return i
        return None

    def predecessor(self, x):
        assert 0 <= x and x < 2

        if x == 0: return None
        assert x == 1
        if self.values[0]:
            return 0

def NewVEBQueue(n):
    if n == 2:
        return VEBQueueSmall()
    else:
        return VEBQueueBase(n)


class VEBQueueBase(object):
    def __init__(self, n):
        """Create a queue containing (0, n-1). n must be = 2^(2^x)."""

        try:
            power = log2(n)
            powpow = log2(n)
        except OverflowError:
            raise ValueError("n must be = 2^(2^x) for some x")

        self.sqrtShift = power / 2
        sqrtN = 1 << self.sqrtShift
        self.sqrtMask = sqrtN - 1
        self.n = n

        self.high = NewVEBQueue(sqrtN)
        self.low = [None] * sqrtN
        self.minValue = None
        self.maxValue = None

    def split(self, x):
        """Returns the high and low portions of x."""

        xHigh = x >> self.sqrtShift
        xLow = x & self.sqrtMask
        return (xHigh, xLow)

    def insert(self, x):
        assert 0 <= x and x < self.n

        if self.minValue is None:
            # Insert in empty queue: O(1)
            assert self.maxValue is None
            self.minValue = x
            self.maxValue = x
            return
        if x == self.minValue:
            # Inserting the minimum again does nothing
            return
    
        if x < self.minValue:
            # Inserting less than min: actually insert min
            oldMin = self.minValue
            self.minValue = x
            x = oldMin
        assert x > self.minValue

        if x > self.maxValue:
            self.maxValue = x

        xHigh, xLow = self.split(x)

        if self.low[xHigh] is None:
            # Empty sub-queue: Create it
            self.low[xHigh] = NewVEBQueue(1 << self.sqrtShift)
            self.high.insert(xHigh)
        self.low[xHigh].insert(xLow)

    def delete(self, x):
        assert 0 <= x and x < self.n

        if self.minValue is None:
            # Delete in empty queue: do nothing
            return
        if x < self.minValue:
            # x does not exist in the queue
            return
        assert x >= self.minValue

        if x == self.minValue:
            # Move the successor to the minimum value and delete that instead
            index = self.high.min()
            if index == None:
                # No successor: we are done
                assert self.maxValue == self.minValue
                self.minValue = None
                self.maxValue = None
                return

            self.minValue = (index << self.sqrtShift) | self.low[index].min()
            x = self.minValue

        xHigh, xLow = self.split(x)

        if self.low[xHigh] == None:
            # Nothing to delete
            return

        # The queue for x must exist. Delete it recursively
        self.low[xHigh].delete(xLow)

        if self.low[xHigh].min() is None:
            # Sub queue is now empty: delete it from the high queue
            self.low[xHigh] = None
            self.high.delete(xHigh)

        if x == self.maxValue:
            # If we deleted the maximum, update it in O(1) time
            maxHigh = self.high.max()
            if maxHigh is None:
                # 1 element in this queue
                assert self.minValue is not None
                self.maxValue = self.minValue
            else:
                self.maxValue = (maxHigh << self.sqrtShift) | self.low[maxHigh].max()

    def max(self):
        return self.maxValue

    def min(self):
        return self.minValue

    def find(self, x):
        assert 0 <= x and x < self.n

        if self.minValue is None: return False
        if x == self.minValue: return True

        xHigh, xLow = self.split(x)
        if self.low[xHigh] is None:
            return False
        return self.low[xHigh].find(xLow)

    def predecessor(self, x):
        assert 0 <= x and x < self.n

        if self.minValue is None or x <= self.minValue:
            # Empty queue or nothing smaller
            return None

        xHigh, xLow = self.split(x)
        if self.low[xHigh] is None or xLow <= self.low[xHigh].min():
            # We need to look before this block: recurse on self.high O(sqrt n)
            index = self.high.predecessor(xHigh)
            if index is None:
                # No predecessors in self.high: Return the min
                return self.minValue

            # Combine the index with the max from the lower block
            return (index << self.sqrtShift) | self.low[index].max()
        else:
            assert xLow > self.low[xHigh].min()
            # We need to look in this block: recurse on self.low O(sqrt n)
            lowerPredecessor = self.low[xHigh].predecessor(xLow)
            assert lowerPredecessor is not None
            return (xHigh << self.sqrtShift) | lowerPredecessor


class VEBQueueTest(unittest.TestCase):
    def testCreateNotEvenPowerOfTwo(self):
        self.assertRaises(ValueError, NewVEBQueue, 0)
        self.assertRaises(ValueError, NewVEBQueue, 3)

    def testInsertFindSmall(self):
        q = NewVEBQueue(2)
        assert not q.find(0)
        assert not q.find(1)
        self.assertRaises(AssertionError, q.find, 2)
        self.assertRaises(AssertionError, q.insert, 2)

        q.insert(0)
        assert q.find(0)
        assert not q.find(1)

        q.insert(1)
        assert q.find(0)
        assert q.find(1)

    def testDeleteSmall(self):
        q = NewVEBQueue(2)
        self.assertRaises(AssertionError, q.delete, 2)
        q.insert(0)
        q.insert(1)
        q.delete(0)
        assert not q.find(0)
        assert q.find(1)

        q.delete(1)
        assert not q.find(0)
        assert not q.find(1)

    def testMaxMinSmall(self):
        q = NewVEBQueue(2)
        assert q.min() is None
        assert q.max() is None

        q.insert(0)
        assert q.min() == 0
        assert q.max() == 0

        q.insert(1)
        assert q.min() == 0
        assert q.max() == 1

    def testPredecessorSmall(self):
        q = NewVEBQueue(2)
        assert q.predecessor(0) is None
        assert q.predecessor(1) is None

        q.insert(0)
        assert q.predecessor(0) is None
        assert q.predecessor(1) == 0

    def testInsertFindMedium(self):
        q = NewVEBQueue(4)
        assert not q.find(0)
        assert not q.find(1)
        assert not q.find(2)
        assert not q.find(3)
        self.assertRaises(AssertionError, q.find, 5)
        self.assertRaises(AssertionError, q.insert, 5)

        q.insert(3)
        q.insert(3) # Inserting twice does nothing
        assert not q.find(0)
        assert not q.find(1)
        assert not q.find(2)
        assert q.find(3)

        q.insert(1)
        assert not q.find(0)
        assert q.find(1)
        assert not q.find(2)
        assert q.find(1)

    def testDeleteMedium(self):
        q = NewVEBQueue(4)
        self.assertRaises(AssertionError, q.delete, 5)
        
        # Delete in empty queue does nothing
        q.delete(3)
        
        q.insert(3)
        q.insert(1)
        q.insert(2)
        q.delete(2)
        assert not q.find(0)
        assert q.find(1)
        assert not q.find(2)
        assert q.find(3)
        assert q.max() == 3
        assert q.min() == 1

        q.delete(2) # 2 does not exist: no problem
        assert not q.find(0)
        assert q.find(1)
        assert not q.find(2)
        assert q.find(3)

        q.delete(3)
        assert not q.find(0)
        assert q.find(1)
        assert not q.find(2)
        assert not q.find(3)
        assert q.max() == 1
        assert q.min() == 1

        q.delete(1)
        assert not q.find(0)
        assert not q.find(1)
        assert not q.find(2)
        assert not q.find(1)
        assert q.max() is None
        assert q.min() is None

    def testMaxMinMedium(self):
        q = NewVEBQueue(4)
        assert q.min() is None
        assert q.max() is None

        q.insert(2)
        assert q.min() == 2
        assert q.max() == 2

        q.insert(3)
        assert q.min() == 2
        assert q.max() == 3

        q.insert(0)
        assert q.min() == 0
        assert q.max() == 3

    def testPredecessorMedium(self):
        q = NewVEBQueue(4)
        assert q.predecessor(0) is None
        assert q.predecessor(1) is None
        assert q.predecessor(2) is None
        assert q.predecessor(3) is None

        q.insert(3)
        assert q.predecessor(1) is None
        assert q.predecessor(2) is None
        assert q.predecessor(3) is None

        q.insert(1)
        assert q.predecessor(0) is None
        assert q.predecessor(1) is None
        assert q.predecessor(2) == 1
        assert q.predecessor(3) == 1

    def testPredecessorBig(self):
        # Error sequence found via random testing
        q = NewVEBQueue(16)
        q.insert(12)
        q.insert(15)
        q.insert(9)
        q.delete(12)
        self.assertEquals(9, q.predecessor(13))

class LameQueue(object):
    def __init__(self):
        self.q = []
    
    def insert(self, x):
        # Do a sorted insert
        insertion_point = bisect.bisect_left(self.q, x)
        if insertion_point == len(self.q) or self.q[insertion_point] != x:
            self.q.insert(insertion_point, x)

    def delete(self, x):
        insertion_point = bisect.bisect_left(self.q, x)
        if insertion_point < len(self.q) and self.q[insertion_point] == x:
            del self.q[insertion_point]

    def find(self, x):
        locate = bisect.bisect_left(self.q, x)
        if locate == len(self.q) or self.q[locate] != x:
            return False
        return True

    def max(self):
        if len(self.q) > 0:
            return self.q[-1]
        return None

    def min(self):
        if len(self.q) > 0:
            return self.q[0]
        return None

    def predecessor(self, x):
        locate = bisect.bisect_left(self.q, x) - 1
        if locate >= 0:
            return self.q[locate]
        return None

class RandomTest(unittest.TestCase):
    def testRandom(self):
        n = 1 << 16
        totalOperations = 1 << 16
        operations = totalOperations

        q = NewVEBQueue(n)
        lame = LameQueue()
        while operations > 0:
            # Do some searches
            numSearches = random.randint(0, 10) 
            operations -= numSearches
            for i in xrange(numSearches):
                search = random.randint(0, n-1)
                r1 = lame.find(search)
                r2 = q.find(search)
                assert r1 == r2

                r1 = lame.predecessor(search)
                r2 = q.predecessor(search)
                assert r1 == r2

            # Change the queue state
            operations -= 1
            value = random.randint(0, n-1)
            stateChange = random.randint(0, 1)
            if stateChange == 0:
                q.insert(value)
                lame.insert(value)
                #~ print "insert", value
            else:
                q.delete(value)
                lame.delete(value)
                #~ print "delete", value

            # Check the max/min variables
            assert lame.max() == q.max()
            assert lame.min() == q.min()

if __name__ == "__main__":
    unittest.main()


    
