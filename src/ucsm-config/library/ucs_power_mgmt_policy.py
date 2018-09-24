#!/usr/bin/python
from __future__ import absolute_import, division, print_function


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ucs_power_mgmt_policy
short_description: Configures ucs global power management.
description:
- Configures ucs global power management
options:
  style:
    description:
    - configures the allocation method.
    choices: [manual-per-blade, intelligent-policy-driven]
    default: manual-per-blade
requirements:
- ucsmsdk
author:
- Milind Dhar (midhar@cisco.com)
- CiscoUcs (@CiscoUcs)
version_added: '2.8'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(
        style=dict(type='str', required=False, default='manual-per-blade', choices=['manual-per-blade', 'intelligent-policy-driven']),
    )
    
    module = AnsibleModule(argument_spec,)
    ucs = UCSModule(module)
    err = False 

    '''  
    print("********Inputs start********")
    print("style=",module.params['style'])
    print("********Inputs end*********")
    '''
    
    # UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
    from ucsmsdk.mometa.power.PowerMgmtPolicy import PowerMgmtPolicy
    changed = False
    try:
        props_match = False
        dn_base = 'org-root'
        dn = dn_base+'/pwr-mgmt-policy'
        mo = ucs.login_handle.query_dn(dn)
        #print(mo)
        kwargs = dict(style=module.params['style'])
        if (mo.check_prop_match(**kwargs)):
            props_match = True

        if not props_match:
            #print("mo props do not match")
            mo = PowerMgmtPolicy(
                    parent_mo_or_dn=dn_base,
                    style=module.params['style'],
            )
            ucs.login_handle.add_mo(mo, True)
            ucs.login_handle.commit()
            changed = True

    except Exception as e:
        print(Exception,e);
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    ucs.result['changed'] = changed

    if err:
        module.fail_json(**ucs.result)

    module.exit_json(**ucs.result)



if __name__ == '__main__':
    main()