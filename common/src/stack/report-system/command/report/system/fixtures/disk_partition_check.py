import pytest
import paramiko
import socket
import re
from collections import namedtuple
from itertools import groupby

# Takes in a hostname and disk attributes, returns the lsblk data in a dictionary of disks with a nested
# dictionary of partitions per disk which each has a named tuple of the name, mountpoint,
# disk label, file system type, and disk size. Returns an empty dictionary if the host
# cannot be ssh into or lsblk does not return any data
def get_partition_data(hostname, attributes):

	disks = {}

	backend_ssh = paramiko.SSHClient()
	backend_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	try:
		backend_ssh.connect(hostname=f'{hostname}')

	except (paramiko.SSHException, socket.error):
		return {}

	# Get backend host partition informaiton using lsblk
	stdin, stdout, stderr = backend_ssh.exec_command(f'lsblk -r -n -o {",".join(attributes)}')

	lsblk_data = stdout.readlines()

	partition_attributes = namedtuple("partition", attributes)

	# For each line in the lsblk output, make it into a tuple
	# Then each partition into a dictionary keyed by it's disk
	if lsblk_data:
		for line in lsblk_data:
			part_values = partition_attributes(*line.rstrip().split(' '))

			# Get the name of the disk by taking the partition name without it's
			# partition number
			disk = ''.join(filter(lambda x: not x.isdigit(), part_values.name))

			if disk == part_values.name:
				continue

			disks.setdefault(disk, {})[part_values.name] = part_values
	else:
		return {}

	return disks


@pytest.fixture
def verify_disk():
	def partition_match_expected(expected_partitions, hostname, check_all_disks=False):

		lsblk_col = ['name', 'mountpoint', 'label', 'fstype', 'size']

		# Get the actual partition info from the host
		part_data = get_partition_data(hostname, lsblk_col)

		# If we could not get it, return empty dict
		if not part_data:
			return {}

		matched_disks = {}

		# Go through each disk
		for disk, partitions in part_data.items():
			matched_partitions = {}

			# Go through each partition that we expect for the disk
			# and see if it is actually there
			if check_all_disks:
				for partition, attributes in partitions.items():
					try:
						check_part = expected_partitions[disk][partition]

						attribute_not_match = {
							field: getattr(attributes, field)
							for field in check_part._fields if getattr(attributes, field)
							!= getattr(check_part, field)
						}

						if attribute_not_match:
							matched_partitions[partition] = attribute_not_match

						else:
							continue

					except KeyError:
						matched_partitions[partition] = {}

			else:
				for partition_num, attributes in expected_partitions.items():

					# If there is a wildcard for the partition, check to see if there
					# is any partition on the disk that matches the attributes
					if partition_num == '*':
						attribute_match = False
						for partition, curr_attr in partitions.items():
							if(
								all([
										getattr(curr_attr, field) == getattr(attributes, field)
										for field in attributes._fields
									]
								)
							):
								attribute_match = True

						if attribute_match:
							continue
						else:
							partition_info = {field: getattr(attributes, field) for field in attributes._fields}
							matched_partitions[disk + partition_num] = partition_info
							continue

					# Otherwise if all the attribute fields match, don't return that partition
					# but if some fields are not the same between the expected and current scheme,
					# return that partition and field
					try:
						check_part = partitions[disk + partition_num]

						attribute_not_match = {
							field: getattr(check_part, field)
							for field in attributes._fields if getattr(check_part, field)
							!= getattr(attributes, field)
						}

						if attribute_not_match:
							matched_partitions[disk + partition_num] = attribute_not_match

						else:
							continue

					except KeyError:
						matched_partitions[disk + partition_num] = {}

			matched_disks[disk] = matched_partitions

		return matched_disks

	return partition_match_expected
