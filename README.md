# OpenShift-UCSM - Deploying Red Hat OpenShift® Container Platform 3.9 with Container-Native Storage on Cisco UCS Managed Servers

## Instructions
Please, refer to [Reference Architecture document](https://www.cisco.com/c/en/us/td/docs/unified_computing/ucs/UCS_CVDs/ucs_openshift_design.html)
 for actual instructions.

### Clone the repository
`git clone https://github.com/CiscoUcs/OpenShift-UCSM.git`

### Creating inventory
Inventory file has to be filled manually.
Refer to *hosts.example* for possible variables.

`cp hosts.example /etc/ansible/hosts;
vim /etc/ansible/hosts`

### Provisioning Bastion Node

`ansible-playbook ipxe-deployer/ipxe.yml`


### Preparing the nodes for OpenShift Container Platform

`ansible-playbook src/prerequisites/nodes_setup.yaml -k`

### Setting up multimaster HA
switch user to *openshift*:

`su - openshift`

run:

`ansible-playbook src/keepalived-multimaster/keepalived.yaml`

### Deploying OpenShift cluster
As user *openshift* run:

`ansible-playbook /usr/share/ansible/openshift-ansible/playbooks/byo/config.yml`
