# A node definition for cobbler
# You will likely also want to change the IP addresses, domain name, and perhaps
# even the proxy address

define cobbler_node($node_type, $mac, $ip, $power_address, $power_id = undef,
  $power_user = 'admin', $power_password = 'password', $power_type = 'ipmitool' ) {
cobbler::node { $name:
    mac            => $mac,
    ip             => $ip,
    ### UCS CIMC Details ###
    # Change these parameters to match the management console settings
    # for your server
    power_address  => $power_address,
    power_user     => $power_user,
    power_password => $power_password,
    power_type     => $power_type,
    power_id       => $power_id,
    ### Advanced Users Configuration ###
    # These parameters typically should not be changed
    profile        => "precise-x86_64-auto",
    domain         => $::domain_name,
    node_type      => $node_type,
    preseed        => "cisco-preseed",
  }
}

node /cobbler-node/ inherits "base" {

if ($::ipv6_ra == "") {
  $ra='0'
} else {
  $ra = $::ipv6_ra 
}

if ($::interface_bonding == 'true'){
  $bonding = "echo 'bonding' >> /target/etc/modules"
} else {
  $bonding = 'echo "no bonding configured"'
}
 
$interfaces_file=regsubst(template("interfaces.erb"), '$', "\\n\\", "G")

####### Shared Variables from Site.pp #######
$cobbler_node_fqdn 	        = "${::build_node_name}.${::domain_name}"

####### Preseed File Configuration #######
 cobbler::ubuntu::preseed { "cisco-preseed":
  admin_user 		=> $::admin_user,
  password_crypted 	=> $::password_crypted,
  packages 		=> "openssh-server vim vlan lvm2 ntp puppet",
  ntp_server 		=> $::build_node_fqdn,
  late_command 		=> sprintf('
sed -e "/logdir/ a pluginsync=true" -i /target/etc/puppet/puppet.conf ; \
sed -e "/logdir/ a server=%s" -i /target/etc/puppet/puppet.conf ; \
echo -e "server %s iburst" > /target/etc/ntp.conf ; \
echo "8021q" >> /target/etc/modules ; \
%s ; \
echo "net.ipv6.conf.default.autoconf=%s" >> /target/etc/sysctl.conf ; \
echo "net.ipv6.conf.default.accept_ra=%s" >> /target/etc/sysctl.conf ; \
echo "net.ipv6.conf.all.autoconf=%s" >> /target/etc/sysctl.conf ; \
echo "net.ipv6.conf.all.accept_ra=%s" >> /target/etc/sysctl.conf ; \
ifconf="`tail +11 </etc/network/interfaces`" ; \
echo -e "%s
" > /target/etc/network/interfaces ; \
sed -e "s/^[ ]*//" -i /target/etc/network/interfaces ; \
', $cobbler_node_fqdn, $cobbler_node_fqdn, $bonding,
   $ra,$ra,$ra,$ra, $interfaces_file),
  proxy 		=> "http://${cobbler_node_fqdn}:3142/",
  expert_disk 		=> $::expert_disk,
  diskpart 		=> [$::install_drive],
  boot_disk 		=> $::install_drive,
  autostart_puppet      => $::autostart_puppet,
  time_zone             => $::time_zone,
  root_part_size        => $::root_part_size,
  var_part_size         => $::var_part_size,
  enable_var            => $::enable_var,
  enable_vol_space      => $::enable_vol_space,
  }


class { cobbler: 
  node_subnet      => $::node_subnet, 
  node_netmask     => $::node_netmask,
  node_gateway     => $::node_gateway,
  node_dns         => $::node_dns,
  ip               => $::ip,
  dns_service      => $::dns_service,
  dhcp_service     => $::dhcp_service,
# change these two if a dynamic DHCP pool is needed
  dhcp_ip_low      => false,
  dhcp_ip_high     => false,
  domain_name      => $::domain_name,
  password_crypted => $::password_crypted,
  ucsm_port        => $::ucsm_port,
}

# This will load the Ubuntu Server OS into cobbler
# COE supprts only Ubuntu precise x86_64
 cobbler::ubuntu { "precise":
  proxy => $::proxy,
 }
}
