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
module: ucs_vmedia_policy
short_description: Configures VMedia Policy on Cisco UCS Manager
description:
- Configures VMedia Policy on Cisco UCS Manager.
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
- name: Test 
  ucs_vmedia_policy:
    name: OCP
    description: OS Boot VMedia
    retry: yes
    mounts:
    - name: bootMedia
      description: something something
      device : cdd
      protocol: http
      remote_ip: 172.28.225.135
      image_name_variable: none
      file: service-profile-template
      path: /
      username: something
      password: something
      remap_on_eject: False
    - name: installMedia
      description: something something
      device : HDD
      protocol: http
      remote_ip: 172.28.225.135
      image_name_variable: service-profile-name
      path: /
      remap_on_eject: True
      
- name: Test
  ucs_vmedia_policy:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: OCP
    state: absent
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

import traceback
import logging

VMEDIA_MOUNT = "mounts"

def main():
    logging.basicConfig(level=logging.INFO)
    argument_spec = ucs_argument_spec
    argument_spec.update(
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        retry=dict(type='str', default='yes', choices=['yes','no']), 
        mounts=dict(type='list'), 
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        )
        
    ucs = UCSModule(module)

    err = False

    # UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
    from ucsmsdk.mometa.cimcvmedia.CimcvmediaMountConfigPolicy import CimcvmediaMountConfigPolicy
    from ucsmsdk.mometa.cimcvmedia.CimcvmediaConfigMountEntry import CimcvmediaConfigMountEntry

    changed = False
    try:
        mo_exists = False
        parent_props_match = False
        child_props_match = False
        # dn is org-root/mnt-cfg-policy-<name> 
        dn_base = 'org-root'
        dn = dn_base + '/mnt-cfg-policy-' + module.params['name']
        

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
            mount_entry_matches = dict()
            mount_entry_dict = dict()

            if mo_exists:
                # check top-level mo props
                kwargs = dict(name=module.params['name'])
                kwargs['descr'] = module.params['description']
                kwargs['retry_on_mount_fail'] = module.params['retry']
                                
                if (mo.check_prop_match(**kwargs)):
                    parent_props_match = True
                    logging.info("Parent Props Match")

            # check mount setting
            mount_entries = module.params.get(VMEDIA_MOUNT)
            if mount_entries:
                child_props_match = verify_mount_entries(mo, dn, mount_entries, mount_entry_dict, mount_entry_matches, ucs)
                logging.info("Child Props Match: %s", child_props_match)
                logging.debug(mount_entry_matches)
            else:
                child_props_match = True

            if not (parent_props_match and child_props_match):
                if not module.check_mode:

                    # remove if some entries are not required
                    if mo_exists:
                        check_and_remove_mount_entries(mo,mount_entry_matches,ucs)

                    # create if mo does not already exist
                    if not parent_props_match:
                        mo = CimcvmediaMountConfigPolicy(
                        parent_mo_or_dn=dn_base,
                        name=module.params['name'],
                        descr=module.params['description'],
                        retry_on_mount_fail=module.params['retry']
                        )
                        ucs.login_handle.add_mo(mo, True)
                    
                    for mount_entry_match in mount_entry_matches.keys():
                        if not mount_entry_matches[mount_entry_match]:
                            logging.info("Adding child dn: %s", mount_entry_match)
                            mount_entry = mount_entry_dict[mount_entry_match]
                            mo_child = CimcvmediaConfigMountEntry(
                                parent_mo_or_dn=mo,
                                mapping_name=mount_entry.get('name'),
                                description=mount_entry.get('description'),
                                device_type=mount_entry.get('device'),
                                mount_protocol=mount_entry.get('protocol'),
                                remote_ip_address=mount_entry.get('remote_ip'),
                                remote_host = mount_entry.get('remote_host'),
                                image_name_variable=mount_entry.get('image_name_variable'),
                                image_file_name = mount_entry.get('file'),
                                image_path=mount_entry.get('path'),
                                user_id = mount_entry.get('username'),
                                password = mount_entry.get('password'),
                                remap_on_eject = mount_entry.get('remap_on_eject'),
                                auth_option = mount_entry.get('auth_option')
                            )
                            ucs.login_handle.add_mo(mo_child, True)
                    ucs.login_handle.commit()
                    changed = True

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)
        traceback.print_exc()

    ucs.result['changed'] = changed
    if err:
        module.fail_json(**ucs.result)
    module.exit_json(**ucs.result)

def check_and_remove_mount_entries(mo, mount_entry_matches, ucs):
    
    mo_list = ucs.login_handle.query_children(in_mo=mo)

    for index, mo_mount_entry in enumerate(mo_list):
        match = mount_entry_matches.get(mo_mount_entry.dn)
        # if there is no entry for this dn, remove it
        if match is None:
            logging.info("Removing Mount Point Entry: %s", mo_mount_entry)
            ucs.login_handle.remove_mo( mo=mo_mount_entry)
            ucs.login_handle.commit()
                

def verify_mount_entries(mo, dn, mount_entries, mount_entry_dict, mount_entry_matches, ucs):
    
    child_props_match = True

    for index, mount_entry in enumerate(mount_entries):
        
        name = mount_entry.get('name')
        child_dn = dn + '/cfg-mnt-entry-' + name
        # put it into dictionary
        mount_entry_dict[child_dn] = mount_entry
        # check if it already exists

        mo_child = None
        if mo:
            mo_child = ucs.login_handle.query_dn(child_dn)
        
        if mo_child:
            kwargs = dict(mapping_name=name)
            kwargs['description'] = mount_entry.get('description')
            kwargs['device_type'] = mount_entry.get('device')
            kwargs['mount_protocol'] = mount_entry.get('protocol')
            kwargs['remote_ip_address'] = mount_entry.get('remote_ip')
            kwargs['remote_host'] = mount_entry.get('remote_host')
            kwargs['image_name_variable'] = mount_entry.get('image_name_variable')
            kwargs['image_file_name'] = mount_entry.get('file')
            kwargs['image_path'] = mount_entry.get('path')
            kwargs['user_id'] = mount_entry.get('username')
            kwargs['password'] = mount_entry.get('password')
            kwargs['remap_on_eject'] = mount_entry.get('remap_on_eject')
            kwargs['auth_option'] = mount_entry.get('auth_option')
            if (mo_child.check_prop_match(**kwargs)):
                mount_entry_matches[child_dn] = True
            else:
                logging.info("Child Props Doesn't Match for dn: %s", child_dn)
                logging.debug(mo_child)
                mount_entry_matches[child_dn] = False
                child_props_match = False
        else:
            mount_entry_matches[child_dn] = False
            child_props_match = False
        
        # make sure length of input mount points matches existing mount points 
    if child_props_match:
        mo_list = ucs.login_handle.query_children(in_mo=mo)
        child_props_match = len(mo_list) == len (mount_entry_matches)
    
    return child_props_match

if __name__ == '__main__':
    main()
