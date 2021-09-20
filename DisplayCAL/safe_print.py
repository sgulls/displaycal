# -*- coding: utf-8 -*-

import locale
import os
import sys

from encoding import get_encoding, get_encodings
from util_str import safe_unicode

original_codepage = None

enc, fs_enc = get_encodings()


_conwidth = None

def _get_console_width():
	global _conwidth
	if _conwidth is None:
		_conwidth = 80
		try:
			if sys.platform == "win32":
				from ctypes import windll, create_string_buffer
				import struct
				# Use stderr handle so that pipes don't affect the reported size
				stderr_handle = windll.kernel32.GetStdHandle(-12)
				buf = create_string_buffer(22)
				consinfo = windll.kernel32.GetConsoleScreenBufferInfo(stderr_handle,
																	  buf)
				if consinfo:
					_conwidth = struct.unpack("hhhhHhhhhhh", buf.raw)[0]
			else:
				_conwidth = int(os.getenv("COLUMNS"))
		except:
			pass
	return _conwidth


class SafePrinter():
	
	def __init__(self, pad=False, padchar=" ", sep=" ", end="\n", 
				 file_=sys.stdout, fn=None, encoding=None):
		"""
		Write safely, avoiding any UnicodeDe-/EncodingErrors on strings 
		and converting all other objects to safe string representations.
		
		sprint = SafePrinter(pad=False, padchar=' ', sep=' ', end='\\n', 
							 file=sys.stdout, fn=None)
		sprint(value, ..., pad=False, padchar=' ', sep=' ', end='\\n', 
			   file=sys.stdout, fn=None)
		
		Writes the values to a stream (default sys.stdout), honoring its 
		encoding and replacing characters not present in the encoding with 
		question marks silently.
		
		Optional keyword arguments:
		pad:     pad the lines to n chars, or os.getenv('COLUMNS') if True.
		padchar: character to use for padding, default a space.
		sep:     string inserted between values, default a space.
		end:     string appended after the last value, default a newline.
		file:    a file-like object (stream); defaults to the sys.stdout.
		fn:      a function to execute instead of printing.
		"""
		self.pad = pad
		self.padchar = padchar
		self.sep = sep
		self.end = end
		self.file = file_
		self.fn = fn
		self.encoding = encoding or (get_encoding(file_) if file_ else None)
	
	def __call__(self, *args, **kwargs):
		self.write(*args, **kwargs)
	
	def flush(self):
		self.file and self.file.flush()
	
	def write(self, *args, **kwargs):
		pad = kwargs.get("pad", self.pad)
		padchar = kwargs.get("padchar", self.padchar)
		sep = kwargs.get("sep", self.sep)
		end = kwargs.get("end", self.end)
		file_ = kwargs.get("file_", self.file)
		fn = kwargs.get("fn", self.fn)
		encoding = kwargs.get("encoding", self.encoding)
		strargs = []
		if encoding:
			cls = basestring
		else:
			cls = unicode
		for arg in args:
			if not isinstance(arg, cls):
				arg = safe_unicode(arg)
			if isinstance(arg, unicode) and encoding:
				arg = arg.encode(encoding, "asciize")
			strargs.append(arg)
		line = sep.join(strargs).rstrip(end)
		if pad is not False:
			if pad is True:
				width = _get_console_width()
			else:
				width = int(pad)
			line = line.ljust(width, padchar)
		if fn:
			fn(line)
		else:
			try:
				file_.write(line)
				if end:
					file_.write(end)
			except IOError:
				pass

safe_print = SafePrinter()

if __name__ == '__main__':
	for arg in sys.argv[1:]:
		safe_print(arg.decode(fs_enc))
