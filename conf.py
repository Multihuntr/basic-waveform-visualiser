import yaml

class dotdict(dict):
  '''dot.notation access to dictionary attributes'''
  __getattr__ = dict.get
  __setattr__ = dict.__setitem__
  __delattr__ = dict.__delitem__

def load(filename):
	with open(filename, 'r') as f:
		try:
			data = yaml.safe_load(f)
			return dotdict(data or {})
		except yaml.YAMLError as exc:
			print(exc)
			return dotdict({})

def save(filename, data):
	with open(filename, 'w') as f:
		try:
			yaml.dump(data, f)
		except yaml.YAMLError as exc:
			print(exc)

