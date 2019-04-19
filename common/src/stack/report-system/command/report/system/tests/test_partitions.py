import pytest
import math
from collections import namedtuple, defaultdict
from stack import api
from stack.commands.report.system.fixtures.disk_partition_check import verify_disk

@pytest.mark.parametrize('hostname',
list(set([host['host'] for host in api.Call('list host partition')]))
)
class TestStoragePartition:

# Test if the way stacki configured the disks is still how they are partitioned

	def test_storage_partition(self, hostname, verify_disk):

		# Get stacki storage config
		storage_config = api.Call(f'list host storage partition {hostname}')
		check_config = defaultdict(dict)
		partition_info = namedtuple('partition', ['name', 'mountpoint', 'label', 'fstype', 'size'])
		errors = []

		# Convert stacki storage data structure to one
		# pytest fixture can use
		for partition in storage_config:
			disk = partition['device']
			disk_num = str(partition['partid'])
			part_label = ''

			if partition['mountpoint'] is None:
				partition['mountpoint'] = ''

			if partition['fstype'] is None:
				partition['fstype'] = ''

			try:
				for option in partition['options'].split(' '):
					if '--label=' in option:
						part_label = option.split('--label=')[1]

			except (KeyError, IndexError):
				pass

			check_config[partition['device']][disk + disk_num] = partition_info(
					name = disk + disk_num, mountpoint = partition['mountpoint'],
					label = part_label, fstype = partition['fstype'], size = partition['size']
			)


		# Call fixture function to find partitions that don't match the config
		match_partitions = verify_disk(check_config, hostname, check_all_disks=True)

		# Output errors
		if match_partitions:
			for disk, partitions in match_partitions.items():
				if partitions:
					errors.append(f'On disk {disk}, the following partitions differ from their original configuration: ')

					for partition, attributes in partitions.items():
						errors.append(f'On partition {partition}: ')

						for attr, value in attributes.items():
							errors.append(f'{attr} found with value {value} but was configured with {getattr(check_config[disk][partition], attr)},')

		assert not errors, f'Host {hostname} found with partitioning mismatch from original config: {" ".join(errors)}'
