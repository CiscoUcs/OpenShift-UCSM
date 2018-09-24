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
module: ucs_boot_policy
short_description: Configures Server Boot Policy on Cisco UCS Manager
description:
- Configures Server Boot Policy on Cisco UCS Manager
- Examples can be used with the UCS Platform Emulator U(https://communities.cisco.com/ucspe).
extends_documentation_fragment: ucs
options:
  state:
    description:
    - If C(present), will verify Boot Policy is present and will create if needed.
    - If C(absent), will verify Boot Policy is absent and will delete if needed.
    choices: [present, absent]
    default: present
  name:
    description:
    - The name assigned to the Boot Policy.
    - The Boot Policy name is case sensitive.
    - This name can be between 1 and 16 alphanumeric characters.
    - "You cannot use spaces or any special characters other than - (hyphen), \"_\" (underscore), : (colon), and . (period)."
    - You cannot change this name after the Boot Policy is created.
    required: yes
  description:
    description:
    - A description of the Boot Policy.
    - Cisco recommends including information about where and when to use the policy.
    - Enter up to 256 characters.
    - "You can use any characters or spaces except the following:"
    - "` (accent mark), \ (backslash), ^ (carat), \" (double quote), = (equal sign), > (greater than), < (less than), or ' (single quote)."
    aliases: [ descr ]
  boot_mode:
    description:
    - legacy, uefi
    - "single-server-single-sioc - The data path is configured through one SIOC when the chassis has single server and single SIOC or dual server and dual SIOCs."
    - "single-server-dual-sioc - When enabled, you can configure the data path through both the primary and auxiliary SIOCs when the chassis has single server and dual SIOCs."
    default: 'single-server-single-sioc'
requirements:
- ucsmsdk
author:
- Surendra Ramarao (@CRSurendra)
- CiscoUcs (@CiscoUcs)
version_added: '2.5'
'''

EXAMPLES = r'''
- name: Add Boot Policy
  ucs_boot_policy:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: first_boot_policy
    boot_mode: 'legecy'
    enforce_vnic_name: 'yes'
    reboot_on_update: 'no'
    boot_order:
        - order: 1
          type: local_disk
        - order: 2
          type: virtual_media
- name: Add another Boot Policy
  ucs_boot_policy:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: 'second boot policy'
    boot_mode: 'uefi'
    boot_security: "no"
    enforce_vnic_name: 'yes'
    reboot_on_update: 'no'
    boot_order:
        - order: 1
          type: local_lun
          params:
            - lun_image:
              type: primary
              lun_name: test
            - lun_image:
              type: secondary
              lun_name: test1
        - order: 2
          type: virtual_media
- name: Remove boot policy
  ucs_boot_policy:
    hostname: 172.16.143.150
    username: admin
    password: password
    name: first_boot_policy
    state: absent
'''

RETURN = r'''
#
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.remote_management.ucs import UCSModule, ucs_argument_spec
import traceback
import logging

BOOT_SECURITY_DN= 'boot-security'
STORAGE_DN = 'storage'
LOCAL_STORAGE_DN = 'local-storage'
LOCAL_DISK_DN= 'storage/local-storage/local-any'
LOCAL_LUN_DN = "storage/local-storage/local-hdd"
VIRTUAL_MEDIA_DN= 'read-only-vm'
CIMC_MEDIA_DVD_DN = 'read-only-remote-cimc-vm'
CIMC_MEDIA_HDD_DN = 'read-write-remote-cimc-vm'

ACCESS_READ_ONLY = 'read-only'
ACCESS_READ_ONLY_REMOTE_CIMC = 'read-only-remote-cimc'
ACCESS_READ_WRITE_REMOTE_CIMC = 'read-write-remote-cimc'

PARAM_BOOT_MODE = 'boot_mode'
PARAM_BOOT_SECURITY = 'boot_security'
BOOT_MODE_UEFI='uefi'
BOOT_ORDER = "boot_order"


def main():
    logging.basicConfig(level=logging.INFO)
    argument_spec = ucs_argument_spec
    argument_spec.update(
        name=dict(type='str', required=True),
        description=dict(type='str', default=''),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        boot_mode=dict(type='str', default='legacy', choices=['legacy', 'uefi']),
        enforce_vnic_name=dict(type='str', default='yes', choices=['yes','no']),
        reboot_on_update=dict(type='str', default='no', choices=['yes', 'no']),
        boot_security=dict(type='str', default='no', choices=['yes','no']),
        boot_order=dict(type='list'),
    )

    module = AnsibleModule(
        argument_spec,
        supports_check_mode=True,
        )
        
    ucs = UCSModule(module)

    err = False

    # UCSModule creation above verifies ucsmsdk is present and exits on failure, so additional imports are done below.
    from ucsmsdk.mometa.lsboot.LsbootBootSecurity import LsbootBootSecurity
    from ucsmsdk.mometa.lsboot.LsbootDefaultLocalImage import LsbootDefaultLocalImage
    # from ucsmsdk.mometa.lsboot.LsbootDef import LsbootDef
    # from ucsmsdk.mometa.lsboot.LsbootEFIShell import LsbootEFIShell
    # from ucsmsdk.mometa.lsboot.LsbootEmbeddedLocalDiskImagePath import LsbootEmbeddedLocalDiskImagePath
    # from ucsmsdk.mometa.lsboot.LsbootEmbeddedLocalDiskImage import LsbootEmbeddedLocalDiskImage
    # from ucsmsdk.mometa.lsboot.LsbootEmbeddedLocalLunImage import LsbootEmbeddedLocalLunImage
    # from ucsmsdk.mometa.lsboot.LsbootIScsiImagePath import LsbootIScsiImagePath
    # from ucsmsdk.mometa.lsboot.LsbootIScsi import LsbootIScsi
    # from ucsmsdk.mometa.lsboot.LsbootLanImagePath import LsbootLanImagePath
    # from ucsmsdk.mometa.lsboot.LsbootLan import LsbootLan
    # from ucsmsdk.mometa.lsboot.LsbootLocalDiskImagePath import LsbootLocalDiskImagePath
    # from ucsmsdk.mometa.lsboot.LsbootLocalDiskImage import LsbootLocalDiskImage
    from ucsmsdk.mometa.lsboot.LsbootLocalHddImage import LsbootLocalHddImage
        
    # from ucsmsdk.mometa.lsboot.LsbootNvmeDiskSsd import LsbootNvmeDiskSsd
    # from ucsmsdk.mometa.lsboot.LsbootNvmePciSsd import LsbootNvmePciSsd
    # from ucsmsdk.mometa.lsboot.LsbootNvme import LsbootNvme
    from ucsmsdk.mometa.lsboot.LsbootPolicy import LsbootPolicy
    # from ucsmsdk.mometa.lsboot.LsbootSanCatSanImagePath import LsbootSanCatSanImagePath
    # from ucsmsdk.mometa.lsboot.LsbootSanCatSanImage import LsbootSanCatSanImage
    # from ucsmsdk.mometa.lsboot.LsbootSanImagePath import LsbootSanImagePath
    # from ucsmsdk.mometa.lsboot.LsbootSanImage import LsbootSanImage
    # from ucsmsdk.mometa.lsboot.LsbootSan import LsbootSan
    
    # from ucsmsdk.mometa.lsboot.LsbootUEFIBootParam import LsbootUEFIBootParam
    # from ucsmsdk.mometa.lsboot.LsbootUsbExternalImage import LsbootUsbExternalImage
    # from ucsmsdk.mometa.lsboot.LsbootUsbFlashStorageImage import LsbootUsbFlashStorageImage
    # from ucsmsdk.mometa.lsboot.LsbootUsbInternalImage import LsbootUsbInternalImage
    from ucsmsdk.mometa.lsboot.LsbootVirtualMedia import LsbootVirtualMedia
    
      
    changed = False
    try:
        mo_exists = False
        parent_props_match = False
        child_props_match = True
        dn_base = 'org-root'
        dn = dn_base + '/boot-policy-' + module.params['name']
                
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
            boot_security_policy_enabled = False
            if module.params[PARAM_BOOT_SECURITY] == 'yes' and module.params[PARAM_BOOT_MODE] == BOOT_MODE_UEFI :
                    boot_security_policy_enabled = True
            boot_order_tree = build_boot_order_tree(dn, module.params[BOOT_ORDER], boot_security_policy_enabled)
            boot_order_matches = dict()

            if mo_exists:
                # check top-level mo props
                kwargs = dict(name=module.params['name'])
                kwargs['descr'] = module.params['description']
                kwargs[PARAM_BOOT_MODE] = module.params[PARAM_BOOT_MODE]
                kwargs['enforce_vnic_name'] = module.params['enforce_vnic_name']
                kwargs['reboot_on_update'] = module.params['reboot_on_update']
                                
                if (mo.check_prop_match(**kwargs)):
                    parent_props_match = True
                    logging.info("parent props match: %s", parent_props_match)
                
                                                            
                # verify boot order settings
                if module.params.get('boot_order'):
                    child_props_match = verify_boot_order_settings(mo, dn, boot_security_policy_enabled, boot_order_matches, boot_order_tree, ucs)

            if not (parent_props_match and child_props_match) :
                if not module.check_mode:
                    # if some boot order entries need to be removed remove them first
                    check_and_remove_boot_order_entries(mo_exists, child_props_match, boot_order_matches, boot_order_tree, ucs)


                    if not parent_props_match:
                        mo = LsbootPolicy(
                            parent_mo_or_dn = dn_base,
                            name = module.params['name'],
                            descr = module.params['description'],
                            boot_mode = module.params['boot_mode'],
                            enforce_vnic_name = module.params['enforce_vnic_name'],
                            reboot_on_update = module.params['reboot_on_update']
                        )
                        ucs.login_handle.add_mo(mo, True)
                   
                                    
                    for boot_order_dn in boot_order_tree.keys():
                        if not (boot_order_matches.get(boot_order_dn) and boot_order_matches[boot_order_dn]):
                            new_order = boot_order_tree.get(boot_order_dn)
                            # boot security
                            if boot_order_dn == get_dn_path(dn, BOOT_SECURITY_DN):
                                # secure_boot='yes' if boot_security_policy_enabled == BOOT_SECURITY_YES else 'no'
                                # print("secure_boot", secure_boot)
                                mo_bsec = LsbootBootSecurity(
                                    parent_mo_or_dn=dn,
                                    secure_boot='yes' if boot_security_policy_enabled else 'no'
                                )
                                ucs.login_handle.add_mo(mo_bsec, True)
                            # local disk
                            elif boot_order_dn == get_dn_path(dn, LOCAL_DISK_DN):
                                logging.info("dn: %s order: %s", boot_order_dn, new_order)
                                mo_blocal_storage = create_local_storage(dn, new_order, ucs)
                                mo_blocal_image = LsbootDefaultLocalImage(
                                    parent_mo_or_dn=mo_blocal_storage,
                                    order=new_order
                                )
                                ucs.login_handle.add_mo(mo_blocal_image, True)
                            # local lun
                            elif boot_order_dn == get_dn_path(dn,LOCAL_LUN_DN):
                                logging.info("dn: %s order: %s", boot_order_dn, new_order)
                                mo_blocal_storage = create_local_storage(dn, new_order, ucs)
                                mo_blocal_lun = LsbootLocalHddImage(
                                    parent_mo_or_dn=mo_blocal_storage,
                                    order=new_order
                                )
                                ucs.login_handle.add_mo(mo_blocal_lun, True)
                                lun_images = get_params(module.params[BOOT_ORDER], LOCAL_LUN)
                                logging.info("dn: %s lun_image: %s", boot_order_dn, lun_images)
                                add_lun_local_image_path(mo_blocal_lun, lun_images, ucs)
                            # local CD/DVD    
                            elif boot_order_dn == get_dn_path(dn, VIRTUAL_MEDIA_DN):
                               logging.info("dn: %s order: %s", boot_order_dn, new_order)
                               mo_bvmedia = LsbootVirtualMedia(
                                   parent_mo_or_dn=dn,
                                   order=new_order,
                                   access=ACCESS_READ_ONLY
                               )
                               ucs.login_handle.add_mo(mo_bvmedia, True)
                            # cimc CD/DVD    
                            elif boot_order_dn == get_dn_path(dn, CIMC_MEDIA_DVD_DN):
                               logging.info("dn: %s order: %s", boot_order_dn, new_order)
                               mo_boot_cimc_vmedia_dvd = LsbootVirtualMedia(
                                   parent_mo_or_dn=dn,
                                   order=new_order,
                                   access=ACCESS_READ_ONLY_REMOTE_CIMC
                               )
                               ucs.login_handle.add_mo(mo_boot_cimc_vmedia_dvd, True)
                            # cimc HDD    
                            elif boot_order_dn == get_dn_path(dn, CIMC_MEDIA_HDD_DN):
                               logging.info("dn: %s order: %s", boot_order_dn, new_order)
                               mo_boot_cimc_vmedia_hdd = LsbootVirtualMedia(
                                   parent_mo_or_dn=dn,
                                   order=new_order,
                                   access=ACCESS_READ_WRITE_REMOTE_CIMC
                               )
                               ucs.login_handle.add_mo(mo_boot_cimc_vmedia_hdd, True)

                    
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

def verify_boot_order_settings(mo, dn, boot_security_policy_enabled, boot_order_matches, boot_order_tree, ucs):
    child_props_match = True
    mo_list = ucs.login_handle.query_children(in_mo=mo)
    if mo_list :
        for index, child in enumerate(mo_list):
            logging.debug("boot order child : %s", child)

            if child.dn ==  get_dn_path(dn, BOOT_SECURITY_DN):
                if not is_boot_security_setting_matching(child, boot_security_policy_enabled, boot_order_matches):
                    child_props_match = False
            elif child.dn == get_dn_path(dn, STORAGE_DN):
                if not is_local_storage_setting_matching(ucs, dn, child, boot_order_tree, boot_order_matches):
                    child_props_match = False
            else:	
                boot_order_matches[child.dn] = True
                order =  boot_order_tree.get(child.dn)
                logging.info("args order: %s child.order: %s dn: %s", order, child.order, child.dn)
                if not(order) or not(order == child.order) :
                    child_props_match = False
                    boot_order_matches[child.dn] = False
    # make sure length of input boot order matches existing boot order - otherwise new items need to be added 
    if child_props_match:
        child_props_match = len(boot_order_matches) == len (boot_order_tree)

    logging.info ("Child Props Match: %s", child_props_match)
    logging.info ("Boot Order match: %s", boot_order_matches)
    return child_props_match

def check_and_remove_boot_order_entries(mo_exists, child_props_match, boot_order_matches, boot_order_tree, ucs):
    if mo_exists and not child_props_match:
        for boot_order_match_dn in boot_order_matches.keys():
            # if the dn doesn't exisit in the new boot order - remove it
            if not boot_order_tree.get(boot_order_match_dn):
                boot_order_mo = ucs.login_handle.query_dn(boot_order_match_dn)
                logging.info("Removing Boot Order Entry: %s", boot_order_mo)
                if boot_order_mo:
                    ucs.login_handle.remove_mo(
                        mo=boot_order_mo
                    )
                ucs.login_handle.commit()

LOCAL_LUN = 'local_lun'
LUN_IMAGE = 'lun_image'
TYPE = 'type'
PARAMS = 'params'
LUN_NAME = 'lun_name'

def get_params(boot_order, boot_type):
    params = None
    for index, boot_from in enumerate(boot_order):
        if boot_from.get(TYPE) == boot_type:
            params = boot_from.get(PARAMS)
    return params
    

def add_lun_local_image_path(dn, lun_images, ucs):
    from ucsmsdk.mometa.lsboot.LsbootLocalLunImagePath import LsbootLocalLunImagePath
    for index, lun_image in enumerate (lun_images):
        mo_lun_image_path = LsbootLocalLunImagePath(
            parent_mo_or_dn=dn,
            type=lun_image[TYPE],
            lun_name=lun_image[LUN_NAME]
        )
        ucs.login_handle.add_mo(mo_lun_image_path, True)
        
def create_local_storage(dn, new_order, ucs):
    from ucsmsdk.mometa.lsboot.LsbootStorage import LsbootStorage
    from ucsmsdk.mometa.lsboot.LsbootLocalStorage import LsbootLocalStorage

    mo_bstorage = LsbootStorage(
        parent_mo_or_dn = dn,
        order=new_order
    )
    ucs.login_handle.add_mo(mo_bstorage, True)
    mo_blocal_storage = LsbootLocalStorage(
        parent_mo_or_dn=mo_bstorage,
    )
    ucs.login_handle.add_mo(mo_blocal_storage, True)
    return mo_blocal_storage

def get_dn_path(parent_dn, child_dn):
    return parent_dn+'/'+child_dn

def is_boot_security_setting_matching(child, boot_security_policy_enabled, boot_order_match):
    secureBootEnabled = False
    if child.secure_boot == 'yes':
            secureBootEnabled = True
    if boot_security_policy_enabled != secureBootEnabled:
        boot_order_match[child.dn] = False
    else:
        boot_order_match[child.dn] = True
    return boot_order_match[child.dn]

LOCAL_DISK = 'local_disk'
VIRTUAL_MEDIA = 'virtual_media'
CIMC_MEDIA_DVD = 'cimc_mounted_dvd'
CIMC_MEDIA_HDD = 'cimc_mounted_hdd'


ORDER='order'

def build_boot_order_tree(dn, boot_order, boot_security_policy_enabled):
    
    bootOrder = dict()
    bootOrder[get_dn_path(dn, BOOT_SECURITY_DN)] = boot_security_policy_enabled
    
    for index, bootFrom in enumerate(boot_order):
        # convert boot order int to string - otherwise you may get serialization error for int
        order = str(bootFrom.get(ORDER))
        boot_type = bootFrom.get(TYPE)
        if boot_type == LOCAL_DISK:
            bootOrder[get_dn_path(dn,LOCAL_DISK_DN)]= order
        elif boot_type == LOCAL_LUN:
            bootOrder[get_dn_path(dn,LOCAL_LUN_DN)]= order
        elif boot_type == VIRTUAL_MEDIA:
            bootOrder[get_dn_path(dn, VIRTUAL_MEDIA_DN)]= order 
        elif boot_type == CIMC_MEDIA_DVD:
            bootOrder[get_dn_path(dn, CIMC_MEDIA_DVD_DN)]=order 
        elif boot_type == CIMC_MEDIA_HDD:
            bootOrder[get_dn_path(dn, CIMC_MEDIA_HDD_DN)]= order
        else:
            print(bootFrom)
    return bootOrder	

def is_local_storage_setting_matching(ucs, dn, child, boot_order_tree, boot_order_match):
    child_props_match = True
    # org-root/boot-policy-test-boot/storage
    if child.dn == get_dn_path(dn, STORAGE_DN):
        mo_storage_list = ucs.login_handle.query_children(in_mo=child)
        for index, child_storage in enumerate(mo_storage_list):
            mo_storage_child_list = ucs.login_handle.query_children(in_mo=child_storage)
            # org-root/boot-policy-test-boot/storage/local-storage
            if(child_storage.dn == get_dn_path(child.dn, LOCAL_STORAGE_DN)):
                for index, local_storage_child in enumerate(mo_storage_child_list):
                    # 	check whether order match for local storage child
                    order = boot_order_tree.get(local_storage_child.dn)
                    if not(order) or not(order == local_storage_child.order) :
                        boot_order_match[local_storage_child.dn] = False
                        child_props_match = False
                    else:
                        boot_order_match[local_storage_child.dn] = True
    return child_props_match
                    
if __name__ == '__main__':
    main()
