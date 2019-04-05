import pathlib
import xml.etree.ElementTree as ET

from common import PalletInfo, Probe

class PalletProberNative(Probe):

	def __init__(self, weight=10, desc='roll.xml files (native stacki)'):
		super().__init__(weight, desc)

	def probe(self, pallet_root):
		roll_files = list(pathlib.Path(pallet_root).glob('**/roll-*.xml'))

		if len(roll_files) != 1:
			return None

		docroot = ET.parse(roll_files[0]).getroot()
		name = docroot.attrib['name']
		info = docroot.find('info')
		version = info.attrib['version']
		release = info.attrib['release']
		arch = info.attrib['arch']
		distro_family = info.attrib['os']

		return PalletInfo(name, version, release, arch, distro_family)
