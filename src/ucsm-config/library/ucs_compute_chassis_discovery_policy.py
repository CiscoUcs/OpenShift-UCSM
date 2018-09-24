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
module: ucs_compute_chassis_discovery_policy
short_description: Configures Chassis Discovery Policy on Cisco UCS Manager
description:
- Configures Compute Chassis Discovery Policy on Cisco UCS Manager.
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
- name: Add Chassis Discovery Policy
  ucs_compute_chassis_discovery_policy:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: test
	action: '1-link'
	link_aggregation_pref: 'port-channel'
  	multicast_hw_hash: 'enabled'
- name: Reset Chassis Discovery Policy
  ucs_compute_chassis_discovery_policy:
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
		action=dict(type='str', default='1-link', choices=['1-link', '2-link', '4-link', '8-link', 'platform-max']),  
		multicast_hw_hash=dict(type='str', default='disabled', choices=['disabled','enabled']), 
		link_aggregation_pref=dict(type='str', default='none', choices=['none', 'port-channel']), 
	)

	module = AnsibleModule(
		argument_spec,
		supports_check_mode=True,
		)
		
	ucs = UCSModule(module)

	err = False

	# UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
	from ucsmsdk.mometa.compute.ComputeChassisDiscPolicy import ComputeChassisDiscPolicy

	changed = False
	try:
		mo_exists = False
		props_match = False
		# dn is org-root//compute-conn-policy-<name> for chassis connection policy
		dn_base = 'org-root'
		#dn = dn_base + '/compute-conn-policy-' + module.params['name']
		dn = dn_base + '/chassis-discovery'

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
				# check top-level mo props
				kwargs = dict(name=module.params['name'])
				kwargs['descr'] = module.params['description']
				kwargs['action'] = module.params['action']
				kwargs['link_aggregation_pref'] = module.params['link_aggregation_pref']
				kwargs['multicast_hw_hash'] = module.params['multicast_hw_hash']
				#kwargs[''] = module.params['']
				
				if (mo.check_prop_match(**kwargs)):
					props_match = True

			if not props_match:
				if not module.check_mode:
					# create if mo does not already exist
					mo = ComputeChassisDiscPolicy(
					parent_mo_or_dn=dn_base,
					name=module.params['name'],
					descr=module.params['description'],
					action=module.params['action'],
					multicast_hw_hash=module.params['multicast_hw_hash'],
					link_aggregation_pref=module.params['link_aggregation_pref'],
					)

					ucs.login_handle.add_mo(mo, True)
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
