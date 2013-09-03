# This document serves as an example of how to deploy
# basic multi-node openstack environments.
# In this scenario Quantum is using OVS with GRE Tunnels

node base {
  $build_node_fqdn = "${::build_node_name}.${::domain_name}"

  ########### Grizzly Release ###############

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
        location    => "$::location/cisco",
        release     => "grizzly-proposed",
        repos       => "main",
        key         => "E8CC67053ED3B199",
        proxy       => $::proxy,
        key_content => '-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.11 (GNU/Linux)

mQENBE/oXVkBCACcjAcV7lRGskECEHovgZ6a2robpBroQBW+tJds7B+qn/DslOAN
1hm0UuGQsi8pNzHDE29FMO3yOhmkenDd1V/T6tHNXqhHvf55nL6anlzwMmq3syIS
uqVjeMMXbZ4d+Rh0K/rI4TyRbUiI2DDLP+6wYeh1pTPwrleHm5FXBMDbU/OZ5vKZ
67j99GaARYxHp8W/be8KRSoV9wU1WXr4+GA6K7ENe2A8PT+jH79Sr4kF4uKC3VxD
BF5Z0yaLqr+1V2pHU3AfmybOCmoPYviOqpwj3FQ2PhtObLs+hq7zCviDTX2IxHBb
Q3mGsD8wS9uyZcHN77maAzZlL5G794DEr1NLABEBAAG0NU9wZW5TdGFja0BDaXNj
byBBUFQgcmVwbyA8b3BlbnN0YWNrLWJ1aWxkZEBjaXNjby5jb20+iQE4BBMBAgAi
BQJP6F1ZAhsDBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRDozGcFPtOxmXcK
B/9WvQrBwxmIMV2M+VMBhQqtipvJeDX2Uv34Ytpsg2jldl0TS8XheGlUNZ5djxDy
u3X0hKwRLeOppV09GVO3wGizNCV1EJjqQbCMkq6VSJjD1B/6Tg+3M/XmNaKHK3Op
zSi+35OQ6xXc38DUOrigaCZUU40nGQeYUMRYzI+d3pPlNd0+nLndrE4rNNFB91dM
BTeoyQMWd6tpTwz5MAi+I11tCIQAPCSG1qR52R3bog/0PlJzilxjkdShl1Cj0RmX
7bHIMD66uC1FKCpbRaiPR8XmTPLv29ZTk1ABBzoynZyFDfliRwQi6TS20TuEj+ZH
xq/T6MM6+rpdBVz62ek6/KBcuQENBE/oXVkBCACgzyyGvvHLx7g/Rpys1WdevYMH
THBS24RMaDHqg7H7xe0fFzmiblWjV8V4Yy+heLLV5nTYBQLS43MFvFbnFvB3ygDI
IdVjLVDXcPfcp+Np2PE8cJuDEE4seGU26UoJ2pPK/IHbnmGWYwXJBbik9YepD61c
NJ5XMzMYI5z9/YNupeJoy8/8uxdxI/B66PL9QN8wKBk5js2OX8TtEjmEZSrZrIuM
rVVXRU/1m732lhIyVVws4StRkpG+D15Dp98yDGjbCRREzZPeKHpvO/Uhn23hVyHe
PIc+bu1mXMQ+N/3UjXtfUg27hmmgBDAjxUeSb1moFpeqLys2AAY+yXiHDv57ABEB
AAGJAR8EGAECAAkFAk/oXVkCGwwACgkQ6MxnBT7TsZng+AgAnFogD90f3ByTVlNp
Sb+HHd/cPqZ83RB9XUxRRnkIQmOozUjw8nq8I8eTT4t0Sa8G9q1fl14tXIJ9szzz
BUIYyda/RYZszL9rHhucSfFIkpnp7ddfE9NDlnZUvavnnyRsWpIZa6hJq8hQEp92
IQBF6R7wOws0A0oUmME25Rzam9qVbywOh9ZQvzYPpFaEmmjpCRDxJLB1DYu8lnC4
h1jP1GXFUIQDbcznrR2MQDy5fNt678HcIqMwVp2CJz/2jrZlbSKfMckdpbiWNns/
xKyLYs5m34d4a0it6wsMem3YCefSYBjyLGSd/kCI/CgOdGN1ZY1HSdLmmjiDkQPQ
UcXHbA==
=v6jg
-----END PGP PUBLIC KEY BLOCK-----',
      }

      if $::supplemental_repo {
        apt::source { "cisco_supplemental-openstack-mirror_grizzly":
          location    => "$::supplemental_repo",
          release     => "grizzly-proposed",
          repos       => "main",
          key         => "E8CC67053ED3B199",
          proxy       => $::proxy,
          key_content => '-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.11 (GNU/Linux)

mQENBE/oXVkBCACcjAcV7lRGskECEHovgZ6a2robpBroQBW+tJds7B+qn/DslOAN
1hm0UuGQsi8pNzHDE29FMO3yOhmkenDd1V/T6tHNXqhHvf55nL6anlzwMmq3syIS
uqVjeMMXbZ4d+Rh0K/rI4TyRbUiI2DDLP+6wYeh1pTPwrleHm5FXBMDbU/OZ5vKZ
67j99GaARYxHp8W/be8KRSoV9wU1WXr4+GA6K7ENe2A8PT+jH79Sr4kF4uKC3VxD
BF5Z0yaLqr+1V2pHU3AfmybOCmoPYviOqpwj3FQ2PhtObLs+hq7zCviDTX2IxHBb
Q3mGsD8wS9uyZcHN77maAzZlL5G794DEr1NLABEBAAG0NU9wZW5TdGFja0BDaXNj
byBBUFQgcmVwbyA8b3BlbnN0YWNrLWJ1aWxkZEBjaXNjby5jb20+iQE4BBMBAgAi
BQJP6F1ZAhsDBgsJCAcDAgYVCAIJCgsEFgIDAQIeAQIXgAAKCRDozGcFPtOxmXcK
B/9WvQrBwxmIMV2M+VMBhQqtipvJeDX2Uv34Ytpsg2jldl0TS8XheGlUNZ5djxDy
u3X0hKwRLeOppV09GVO3wGizNCV1EJjqQbCMkq6VSJjD1B/6Tg+3M/XmNaKHK3Op
zSi+35OQ6xXc38DUOrigaCZUU40nGQeYUMRYzI+d3pPlNd0+nLndrE4rNNFB91dM
BTeoyQMWd6tpTwz5MAi+I11tCIQAPCSG1qR52R3bog/0PlJzilxjkdShl1Cj0RmX
7bHIMD66uC1FKCpbRaiPR8XmTPLv29ZTk1ABBzoynZyFDfliRwQi6TS20TuEj+ZH
xq/T6MM6+rpdBVz62ek6/KBcuQENBE/oXVkBCACgzyyGvvHLx7g/Rpys1WdevYMH
THBS24RMaDHqg7H7xe0fFzmiblWjV8V4Yy+heLLV5nTYBQLS43MFvFbnFvB3ygDI
IdVjLVDXcPfcp+Np2PE8cJuDEE4seGU26UoJ2pPK/IHbnmGWYwXJBbik9YepD61c
NJ5XMzMYI5z9/YNupeJoy8/8uxdxI/B66PL9QN8wKBk5js2OX8TtEjmEZSrZrIuM
rVVXRU/1m732lhIyVVws4StRkpG+D15Dp98yDGjbCRREzZPeKHpvO/Uhn23hVyHe
PIc+bu1mXMQ+N/3UjXtfUg27hmmgBDAjxUeSb1moFpeqLys2AAY+yXiHDv57ABEB
AAGJAR8EGAECAAkFAk/oXVkCGwwACgkQ6MxnBT7TsZng+AgAnFogD90f3ByTVlNp
Sb+HHd/cPqZ83RB9XUxRRnkIQmOozUjw8nq8I8eTT4t0Sa8G9q1fl14tXIJ9szzz
BUIYyda/RYZszL9rHhucSfFIkpnp7ddfE9NDlnZUvavnnyRsWpIZa6hJq8hQEp92
IQBF6R7wOws0A0oUmME25Rzam9qVbywOh9ZQvzYPpFaEmmjpCRDxJLB1DYu8lnC4
h1jP1GXFUIQDbcznrR2MQDy5fNt678HcIqMwVp2CJz/2jrZlbSKfMckdpbiWNns/
xKyLYs5m34d4a0it6wsMem3YCefSYBjyLGSd/kCI/CgOdGN1ZY1HSdLmmjiDkQPQ
UcXHbA==
=v6jg
-----END PGP PUBLIC KEY BLOCK-----',
        }
        apt::pin { "cisco_supplemental":
          priority   => '990',
          originator => 'Cisco_Supplemental'
        }
      }

      apt::pin { "cisco":
        priority   => '990',
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
      descr    => "Cisco Openstack Repository",
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
  if ! $::node_gateway {
    Package <| provider=='pip' |> {
      install_options => "--index-url=http://${build_node_name}/packages/simple/",
    }
  } else {
    if($::proxy) {
      Package <| provider=='pip' |> {
        install_options => "--proxy=$::proxy"
      }
    }
  }
  # (the equivalent work for apt is done by the cobbler boot, which 
  # sets this up as a part of the installation.)

  # /etc/hosts entries for the controller nodes
  host { $::controller_hostname:
    ip => $::controller_node_internal
  }

  class { 'collectd':
    graphitehost         => $build_node_fqdn,
    management_interface => $::public_interface,
  }
}

node os_base inherits base {
  $build_node_fqdn = "${::build_node_name}.${::domain_name}"

  class { ntp:
    servers     => [$build_node_fqdn],
    ensure      => running,
    autoupdate 	=> true,
  }

  # Deploy a script that can be used to test nova
  class { 'openstack::test_file':
    image_type => $::test_file_image_type,
  }

  class { 'openstack::auth_file':
    admin_password  => $admin_password,
    controller_node => $controller_node_internal,
  }

  class { "naginator::base_target": }

  # This value can be set to true to increase debug logging when
  # trouble-shooting services. It should not generally be set to
  # true as it is known to break some OpenStack components
  $verbose            = false
}

class control(
  $tunnel_ip                         = $::controller_node_internal,
  $public_address                    = $::controller_node_public,
  # ha (use site.pp.ha.example if setting to true)
  $enable_ha                         = false,
  $galera_master_ip                  = false,
  $keystone_swift_endpoint           = false,
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
  $glance_backend                    = $::glance_backend,
  $rbd_store_user                    = $::glance_ceph_user,
  $rbd_store_pool                    = $::glance_ceph_pool,
  $nova_db_password                  = $::nova_db_password,
  $nova_user_password                = $::nova_user_password,
  $rabbit_password                   = $::rabbit_password,
  $rabbit_user                       = $::rabbit_user,

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
  $enable_dhcp_agent                 = true,
  $enable_l3_agent                   = true,
  $enable_metadata_agent             = true,
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
) {

  if $enable_ha {
    # HA setup
    class { 'openstack-ha::controller':
      # Galera
      galera_monitor_password  => $galera_monitor_password,
      wsrep_sst_password       => $wsrep_sst_password,
      galera_master_ip         => $galera_master_ip,
      mysql_bind_address       => $internal_address,
      mysql_root_password      => $mysql_root_password,
      mysql_account_security   => false,
      db_host                  => $controller_cluster_vip,
      sql_idle_timeout         => '30',
      # Networking
      public_address           => $controller_cluster_vip,
      debug                    => $debug,
      verbose                  => $::verbose,
      admin_email              => $admin_email,
      admin_password           => $admin_password,
      keystone_bind_address    => $internal_address,
      keystone_host            => $controller_cluster_vip,
      keystone_db_password     => $keystone_db_password,
      keystone_admin_token     => $keystone_admin_token,
      swift                    => $keystone_swift_endpoint,
      swift_user_password      => $::swift_password,
      swift_public_address     => $::swiftproxy_cluster_vip,
      glance_bind_address      => $internal_address,
      glance_api_servers       => "${controller_cluster_vip}:9292",
      glance_db_password       => $glance_db_password,
      glance_user_password     => $glance_user_password,
      memcached_listen_ip      => $internal_address,
      cache_server_ip          => $internal_address,
      swift_store_user         => "${services_tenant}:${swift_user}",
      swift_store_key          => $::swift_password,
      swift_store_auth_address => "http://$controller_cluster_vip:5000/v2.0/",
      # nova
      enabled_apis             => 'ec2,osapi_compute',
      memcached_servers        => ["$controller01_ip:11211","${controller02_ip}:11211","${controller03_ip}:11211"],
      vncproxy_host            => '0.0.0.0',
      glance_registry_host     => $controller_cluster_vip,
      nova_bind_address        => $internal_address,
      nova_admin_tenant_name   => $services_tenant,
      nova_db_password         => $nova_db_password,
      nova_user_password       => $nova_user_password,
      rabbit_password          => $rabbit_password,
      rabbit_user              => $rabbit_user,
      rabbit_hosts             => [$controller_vip_hostname],
      rabbit_cluster_nodes     => [$controller01_hostname, $controller02_hostname, $controller03_hostname],
      # quantum
      quantum_bind_address     => $internal_address,
      quantum_auth_url         => "http://${controller_cluster_vip}:35357/v2.0",
      quantum_db_password      => $quantum_db_password,
      network_vlan_ranges      => "physnet1:${vlan_ranges}",
      bridge_interface         => $external_interface,
      enable_dhcp_agent        => true,
      # Keystone
      quantum_user_password    => $quantum_user_password,
      # horizon
      secret_key               => $secret_key,
      # cinder
      cinder_bind_address      => $internal_address,
      cinder_user_password     => $cinder_user_password,
      cinder_db_password       => $cinder_db_password,
    }
    # Sets up Nagios control-node monitoring.
    class { "naginator::control_target": }

    network_config { $::external_interface:
      ensure    => 'present',
      hotplug   => false,
      family    => 'inet',
      method    => 'manual',
      onboot    => 'true',
      notify    => Exec['network-restart'],
      options   => {
        'up'    => 'ifconfig $IFACE 0.0.0.0 up',
        'down'  => 'ifconfig $IFACE 0.0.0.0 down',
      }
    }
    # Changed from service to exec due to Ubuntu bug #440179
    exec { 'network-restart':
      command     => '/etc/init.d/networking restart',
      path        => '/usr/bin:/usr/sbin:/bin:/sbin',
      refreshonly => true
    }
  } else {
    # Non-HA setup

    # Set up Cisco or OVS core plugin.
    if $core_plugin == 'cisco' {
      $core_plugin_real = 'quantum.plugins.cisco.network_plugin.PluginV2'
    } else {
      $core_plugin_real = 'quantum.plugins.openvswitch.ovs_quantum_plugin.OVSQuantumPluginV2'
    }

    # Nexus 1000v security group settings.
    if $cisco_vswitch_plugin == 'n1k' {
      # If n1k, set security group api to nova.  The default
      # firewall_driver is NoopFirewallDriver in puppet-nova,
      # so this effectively disables security groups.
      $security_group_api_real = 'nova'
    } else {
      $security_group_api_real = 'quantum'
    }

    if ($::swift_proxy_address) {
      $swift_real = true
    } else {
      $swift_real = false
    }

    # Set up controller.
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
      security_group_api      => $security_group_api_real,

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
      # swift
      swift                   => $swift_real,
      swift_store_user        => "services:swift",
      swift_store_key         => $::swift_password,
      swift_user_password     => $::swift_password,
      swift_public_address    => $::swift_proxy_address,
    }

    # Sets up Nagios control-node monitoring.
    class { "naginator::control_target": }

    # Set up Quantum quota support.
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
        owner   => 'root',
        group   => 'root',
        content => template('nexus.ini.erb')
      } ~> Service['quantum-server']
    } else {
      $cisco_nexus_plugin_real = undef
    }

    if $nexus_credentials {
      file {'/var/lib/quantum/.ssh':
        ensure  => directory,
        owner   => 'quantum',
        require => Package['quantum-server']
      }
      nexus_creds{ $nexus_credentials:
        require => File['/var/lib/quantum/.ssh']
      }
    }

    if $core_plugin == 'cisco' {
      class { 'quantum::plugins::cisco':
        database_name     => $quantum_db_name,
        database_user     => $quantum_db_user,
        database_pass     => $quantum_db_password,
        database_host     => $db_host,
        keystone_username => 'quantum',
        keystone_password => $quantum_user_password,
        keystone_auth_url => "http://${controller_node_public}:35357/v2.0/",
        keystone_tenant   => 'services',
        vswitch_plugin    => $cisco_vswitch_plugin_real,
        nexus_plugin      => $cisco_nexus_plugin_real
      }
    }
  
    class { "coe::quantum_log": }

    # Set up various Ceph scenarios.
    if $::controller_has_mon {
      class { 'coe::ceph::control': }
    }
    elsif $::cinder_ceph_enabled {
      class { 'coe::ceph::control': }
    }
    elsif $::glance_ceph_enabled {
      class { 'coe::ceph::control': }
    }
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
  class { 'ceph_common': }
  ceph::mon { $id:
    monitor_secret => $::ceph_monitor_secret,
    mon_port       => 6789,
    mon_addr       => $::ceph_monitor_address,
  }
}

### end ceph

# Class for compute nodes.
class compute(
  $internal_ip,
  $tunnel_ip                         = $internal_ip,
  # ha (use site.pp.ha.example if setting to true)
  $enable_ha                         = false,
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
  $force_config_drive                = $::force_config_drive,
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
  $quantum                           = true,
  $quantum_user_password             = $::quantum_user_password,
  # Quantum OVS
  $enable_ovs_agent                  = true,
  $ovs_local_ip                      = $tunnel_ip,
  $ovs_bridge_mappings               = $::ovs_bridge_mappings,
  $ovs_bridge_uplinks                = $::ovs_bridge_uplinks,
  $cisco_vswitch_plugin              = $::cisco_vswitch_plugin,
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

  # Nexus 1000v security group settings.
  if $cisco_vswitch_plugin == 'n1k' {
    # If n1k, set security group api to nova.  The default
    # firewall_driver is NoopFirewallDriver in puppet-nova,
    # so this effectively disables security groups.
    $security_group_api_real     = 'nova'
  } else {
    $security_group_api_real     = 'quantum'
  }

  # If using the HA, the compute nodes get a few different
  # settings for control services.
  if ($enable_ha) {
    class { 'openstack-ha::compute':
      # Networking
      internal_address      => $internal_ip,
      # Database
      db_host               => $controller_cluster_vip,
      # Keystone
      keystone_host         => $controller_cluster_vip,
      # Rabbit
      rabbit_hosts          => [$controller_vip_hostname],
      rabbit_password       => $rabbit_password,
      rabbit_user           => $rabbit_user,
      # Nova
      libvirt_type          => $libvirt_type,
      nova_user_password    => $nova_user_password,
      nova_db_password      => $nova_db_password,
      libvirt_vif_driver    => 'nova.virt.libvirt.vif.LibvirtHybridOVSBridgeDriver',
      glance_api_servers    => "${controller_cluster_vip}:9292",
      vncproxy_host         => $controller_cluster_vip,
      vncserver_listen      => '0.0.0.0',
      memcached_servers     => ["$controller01_ip:11211","${controller02_ip}:11211","${controller03_ip}:11211"],
      enabled_apis          => 'ec2,osapi_compute',
      # Cinder
      cinder_db_password    => $cinder_db_password,
      iscsi_ip_address      => $internal_ip,
      # Quantum
      quantum_host          => $controller_cluster_vip,
      quantum_user_password => $quantum_user_password,
      quantum_auth_url      => "http://${controller_cluster_vip}:35357/v2.0",
      bridge_interface      => $external_interface,
      # General
      enabled               => true,
      debug                 => $debug,
      verbose               => $::verbose,
    }

    class { "naginator::compute_target": }

    network_config { $::external_interface:
      ensure    => 'present',
      hotplug   => false,
      family    => 'inet',
      method    => 'manual',
      onboot    => 'true',
      notify    => Exec['network-restart'],
      options   => {
        'up'    => 'ifconfig $IFACE 0.0.0.0 up',
        'down'  => 'ifconfig $IFACE 0.0.0.0 down',
      }
    }
    # Changed from service to exec due to Ubuntu bug #440179
    exec { 'network-restart':
      command     => '/etc/init.d/networking restart',
      path        => '/usr/bin:/usr/sbin:/bin:/sbin',
      refreshonly => true
    }
  } else {
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
      force_config_drive      => $force_config_drive,
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
      quantum                 => $quantum,
      quantum_user_password   => $quantum_user_password,
      # Quantum OVS
      enable_ovs_agent        => $enable_ovs_agent,
      ovs_local_ip            => $ovs_local_ip,
      bridge_mappings         => $ovs_bridge_mappings,
      bridge_uplinks          => $ovs_bridge_uplinks,
      security_group_api      => $security_group_api_real,
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

    if $::cinder_ceph_enabled {
      class { 'coe::ceph::compute':
        poolname => $::cinder_rbd_pool,
      }
    }
  }
}

# A class for standalone network nodes.
class network (
  $internal_ip,
  $tunnel_ip             = $internal_ip,
  $quantum_user_password = $::quantum_user_password,
  $enable_ovs_agent      = $::enable_ovs_agent,
  $enable_l3_agent       = $::enable_l3_agent,
  $enable_dhcp_agent     = $::enable_dhcp_agent,
  $quantum_auth_url      = "http://$::controller_node_internal:35357/v2.0",
  $keystone_host         = $::controller_node_internal,
  $quantum_host          = $::controller_node_internal,
  $ovs_local_ip          = $tunnel_ip,
  $bridge_mappings       = $::ovs_bridge_mappings,
  $bridge_uplinks        = $::ovs_bridge_uplinks,
  $rabbit_password       = $::rabbit_password,
  $rabbit_host           = $::controller_node_internal,
  $rabbit_user           = $::rabbit_user,
  $db_host               = $::controller_node_address,
  $verbose               = $::verbose,
  $enabled               = true
) {

  # Use $internal_address for $ovs_local_ip if the latter
  # isn't actually specified.
  if $ovs_local_ip {
    $ovs_local_ip_real = $ovs_local_ip
  } else {
    $ovs_local_ip_real = $internal_address
  }

  class { 'openstack::quantum':
    user_password     => $quantum_user_password,
    enable_ovs_agent  => $enable_ovs_agent,
    enable_l3_agent   => $enable_l3_agent,
    enable_dhcp_agent => $enable_dhcp_agent,
    auth_url          => $quantum_auth_url,
    keystone_host     => $keystone_host,
    ovs_local_ip      => $ovs_local_ip_real,
    bridge_mappings   => $ovs_bridge_mappings,
    bridge_uplinks    => $ovs_bridge_uplinks,
    rabbit_password   => $rabbit_password,
    rabbit_host       => $rabbit_host,
    rabbit_user       => $rabbit_user,
    db_host           => $db_host,
    verbose           => $verbose,
    enabled           => $enabled,
    enable_server     => false,
  }
}

# A class for load balancer nodes (used in the HA model).
class load-balancer (
  $controller_state,
  $swift_proxy_state,
  $controller_virtual_ip   = $::controller_cluster_vip,
  $swift_proxy_virtual_ip  = $::swiftproxy_cluster_vip,
  $keepalived_interface    = $::public_interface,
  $controller_names        = [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
  $controller_ipaddresses  = [$::controller01_ip, $::controller02_ip, $::controller03_ip],
  $swift_proxy_names       = [$::swiftproxy01_hostname, $::swiftproxy02_hostname],
  $swift_proxy_ipaddresses = [$::swiftproxy01_public_net_ip, $::swiftproxy02_public_net_ip]
) {

  class { 'openstack-ha::load-balancer':
    controller_virtual_ip   => $controller_virtual_ip,
    swift_proxy_virtual_ip  => $swift_proxy_virtual_ip,
    keepalived_interface    => $keepalived_interface,
    controller_state        => $controller_state,
    swift_proxy_state       => $swift_proxy_state,
    controller_names        => $controller_names,
    controller_ipaddresses  => $controller_ipaddresses,
    swift_proxy_names       => $swift_proxy_names,
    swift_proxy_ipaddresses => $swift_proxy_ipaddresses,
  }
}
########### Definition of the Build Node #######################
#
# Definition of this node should match the name assigned to the build node
# in your deployment.  In this example we are using build-node. Note that
# just the host name is used, not the FQDN.
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
    servers    => $::ntp_servers,
    ensure     => running,
    autoupdate => true,
  }

  class { 'naginator': }

  class { 'graphite':
    graphitehost => $build_node_fqdn,
  }

  class { 'coe::site_index': }

  # Set up a local apt cache.  Eventually this may become a local
  # mirror/repo instead.
  class { apt-cacher-ng:
    proxy          => $::proxy,
    avoid_if_range => true, # Some proxies have issues with range headers
                            # this stops us attempting to use them
                            # marginally less efficient with other proxies
  }

  if ! $::node_gateway {
    # Prefetch the pip packages and put them somewhere the openstack nodes
    # can fetch them

    file {  "/var/www/packages":
      ensure  => 'directory',
      require => File['/var/www'],
    }

    if($::proxy) {
      $proxy_pfx = "/usr/bin/env http_proxy=${::proxy} https_proxy=${::proxy} "
    } else {
      $proxy_pfx = ""
    }

    exec { 'pip2pi':
      # Can't use package provider because we're changing it's behaviour
      # to use the cache.
      command => "${proxy_pfx}/usr/bin/pip install pip2pi",
      creates => "/usr/local/bin/pip2pi",
      require => Package['python-pip'],
    }
    Package <| provider=='pip' |> {
      require => Exec['pip-cache']
    }
    exec { 'pip-cache':
      # All the packages that all nodes - build, compute and control - require
      # from pip.  We cache these ahead of time.  Note that this creates
      # /var/www/packages/simple, but you'll want to force a refresh if you
      # change the 'command' line below.
      command => "${proxy_pfx}/usr/local/bin/pip2pi /var/www/packages collectd xenapi django-tagging graphite-web carbon whisper anyjson==0.3.3 amqp==0.9.4 kombu==2.4.7",
      creates => '/var/www/packages/simple',
      require => Exec['pip2pi'],
    }
  }

  # Set the right local puppet environment up.  This builds puppetmaster
  # with storedconfigs (and a local mysql instance).
  class { puppet:
    run_master           => true,
    puppetmaster_address => $build_node_fqdn, 
    certname             => $build_node_fqdn,
    mysql_password       => 'ubuntu',
  }<-

  file {'/etc/puppet/files':
    ensure => directory,
    owner  => 'root',
    group  => 'root',
    mode   => '0755',
  }

  file {'/etc/puppet/fileserver.conf':
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
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
    unless  => "/bin/cat /var/lib/quantum/.ssh/known_hosts | /bin/grep ${args[0]}",
    command => "/usr/bin/ssh-keyscan -t rsa ${args[0]} >> /var/lib/quantum/.ssh/known_hosts",
    user    => 'quantum',
    require => Package['quantum-server']
  }
}
