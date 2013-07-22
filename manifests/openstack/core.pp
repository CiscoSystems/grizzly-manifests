# This is the base node definitions for the 
# Grizzly puppet MaaS combo install
# This document serves as an example of how to deploy
# basic multi-node openstack environments.
# In this scenario Quantum is using OVS with GRE Tunnels
# Swift is not included.

node base {
  $build_node_fqdn = "${::build_node_name}.${::domain_name}"
  
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
      # Get apt pgp key from template.
      $aptkey = template("aptkey.erb")
      apt::source { "cisco-openstack-mirror_grizzly":
        location => $::location,
        release => "grizzly-proposed",
        repos => "main",
        key => "E8CC67053ED3B199",
        key_content => $aptkey,
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
}

node os_base inherits base {
  $build_node_fqdn = "${::build_node_name}.${::domain_name}"

  class { 'openstack::auth_file':
    admin_password       => $admin_password,
    keystone_admin_token => $keystone_admin_token,
    controller_node      => $controller_node_internal,
  }

  # This value can be set to true to increase debug logging when
  # trouble-shooting services. It should not generally be set to
  # true as it is known to break some OpenStack components
  $verbose = true
}

class control(
  $tunnel_ip,
  $public_address          = $::controller_node_public,
  # network
  $internal_address        = $::controller_node_internal,
  # by default it does not enable multi-host mode
  $multi_host              = $::multi_host,
  $verbose                 = $::verbose,
  $auto_assign_floating_ip = $::auto_assign_floating_ip,
  $mysql_root_password     = $::mysql_root_password,
  $admin_email             = $::admin_email,
  $admin_password          = $::admin_password,
  $keystone_db_password    = $::keystone_db_password,
  $keystone_admin_token    = $::keystone_admin_token,
  $glance_db_password      = $::glance_db_password,
  $glance_user_password    = $::glance_user_password,

  # TODO this needs to be added
  $glance_backend          = $::glance_backend,

  $nova_db_password        = $::nova_db_password,
  $nova_user_password      = $::nova_user_password,
  $rabbit_password         = $::rabbit_password,
  $rabbit_user             = $::rabbit_user,
  # TODO deprecated
  #export_resources        = false,

  ######### quantum variables #############
  # need to set from a variable
  # database
  $db_host                 = $::controller_node_address,
  $quantum_db_password     = $quantum_db_password,
  $quantum_db_name         = 'quantum',
  $quantum_db_user         = 'quantum',
  # enable quantum services
  $enable_dhcp_agent       = $true,
  $enable_l3_agent         = $true,
  $enable_metadata_agent   = $true,
  # Metadata Configuration
  $metadata_shared_secret  = 'secret',
  # ovs config
  $ovs_local_ip            = $tunnel_ip,
  $bridge_interface        = $::external_interface,
  $enable_ovs_agent        = true,
  # Keystone
  $quantum_user_password   = $::quantum_user_password,
  # horizon
  $secret_key              = 'super_secret',
  # cinder
  $cinder_user_password    = $::cinder_user_password,
  $cinder_db_password      = $::cinder_db_password,
)
{
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
    # Keystone
    quantum_user_password   => $quantum_user_password,
    # horizon
    secret_key              => $secret_key,
    # cinder
    cinder_user_password    => $cinder_user_password,
    cinder_db_password      => $cinder_db_password,
  }
}


class compute(
  $internal_ip,
  $tunnel_ip,
  # keystone
  $db_host               = $::controller_node_internal,
  $keystone_host         = $::controller_node_internal,
  $quantum_host          = $::controller_node_internal,
  $internal_address      = $internal_ip,
  $libvirt_type          = $::libvirt_type,
  $multi_host            = $::multi_host,
  # rabbit
  $rabbit_host           = $::controller_node_internal,
  $rabbit_password       = $::rabbit_password,
  $rabbit_user           = $::rabbit_user,
  # nova
  $nova_user_password    = $::nova_user_password,
  $nova_db_password      = $::nova_db_password,
  $glance_api_servers    = "${::controller_node_internal}:9292",
  $vncproxy_host         = $::controller_node_public,
  $vnc_enabled           = true,
  # cinder parameters
  $cinder_db_password    = $::cinder_db_password,
  $manage_volumes        = true,
  $volume_group          = 'cinder-volumes',
  $setup_test_volume     = true,
  # quantum config
  $quantum	         = true,
  $quantum_user_password = $::quantum_user_password,
  # Quantum OVS
  $enable_ovs_agent      = true,
  $ovs_local_ip          = $tunnel_ip,
  # Quantum L3 Agent
  $enable_l3_agent       = false,
  $enable_dhcp_agent     = false,
  # general
  $enabled               = true,
  $verbose               = $::verbose,
)
{
  class { 'openstack::compute':
    # keystone
    db_host               => $db_host,
    keystone_host         => $keystone_host,
    quantum_host          => $quantum_host,
    internal_address      => $internal_address,
    libvirt_type          => $libvirt_type,
    multi_host            => $multi_host,
    # rabbit
    rabbit_host           => $rabbit_host,
    rabbit_password       => $rabbit_password,
    rabbit_user           => $rabbit_user,
    # nova
    nova_user_password    => $nova_user_password,
    nova_db_password      => $nova_db_password,
    glance_api_servers    => $glance_api_servers,
    vncproxy_host         => $vncproxy_host,
    vnc_enabled           => $vnc_enabled,
    # cinder parameters
    cinder_db_password    => $cinder_db_password,
    manage_volumes        => $manage_volumes,
    volume_group          => $volume_group,
    setup_test_volume     => $setup_test_volume,
    # quantum config
    quantum	          => $quantum,
    quantum_user_password => $quantum_user_password,
    # Quantum OVS
    enable_ovs_agent      => $enable_ovs_agent,
    ovs_local_ip          => $ovs_local_ip,
     # Quantum L3 Agent
    enable_l3_agent       => $enable_l3_agent,
    enable_dhcp_agent     => $enable_dhcp_agent,
    # general
    enabled               => $enabled,
    verbose               => $verbose,
  }
}
