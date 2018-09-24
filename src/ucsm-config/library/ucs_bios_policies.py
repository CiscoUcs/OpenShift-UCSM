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
        name=dict(type='str', required=True),
        descr=dict(type='str', required=False),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        reboot_on_update=dict(type='str', default='true', choices=['false', 'true', 'no', 'yes']),
        vp_energy_performance=dict(type='str', default='performance'),
        vp_power_technology=dict(type='str', default='performance'),
        vp_workload_configuration=dict(type='str', default='io-sensitive'),
        vp_processor_c3_report=dict(type='str', default='disabled'),
        vp_processor_c7_report=dict(type='str', default='disabled'),
        vp_processor_c6_report=dict(type='str', default='disabled'),
        vp_cpu_performance=dict(type='str', default='high-throughput'),
    )
    
    module = AnsibleModule(argument_spec,)
    ucs = UCSModule(module)
    err = False

    '''
    print("********Inputs start********")
    print("name=",module.params['name'])
    print("descr=",module.params['descr'])
    print("state=",module.params['state'])
    print("reboot_on_update=",module.params['reboot_on_update'])
    print("vp_energy_performance=",module.params['vp_energy_performance'])
    print("vp_power_technology=",module.params['vp_power_technology'])
    print("vp_workload_configuration=",module.params['vp_workload_configuration'])
    print("vp_processor_c3_report=",module.params['vp_processor_c3_report'])
    print("vp_processor_c7_report=",module.params['vp_processor_c7_report'])
    print("vp_processor_c6_report=",module.params['vp_processor_c6_report'])
    print("vp_cpu_performance=",module.params['vp_cpu_performance'])
    print("********Inputs end*********")
    '''
    
    
    # UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
    from ucsmsdk.mometa.bios.BiosVProfile import BiosVProfile
    from ucsmsdk.mometa.bios.BiosVfProcessorEnergyConfiguration import BiosVfProcessorEnergyConfiguration
    from ucsmsdk.mometa.bios.BiosVfWorkloadConfiguration import BiosVfWorkloadConfiguration
    from ucsmsdk.mometa.bios.BiosVfProcessorC3Report import BiosVfProcessorC3Report
    from ucsmsdk.mometa.bios.BiosVfProcessorC7Report import BiosVfProcessorC7Report
    from ucsmsdk.mometa.bios.BiosVfProcessorC6Report import BiosVfProcessorC6Report
    from ucsmsdk.mometa.bios.BiosVfCPUPerformance import BiosVfCPUPerformance

    changed = False
    try:
        mo_exists = False
        props_match = False
        dn_base = 'org-root'
        dn = dn_base+'/bios-prof-'+module.params['name']
        mo = ucs.login_handle.query_dn(dn)
        dn_bios_vf_processor_energy_configuration = dn+'/Processor-Energy-Configuration'
        dn_bios_vf_workload_configuration = dn+'/Workload-Configuration'
        dn_bios_vf_processor_c3_report = dn+'/Processor-C3-Report'
        dn_bios_vf_processor_c7_report = dn+'/Processor-C7-Report'
        dn_bios_vf_processor_c6_report = dn+'/Processor-C6-Report'
        dn_bios_vf_cpu_performance = dn+'/CPU-Performance'

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
                kwargs = dict(reboot_on_update=module.params['reboot_on_update'])
                if (mo.check_prop_match(**kwargs)):
                    props_match = True
            if not props_match:
                print("mo do not exists or props do not match")
                mo = BiosVProfile(
                        parent_mo_or_dn=dn_base,
                        name=module.params['name'],
                        descr=module.params['descr'],
                        reboot_on_update=module.params['reboot_on_update'],
                )
                ucs.login_handle.add_mo(mo, True)
                ucs.login_handle.commit()
                changed = True

            # check child-level mo BiosVfProcessorEnergyConfiguration props
            props_match_bios_vf_processor_energy_configuration = False
            mo_bios_vf_processor_energy_configuration = ucs.login_handle.query_dn(dn_bios_vf_processor_energy_configuration)

            kwargs_bios_vf_processor_energy_configuration = dict(vp_energy_performance=module.params['vp_energy_performance'])
            kwargs_bios_vf_processor_energy_configuration = dict(vp_power_technology=module.params['vp_power_technology'])
            if (mo_bios_vf_processor_energy_configuration.check_prop_match(**kwargs_bios_vf_processor_energy_configuration)):
                props_match_bios_vf_processor_energy_configuration = True
            if not props_match_bios_vf_processor_energy_configuration:
                mo_bios_vf_processor_energy_configuration =  BiosVfProcessorEnergyConfiguration(
                        parent_mo_or_dn=dn,
                        vp_energy_performance=module.params['vp_energy_performance'],
                        vp_power_technology=module.params['vp_power_technology'],
                )
                ucs.login_handle.add_mo(mo_bios_vf_processor_energy_configuration, True)
                ucs.login_handle.commit()
                changed = True

            # check child-level mo BiosVfWorkloadConfiguration props
            props_match_bios_vf_workload_configuration = False
            mo_bios_vf_workload_configuration = ucs.login_handle.query_dn(dn_bios_vf_workload_configuration)

            kwargs_bios_vf_workload_configuration = dict(vp_workload_configuration=module.params['vp_workload_configuration'])
            if (mo_bios_vf_workload_configuration.check_prop_match(**kwargs_bios_vf_workload_configuration)):
                props_match_bios_vf_workload_configuration = True
            if not props_match_bios_vf_workload_configuration:
                mo_bios_vf_workload_configuration =  BiosVfWorkloadConfiguration(
                        parent_mo_or_dn=dn,
                        vp_workload_configuration=module.params['vp_workload_configuration'],
                )
                ucs.login_handle.add_mo(mo_bios_vf_workload_configuration, True)
                ucs.login_handle.commit()
                changed = True

            # check child-level mo BiosVfProcessorC3Report props
            props_match_bios_vf_processor_c3_report = False
            mo_bios_vf_processor_c3_report = ucs.login_handle.query_dn(dn_bios_vf_processor_c3_report)

            kwargs_bios_vf_processor_c3_report = dict(vp_processor_c3_report=module.params['vp_processor_c3_report'])
            if (mo_bios_vf_processor_c3_report.check_prop_match(**kwargs_bios_vf_processor_c3_report)):
                props_match_bios_vf_processor_c3_report = True
            if not props_match_bios_vf_processor_c3_report:
                mo_bios_vf_processor_c3_report =  BiosVfProcessorC3Report(
                        parent_mo_or_dn=dn,
                        vp_processor_c3_report=module.params['vp_processor_c3_report'],
                )
                ucs.login_handle.add_mo(mo_bios_vf_processor_c3_report, True)
                ucs.login_handle.commit()
                changed = True

            # check child-level mo BiosVfProcessorC7Report props
            props_match_bios_vf_processor_c7_report = False
            mo_bios_vf_processor_c7_report = ucs.login_handle.query_dn(dn_bios_vf_processor_c7_report)

            kwargs_bios_vf_processor_c7_report = dict(vp_processor_c7_report=module.params['vp_processor_c7_report'])
            if (mo_bios_vf_processor_c7_report.check_prop_match(**kwargs_bios_vf_processor_c7_report)):
                props_match_bios_vf_processor_c7_report = True
            if not props_match_bios_vf_processor_c7_report:
                mo_bios_vf_processor_c7_report =  BiosVfProcessorC7Report(
                        parent_mo_or_dn=dn,
                        vp_processor_c7_report=module.params['vp_processor_c7_report'],
                )
                ucs.login_handle.add_mo(mo_bios_vf_processor_c7_report, True)
                ucs.login_handle.commit()
                changed = True

            # check child-level mo BiosVfProcessorC6Report props
            props_match_bios_vf_processor_c6_report = False
            mo_bios_vf_processor_c6_report = ucs.login_handle.query_dn(dn_bios_vf_processor_c6_report)

            kwargs_bios_vf_processor_c6_report = dict(vp_processor_c6_report=module.params['vp_processor_c6_report'])
            if (mo_bios_vf_processor_c6_report.check_prop_match(**kwargs_bios_vf_processor_c6_report)):
                props_match_bios_vf_processor_c6_report = True
            if not props_match_bios_vf_processor_c6_report:
                mo_bios_vf_processor_c6_report =  BiosVfProcessorC6Report(
                        parent_mo_or_dn=dn,
                        vp_processor_c6_report=module.params['vp_processor_c6_report'],
                )
                ucs.login_handle.add_mo(mo_bios_vf_processor_c6_report, True)
                ucs.login_handle.commit()
                changed = True

            # check child-level mo BiosVfCPUPerformance props
            props_match_bios_vf_cpu_performance = False
            mo_bios_vf_cpu_performance = ucs.login_handle.query_dn(dn_bios_vf_cpu_performance)

            kwargs_bios_vf_cpu_performance = dict(vp_cpu_performance=module.params['vp_cpu_performance'])
            if (mo_bios_vf_cpu_performance.check_prop_match(**kwargs_bios_vf_cpu_performance)):
                props_match_bios_vf_cpu_performance = True
            if not props_match_bios_vf_cpu_performance:
                mo_bios_vf_cpu_performance =  BiosVfCPUPerformance(
                        parent_mo_or_dn=dn,
                        vp_cpu_performance=module.params['vp_cpu_performance'],
                )
                ucs.login_handle.add_mo(mo_bios_vf_cpu_performance, True)
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