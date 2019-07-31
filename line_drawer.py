import tkinter as tk
import numpy as np

class LineDrawer(tk.Canvas):
  '''
  Canvas that draws lines based on some loudnesses.
  '''
  def __init__(self, root, min_width, min_height, get_loudnesses, line_colour, bg_colour,
        min_thresh, max_thresh, line_width, gain, steepness, curviness, momentum,
        min_loud_thresh):
    '''
    Args:
      self
      root (tk.Tk): container to hold canvas
      min_width (int): minimum pixel width of canvas
      min_height (int): minimumm pixel height of canvas
      get_loudnesses (callable): takes no parameters, returns list of
        loudnesses at discrete time steps
      line_colour (tk.StringVar): Colour of the line to draw
      bg_colour (tk.StringVar): Colour of the background
      min_thresh (tk.IntVar): Minimum frequency threshold variable holder
      max_thresh (tk.IntVar): Maximum frequency threshold variable holder
      line_width (tk.StringVar): Line width as string, casts to float
      gain (tk.StringVar): Gain on audio as string, casts to float
      steepness (tk.StringVar): Steepness on envelope for tapering, casts to float
      curviness (tk.StringVar): Curviness on envelope for tapering, casts to float
      momentum (tk.StringVar): Momentum on a per-element basis of waveform buffer, casts to float
      min_loud_thresh (tk.StringVar): Minimum loudness threshold required to show a waveform
    '''
    super().__init__(root)
    self.root = root
    self.min_width = min_width
    self.min_height = min_height
    self.get_loudnesses = get_loudnesses

    self.line_colour = line_colour
    bg_colour.trace('w', lambda *args: self.change_bg_colour(bg_colour.get()))
    self.change_bg_colour(bg_colour.get())
    self.min_thresh = min_thresh
    self.max_thresh = max_thresh
    self.line_width = line_width
    self.gain = gain
    self.colour = 'blue'
    self.steepness = steepness
    self.curviness = curviness
    self.momentum = momentum
    self.min_loud_thresh = min_loud_thresh
    self.prev = None

  def change_bg_colour(self, colour):
    try:
      self.configure(background=colour)
    except:
      pass

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
      colour = self.line_colour.get()
      min_loud_thresh = float(self.min_loud_thresh.get())
    except ValueError:
      return
    if steepness < 0 or steepness > 1:
      return
    self.delete('all')
    if v.max() < min_loud_thresh/2:
      v = np.zeros_like(v)
    # Apply transformations
    v *= float(gain)
    v = self.taper(v, steepness, curviness)
    v += 0.5

    # Moving average per point
    if self.prev is not None:
      if v.shape[0] == self.prev.shape[0]:
        v = self.prev*(momentum) + v*(1-momentum)
    self.prev = v

    # Put in format for tkinter
    xy = []
    for (x,y) in enumerate(v):
      xy.append(x*self.root.winfo_width()/self.min_width)
      xy.append(y*max(self.min_height, self.root.winfo_height()))
    try:
      self.create_line(xy, fill=colour, width=width)
    except tk.TclError as e:
      pass
    except Exception as e:
      print(e)

  def main_loop(self):
    while True:
      try:
        min_thresh = int(self.min_thresh.get())
        max_thresh = int(self.max_thresh.get())
      except ValueError:
        self.root.update()
        continue
      # Sample the loudnesses over a short period of time
      loudnesses, rate = self.get_loudnesses()

      # w is the real part of the frequencies in loudnesses
      w = np.fft.rfft(loudnesses)
      freqs = np.fft.rfftfreq(len(loudnesses), d=1/rate)

      # Zero out the frequencies below min and above max
      min_freq_idx = np.count_nonzero(freqs < min_thresh)
      max_freq_idx = np.count_nonzero(freqs < max_thresh)
      w[:min_freq_idx] = 0
      w[max_freq_idx:] = 0

      # Return it to loudnesses, sampling the min_width number of elements
      try:
        cleaned = np.fft.irfft(w, n=self.min_width)
      except:
        print('Exiting due to width not being readable')
        break

      # Draw it to the screen
      self.new_line(cleaned)
      self.root.update()