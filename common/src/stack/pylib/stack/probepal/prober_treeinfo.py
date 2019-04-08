import pathlib

from common import PalletInfo, Prober

class TreeinfoProber(Prober):
	'''
	This prober is intended to look for and parse a .treeinfo file which indicates a rhel 7+ or sles15 iso

	The contents of this file look like:

	[general]
	name = CentOS-7
	family = CentOS
	timestamp = 1504618609.47
	variant =
	version = 7
	packagedir =
	arch = x86_64

	[stage2]
	mainimage = LiveOS/squashfs.img

	[images-x86_64]
	kernel = images/pxeboot/vmlinuz
	initrd = images/pxeboot/initrd.img
	boot.iso = images/boot.iso

	[images-xen]
	kernel = images/pxeboot/vmlinuz
	initrd = images/pxeboot/initrd.img
	'''


	def __init__(self, weight=10, desc='treeinfo files (rhel-based, sles15)'):
		super().__init__(weight, desc)

	def probe(self, pallet_root):
		if not pathlib.Path(f'{pallet_root}/.treeinfo').exists():
			return None

		with open(f'{pallet_root}/.treeinfo', 'r') as fi:
			lines = fi.readlines()

		name, version, release, arch, distro_family = [None] * 5

		for line in lines:
			kv = line.split('=')
			if len(kv) != 2:
				continue

			key, value = kv[0].strip(), kv[1].strip()

			if key == 'family':
				if value == 'Red Hat Enterprise Linux':
					name = 'RHEL'
					distro_family = 'redhat'
				elif value.startswith('CentOS'):
					name = 'CentOS'
					distro_family = 'redhat'
				elif value.startswith('Oracle'):
					name = 'OLE'
					distro_family = 'redhat'
				elif value.startswith('Scientific'):
					name = 'SL'
					distro_family = 'redhat'
				elif value.startswith('SUSE Linux Enterprise'):
					name = 'SLES'
					distro_family = 'sles'
			elif key == 'version':
				version = value
			elif key == 'arch':
				arch = value

		release = distro_family + version
		if pathlib.Path(f'{pallet_root}/.discinfo').exists():
			with open(f'{pallet_root}/.discinfo', 'r') as fi:
				lines = fi.readlines()
				release = lines[1].strip()

		return PalletInfo(name, version, release, arch, distro_family)
