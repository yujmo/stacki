import pathlib

from common import PalletInfo, Probe

class PalletProberSles11_12(Probe):

	def __init__(self, weight=30, desc='sles 11-12'):
		super().__init__(weight, desc)

	def probe(self, pallet_root):
		if not pathlib.Path(f'{pallet_root}/content').exists():
			return None

		with open(f'{pallet_root}/content', 'r') as fi:
			lines = fi.readlines()

		name = None
		version = None
		release = None
		arch = 'x86_64'
		distro_family = 'sles'

		for line in lines:
			l = line.split(None, 1)
			if len(l) > 1:
				key = l[0].strip()
				value = l[1].strip()

				# SLES11 ISO's
				if key == 'NAME':
					if value == 'SUSE_SLES':
						name = 'SLES'
					elif value == 'sle-sdk':
						name = 'SLE-SDK'
				elif key == 'VERSION':
					version = value
				elif key == 'RELEASE':
					release = value
				elif key == 'BASEARCHS':
					arch = value

				# SLES12 ISO's
				elif key == 'DISTRO':
					a = value.split(',')
					v = a[0].split(':')

					if v[3] == 'sles':
						name = 'SLES'
					elif v[3] == 'sle-sdk':
						name = 'SLE-SDK'
					elif v[3] == 'ses':
						name = 'SUSE-Enterprise-Storage'

					if name:
						version = v[4]
						if len(v) > 5:
							release = v[5]
						break

		return PalletInfo(name, version, release, arch, distro_family)
