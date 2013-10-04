# A node definition for cobbler
# You will likely also want to change the IP addresses, domain name, and perhaps
# even the proxy address

define cobbler_node($mac, $ip, $power_address, $power_id = undef,
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
  $ifenslave='ifenslave-2.6'
  $bonding = "echo 'bonding' >> /target/etc/modules"
} else {
  $ifenslave=''
  $bonding = 'echo "no bonding configured"'
}
 
$interfaces_file=regsubst(template("interfaces.erb"), '$', "\\n\\", "G")

####### Shared Variables from Site.pp #######
$cobbler_node_fqdn 	        = "${::build_node_name}.${::domain_name}"

####### Set up to load custom kernel #######
if $::load_kernel_pkg {
  $kernel_cmd = "in-target /usr/bin/apt-get install -y $::load_kernel_pkg ; \\
export kernel_ver=`echo '$::load_kernel_pkg'|/bin/sed 's/linux-image-//'` ; \\
export prev_starts_at=`grep -n Previous /target/boot/grub/grub.cfg | /target/usr/bin/cut -f1 -d:` ; \\
export kern_starts_at=`grep -n \"Ubuntu, with Linux \$kernel_ver'\" /target/boot/grub/grub.cfg|/target/usr/bin/cut -f1 -d:` ; \\
if [ \"\$prev_starts_at\" ] && [ \"\$prev_starts_at\" -lt \"\$kern_starts_at\" ] ; \\
then \\
in-target /bin/sed -i \"/GRUB_DEFAULT=/ s/[0-9]/\\\"Previous Linux versions>Ubuntu, with Linux \$kernel_ver\\\"/\" /etc/default/grub ; \\
else \\
in-target /bin/sed -i \"/GRUB_DEFAULT=/ s/[0-9]/\\\"Ubuntu, with Linux \$kernel_ver\\\"/\" /etc/default/grub ; \\
fi ; \\
in-target /usr/sbin/update-grub ; "
} else {
  $kernel_cmd = ''
}

####### Set up to load custom kernel boot params #######
if $::kernel_boot_params {
  $kernel_boot_params_cmd ="in-target /bin/sed -i \"s/GRUB_CMDLINE_LINUX_DEFAULT=\\\"[a-zA-Z ]\\\+\\\"/GRUB_CMDLINE_LINUX_DEFAULT=\\\"$::kernel_boot_params\\\"/\" /etc/default/grub ; \\
in-target /usr/sbin/update-grub ; "
} else {
  $kernel_boot_params_cmd = ''
}

####### Preseed File Configuration #######
 cobbler::ubuntu::preseed { "cisco-preseed":
  admin_user 		=> $::admin_user,
  password_crypted 	=> $::password_crypted,
  packages 		=> "openssh-server vim vlan lvm2 ntp puppet ${ifenslave}",
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
%s \
%s \
', $cobbler_node_fqdn, $cobbler_node_fqdn, $bonding,
   $ra,$ra,$ra,$ra, $interfaces_file, $kernel_cmd, $kernel_boot_params_cmd),
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
