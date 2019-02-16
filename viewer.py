import os
import pyaudio
import threading
import math
import wave
import tkinter as tk
import tkinter.colorchooser
import numpy as np
import time

root = tk.Tk()

class LineDrawer(tk.Canvas):
	'''
	Canvas that draws lines based on some loudnesses.
	'''
	def __init__(self, root, width, height, get_loudnesses, min_thresh, max_thresh,
				line_width, gain, steepness, curviness, momentum):
		'''
		Args:
			self
			root (tk.Tk): container to hold canvas
			width (int): pixel width of canvas
			height (int): pixel height of canvas
			get_loudnesses (callable): takes no parameters, returns list of
				loudnesses at discrete time steps
			min_thresh (tk.IntVar): Minimum frequency threshold variable holder
			max_thresh (tk.IntVar): Maximum frequency threshold variable holder
			line_width (tk.StringVar): Line width as string, casts to float
			gain (tk.StringVar): Gain on audio as string, casts to float
			steepness (tk.StringVar): Steepness on envelope for tapering, casts to float
			curviness (tk.StringVar): Curviness on envelope for tapering, casts to float
			momentum (tk.StringVar): Momentum on a per-element basis of waveform buffer, casts to float
		'''
		super().__init__(root, width=width, height=height)
		self.root = root
		self.width = width
		self.height = height
		self.centre = self.height//2
		self.get_loudnesses = get_loudnesses

		self.min_thresh = min_thresh
		self.max_thresh = max_thresh
		self.line_width = line_width
		self.gain = gain
		self.colour = 'blue'
		self.steepness = steepness
		self.curviness = curviness
		self.momentum = momentum
		self.prev = None

	def change_colour(self):
		self.colour = tkinter.colorchooser.askcolor()[1]

	def set_min_thresh(self, v):
		self.min_thresh = v

	def set_max_thresh(self, v):
		self.max_thresh = v

	def taper(self, v, steepness, curviness):
		domain_end = 5*np.log(curviness)
		domain_len = len(v)//2
		domain = np.linspace(0, 2*domain_end, domain_len)
		domain -= domain_end*steepness
		envelope = 1/(1+np.exp(-domain))/2
		v[:domain_len] *= envelope
		v[-domain_len:] *= np.flip(envelope, 0)
		return v

	def new_line(self, v):
		# If the floats can't be parsed, then do nothing
		width = 0
		gain = 1
		try:
			width = float(self.line_width.get())
			gain = float(self.gain.get())
			steepness = float(self.steepness.get())
			curviness = float(self.curviness.get())
			momentum = float(self.momentum.get())
		except ValueError:
			return
		if steepness < 0 or steepness > 1:
			return
		self.delete('all')
		# Apply transformations
		v *= float(gain)
		v = self.taper(v, steepness, curviness)
		v += 0.5

		# Moving average per point
		if self.prev is not None:
			v = self.prev*(momentum) + v*(1-momentum)
		self.prev = v

		# Put in format for tkinter
		xy = []
		for (x,y) in enumerate(v):
			xy.append(x)
			xy.append(y*self.height)
		self.create_line(xy, fill=self.colour, width=width)

	def main_loop(self):
		while True:
			try:
				min_thresh = int(self.min_thresh.get())
				max_thresh = int(self.max_thresh.get())
			except ValueError:
				root.update()
				continue
			loudnesses, rate = self.get_loudnesses()
			w = np.fft.rfft(loudnesses)
			freqs = np.fft.rfftfreq(len(loudnesses), d=1/rate)
			min_freq_idx = np.count_nonzero(freqs < min_thresh)
			max_freq_idx = np.count_nonzero(freqs < max_thresh)
			w[:min_freq_idx] = 0
			w[max_freq_idx:] = 0
			cleaned = np.fft.irfft(w, n=1024)
			self.new_line(cleaned)
			root.update()

class Audio:
	def __init__(self, vfps=60):
		self.rate = 44100
		self.vfps = vfps
		self.chunk = self.rate // vfps

		self.p = pyaudio.PyAudio()
		self.stream = self.p.open(format=pyaudio.paInt16,
				channels=1,
				rate=44100,
				input=True,
				frames_per_buffer=self.chunk)

	def normalise(self, v, dtype=np.float32):
		inf = np.iinfo(v.dtype)
		abs_max = inf.max - inf.min
		return (v.astype(dtype) - inf.min) / abs_max

	def loudnesses(self):
		data = self.stream.read(self.chunk, exception_on_overflow=False)
		loudnesses = np.frombuffer(data, dtype='<i2')
		return self.normalise(loudnesses), self.rate

	def close():
		self.stream.stop_stream()
		self.stream.close()
		self.p.terminate()


min_thresh = tk.StringVar()
min_thresh.set(500)
max_thresh = tk.StringVar()
max_thresh.set(2000)
line_width = tk.StringVar()
line_width.set("3.")
gain = tk.StringVar()
gain.set("5.")
steepness = tk.StringVar()
steepness.set("0.5")
curviness = tk.StringVar()
curviness.set("2.")
momentum = tk.StringVar()
momentum.set("0.")

audio = Audio()
ld = LineDrawer(root, width=1024, height=300,
	get_loudnesses=audio.loudnesses,
	min_thresh=min_thresh,
	max_thresh=max_thresh,
	line_width=line_width,
	gain=gain,
	steepness=steepness,
	curviness=curviness,
	momentum=momentum)


def set_background():
	ld.configure(background=tkinter.colorchooser.askcolor()[1])


ld.pack()
change_colour_btn = tk.Button(text='Line Colour', command=ld.change_colour)
bg_colour_btn = tk.Button(text='Bg Colour', command=set_background)
min_thresh_lbl = tk.Label(root, text="Min. Freq.")
max_thresh_lbl = tk.Label(root, text="Max. Freq.")
line_width_lbl = tk.Label(root, text="Width")
gain_lbl = tk.Label(root, text="Gain (factor)")
steepness_lbl = tk.Label(root, text="Steepness (0-1)")
curviness_lbl = tk.Label(root, text="Curviness (factor)")
momentum_lbl = tk.Label(root, text="Momentum (0-1)")
min_thresh_box = tk.Entry(root, textvariable=min_thresh)
max_thresh_box = tk.Entry(root, textvariable=max_thresh)
line_width_box = tk.Entry(root, textvariable=line_width)
gain_box = tk.Entry(root, textvariable=gain)
steepness_box = tk.Entry(root, textvariable=steepness)
curviness_box = tk.Entry(root, textvariable=curviness)
momentum_box = tk.Entry(root, textvariable=momentum)
change_colour_btn.pack(padx=5, side=tk.LEFT)
bg_colour_btn.pack(padx=5, side=tk.LEFT)
min_thresh_lbl.pack(padx=5, side=tk.LEFT)
min_thresh_box.pack(padx=5, side=tk.LEFT)
max_thresh_lbl.pack(padx=5, side=tk.LEFT)
max_thresh_box.pack(padx=5, side=tk.LEFT)
line_width_lbl.pack(padx=5, side=tk.LEFT)
line_width_box.pack(padx=5, side=tk.LEFT)
gain_lbl.pack(padx=5)
gain_box.pack(padx=5)
steepness_lbl.pack(padx=5)
steepness_box.pack(padx=5)
curviness_lbl.pack(padx=5)
curviness_box.pack(padx=5)
momentum_lbl.pack(padx=5)
momentum_box.pack(padx=5)

ld.main_loop()


