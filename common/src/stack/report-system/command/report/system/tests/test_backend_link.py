import pytest
import paramiko
import socket
from stack import api

@pytest.mark.parametrize('backend',
[host['host'] for host in  api.Call('list host', args=['a:backend'])]
)
class TestLinkUp:

	# See if the interfaces stacki configures are actually up on the hosts

		def test_link_status(self, backend):
			errors = []
			backend_ssh = paramiko.SSHClient()
			backend_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

			# Get all interfaces for this host
			interfaces = [
				host['interface'] for host in api.Call('list host interface ', args=['a:backend']) if host['host'] == backend
			]

			try:
				backend_ssh.connect(hostname=f'{backend}', timeout=5)

			except (paramiko.SSHException, socket.error):
				pytest.skip(f'Could not ssh into host {backend}')

			for link in interfaces:

				# Run ethtool on the interface
				stdin, stdout, stderr = backend_ssh.exec_command(f'ethtool {link}')
				interface_data = stdout.readlines()

				# Flag which is set to true if ethtool reports the link is up
				link_up = False

				for line in interface_data:
					if 'Link detected: yes' in line.rstrip():
						link_up = True

				if not link_up:
					errors.append(link)

			assert not errors, f'On host {backend} the following links were found not connected: {",".join(errors)}'
