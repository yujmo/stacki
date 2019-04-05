import sys
from operator import attrgetter
import importlib
import pkgutil

from common import UnrecognizedPallet

# general:
# this package allows for fingerprinting a directory to determine if it contains a stacki pallet
# the design allows for the dynamic discovery of additional finderprinting probes,
# along with a means of weighting which probes are used first as well as catching partial matches
# probes can be added by creating a new python module whose name begins with `prober_` and which
# has a subclass of the Probe class.  See common.py for more detail. 


if __name__ == '__main__':
	# find and import all 'prober' modules in the directory
	plugins = {
		name: importlib.import_module(name)
		for finder, name, ispkg
		in pkgutil.iter_modules()
		if name.startswith('prober')
	}

	probes = []
	# within those modules, find and instantiate any PalletProber* classes
	for module in plugins.values():
		probes.extend(getattr(module, cls)() for cls in dir(module) if cls.startswith('PalletProber'))

	# sort the probes by weight
	# this lets us do things like check for rolls.xml inside foreign pallets,
	# or potentially insert a probe later which might false-positive ID something else
	probes = sorted(probes, key=attrgetter('weight'))

	debug = False
	if sys.argv[1] == '--debug':
		debug = True
		print('debug=True')
		del sys.argv[1]

	print_debug = print if debug else lambda *a, **k: None

	args = sys.argv[1:]
	for arg in args:
		print(f'====== probing {arg} ======')
		for probe in probes:
			# probes return None if it's a hard non-match
			# or raise UnrecognizedPallet if it's a partial match
			# in both cases, keep looking -- a later probe has a better chance to ID
			try:
				print_debug(f'==== checking with {probe} ====')
				pallet = probe.probe(arg)
				if pallet is not None:
					# success!
					print(pallet)
					break
			except UnrecognizedPallet as e:
				print_debug(e)
		else: #nobreak
			print('could not identify pallet')
