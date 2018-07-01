# OpenShift-UCSM - Deploying Red Hat OpenShift® Container Platform 3.9 with Container-Native Storage on Cisco UCS Managed Servers

## Instructions
This repos contains Ansible Playbook code for deploying RedHat OpenShift Containe Platform v3.9 on Cisco UCS bare metal servers. Following pre-requisites/important notes, are needed before the play-book can be played on -

1. UCS Manager Service Profile configuration is out of scope of this playbook. It is expected that Day0/1 tasks for setting up UCS servers, storage configuration, network configuration have already been taken care of. Detailed instructions/know-hows are part of deployment guide on the solution.
2. Bare Metal OS with RHEL Atomic Host 7.5 has been taken care of before hand. This requirement gets done in an automated fashion through UCSM vMedia Policy implimentations. 
3. All nodes in the cluster should have atleast 2 VDs, one for OS boot and the other one for Docker usage. This again automated through UCSM Storage Profile Policy.
4. Playbooks are to be run from the Bastion node, which is a node out of the OpenShift Container Platform cluster setup. It acts as a build server so to speak.
5. This playbook is written for environment which works behind proxy, if proxy is not needed certain sub-tasks should be skipped.
6. Inventory file and parameters defined in it are the final source to run these playbooks including RedHat provided OpenShift Container Platform deployment playbooks.

Please, refer to [Reference Architecture document](https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/UCS_CVDs/ucs_openshift_design.html) & [Solution Deployment Guide]() for detail instructions and know-hows.

### Clone the repository
`git clone https://github.com/CiscoUcs/OpenShift-UCSM.git`

### Creating inventory
Inventory file has to be filled manually.
Refer to *hosts.example* for possible variables.

`cp hosts.example /etc/ansible/hosts;
vim /etc/ansible/hosts`

### Provisioning Bastion Node

`ansible-playbook src/bastion-config/bastion_config.yml -vvv`


### Preparing the nodes for OpenShift Container Platform

`ansible-playbook src/prerequisites/nodes_setup.yaml` 

### Setting up multimaster HA

`ansible-playbook src/keepalived-multimaster/keepalived.yaml`

### Deploying OpenShift Container Platform cluster

1. Run the prequisites.yml playbook. This must be run only once before deploying a new cluster. Use the following command, specifying -i if your inventory file located somewhere other than /etc/ansible/hosts:

`ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/prerequisites.yml`

2. Run the deploy_cluster.yml playbook to initiate the cluster installation:

`ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/deploy_cluster.yml`

