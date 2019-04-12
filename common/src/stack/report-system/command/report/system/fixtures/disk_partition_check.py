import pytest
import paramiko
import socket
import re
from collections import namedtuple
from itertools import groupby

# Takes in a hostname, returns the lsblk data in a dictionary of disks with a nested
# dictionary of partitions per disk which each has a named tuple of the name, mountpoint,
# disk label, file system type, and disk size. Returns an empty dictionary if the host
# cannot be ssh into or lsblk does not return any data
def get_partition_data(hostname):

	disks = {}
	partitions = {}

	backend_ssh = paramiko.SSHClient()
	backend_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

	# Skip the test if we can't ssh in
	try:
			backend_ssh.connect(hostname=f'{hostname}')

	except (paramiko.SSHException, socket.error):
		return {}

	# Get backend host partition informaiton using lsblk
	stdin, stdout, stderr = backend_ssh.exec_command('lsblk -r -n -o name,mountpoint,label,fstype,size')

	lsblk_data = stdout.readlines()

	# Turn each key value string pair into it's own entry into the list
	if lsblk_data:
		host_part_data = ' '.join(lsblk_data).replace('\n', '').split(' ')

	else:
		return {}

	# Convert to a list of named tuples for each partition consisting
	# of the partition name, label, and mountpoint
	for part in zip(

		# Iterate through each partition which is seperated every 5 elements
		# in the list of lsblk output
		host_part_data[::5], host_part_data[1::5], host_part_data[2::5],
		host_part_data[3::5], host_part_data[4::5]
	):
		part_name = part[0]
		part_tuple = namedtuple(part_name, ['name', 'mountpoint', 'label', 'fstype', 'size'])
		part_values = part_tuple(part_name, part[1], part[2], part[3], part[4])
		partitions[part_name] = part_values

	# Group partitions by disk name to create a nested dictionary
	# The key hierarchy is disk, disk partition, and then the partition values named tuple
	for disk, part_list in groupby(partitions, lambda part_name : re.search("[a-zA-Z]+", part_name).group(0)):
		disk_partitions = {}
		for part in part_list:
			disk_partitions[part] = partitions[part]

		# Remove disk name entry lsblk in output
		disk_partitions.pop(disk)
		disks[disk] = disk_partitions

	return disks


@pytest.fixture()
def verify_disk():
	def partition_match_expected(expected_partitions, hostname, check_all_disks=False):

		# Get the actual partition info from the host
		current_partition_data = get_partition_data(hostname)

		# If we could not get it, return empty dict
		if not current_partition_data:
			return {}

		matched_disks = {}

		# Go through each disk
		for disk, curr_partitions in current_partition_data.items():
			matched_partitions = {}

			# If this flag is set to true, we assume we have a one to one mapping of
			# expected disk partition scheme that is  expected to match the actual output
			# and therefore iterate as such
			if check_all_disks:
				try:
					partitions_to_check = expected_partitions[disk]

				# Return an empty dict if a disk doesn't exist in the expected output
				except KeyError:
					matched_disks[disk] = {}
					continue

			# Otherwise assume that there is only one disk configuration
			# and try to see if each disk matches it
			else:
				partitions_to_check = expected_partitions

			# Go through each partition on the disk
			for partition_num, attributes in partitions_to_check.items():

				partition_name = disk + partition_num

				try:
					curr_attr = curr_partitions[partition_name]

				# If we cannot find the partition, return a blank dict
				except KeyError:
					attribute_match = {}
					matched_partitions[partition_name] = attribute_match
					continue

				# Otherwise if all the attribute fields match, don't return that partition
				# but if some fields are not the same between the expected and current scheme,
				# return that partition and field
				attribute_match = {
					field: getattr(curr_partitions[partition_name], field)
					for field in attributes._fields if getattr(curr_partitions[partition_name], field)
					!= getattr(attributes, field)
				}

				if attribute_match:
					matched_partitions[partition_name] = attribute_match

			matched_disks[disk] = matched_partitions

		return matched_disks

	return partition_match_expected
