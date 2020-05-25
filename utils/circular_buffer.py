# class CircularBuffer:
#
#     def __init__(self, size):
#         """Store buffer in given storage."""
#         self.buffer = [None]*size
#         self.low = 0
#         self.high = 0
#         self.size = size
#         self.count = 0
#
#     def isEmpty(self):
#         return self.count == 0
#
#     def isFull(self):
#         return self.count == self.size
#
#     def __len__(self):
#         return self.count
#
#     def add(self, value):
#         if self.isFull():
#             self.low = (self.low+1) % self.size
#         else:
#             self.count += 1
#         self.buffer[self.high] = value
#         self.high = (self.high + 1) % self.size
#
#     def remove(self):
#         if self.count == 0:
#             raise Exception ("Circular Buffer is empty");
#         value = self.buffer[self.low]
#         self.low = (self.low + 1) % self.size
#         self.count -= 1
#         return value
#
#     def __iter__(self):
#         idx = self.low
#         num = self.count
#         while num > 0:
#             yield self.buffer[idx]
#             idx = (idx + 1) % self.size
#             num -= 1
#
#     def __repr__(self):
#         if self.isEmpty():
#             return 'cb:[]'
#
#         return 'cb:[' + ','.join(map(str,self)) + ']'
