import pyaudio
import numpy as np

class Audio:
  '''
  Wraps a pyaudio stream with some default parameters, and the ability to return
  normalised values as a numpy array.
  '''
  def __init__(self, vfps=30):
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
    # data is read as bytes, with a max size of 2^15
    data = self.stream.read(self.chunk, exception_on_overflow=False)
    loudnesses = np.frombuffer(data, dtype='<i2')
    return self.normalise(loudnesses), self.rate

  def close():
    self.stream.stop_stream()
    self.stream.close()
    self.p.terminate()
