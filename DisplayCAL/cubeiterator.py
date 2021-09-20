# -*- coding: utf-8 -*-


class Cube3D(object):

	def __init__(self, size=65, start=0, end=None):
		orange = start, end
		numentries = size ** 3
		if end is None:
			end = numentries
		for name in ("start", "end"):
			v = locals()[name]
			if not isinstance(v, (int, long)):
				raise TypeError("integer %s argument expected, got %s" %
								(name, v.__class__.__name__))
		start = self._clamp(start, 0, numentries, -1)
		end = self._clamp(end, 0, numentries, -1)
		for i, name in enumerate(("start", "end")):
			v = locals()[name]
			if v == -1:
				raise ValueError("%s argument %i out of range" %
								 (name, orange[i]))
		self._size = size
		self._start = start
		self._len = end - start

	def get(self, i, default=None):
		if i < 0:
			i = self._len + i
		if i < 0 or i > self._len - 1:
			return default
		return self[i]

	def index(self, (c0, c1, c2)):
		if not (c0, c1, c2) in self:
			raise ValueError("%r not in %r" % ((c0, c1, c2), self))
		i = c0 * self._size ** 2 + c1 * self._size + c2
		return int(i) - self._start

	def _clamp(self, v, lower=0, upper=None, fallback=None):
		if not upper:
			upper = self._len
		if v < lower:
			if v < -upper:
				v = fallback or lower
			else:
				v = upper + v
		elif v > upper:
			v = fallback or upper
		return v

	def __contains__(self, (c0, c1, c2)):
		return (c0 == int(c0) and c1 == int(c1) and c2 == int(c2) and
				max(c0, c1, c2) < self._size and
				self._start <= c0 * self._size ** 2 +
							   c1 * self._size +
							   c2 < self._len + self._start)

	def __getitem__(self, i):
		oi = i
		if i < 0:
			i = self._len + i
		if i < 0 or i > self._len - 1:
			raise IndexError("index %i out of range" % oi)
		i += self._start
		return (i // self._size // self._size,
				i // self._size % self._size,
				i % self._size)
	
	def __getslice__(self, i, j):
		i = self._clamp(i)
		j = self._clamp(j)
		return self.__class__(self._size, self._start + i, self._start + j)

	def __len__(self):
		return self._len

	def __repr__(self):
		return (self.__class__.__name__ + "(size=%i, start=%i, end=%i)" %
				(self._size, self._start, self._start + self._len))


class Cube3DIterator(Cube3D):

	# This iterator is actually slightly slower especially with large cubes
	# than using iter(<Cube3D instance>)

	def __init__(self, *args, **kwargs):
		Cube3D.__init__(self, *args, **kwargs)
		self._next = 0

	def __iter__(self):
		return self

	def next(self):
		if self._next == self._len:
			raise StopIteration
		else:
			result = self[self._next]
			self._next += 1
			return result
