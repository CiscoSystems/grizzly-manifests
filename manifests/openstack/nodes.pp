########### package repo configuration ##########
#
# The package repos used to install openstack
$package_repo 		= 'cisco_repo'
# Alternatively, the upstream Ubuntu package from cloud archive can be used
# $package_repo = 'cloud_archive'

# If you are behind a proxy you may choose not to use our ftp distribution, and
# instead try our http distribution location. Note the http location is not
# a permanent location and may change at any time.
$location 		= "ftp://ftpeng.cisco.com/openstack/cisco"
# Alternate, uncomment this one, and comment out the one above
#$location		= "http://openstack-repo.cisco.com/openstack/cisco"
########### Build Node (Cobbler, Puppet Master, NTP) ######
# Change the following to the host name you have given your build node.
# This name should be in all lower case letters due to a Puppet limitation
# (refer to http://projects.puppetlabs.com/issues/1168).
$build_node_name        = "puppetMaster"

########### NTP Configuration ############
# Change this to the location of a time server in your organization accessible to the build server
# The build server will synchronize with this time server, and will in turn function as the time
# server for your OpenStack nodes
$ntp_servers		= ["172.29.86.1"]

########### Build Node Cobbler Variables ############
# Change these 5 parameters to define the IP address and other network settings of your build node
# The cobbler node *must* have this IP configured and it *must* be on the same network as
# the hosts to install
$cobbler_node_ip 	= '172.29.86.25'
$node_subnet 		= '172.29.86.0'
$node_netmask 		= '255.255.255.192'

# This gateway is optional - if there's a gateway providing a default route, put it here
# If not, comment it out
$node_gateway 		= '172.29.86.1'

# This domain name will be the name your build and compute nodes use for the local DNS
# It doesn't have to be the name of your corporate DNS - a local DNS server on the build
# node will serve addresses in this domain - but if it is, you can also add entries for
# the nodes in your corporate DNS environment they will be usable *if* the above addresses
# are routeable from elsewhere in your network.
$domain_name 		= 'bigdata.lab'

# This setting likely does not need to be changed
# To speed installation of your OpenStack nodes, it configures your build node to function
# as a caching proxy storing the Ubuntu install files used to deploy the OpenStack nodes
$cobbler_proxy 		= "http://${cobbler_node_ip}:3142/"

####### Preseed File Configuration #######
# This will build a preseed file called 'cisco-preseed' in /etc/cobbler/preseeds/
# The preseed file automates the installation of Ubuntu onto the OpenStack nodes
#
# The following variables may be changed by the system admin:
# 1) admin_user
# 2) password_crypted
# 3) autostart_puppet -- whether the puppet agent will auto start
# Default user is: localadmin 
# Default SHA-512 hashed password is "ubuntu": $6$UfgWxrIv$k4KfzAEMqMg.fppmSOTd0usI4j6gfjs0962.JXsoJRWa5wMz8yQk4SfInn4.WZ3L/MCt5u.62tHDGB36EhiKF1
# To generate a new SHA-512 hashed password, run the following replacing
# the word "password" with your new password. Then use the result as the
# $password_crypted variable
# python -c "import crypt, getpass, pwd; print crypt.crypt('password', '\$6\$UfgWxrIv\$')"
$admin_user 		= 'localadmin'
$password_crypted 	= '$6$UfgWxrIv$k4KfzAEMqMg.fppmSOTd0usI4j6gfjs0962.JXsoJRWa5wMz8yQk4SfInn4.WZ3L/MCt5u.62tHDGB36EhiKF1'
$autostart_puppet       = true

# If the setup uses the UCS Bseries blades, enter the port on which the
# ucsm accepts requests. By default the UCSM is enabled to accept requests
# on port 443 (https). If https is disabled and only http is used, set
# $ucsm_port = '80'
$ucsm_port = '443'

########### OpenStack Variables ############
# These values define parameters which will be used to deploy and configure OpenStack
# once Ubuntu is installed on your nodes
#
# Change these next 3 parameters to the network settings of the node which 
# will be your OpenStack control node.  Note that the $controller_hostname
# should be in all lowercase letters due to a limitation of Puppet
# (refer to http://projects.puppetlabs.com/issues/1168).
$controller_node_address       = '172.29.86.33'
$controller_node_network       = '172.29.86.0'
$controller_hostname           = 'openstackcontrol'

# Specify the network which should have access to the MySQL database on the OpenStack control
# node. Typically, this will be the same network as defined in the controller_node_network
# parameter above. Use MySQL network wild card syntax to specify the desired network.
$db_allowed_network            = '172.29.86.%'

# These next two values typically do not need to be changed. They define the network connectivity
# of the OpenStack controller
# This is the interface used to connect to Horizon dashboard
$controller_node_public        = $controller_node_address
# This is the interface used for external backend communication
$controller_node_internal      = $controller_node_address

# These next three parameters specify the networking hardware used in each node
# Current assumption is that all nodes have the same network interfaces and are
# cabled identically
#
# public_interface is the interface that each service's API listens on
#   it's also commonly referred to as the management interface
$public_interface        	= 'eth0'
# private_interface is the interface used for network connectivity between VMs.
#   specifying and interface allows you to create a network specifically for GRE 
#   tunneled traffic between compute and network nodes.
$private_interface		= 'eth0'
# external_interface is used for external connectivity such as floating IPs (only in network/controller node)
$external_interface	 	= 'eth1'

# Select the drive on which Ubuntu and OpenStack will be installed in each node. Current assumption is
# that all nodes will be installed on the same device name
$install_drive           = '/dev/sda'

########### OpenStack Service Credentials ############
# This block of parameters is used to change the user names and passwords used by the services which
# make up OpenStack. The following defaults should be changed for any production deployment
$admin_email             = 'root@localhost'
$admin_password          = 'Cisco123'
$keystone_db_password    = 'keystone_db_pass'
$keystone_admin_token    = 'keystone_admin_token'
$nova_user               = 'nova'
$nova_db_password        = 'nova_pass'
$nova_user_password      = 'nova_pass'
$libvirt_type            = 'kvm'
$glance_db_password      = 'glance_pass'
$glance_user_password    = 'glance_pass'
$glance_sql_connection   = "mysql://glance:${glance_db_password}@${controller_node_address}/glance"
$glance_on_swift         = false
$cinder_user_password    = 'cinder_pass'
$cinder_db_password      = 'cinder_pass'
$quantum_user_password   = 'quantum_pass'
$quantum_db_password     = 'quantum_pass'
$rabbit_password         = 'openstack_rabbit_password'
$rabbit_user             = 'openstack_rabbit_user'
# Nova DB connection
$sql_connection 	 = "mysql://${nova_user}:${nova_db_password}@${controller_node_address}/nova"
# glance backend configuration, supports file or swift
$glance_backend = 'file'

########### Test variables ############
# variables used to populate test script:
# /tmp/test_nova.sh
#
# image to use for tests. Accepts kvm or cirros
$test_file_image_type = 'kvm'

#### end shared variables #################

# Storage Configuration
# Set to true to enable Cinder services
$cinder_controller_enabled     = true

# Set to true to enable Cinder deployment to all compute nodes
$cinder_compute_enabled        = true

# The cinder storage driver to use. Default is iscsi
$cinder_storage_driver         = 'iscsi'

# Other drivers exist for cinder. Here are examples on how to enable them.
#
# NetApp iSCSI Driver
# $cinder_storage_driver = 'netapp'
# $netapp_wsdl_url       = ''
# $netapp_login          = ''
# $netapp_password       = ''
#
# NFS
# share information is stored in flat text file specified in $nfs_shares_config
# the format for this file is hostname:/mountpoint eg 192.168.2.55:/myshare, with only one entry per line
#
# $cinder_storage_driver = 'nfs'
# $nfs_shares_config     = '/etc/cinder/shares.conf'

###### NODES ######

define hosts_file {
  $ip_address = $title  
  $host_name = "${hostname}"
  $fqdn = "${fqdn}" 

  file { "hosts-${title}":
    path    => "/etc/hosts",
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('hosts.erb'),
  }
}

define interfaces {
  file { "interfaces":
    path    => "/etc/network/interfaces",
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('interfaces.erb'),
  }
  
  exec { "ifup -a":
    subscribe => File['interfaces'],
    path      => ["/sbin/"],
  }
}

node /openstackcontrol/ inherits os_base {
  hosts_file { "${ipaddress}": }  
  ->
  interfaces { "interfaces": }
  -> 
  class { 'control':
    tunnel_ip   => "${ipaddress}",
  }
  
  # Include this in the future, for curvature 	
  # class { 'curvature': }
}

node /openstackcompute\d+/ inherits os_base {
  hosts_file { "${ipaddress}": }  
  ->
  class { 'compute':
    internal_ip => "${ipaddress}",
    tunnel_ip   => "${ipaddress}",
  }
}

#### END NODES ####

########################################################################
### All parameters below this point likely do not need to be changed ###
########################################################################

### Advanced Users Configuration ###
# These four settings typically do not need to be changed
# In the default deployment, the build node functions as the DNS and static DHCP server for
# the OpenStack nodes. These settings can be used if alternate configurations are needed
$node_dns       = "${cobbler_node_ip}"
$ip 		= "${cobbler_node_ip}"
$dns_service 	= "dnsmasq"
$dhcp_service 	= "dnsmasq"
$time_zone      = "UTC"

# Configure the maximum number of times mysql-server will allow
# a host to fail connecting before banning it
$max_connect_errors = '10'

### Puppet Parameters ###
# These settings load other puppet components. They should not be changed
import 'core'
