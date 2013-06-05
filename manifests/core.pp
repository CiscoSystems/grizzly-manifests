# This document serves as an example of how to deploy
# basic multi-node openstack environments.
# In this scenario Quantum is using OVS with GRE Tunnels
# Swift is not included.


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
        key => "E8CC67053ED3B199",
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
	  keystone_admin_token => $keystone_admin_token,
	  controller_node      => $controller_node_internal,
  }

  class { "naginator::base_target": }

  # This value can be set to true to increase debug logging when
  # trouble-shooting services. It should not generally be set to
  # true as it is known to break some OpenStack components
  $verbose            = false

}

class control(
  $internal_ip,
  $vm_net_ip
) {

  # in the currently support deployment scenario
  # all network control services are on the controller.
  # this is not recomended for production and is merely
  # used for test setups
  $enable_dhcp_agent      = true
  $enable_l3_agent        = true
  $enable_metadata_agent  = true

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

    # TODO this needs to be added
    glance_backend          => $glance_backend,

    nova_db_password        => $nova_db_password,
    nova_user_password      => $nova_user_password,
    rabbit_password         => $rabbit_password,
    rabbit_user             => $rabbit_user,
    # TODO deprecated
    #export_resources        => false,

    ######### quantum variables #############
    # need to set from a variable
    # database
    db_host     => $controller_node_address,
    quantum_db_password => $quantum_db_password,
    quantum_db_name     => 'quantum',
    quantum_db_user     => 'quantum',
    # enable quantum services
    enable_dhcp_agent     => $enable_dhcp_agent,
    enable_l3_agent       => $enable_l3_agent,
    enable_metadata_agent => $enable_metadata_agent,
    # Metadata Configuration
    metadata_shared_secret => 'secret',
    # ovs config
    ovs_local_ip        => $vm_net_ip,
    bridge_interface    => $external_interface,
    enable_ovs_agent    => true,
    # Keystone
    quantum_user_password => $quantum_user_password,
    # horizon
    secret_key => 'super_secret',
    # cinder
    cinder_user_password => $cinder_user_password,
    cinder_db_password   => $cinder_db_password,
  }

  class { "naginator::control_target": }

}


class compute(
  $internal_ip,
  $vm_net_ip
) {

  class { 'openstack::compute':
    # keystone
    db_host            => $controller_node_internal,
    keystone_host      => $controller_node_internal,
    quantum_host       => $controller_node_internal,
    internal_address   => $internal_ip,
    libvirt_type       => $libvirt_type,
    multi_host         => $multi_host,
    # rabbit
    rabbit_host        => $controller_node_internal,
    rabbit_password    => $rabbit_password,
    rabbit_user        => $rabbit_user,
    # nova
    nova_user_password => $nova_user_password,
    nova_db_password   => $nova_db_password,
    glance_api_servers => "${controller_node_internal}:9292",
    vncproxy_host      => $controller_node_public,
    vnc_enabled        => true,
    # cinder parameters
    cinder_db_password    => $cinder_db_password,
    manage_volumes        => true,
    volume_group          => 'cinder-volumes',
    setup_test_volume     => true,
    # quantum config
    quantum			          => true,
    quantum_user_password => $quantum_user_password,
    # Quantum OVS
    enable_ovs_agent      => true,
    ovs_local_ip          => $vm_net_ip,
     # Quantum L3 Agent
    enable_l3_agent       => false,
    enable_dhcp_agent     => false,
    # general
    enabled               => true,
    verbose               => $verbose,
  }

  class { "naginator::compute_target": }

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

