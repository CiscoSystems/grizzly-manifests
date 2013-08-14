#
# This file is to serve as an example for deploying 
# two dedicated HAproxy nodes for load-balancing 
# three OpenStack Controllers and two Swift Proxies
# This example file should then be imported into your Site.pp manifest
#

node /slb01/ inherits base {

  # Required for supporting a virtual IP address not directly associated to the node.
  sysctl::value { "net.ipv4.ip_nonlocal_bind": value => "1" }

  # Keepalived is used to provide high-availability between HAProxy Nodes.
  # Two instances are created, one for the Controller Cluster VIP and the other for the Swift Proxy VIP.
  # Take note that this node is active for the Controller VIP.
  class { keepalived: }
  
  keepalived::instance { '50':
    interface         => 'eth0',
    virtual_ips       => "${controller_cluster_vip} dev eth0",
    state             => 'MASTER',
    priority          => '101',
    track_script      => ['haproxy'],
  }

  keepalived::vrrp_script { 'haproxy':
    name_is_process   => true,
  }

  # Take note that this node is the backup for the Swift Proxy VIP.
  keepalived::instance { '51':
    interface         => 'eth0',
    virtual_ips       => "${swiftproxy_cluster_vip} dev eth0",
    state             => 'BACKUP',
    priority          => '100',
    track_script      => ['haproxy'],
  }

  # This class configures all global, default, and server cluster parameters.
  # Note that all haproxy::config definition use the Controller VIP except the swift_proxy_cluster.
  class { 'haproxy': 
    defaults_options => {
      'log'     => 'global',
      'option'  => 'redispatch',
      'retries' => '3',
      'timeout' => [
        'http-request 10s',
        'queue 1m',
        'connect 10s',
        'client 1m',
        'server 1m',
        'check 10s',
      ],
      'maxconn' => '8000'
    }
  }

  haproxy::listen { 'galera_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '3306',
    options   => {
      'option'  => ['httpchk'],
      'mode'    => 'tcp',
#      'balance' => 'roundrobin'
#      'balance' => 'leastconn'
      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'galera': 
    listening_service => 'galera_cluster',
    ports             => '3306',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    # Note: Checking port 9200 due to health_check script.
    options           => 'check port 9200 inter 2000 rise 2 fall 5',
  }

#  haproxy::listen { 'rabbit_cluster':
#    ipaddress => $controller_cluster_vip,
#    ports     => '5672',
#    options   => {
#      'option'  => ['tcpka', 'tcplog'],
#      'mode'    => 'tcp',
#      'balance' => 'roundrobin'
#    }
#  }

#  haproxy::balancermember { 'rabbit;':
#    listening_service => 'rabbit_cluster',
#    ports             => '5672',
#    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
#    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
#    options           => 'check inter 2000 rise 2 fall 5',
#  }

  haproxy::listen { 'keystone_public_internal_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '5000',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['httpchk'],
      'mode'    => 'http',
#      'mode'    => 'tcp',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
#      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'keystone_public_internal':
    listening_service => 'keystone_public_internal_cluster',
    ports             => '5000',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'keystone_admin_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '35357',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['httpchk'],
      'mode'    => 'http',
#      'mode'    => 'tcp',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
#      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'keystone_admin':
    listening_service => 'keystone_admin_cluster',
    ports             => '35357',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'nova_ec2_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '8773',
    options   => {
#      'option'  => ['tcpka', 'httpchk GET /services/Cloud', 'tcplog'],
      'option'  => ['forwardfor'],
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'nova_ec2':
    listening_service => 'nova_ec2_api_cluster',
    ports             => '8773',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'nova_osapi_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '8774',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['forwardfor'],
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'nova_osapi':
    listening_service => 'nova_osapi_cluster',
    ports             => '8774',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'nova_metadata_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '8775',
    options   => {
#      'option'  => ['tcpka', 'tcplog'],
      'option'  => ['forwardfor'],
#      'mode'    => 'tcp',
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'nova_metadata':
    listening_service => 'nova_metadata_api_cluster',
    ports             => '8775',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'cinder_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '8776',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['forwardfor', 'httpchk'],
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'cinder_api':
    listening_service => 'cinder_api_cluster',
    ports             => '8776',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'glance_registry_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '9191',
    options   => {
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'glance_registry':
    listening_service => 'glance_registry_cluster',
    ports             => '9191',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'glance_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '9292',
    options   => {
      'option'  => ['tcpka', 'httpchk', 'tcplog'],
#      'option'  => ['httpchk'],
#      'mode'    => 'http',
      'mode'    => 'tcp',
#      'cookie'  => 'SERVERID rewrite',
#      'balance' => 'roundrobin'
      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'glance_api':
    listening_service => 'glance_api_cluster',
    ports             => '9292',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
#    define_cookies    => true
  }

  # Note: Failures were experienced when the balance-member was named Horizon.
  haproxy::listen { 'dashboard_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '80',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['forwardfor', 'httpchk', 'httpclose'],
      'mode'    => 'http',
      'cookie'  => 'SERVERID insert indirect nocache',
      'capture' => 'cookie vgnvisitor= len 32',
      'balance' => 'roundrobin',
      'rspidel' => '^Set-cookie:\ IP='
    }
  }

  # Note: Failures were experienced when the balance-member was named Horizon.
  haproxy::balancermember { 'dashboard':
    listening_service => 'dashboard_cluster',
    ports             => '80',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  # Uncomment if using NoVNC
  haproxy::listen { 'novnc_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '6080',
    options   => {
      'option'  => ['tcpka', 'tcplog'],
      'mode'    => 'tcp',
      'balance' => 'roundrobin'
    }
  }

  # Uncomment if using Spice
#  haproxy::listen { 'spice_cluster':
#    ipaddress => $controller_cluster_vip,
#    ports     => '6082',
#    options   => {
#      'option'  => ['tcpka', 'tcplog'],
#      'balance' => 'source'
#    }
#  }

  # Uncomment if using NoVNC
  haproxy::balancermember { 'novnc':
    listening_service => 'novnc_cluster',
    ports             => '6080',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
  }

  # Uncomment if using Spice
#  haproxy::balancermember { 'spice':
#    listening_service => 'spice_cluster',
#    ports             => '6082',
#    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
#    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
#    options           => 'check inter 2000 rise 2 fall 5',
#  }

  haproxy::listen { 'nova_memcached_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '11211',
    options   => {
      'option'  => ['tcpka', 'tcplog'],
      'mode'    => 'tcp',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'nova_memcached':
    listening_service => 'nova_memcached_cluster',
    ports             => '11211',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
  }

  haproxy::listen { 'swift_memcached_cluster':
    ipaddress => $swiftproxy_cluster_vip,
    ports     => '11211',
    options   => {
      'option'  => ['tcpka', 'tcplog'],
      'mode'    => 'tcp',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'swift_memcached':
    listening_service => 'swift_memcached_cluster',
    ports             => '11211',
    server_names      => [$::swiftproxy01_hostname, $::swiftproxy02_hostname],
    ipaddresses       => [$::swiftproxy01_public_net_ip, $::swiftproxy02_public_net_ip],
    options           => 'check inter 2000 rise 2 fall 5',
  }

  haproxy::listen { 'quantum_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '9696',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['forwardfor', 'httpchk',],
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'quantum_api':
    listening_service => 'quantum_api_cluster',
    ports             => '9696',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'swift_proxy_cluster':
    ipaddress => $swiftproxy_cluster_vip,
    ports     => '8080',
    options   => {
#      'option'  => ['httpchk GET /healthcheck'],
#      'mode'    => 'http',
      'mode'    => 'tcp',
#      'cookie'  => 'SERVERID rewrite',
#      'balance' => 'roundrobin'
      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'swift_proxy':
    listening_service => 'swift_proxy_cluster',
    ports             => '8080',
    server_names      => [$::swiftproxy01_hostname, $::swiftproxy02_hostname],
    ipaddresses       => [$::swiftproxy01_public_net_ip, $::swiftproxy02_public_net_ip],
    options           => 'check inter 2000 rise 2 fall 5',
#    define_cookies    => true
  }

}

node /slb02/ inherits base {

  # Required for supporting a virtual IP address not directly associated to the node.
  sysctl::value { "net.ipv4.ip_nonlocal_bind": value => "1" }

  # Keepalived is used to provide high-availability between HAProxy Nodes.
  # Two instances are created, one for the Controller Cluster VIP and the other for the Swift Proxy VIP.
  # Take note that this node is active for the Swift Proxy VIP.
  class { keepalived: }
  
  keepalived::instance { '50':
    interface         => 'eth0',
    virtual_ips       => "${controller_cluster_vip} dev eth0",
    state             => 'BACKUP',
    priority          => '100',
    track_script      => ['haproxy'],
  }

  # Take note that this node is the backup for the Controller Cluster VIP.
  keepalived::instance { '51':
    interface         => 'eth0',
    virtual_ips       => "${swiftproxy_cluster_vip} dev eth0",
    state             => 'MASTER',
    priority          => '101',
    track_script      => ['haproxy'],
  }

  keepalived::vrrp_script { 'haproxy':
    name_is_process   => true,
  }

  # This class configures all global, default, and server cluster parameters.
  # Note that all haproxy::config definition use the Controller VIP except the swift_proxy_cluster.
  class { 'haproxy': 
    defaults_options => {
      'log'     => 'global',
      'option'  => 'redispatch',
      'retries' => '3',
      'timeout' => [
        'http-request 10s',
        'queue 1m',
        'connect 10s',
        'client 1m',
        'server 1m',
        'check 10s',
      ],
      'maxconn' => '8000'
    }
  }

  haproxy::listen { 'galera_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '3306',
    options   => {
      'option'  => ['httpchk'],
      'mode'    => 'tcp',
#      'balance' => 'roundrobin'
#      'balance' => 'leastconn'
      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'galera': 
    listening_service => 'galera_cluster',
    ports             => '3306',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    # Note: Checking port 9200 due to health_check script.
    options           => 'check port 9200 inter 2000 rise 2 fall 5',
  }

#  haproxy::listen { 'rabbit_cluster':
#    ipaddress => $controller_cluster_vip,
#    ports     => '5672',
#    options   => {
#      'option'  => ['tcpka', 'tcplog'],
#      'mode'    => 'tcp',
#      'balance' => 'roundrobin'
#    }
#  }

#  haproxy::balancermember { 'rabbit;':
#    listening_service => 'rabbit_cluster',
#    ports             => '5672',
#    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
#    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
#    options           => 'check inter 2000 rise 2 fall 5',
#  }

  haproxy::listen { 'keystone_public_internal_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '5000',
    options   => {
      'option'  => ['tcpka', 'httpchk', 'tcplog'],
#      'option'  => ['httpchk'],
#      'mode'    => 'http',
      'mode'    => 'tcp',
#      'cookie'  => 'SERVERID rewrite',
#      'balance' => 'roundrobin'
      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'keystone_public_internal':
    listening_service => 'keystone_public_internal_cluster',
    ports             => '5000',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
#    define_cookies    => true
  }

  haproxy::listen { 'keystone_admin_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '35357',
    options   => {
      'option'  => ['tcpka', 'httpchk', 'tcplog'],
#      'option'  => ['httpchk'],
#      'mode'    => 'http',
      'mode'    => 'tcp',
#      'cookie'  => 'SERVERID rewrite',
#      'balance' => 'roundrobin'
      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'keystone_admin':
    listening_service => 'keystone_admin_cluster',
    ports             => '35357',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
#    define_cookies    => true
  }

  haproxy::listen { 'nova_ec2_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '8773',
    options   => {
#      'option'  => ['tcpka', 'httpchk GET /services/Cloud', 'tcplog'],
      'option'  => ['forwardfor'],
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'nova_ec2':
    listening_service => 'nova_ec2_api_cluster',
    ports             => '8773',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'nova_osapi_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '8774',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['forwardfor'],
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'nova_osapi':
    listening_service => 'nova_osapi_cluster',
    ports             => '8774',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'nova_metadata_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '8775',
    options   => {
#      'option'  => ['tcpka', 'tcplog'],
      'option'  => ['forwardfor'],
#      'mode'    => 'tcp',
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'nova_metadata':
    listening_service => 'nova_metadata_api_cluster',
    ports             => '8775',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'cinder_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '8776',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['forwardfor', 'httpchk'],
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'cinder_api':
    listening_service => 'cinder_api_cluster',
    ports             => '8776',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'glance_registry_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '9191',
    options   => {
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'glance_registry':
    listening_service => 'glance_registry_cluster',
    ports             => '9191',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'glance_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '9292',
    options   => {
      'option'  => ['tcpka', 'httpchk', 'tcplog'],
#      'option'  => ['httpchk'],
#      'mode'    => 'http',
      'mode'    => 'tcp',
#      'cookie'  => 'SERVERID rewrite',
#      'balance' => 'roundrobin'
      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'glance_api':
    listening_service => 'glance_api_cluster',
    ports             => '9292',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
#    define_cookies    => true
  }

  # Note: Failures were experienced when the balance-member was named Horizon.
  haproxy::listen { 'dashboard_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '80',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['forwardfor', 'httpchk', 'httpclose'],
      'mode'    => 'http',
      'cookie'  => 'SERVERID insert indirect nocache',
      'capture' => 'cookie vgnvisitor= len 32',
      'balance' => 'roundrobin',
      'rspidel' => '^Set-cookie:\ IP='
    }
  }

  # Note: Failures were experienced when the balance-member was named Horizon.
  haproxy::balancermember { 'dashboard':
    listening_service => 'dashboard_cluster',
    ports             => '80',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  # Uncomment if using NoVNC
  haproxy::listen { 'novnc_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '6080',
    options   => {
      'option'  => ['tcpka', 'tcplog'],
      'mode'    => 'tcp',
      'balance' => 'roundrobin'
    }
  }

  # Uncomment if using Spice
#  haproxy::listen { 'spice_cluster':
#    ipaddress => $controller_cluster_vip,
#    ports     => '6082',
#    options   => {
#      'option'  => ['tcpka', 'tcplog'],
#      'balance' => 'source'
#    }
#  }

  # Uncomment if using NoVNC
  haproxy::balancermember { 'novnc':
    listening_service => 'novnc_cluster',
    ports             => '6080',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
  }

  # Uncomment if using Spice
#  haproxy::balancermember { 'spice':
#    listening_service => 'spice_cluster',
#    ports             => '6082',
#    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
#    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
#    options           => 'check inter 2000 rise 2 fall 5',
#  }

  haproxy::listen { 'nova_memcached_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '11211',
    options   => {
      'option'  => ['tcpka', 'tcplog'],
      'mode'    => 'tcp',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'nova_memcached':
    listening_service => 'nova_memcached_cluster',
    ports             => '11211',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
  }

  haproxy::listen { 'swift_memcached_cluster':
    ipaddress => $swiftproxy_cluster_vip,
    ports     => '11211',
    options   => {
      'option'  => ['tcpka', 'tcplog'],
      'mode'    => 'tcp',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'swift_memcached':
    listening_service => 'swift_memcached_cluster',
    ports             => '11211',
    server_names      => [$::swiftproxy01_hostname, $::swiftproxy02_hostname],
    ipaddresses       => [$::swiftproxy01_public_net_ip, $::swiftproxy02_public_net_ip],
    options           => 'check inter 2000 rise 2 fall 5',
  }

  haproxy::listen { 'quantum_api_cluster':
    ipaddress => $controller_cluster_vip,
    ports     => '9696',
    options   => {
#      'option'  => ['tcpka', 'httpchk', 'tcplog'],
      'option'  => ['forwardfor', 'httpchk',],
      'mode'    => 'http',
      'cookie'  => 'SERVERID rewrite',
      'balance' => 'roundrobin'
    }
  }

  haproxy::balancermember { 'quantum_api':
    listening_service => 'quantum_api_cluster',
    ports             => '9696',
    server_names      => [$::controller01_hostname, $::controller02_hostname, $::controller03_hostname],
    ipaddresses       => [$::controller01_ip, $::controller02_ip, $::controller03_ip],
    options           => 'check inter 2000 rise 2 fall 5',
    define_cookies    => true
  }

  haproxy::listen { 'swift_proxy_cluster':
    ipaddress => $swiftproxy_cluster_vip,
    ports     => '8080',
    options   => {
#      'option'  => ['httpchk GET /healthcheck'],
#      'mode'    => 'http',
      'mode'    => 'tcp',
#      'cookie'  => 'SERVERID rewrite',
#      'balance' => 'roundrobin'
      'balance' => 'source'
    }
  }

  haproxy::balancermember { 'swift_proxy':
    listening_service => 'swift_proxy_cluster',
    ports             => '8080',
    server_names      => [$::swiftproxy01_hostname, $::swiftproxy02_hostname],
    ipaddresses       => [$::swiftproxy01_public_net_ip, $::swiftproxy02_public_net_ip],
    options           => 'check inter 2000 rise 2 fall 5',
#    define_cookies    => true
  }

}
