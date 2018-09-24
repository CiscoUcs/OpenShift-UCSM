#!/usr/bin/python
from __future__ import absolute_import, division, print_function


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ucs_local_disc_config_policy
short_description: Configures Local Disk Config Policies .
description:
- Configures Local Disk Config Policies for Cisco UCS 
options:
  mode:
    description:
    - Configures the mode for the local disc config policy.
    default: any-configuration
    required: no
  protect_config:
    description:
    - Configures the protect configuration for the local disc config policy.
    default: true
    required: no
  flex_flash_state:
    description:
    - Configures the flex flash state for the local disc config policy.
    default: disable
    required: no
  flex_flash_raid_reporting_state:
    description:
    - Configures the flex flash raid reporting state for the local disc config policy.
    default: disable
    required: no	
  descr:
    description:
    - Description for the host firmware package
    required: yes
  name:
    description:
    - Name for the local disc config policy
    required: yes
  state:
    description:
    - If present, will verify the local disc config policy is present and will create if needed.
    - If absent, will verify the local disc config policy is absent and will delete if needed.
    choices: [present, absent]
    default: present
requirements:
- ucsmsdk
author:
- Milind Dhar (midhar@cisco.com)
- CiscoUcs (@CiscoUcs)
version_added: '2.8'
'''

EXAMPLES = '''
- name: Test ucs_local_disc_config_policy  
  ucs_local_disc_config_policy:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: MyLocalDiscConfigPolicy
    descr: 'some description'
'''					
					
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),		
        descr=dict(type='str', required=False),
        mode=dict(type='str', default='any-configuration'),
        protect_config=dict(type='str', default='true', choices=['false', 'true', 'no', 'yes']),
        flex_flash_state=dict(type='str', default='disable', choices=['disable', 'enable']),
        flex_flash_raid_reporting_state=dict(type='str', default='disable', choices=['disable', 'enable']),		
    )
    
    module = AnsibleModule(argument_spec,)
    ucs = UCSModule(module)
    err = False
    '''
    print("********Inputs start********")
    print("name=",module.params['name'])
    print("state=",module.params['state'])
    print("descr=",module.params['descr'])
    print("mode=",module.params['mode'])
    print("protect_config=",module.params['protect_config'])
    print("flex_flash_state=",module.params['flex_flash_state'])
    print("flex_flash_raid_reporting_state=",module.params['flex_flash_raid_reporting_state'])
    print("********Inputs end********")
    '''

    # UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
    from ucsmsdk.mometa.storage.StorageLocalDiskConfigPolicy import StorageLocalDiskConfigPolicy
    changed = False
    try:
        mo_exists = False
        props_match = False
        # dn is org-root/local-disk-config-<name>
        #dn_base = 'org-root/local-disk-config-'
        dn_base = 'org-root'
        dn = dn_base+'/local-disk-config-'+module.params['name'] 
        mo = ucs.login_handle.query_dn(dn)
        #print(str(mo))	

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
                print("mo exists")
                # check top-level mo props 
                kwargs = dict(name=module.params['name'])
                kwargs = dict(descr=module.params['descr'])
                kwargs = dict(mode=module.params['mode'])
                kwargs = dict(protect_config=module.params['protect_config'])
                kwargs = dict(flex_flash_state=module.params['flex_flash_state'])
                kwargs = dict(flex_flash_raid_reporting_state=module.params['flex_flash_raid_reporting_state'])
                if (mo.check_prop_match(**kwargs)):
                    props_match = True
            if not props_match:
                print("mo do not exists or props do not match")
                mo = StorageLocalDiskConfigPolicy(
                        parent_mo_or_dn=dn_base,
                        name=module.params['name'],
                        descr=module.params['descr'],
                        mode=module.params['mode'],
                        protect_config=module.params['protect_config'],
                        flex_flash_state=module.params['flex_flash_state'],
                        flex_flash_raid_reporting_state=module.params['flex_flash_raid_reporting_state'],
                )
                ucs.login_handle.add_mo(mo, True)
                ucs.login_handle.commit()
                changed = True

        print("props_match=",props_match);
        #print(str(mo));

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    ucs.result['changed'] = changed

    if err:
        module.fail_json(**ucs.result)

    module.exit_json(**ucs.result)

    

if __name__ == '__main__':
    main()
