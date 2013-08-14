# This document serves as an example of how to deploy
# basic multi-node openstack environments.
# In this scenario Quantum is using OVS with GRE Tunnels


node base {
  $build_node_fqdn = "${::build_node_name}.${::domain_name}"

  ########### Folsom Release ###############

    # Disable pipelining to avoid unfortunate interactions between apt and
    # upstream network gear that does not properly handle http pipelining
    # See https://bugs.launchpad.net/ubuntu/+source/apt/+bug/996151 for details
  if ($osfamily == 'debian') {
    file { '/etc/apt/apt.conf.d/00no_pipelining':
      ensure  => file,
      owner   => 'root',
      group   => 'root',
      mode    => '0644',
      content => 'Acquire::http::Pipeline-Depth "0";'
    }

    # Load apt prerequisites.  This is only valid on Ubuntu systmes

    if($::package_repo == 'cisco_repo') {
      apt::source { "cisco-openstack-mirror_grizzly":
        location => $::location,
        release => "grizzly-proposed",
        repos => "main",
        key => "6B7A62576A4F98AD",
        key_content => '-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.11 (GNU/Linux)

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
ui5ouWe8Ig9ur+rOvOGMrsSa
=HyLD
-----END PGP PUBLIC KEY BLOCK-----',
        proxy => $::proxy,
      }

      apt::pin { "cisco":
        priority => '990',
        originator => 'Cisco'
      }
    } elsif($::package_repo == 'cloud_archive') {
      apt::source { 'openstack_cloud_archive':
        location          => "http://ubuntu-cloud.archive.canonical.com/ubuntu",
        release           => "precise-updates/grizzly",
        repos             => "main",
        required_packages => 'ubuntu-cloud-keyring',
      }
    } else {
      fail("Unsupported package repo ${::package_repo}")
    }
  }
  elsif ($osfamily == 'redhat') {
    yumrepo { 'cisco-openstack-mirror':
      descr     => "Cisco Openstack Repository",
      baseurl  => $::location,
      gpgcheck => "0", #TODO(prad): Add gpg key
      enabled  => "1";
    }
    # add a resource dependency so yumrepo loads before package
    Yumrepo <| |> -> Package <| |>
  }

  class { pip: }

  # Ensure that the pip packages are fetched appropriately when we're using an
  # install where there's no direct connection to the net from the openstack
  # nodes
  if ! $::default_gateway {
    Package <| provider=='pip' |> {
      install_options => "--index-url=http://${build_node_name}/packages/simple/",
    }
  } else {
    if($::proxy) {
      Package <| provider=='pip' |> {
        # TODO(ijw): untested
        install_options => "--proxy=$::proxy"
      }
    }
  }
  # (the equivalent work for apt is done by the cobbler boot, which sets this up as
  # a part of the installation.)


  # /etc/hosts entries for the controller nodes
  host { $::controller_hostname:
	  ip => $::controller_node_internal
  }

  class { 'collectd':
    graphitehost		=> $build_node_fqdn,
	  management_interface	=> $::public_interface,
  }
}

node os_base inherits base {
  $build_node_fqdn = "${::build_node_name}.${::domain_name}"

  class { ntp:
	  servers		=> [$build_node_fqdn],
	  ensure 		=> running,
	  autoupdate 	=> true,
  }

    # Deploy a script that can be used to test nova
    class { 'openstack::test_file':
      image_type => $::test_file_image_type,
    }

  class { 'openstack::auth_file':
	  admin_password       => $admin_password,
	  controller_node      => $controller_node_internal,
  }

  class { "naginator::base_target": }

  # This value can be set to true to increase debug logging when
  # trouble-shooting services. It should not generally be set to
  # true as it is known to break some OpenStack components
  $verbose            = false

}

class control(
  $tunnel_ip,
  $public_address                    = $::controller_node_public,
  # network
  $internal_address                  = $::controller_node_internal,
  # by default it does not enable multi-host mode
  $multi_host                        = $::multi_host,
  $verbose                           = $::verbose,
  $auto_assign_floating_ip           = $::auto_assign_floating_ip,
  $mysql_root_password               = $::mysql_root_password,
  $admin_email                       = $::admin_email,
  $admin_password                    = $::admin_password,
  $keystone_db_password              = $::keystone_db_password,
  $keystone_admin_token              = $::keystone_admin_token,
  $glance_db_password                = $::glance_db_password,
  $glance_user_password              = $::glance_user_password,

  # TODO this needs to be added
  $glance_backend                    = $::glance_backend,
  $rbd_store_user                    = $::glance_ceph_user,
  $rbd_store_pool                    = $::glance_ceph_pool,

  $nova_db_password                  = $::nova_db_password,
  $nova_user_password                = $::nova_user_password,
  $rabbit_password                   = $::rabbit_password,
  $rabbit_user                       = $::rabbit_user,
  # TODO deprecated
  #export_resources                  = false,

  ######### quantum variables #############
  $core_plugin                       = $::quantum_core_plugin,
  $cisco_vswitch_plugin              = $::cisco_vswitch_plugin,
  $cisco_nexus_plugin                = $::cisco_nexus_plugin,
  $nexus_credentials                 = $::nexus_credentials,
  # need to set from a variable
  # database
  $db_host                           = $::controller_node_address,
  $quantum_db_password               = $quantum_db_password,
  $quantum_db_name                   = 'quantum',
  $quantum_db_user                   = 'quantum',
  # enable quantum services
  $enable_dhcp_agent                 = $true,
  $enable_l3_agent                   = $true,
  $enable_metadata_agent             = $true,
  # Metadata Configuration
  $metadata_shared_secret            = 'secret',
  # ovs config
  $ovs_local_ip                      = $tunnel_ip,
  $bridge_interface                  = $::external_interface,
  $enable_ovs_agent                  = true,
  $ovs_vlan_ranges                   = $::ovs_vlan_ranges,
  $ovs_bridge_mappings               = $::ovs_bridge_mappings,
  $ovs_bridge_uplinks                = $::ovs_bridge_uplinks,
  $tenant_network_type               = $::tenant_network_type,
  # Keystone
  $quantum_user_password             = $::quantum_user_password,
  # horizon
  $secret_key                        = 'super_secret',
  # cinder
  $cinder_user_password              = $::cinder_user_password,
  $cinder_db_password                = $::cinder_db_password,
  # Quantum quotas
  $quantum_quota_network             = $::quantum_quota_network,
  $quantum_quota_subnet              = $::quantum_quota_subnet,
  $quantum_quota_port                = $::quantum_quota_port,
  $quantum_quota_router              = $::quantum_quota_router,
  $quantum_quota_floatingip          = $::quantum_quota_floatingip,
  $quantum_quota_security_group      = $::quantum_quota_security_group,
  $quantum_quota_security_group_rule = $::quantum_quota_security_group_rule,
)
{
  if $core_plugin == 'cisco' {
     $core_plugin_real = 'quantum.plugins.cisco.network_plugin.PluginV2'
  } else {
     $core_plugin_real = 'quantum.plugins.openvswitch.ovs_quantum_plugin.OVSQuantumPluginV2'
  }
  if $cisco_vswitch_plugin == 'n1k' { 
    $security_group_api = 'nova'
  } else {
    $security_group_api = 'quantum'
  }
  class { 'openstack::controller':
    public_address          => $controller_node_public,
    # network
    internal_address        => $controller_node_internal,
    # by default it does not enable multi-host mode
    multi_host              => $multi_host,
    verbose                 => $verbose,
    auto_assign_floating_ip => $auto_assign_floating_ip,
    mysql_root_password     => $mysql_root_password,
    admin_email             => $admin_email,
    admin_password          => $admin_password,
    keystone_db_password    => $keystone_db_password,
    keystone_admin_token    => $keystone_admin_token,
    glance_db_password      => $glance_db_password,
    glance_user_password    => $glance_user_password,

    glance_backend          => $glance_backend,
    rbd_store_user          => $rbd_store_user,
    rbd_store_pool          => $rbd_store_pool,


    nova_db_password        => $nova_db_password,
    nova_user_password      => $nova_user_password,
    rabbit_password         => $rabbit_password,
    rabbit_user             => $rabbit_user,
    security_group_api      => $security_group_api,
    # TODO deprecated
    #export_resources        => false,

    ######### quantum variables #############
    quantum_core_plugin     => $core_plugin_real,
    # need to set from a variable
    # database
    db_host                 => $db_host,
    quantum_db_password     => $quantum_db_password,
    quantum_db_name         => $quantum_db_name,
    quantum_db_user         => $quantum_db_user,
    # enable quantum services
    enable_dhcp_agent       => $enable_dhcp_agent,
    enable_l3_agent         => $enable_l3_agent,
    enable_metadata_agent   => $enable_metadata_agent,
    # Metadata Configuration
    metadata_shared_secret  => $metadata_shared_secret,
    # ovs config
    ovs_local_ip            => $ovs_local_ip,
    bridge_interface        => $bridge_interface,
    enable_ovs_agent        => $enable_ovs_agent,
    network_vlan_ranges     => $ovs_vlan_ranges,
    bridge_mappings         => $ovs_bridge_mappings,
    bridge_uplinks          => $ovs_bridge_uplinks,
    tenant_network_type     => $tenant_network_type,
    # Keystone
    quantum_user_password   => $quantum_user_password,
    # horizon
    secret_key              => $secret_key,
    # cinder
    cinder_user_password    => $cinder_user_password,
    cinder_db_password      => $cinder_db_password,
  }

  if ($::swift_proxy_address) { 
    class { 'swift::keystone::auth':
      auth_name        => $swift_user,
      password         => $swift_password,
      public_address   => $::swift_proxy_address,
      admin_address    => $::swift_proxy_address,
      internal_address => $::swift_proxy_address,
    }
  }

  class { "naginator::control_target": }

  class { "quantum::quota":
    quota_network             => $quantum_quota_network,
    quota_subnet              => $quantum_quota_subnet,
    quota_port                => $quantum_quota_port,
    quota_router              => $quantum_quota_router,
    quota_floatingip          => $quantum_quota_floatingip,
    quota_security_group      => $quantum_quota_security_group,
    quota_security_group_rule => $quantum_quota_security_group_rule,
  }

  if $cisco_vswitch_plugin == 'n1k' {
    $cisco_vswitch_plugin_real = 'quantum.plugins.cisco.n1kv.n1kv_quantum_plugin.N1kvQuantumPluginV2'
  } else {
    $cisco_vswitch_plugin_real = 'quantum.plugins.openvswitch.ovs_quantum_plugin.OVSQuantumPluginV2'
  }

  if $cisco_nexus_plugin == 'nexus' {
    $cisco_nexus_plugin_real = 'quantum.plugins.cisco.nexus.cisco_nexus_plugin_v2.NexusPlugin'

    package { 'python-ncclient':
      ensure => installed,
    } ~> Service['quantum-server']

    # hack to make sure the directory is created
    Quantum_plugin_cisco<||> ->
    file {'/etc/quantum/plugins/cisco/nexus.ini':
      owner => 'root',
      group => 'root',
      content => template('nexus.ini.erb')
    } ~> Service['quantum-server']
  } else {
    $cisco_nexus_plugin_real = undef
  }

  if $nexus_credentials {
    file {'/var/lib/quantum/.ssh':
      ensure => directory,
      owner  => 'quantum',
      require => Package['quantum-server']
    } ->
    nexus_creds{ $nexus_credentials: }
  }

  if $core_plugin == 'cisco' {
    class { 'quantum::plugins::cisco':
      database_name => $quantum_db_name,
      database_user => $quantum_db_user,
      database_pass => $quantum_db_password,
      database_host => $db_host,
      keystone_username => 'quantum',
      keystone_password => $quantum_user_password,
      keystone_auth_url => "http://${controller_node_public}:35357/v2.0/",
      keystone_tenant   => 'services',
      vswitch_plugin    => $cisco_vswitch_plugin_real,
      nexus_plugin      => $cisco_nexus_plugin_real
    }
  }
  
  class { "coe::quantum_log": }

  if ($::glance_ceph_enabled) and ($::controller_has_mon) {
    class { 'coe::ceph::glance': }
  }
  elsif ($::glance_ceph_enabled) and (!$::controller_has_mon) {
    class { 'coe::ceph::control': }
  }

}

### begin cinder standalone nodes
class cinder_node() {
  class { 'cinder':
    rabbit_userid   => $::rabbit_user,
    rabbit_host     => $::controller_node_address,
    rabbit_password => $::rabbit_password,
    sql_connection  => "mysql://${cinder_user}:${cinder_db_password}@${controller_node_address}/cinder",
    verbose         => true,
  }
  class { 'cinder::volume': }

  package {'python-mysqldb':
    ensure => present,
  }

}

### end cinder standalone nodes
 

### begin ceph ###
class ceph_common (
  $fsid,
  $auth_type = $::ceph_auth_type,
) {
  class { 'ceph::conf':
    fsid            => $::ceph_monitor_fsid,
    auth_type       => $::ceph_auth_type,
    cluster_network => $::ceph_cluster_network,
    public_network  => $::ceph_public_network,
  }
}

class ceph_mon (
  $id
) {
  class { 'ceph_common':
    fsid      => $::ceph_monitor_fsid,
    auth_type => $::ceph_auth_type,
  }
  ceph::mon { $id:
    monitor_secret => $::ceph_monitor_secret,
    mon_port       => 6789,
    mon_addr       => $::ceph_monitor_address,
  }
}

### end ceph

class compute(
  $internal_ip,
  $tunnel_ip,
  # keystone
  $db_host                           = $::controller_node_internal,
  $keystone_host                     = $::controller_node_internal,
  $quantum_host                      = $::controller_node_internal,
  $internal_address                  = $internal_ip,
  $libvirt_type                      = $::libvirt_type,
  $multi_host                        = $::multi_host,
  # rabbit
  $rabbit_host                       = $::controller_node_internal,
  $rabbit_password                   = $::rabbit_password,
  $rabbit_user                       = $::rabbit_user,
  # nova
  $nova_user_password                = $::nova_user_password,
  $nova_db_password                  = $::nova_db_password,
  $glance_api_servers                = "${::controller_node_internal}:9292",
  $vncproxy_host                     = $::controller_node_public,
  $vnc_enabled                       = true,
  # cinder parameters
  $cinder_db_password                = $::cinder_db_password,
  $manage_volumes                    = true,
  $volume_group                      = 'cinder-volumes',
  $setup_test_volume                 = true,
  $cinder_volume_driver              = $::cinder_storage_driver,
  $cinder_rbd_user                   = $::cinder_rbd_user,
  $cinder_rbd_pool                   = $::cinder_rbd_pool,
  $cinder_rbd_secret_uuid            = $::cinder_rbd_secret_uuid,
  # quantum config
  $quantum	                     = true,
  $quantum_user_password             = $::quantum_user_password,
  # Quantum OVS
  $enable_ovs_agent                  = true,
  $ovs_local_ip                      = $tunnel_ip,
  $ovs_bridge_mappings               = $::ovs_bridge_mappings,
  $ovs_bridge_uplinks                = $::ovs_bridge_uplinks,
  # Quantum L3 Agent
  $enable_l3_agent                   = false,
  $enable_dhcp_agent                 = false,
  # Quantum quotas
  $quantum_quota_network             = $::quantum_quota_network,
  $quantum_quota_subnet              = $::quantum_quota_subnet,
  $quantum_quota_port                = $::quantum_quota_port,
  $quantum_quota_router              = $::quantum_quota_router,
  $quantum_quota_floatingip          = $::quantum_quota_floatingip,
  $quantum_quota_security_group      = $::quantum_quota_security_group,
  $quantum_quota_security_group_rule = $::quantum_quota_security_group_rule,
  # general
  $enabled                           = true,
  $verbose                           = $::verbose,
)
{

  class { 'openstack::compute':
    # keystone
    db_host                 => $db_host,
    keystone_host           => $keystone_host,
    quantum_host            => $quantum_host,
    internal_address        => $internal_address,
    libvirt_type            => $libvirt_type,
    multi_host              => $multi_host,
    # rabbit
    rabbit_host             => $rabbit_host,
    rabbit_password         => $rabbit_password,
    rabbit_user             => $rabbit_user,
    # nova
    nova_user_password      => $nova_user_password,
    nova_db_password        => $nova_db_password,
    glance_api_servers      => $glance_api_servers,
    vncproxy_host           => $vncproxy_host,
    vnc_enabled             => $vnc_enabled,
    # cinder parameters
    cinder_db_password      => $cinder_db_password,
    manage_volumes          => $manage_volumes,
    volume_group            => $volume_group,
    setup_test_volume       => $setup_test_volume,
    cinder_volume_driver    => $cinder_volume_driver,
    cinder_rbd_user         => $cinder_rbd_user,
    cinder_rbd_pool         => $cinder_rbd_pool,
    cinder_rbd_secret_uuid  => $cinder_rbd_secret_uuid,
    # quantum config
    quantum	            => $quantum,
    quantum_user_password   => $quantum_user_password,
    # Quantum OVS
    enable_ovs_agent        => $enable_ovs_agent,
    ovs_local_ip            => $ovs_local_ip,
    bridge_mappings         => $ovs_bridge_mappings,
    bridge_uplinks          => $ovs_bridge_uplinks,
    # Quantum L3 Agent
    enable_l3_agent         => $enable_l3_agent,
    enable_dhcp_agent       => $enable_dhcp_agent,
    # Quantum Security Groups with OVS
    libvirt_vif_driver      => $libvirt_vif_driver,
    quantum_firewall_driver => $quantum_firewall_driver,
    # general
    enabled                 => $enabled,
    verbose                 => $verbose,
  }

  class { "naginator::compute_target": }

  class { "quantum::quota":
    quota_network             => $quantum_quota_network,
    quota_subnet              => $quantum_quota_subnet,
    quota_port                => $quantum_quota_port,
    quota_router              => $quantum_quota_router,
    quota_floatingip          => $quantum_quota_floatingip,
    quota_security_group      => $quantum_quota_security_group,
    quota_security_group_rule => $quantum_quota_security_group_rule,
  }

  class { "coe::quantum_log": }

}


########### Definition of the Build Node #######################
#
# Definition of this node should match the name assigned to the build node in your deployment.
# In this example we are using build-node, you dont need to use the FQDN.
#
node master-node inherits "cobbler-node" {
  $build_node_fqdn = "${::build_node_name}.${::domain_name}"

  host { $build_node_fqdn:
	  ip => $::cobbler_node_ip
  }

  host { $::build_node_name:
	  ip => $::cobbler_node_ip
  }

  # Change the servers for your NTP environment
  # (Must be a reachable NTP Server by your build-node, i.e. ntp.esl.cisco.com)
  class { ntp:
	  servers 	=> $::ntp_servers,
	  ensure 		=> running,
	  autoupdate 	=> true,
  }

  class { 'naginator': }

  class { 'graphite':
	  graphitehost 	=> $build_node_fqdn,
  }

  class { 'coe::site_index': }

  # set up a local apt cache.  Eventually this may become a local mirror/repo instead
  class { apt-cacher-ng:
  	proxy 		=> $::proxy,
  	avoid_if_range  => true, # Some proxies have issues with range headers
                             # this stops us attempting to use them
                             # marginally less efficient with other proxies
  }

  if ! $::default_gateway {
    # Prefetch the pip packages and put them somewhere the openstack nodes can fetch them

    file {  "/var/www":
      ensure => 'directory',
	  }

    file {  "/var/www/packages":
      ensure  => 'directory',
      require => File['/var/www'],
    }

    if($::proxy) {
      $proxy_pfx = "/usr/bin/env http_proxy=${::proxy} https_proxy=${::proxy} "
    } else {
      $proxy_pfx=""
    }
    exec { 'pip2pi':
      # Can't use package provider because we're changing its behaviour to use the cache
      command => "${proxy_pfx}/usr/bin/pip install pip2pi",
      creates => "/usr/local/bin/pip2pi",
      require => Package['python-pip'],
    }
    Package <| provider=='pip' |> {
      require => Exec['pip-cache']
    }
    exec { 'pip-cache':
      # All the packages that all nodes - build, compute and control - require from pip
      command => "${proxy_pfx}/usr/local/bin/pip2pi /var/www/packages collectd xenapi django-tagging graphite-web carbon whisper",
      creates => '/var/www/packages/simple', # It *does*, but you'll want to force a refresh if you change the line above
      require => Exec['pip2pi'],
    }
  }

  # set the right local puppet environment up.  This builds puppetmaster with storedconfigs (a nd a local mysql instance)
  class { puppet:
	  run_master 		=> true,
	  puppetmaster_address 	=> $build_node_fqdn, 
	  certname 		=> $build_node_fqdn,
	  mysql_password 		=> 'ubuntu',
  }<-

  file {'/etc/puppet/files':
	  ensure => directory,
	  owner => 'root',
	  group => 'root',
	  mode => '0755',
  }

  file {'/etc/puppet/fileserver.conf':
	  ensure => file,
	  owner => 'root',
	  group => 'root',
	  mode => '0644',
	  content => '

# This file consists of arbitrarily named sections/modules
# defining where files are served from and to whom

# Define a section "files"
# Adapt the allow/deny settings to your needs. Order
# for allow/deny does not matter, allow always takes precedence
# over deny
[files]
  path /etc/puppet/files
  allow *
#  allow *.example.com
#  deny *.evil.example.com
#  allow 192.168.0.0/24

[plugins]
#  allow *.example.com
#  deny *.evil.example.com
#  allow 192.168.0.0/24
',
    }
}

define nexus_creds {
  $args = split($title, '/')
  quantum_plugin_cisco_credentials {
    "${args[0]}/username": value => $args[1];
    "${args[0]}/password": value => $args[2];
  }
  exec {"${title}":
    unless => "/bin/cat /var/lib/quantum/.ssh/known_hosts | /bin/grep ${args[0]}",
    command => "/usr/bin/ssh-keyscan -t rsa ${args[0]} >> /var/lib/quantum/.ssh/known_hosts",
    user    => 'quantum',
    require => Package['quantum-server']
  }
}
