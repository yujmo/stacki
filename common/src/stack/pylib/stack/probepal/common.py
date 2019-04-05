class UnrecognizedPallet(Exception):
	pass

class PalletInfo:
	'''
	A basic class to hold the data about a pallet that stacki cares about
	# TODO could be a named tuple, maybe?
	'''
	def __init__(self, name=None, version=None, release=None, arch=None, distro_family=None):
		self.name = name
		self.version = version
		self.release = release
		self.arch = arch
		self.distro_family = distro_family
		if not self.is_complete():
			raise UnrecognizedPallet(f'{self}')

	def __str__(self):
		attrs = ' '.join(
			f'{attr}={getattr(self, attr)}'
			for attr in ('name', 'version', 'release', 'arch', 'distro_family')
		)
		return f'{self.__class__.__name__}: {attrs}'

	def is_complete(self):
		return all((self.name, self.version, self.release, self.arch, self.distro_family))

class Probe:
	'''
	Base probe class.  Subclasses must implement probe() and probably __init__()
	Lower weight probes will be attempted first.

	`probe()` must return None or a PalletInfo() object
	'''

	def __init__(self, weight=90, desc=''):
		self.weight = weight
		self.desc = desc

	def probe(self, pallet_root):
		return None

	def __str__(self):
		return f'{self.__class__.__name__} (supports {self.desc})'

	def __repr__(self):
		return f'{self.__class__.__name__}(weight={self.weight})'

