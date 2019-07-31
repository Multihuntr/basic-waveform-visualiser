import tkinter as tk
import tkinter.colorchooser

from audio import Audio
from line_drawer import LineDrawer
import conf

# Open tkinter windows
line_w = tk.Tk()
line_w.title("Visualiser - Line")
opts_w = tk.Toplevel()
opts_w.title("Visualiser - Options")


# Load editable variables
conf_filename = './config.yaml'
c = conf.load(conf_filename)

line_colour = tk.StringVar()
line_colour.set(c.line_colour or 'blue')
bg_colour = tk.StringVar()
bg_colour.set(c.bg_colour or 'white')
min_thresh = tk.StringVar()
min_thresh.set(c.min_thresh or 500)
max_thresh = tk.StringVar()
max_thresh.set(c.max_thresh or 2000)
line_width = tk.StringVar()
line_width.set(c.line_width or "3.")
gain = tk.StringVar()
gain.set(c.gain or "5.")
steepness = tk.StringVar()
steepness.set(c.steepness or "0.5")
curviness = tk.StringVar()
curviness.set(c.curviness or "2.")
momentum = tk.StringVar()
momentum.set(c.momentum or "0.")
min_loud_thresh = tk.StringVar()
min_loud_thresh.set(c.min_loud_thresh or "0.")



# Create UI elements
def line_colour_fnc():
	line_colour.set(tkinter.colorchooser.askcolor()[1])

def bg_colour_fnc():
  bg_colour.set(tkinter.colorchooser.askcolor()[1])

change_colour_btn = tk.Button(opts_w, text='Line Colour', command=line_colour_fnc)
bg_colour_btn = tk.Button(opts_w, text='Bg Colour', command=bg_colour_fnc)
min_thresh_lbl = tk.Label(opts_w, text="Min. Freq.")
max_thresh_lbl = tk.Label(opts_w, text="Max. Freq.")
line_width_lbl = tk.Label(opts_w, text="Width")
gain_lbl = tk.Label(opts_w, text="Gain (factor)")
steepness_lbl = tk.Label(opts_w, text="Steepness (0-1)")
curviness_lbl = tk.Label(opts_w, text="Curviness (factor)")
momentum_lbl = tk.Label(opts_w, text="Momentum (0-1)")
min_loud_thresh_lbl = tk.Label(opts_w, text="Min. Loud. Thresh.(0-1)")
line_colour_box = tk.Entry(opts_w, textvariable=line_colour)
bg_colour_box = tk.Entry(opts_w, textvariable=bg_colour)
min_thresh_box = tk.Entry(opts_w, textvariable=min_thresh)
max_thresh_box = tk.Entry(opts_w, textvariable=max_thresh)
line_width_box = tk.Entry(opts_w, textvariable=line_width)
gain_box = tk.Entry(opts_w, textvariable=gain)
steepness_box = tk.Entry(opts_w, textvariable=steepness)
curviness_box = tk.Entry(opts_w, textvariable=curviness)
momentum_box = tk.Entry(opts_w, textvariable=momentum)
min_loud_thresh_box = tk.Entry(opts_w, textvariable=min_loud_thresh)
change_colour_btn.pack(padx=5, pady=3)
line_colour_box.pack(padx=5, pady=3)
bg_colour_btn.pack(padx=5, pady=3)
bg_colour_box.pack(padx=5, pady=3)
min_thresh_lbl.pack(padx=40, pady=3)
min_thresh_box.pack(padx=40, pady=3)
max_thresh_lbl.pack(padx=40, pady=3)
max_thresh_box.pack(padx=40, pady=3)
line_width_lbl.pack(padx=40, pady=3)
line_width_box.pack(padx=40, pady=3)
gain_lbl.pack(padx=40, pady=3)
gain_box.pack(padx=40, pady=3)
steepness_lbl.pack(padx=40, pady=3)
steepness_box.pack(padx=40, pady=3)
curviness_lbl.pack(padx=40, pady=3)
curviness_box.pack(padx=40, pady=3)
momentum_lbl.pack(padx=40, pady=3)
momentum_box.pack(padx=40, pady=3)
min_loud_thresh_lbl.pack(padx=40, pady=3)
min_loud_thresh_box.pack(padx=40, pady=3)


# Create line canvas
audio = Audio()
ld = LineDrawer(line_w, min_width=1024, min_height=50,
  get_loudnesses=audio.loudnesses,
  line_colour=line_colour,
  bg_colour=bg_colour,
  min_thresh=min_thresh,
  max_thresh=max_thresh,
  line_width=line_width,
  gain=gain,
  steepness=steepness,
  curviness=curviness,
  momentum=momentum,
  min_loud_thresh=min_loud_thresh)
line_w.geometry(c.geom)
ld.pack(fill="both", expand=True)

# Ensure variables are saved on exit
def close():
	conf.save(conf_filename, {
		'geom': line_w.geometry(),
		'line_colour': line_colour.get(),
	  'bg_colour': bg_colour.get(),
	  'min_thresh': min_thresh.get(),
	  'max_thresh': max_thresh.get(),
	  'line_width': line_width.get(),
	  'gain': gain.get(),
	  'steepness': steepness.get(),
	  'curviness': curviness.get(),
	  'momentum': momentum.get(),
	})
	line_w.destroy()
opts_w.protocol("WM_DELETE_WINDOW", close)
line_w.protocol("WM_DELETE_WINDOW", close)

# Wait until loop is cancelled
ld.main_loop()
