#!/usr/bin/python
#!/usr/bin/python
from __future__ import absolute_import, division, print_function


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: ucs_fabric_eth_lac_pc
short_description: Configures Fabric Port Channel.
description:
- Configures Fabric Port Channel for Cisco UCS 
options:
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
  port_id:
    description:
    - Port id.
    required: yes
  switch_id:
    description:
    - Switch id.
    required: yes
  lacp_policy_name:
    description:
    - LACP policy name.
    default: default
    required: no
  flow_ctrl_policy:
    description:
    - Flow control policy.
    default: default
    required: no
  admin_speed:
    description:
    - Sets the admin speed.
    default: 10gbps
    choices: ['1gbps','10gbps','40gbps']
    required: no
  ports:
    description:
    - List of ports to be added to the port channel.
      example [{"slot_id":"1","port_id":"9"},{"slot_id":"1","port_id":"10"}]
      any ports not present in the list will if deleted if present in the port channel
    default: []
    required: no
requirements:
- ucsmsdk
author:
- Milind Dhar (midhar@cisco.com)
- CiscoUcs (@CiscoUcs)
version_added: '2.8'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec
from ucsmsdk.mometa.fabric.FabricEthLanPcEp import FabricEthLanPcEp

def main():
    argument_spec = ucs_argument_spec
    argument_spec.update(
        name=dict(type='str', required=True),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        switch_id=dict(type='str', required=True),
        port_id=dict(type='str', required=True),
        descr=dict(type='str', required=False),
        flow_ctrl_policy=dict(type='str', default='default'),
        lacp_policy_name=dict(type='str', default='default'),
        admin_speed=dict(type='str', default='10gbps', choices=['1gbps','10gbps','40gbps']),
        ports=dict(type='list', default=[]),
    )
    
    module = AnsibleModule(argument_spec,)
    ucs = UCSModule(module)
    err = False
    ''' 
    print("********Inputs start********")
    print("name=",module.params['name'])
    print("state=",module.params['state'])
    print("switch_id=",module.params['switch_id'])
    print("port_id=",module.params['port_id'])
    print("descr=",module.params['descr'])
    print("flow_ctrl_policy=",module.params['flow_ctrl_policy'])
    print("lacp_policy_name=",module.params['lacp_policy_name'])
    print("admin_speed=",module.params['admin_speed'])
    print("ports=",module.params['ports'])
    print("********Inputs end********") '''

    
    # UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
    from ucsmsdk.mometa.fabric.FabricEthLanPc import FabricEthLanPc

    
    changed = False

    try:
        mo_exists = False
        props_match = False
        #fabric/lan/A/pc-2
        dn_base = 'fabric/lan'+'/'+module.params['switch_id'];
        dn = dn_base+'/pc-'+module.params['port_id'] 
        mo = ucs.login_handle.query_dn(dn)
        #print(mo)

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
                #print("mo exists")
                # check top-level mo props 
                kwargs = dict(name=module.params['name'])
                kwargs = dict(descr=module.params['descr'])
                kwargs = dict(switch_id=module.params['switch_id'])
                kwargs = dict(port_id=module.params['port_id'])
                kwargs = dict(flow_ctrl_policy=module.params['flow_ctrl_policy'])
                kwargs = dict(lacp_policy_name=module.params['lacp_policy_name'])
                kwargs = dict(admin_speed=module.params['admin_speed'])
                if (mo.check_prop_match(**kwargs)):
                    props_match = True
                if((mo.name != module.params['name']) or (mo.descr != module.params['descr'])):
                    props_match = False
                #print('props_match=',props_match)
            if not props_match:
                #print("mo do not exists or props do not match")
                
                mo = FabricEthLanPc(
                        parent_mo_or_dn=dn_base,
                        name=module.params['name'],
                        #switch_id=module.params['switch_id'], not a read write field
                        descr=module.params['descr'],
                        port_id=module.params['port_id'],
                        flow_ctrl_policy=module.params['flow_ctrl_policy'],
                        lacp_policy_name=module.params['lacp_policy_name'],
                        admin_speed=module.params['admin_speed'],
                )
                
                ucs.login_handle.add_mo(mo, True)
                ucs.login_handle.commit()
                changed = True


            mo_list = ucs.login_handle.query_children(in_mo=mo, class_id="FabricEthLanPcEp")
            for port in module.params['ports']:
                if not portExists(port,mo_list):
                    createFabricEthLanPcEp(mo.dn,port["slot_id"],port["port_id"],ucs)
                    changed = True

            for port in mo_list:
                if deletePort(port,module.params['ports']):
                    ucs.login_handle.remove_mo(port)
                    ucs.login_handle.commit()
                    changed = True

    except Exception as e:
        err = True
        ucs.result['msg'] = "setup error: %s " % str(e)

    ucs.result['changed'] = changed

    if err:
        module.fail_json(**ucs.result)

    module.exit_json(**ucs.result)

def deletePort(port,ports):
    deletePort = True;

    for child in ports:

        if((child['port_id'] == port.port_id) and (child['slot_id'] == port.slot_id)):
            deletePort = False 
    
    return deletePort;

def portExists(port,mo_list):
    portExists = False;
    for child in mo_list:
        if((child.port_id == port["port_id"]) and (child.slot_id == port["slot_id"])):
            portExists=True
            break
    return portExists
    
def createFabricEthLanPcEp(parent_dn,s_id,p_id,ucs):

    child_mo = FabricEthLanPcEp(
            parent_mo_or_dn=parent_dn,
            slot_id=s_id,
            port_id=p_id,
    )
    ucs.login_handle.add_mo(child_mo, True)
    ucs.login_handle.commit()


if __name__ == '__main__':
    main()