#!/usr/bin/python
# -*- coding: utf-8 -*-

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = r'''
---
module: ucs_fabric_interconnect_ports
short_description: Configures Fabric Interconnect Ports on Cisco UCS Manager
description:
- Configures Fabric Interconnect Ports on Cisco UCS Manager
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify Chassis Discovery Policy is present and will create if needed.
    - If C(absent), will verify Chassis Discovery Policy is absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - The name assigned to the Chassis Discovery Policy.
    - The Chassis discovery Policy name is case sensitive.
    - This name can be between 1 and 16 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    - You cannot change this name after the Chassis Discovery Policy is created.
    required: yes
  description:
    description:
    - A description of the Chassis Discovery Policy.
    - Cisco recommends including information about where and when to use the policy.
    - Enter up to 256 characters.
    - "You can use any characters or spaces except the following:"
    - "` (accent mark), \ (backslash), ^ (carat), \" (double quote), = (equal sign), > (greater than), < (less than), or ' (single quote)."
    aliases: [ descr ]
  
requirements:
- ucsmsdk
author:
- Surendra Ramarao (@CRSurendra)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Add fabric interconnect port configs
  ucs_fabric_interconnect_ports:
    hostname: 172.16.143.150
    username: admin
    password: password
    - name: "test"
  	  id: "A"
  	  ether_ports_list:
  	  - name: "Port 1"
    	port_id: "1"
    	slot_id: "1"
    	port_type: "network"
  	  - name: "Port 2"
    	port_id: "2"
    	slot_id: "1"
    	port_type: "server"
      - name: "Port 9"
    	port_id: "9"
    	slot_id: "1"
    	port_type: "unconfigured"
- name: Reset Fabric Interconnect Port Configs
  ucs_fabric_interconnect_ports:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: test
    state: absent
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec


def main():
	argument_spec = ucs_argument_spec
	argument_spec.update(
		name=dict(type='str', required=True),
		description=dict(type='str', default=''),
		state=dict(type='str', default='present', choices=['present', 'absent']),
		id=dict(type='str', default='NONE', choices=['A', 'B', 'NONE']),  
		ether_ports_list=dict(type='list'),
		fc_ports_list=dict(type='list'),
	)

	module = AnsibleModule(
		argument_spec,
		supports_check_mode=True,
		)
		
	ucs = UCSModule(module)

	err = False

	# UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
	from ucsmsdk.mometa.fabric.FabricDceSwSrv import FabricDceSwSrv
	from ucsmsdk.mometa.fabric.FabricDceSwSrvEp import FabricDceSwSrvEp
	from ucsmsdk.mometa.fabric.FabricEthLan import FabricEthLan
	from ucsmsdk.mometa.fabric.FabricEthLanEp import FabricEthLanEp
	
	ROLE_SERVER = 'server'
	ROLE_NETWORK = 'network'
	ROLE_UNCONFIGURED = 'unconfigured'
	ROLE_UNKNOWN = 'unknown'
	
	
	changed = False
	try:
		mo_exists = False
		props_match = False
		# dn is fabric/server/sw-<id>
		dn_base = 'sys'
		dn = dn_base + '/switch-' + module.params['id']
		dn_fc = dn + '/slot-1'+ '/switch-fc'
		dn_eth = dn + '/slot-1'+ '/switch-ether'
		dn_server_base = 'fabric/server'
		dn_network_base = 'fabric/lan'
		
		mo = ucs.login_handle.query_dn(dn)
		if mo:
			mo_exists = True

		if module.params['state'] == 'absent':
			# mo must exist but all properties do not have to match
			if mo_exists:
				if not module.check_mode:
					ucs.login_handle.remove_mo(mo)
					ucs.login_handle.commit()
				changed = True
		else:
			if mo_exists:
				# verify port settings
				if module.params.get('ether_ports_list'):
					ether_props_match = []
					props_match = True
					for index, ePort in enumerate(module.params['ether_ports_list']):
						ether_props_match.append(False)
						child_dn = dn_eth + '/port-' + ePort['port_id']
						mo_1 = ucs.login_handle.query_dn(child_dn)
						if mo_1:
							if ePort['port_type'] == ROLE_SERVER:
								if mo_1.if_role == ROLE_SERVER:
									ether_props_match[index] = True
								else:
									props_match = False
							elif ePort['port_type'] == ROLE_NETWORK:
								if mo_1.if_role == ROLE_NETWORK:
									ether_props_match[index] = True
								else:
									props_match = False
							elif ePort['port_type'] == ROLE_UNCONFIGURED:
								if mo_1.if_role == ROLE_UNKNOWN:
									ether_props_match[index] = True
								else:
									props_match = False
								
			if not props_match:
				if not module.check_mode:
					for index, ePort in enumerate(module.params['ether_ports_list']):
						if not ether_props_match[index]:
							if ePort['port_type'] == ROLE_SERVER:
								dn_server = dn_server_base + '/sw-' + module.params['id']
								mo_port = FabricDceSwSrvEp(
											parent_mo_or_dn=dn_server,
											slot_id=ePort['slot_id'],
											port_id=ePort['port_id']
										)
								ucs.login_handle.add_mo(mo_port, True)
								ucs.login_handle.commit()
								changed = True
							elif ePort['port_type'] == ROLE_NETWORK:
								dn_network = dn_network_base + '/' + module.params['id']
								mo_port = FabricEthLanEp(
											parent_mo_or_dn=dn_network,
											slot_id=ePort['slot_id'],
											port_id=ePort['port_id']
										)
								ucs.login_handle.add_mo(mo_port, True)
							elif ePort['port_type'] == ROLE_UNCONFIGURED:
								child_dn = dn_eth + '/port-' + ePort['port_id']
								mo_1 = ucs.login_handle.query_dn(child_dn)
								if mo_1:
									dn_to_remove = mo_1.ep_dn
									mo_to_remove = ucs.login_handle.query_dn(dn_to_remove)
									if mo_to_remove:
										ucs.login_handle.remove_mo(mo_to_remove)
							ucs.login_handle.commit()
							changed = True	

					
				

	except Exception as e:
		err = True
		ucs.result['msg'] = "setup error: %s " % str(e)

	ucs.result['changed'] = changed
	if err:
		module.fail_json(**ucs.result)
	module.exit_json(**ucs.result)


if __name__ == '__main__':
    main()
