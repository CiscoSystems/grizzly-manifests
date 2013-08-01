import 'core'

node build-server {

  $nexus_hash = {'1.1.1.1' => {'compute1' => '1/1', 'compute2' => '1/2' }, '2.2.2.2' => { 'compute3' => '1/3', 'compute4' => '1/4'} }

  $nexus_credentials = ['1.1.1.1/nexus_username1/secret1',
                        '2.2.2.2/nexus_username2/secret2']
  nexus_creds{$nexus_credentials:}  
}

