#! /usr/bin/python
import os
import string
import shutil
import sys
import getpass
import socket
import re
import crypt
import getpass
import pwd
import datetime
import getopt

# Globals
version = 20
log_path = '/home/n1kv/logs'
if not os.path.exists(log_path):
    os.makedirs(log_path)

inputfile = ''
interactive_mode = 0
stop_file_read = 0

def get_globals(argv):
   try:
      opts, args = getopt.getopt(argv,"hf:i",["ifile="])
   except getopt.GetoptError:
      print 'create_sitepp.py -f <inputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print "These are the different options for this script"
         print "create_site.py"
         print 'create_sitepp.py -f <inputfile> '
         print ""
         sys.exit()
      if opt == '-i':
         print "Interactive mode turned OFF"
         global interactive_mode
         interactive_mode = 1
      elif opt in ("-f", "--ifile"):
         if not arg:
            print "A file name should be provided with -f option"
            exit()
         tempinput = arg
         if not (os.path.isfile(tempinput)):
             print "Input file not found"
             exit()
         else:
            os.system ('cp %s "temp_input.txt"' % tempinput)
            global inputfile
            inputfile = "temp_input.txt"


def get_yes_no(yes_no_q, search_str):
    out = 0
    if not (inputfile == ""):
        if not (search_str == "NONE"):
            out = get_from_file(yes_no_q, search_str)
            if not (out == "NONE"):
                out = int(out)
                log_site(search_str, out)
                return out
    while True:
        i = raw_input("%s" % yes_no_q )
        if i.lower() in ('yes','y'):
            out = 1
            break
        elif i.lower() in ('no','n'):
            out = 0
            break
        else:
            print("Wrong values Try again")
            continue
    log_site(search_str, out)
    return out


def create_element(my_list):
    my_string = ""
    list_len = len(my_list)
    k = 0
    while True:
        if(k == list_len):
            break
        else:
            my_string = my_string + my_list[k]
            k = k +1

    my_string_1 = my_string.lstrip(" ")
    return my_string_1


def get_vtep(line):
    my_list = []
    return_list = []
    comma = ","
    paren = "]"
    open_paren = "["
    escape = "\'"
    my_string = ""
    word = line.split()[0]
    act_line = line.strip(word)
    i = 0
    while True:
        if (act_line[i] == comma):
            # Check if we already saw an escape character
            if (act_line[i-1] == "\'"):
                concat_str = create_element(my_list)
                return_list.append(concat_str)
                my_list = []
                i = i + 1
                continue
            #This is a comma in between the escapes. Continue scanning
            else:
                my_list.append(act_line[i])
                i = i + 1
                continue

        elif (act_line[i] == paren):
            break
        if (act_line[i] == escape or act_line[i] == open_paren):
            i = i + 1
            continue
        else:
            my_list.append(act_line[i])
            i = i + 1

    concat_str = create_element(my_list)
    return_list.append(concat_str)
    return return_list


def get_vtep_list_from_file(search_string, no_of_entries):
    tmp_list = []
    test_file = file(inputfile, 'r')
    for line in test_file:
        if search_string in line:
            tmp_list = get_vtep(line)

    test_file.close()
    return tmp_list

# Get the list entries for search nodes
def get_list_from_file(search_string, no_of_entries):
    tmp_list = []
    test_file = file(inputfile, 'r')
    for line in test_file:
        if search_string in line:
            j = int(no_of_entries)
            i = 1
            while True:
                if (i  > j):
                    test_file.close()
                    return tmp_list
                word = line.split()[i]
                temp_word = word.strip('[')
                temp_word1 = temp_word.strip(']')
                temp_word2 = temp_word1.strip(',')
                temp_word3 = temp_word2.strip('\'')
                tmp_list.append(temp_word3)
                i = i +1

    test_file.close()
    return tmp_list

def check_if_file_exists_and_backup():
    #First check if the file already exists and if so
    #prompt the user if it is OK to replace 
    overwrite = 0
    total_backup_files = 10
    total_log_data_files = 20
    if (os.path.isfile('/etc/puppet/manifests/site.pp')):
        print "A site.pp file is already present"
        print "If you run choose to proceed this file"
        print "will be backed up and a new site.pp file will be created"
        overwrite = get_yes_no_plane_vanilla("Moving existing site.pp to"\
                                 " /home/n1kv/logs/site.pp.1. Proceed? [Y/N]? ",
                                 "NONE")
    else:
        overwrite = 1

    if (overwrite == 0):
        print "User selected NO. So exiting"
        exit()

    # Backup site.pp files. Upto 10
    n = total_backup_files - 1
    while True:
        if (n == 0):
            break
        if (os.path.isfile('/home/n1kv/logs/site.pp.%s' % n)):
            tmp = n + 1
            shutil.copy2('/home/n1kv/logs/site.pp.%s' % n,
                            '/home/n1kv/logs/site.pp.%s' % tmp)
        n = n -1

        if (os.path.isfile('/etc/puppet/manifests/site.pp')):
            shutil.copy2('/etc/puppet/manifests/site.pp', 
                              '/home/n1kv/logs/site.pp.1')

    # Backup log and data files (upto 5)
    x = total_log_data_files -1
    while True:
        if (x == 0):
            break
        if (os.path.isfile('/home/n1kv/logs/site_data_file.txt.%s' % x)):
            tmp = x + 1
            shutil.copy2('/home/n1kv/logs/site_data_file.txt.%s' % x, 
                      '/home/n1kv/logs/site_data_file.txt.%s' % tmp)
        if (os.path.isfile('/home/n1kv/logs/log_site_pp.txt.%s' % x)):
            tmp = x + 1
            shutil.copy2('/home/n1kv/logs/log_site_pp.txt.%s' % x, 
                       '/home/n1kv/logs/log_site_pp.txt.%s' % tmp)
        x = x -1

        one = 1
        if (os.path.isfile('/home/n1kv/logs/log_site_pp.txt')):
            shutil.copy2('/home/n1kv/logs/log_site_pp.txt', 
                  '/home/n1kv/logs/log_site_pp.txt.%s' % one)
        if (os.path.isfile('/home/n1kv/logs/site_data_file.txt')):
            shutil.copy2('/home/n1kv/logs/site_data_file.txt', 
                   '/home/n1kv/logs/site_data_file.txt.%s' % one)

def get_vsm_role():
    
    print ""
    print "========================================================="
    print "VSM Role options"
    print "1. Standalone"
    print "2. Primary"
    print "========================================================="
    print ""

    if not (inputfile == ""):
        out = get_from_file("vsm_role","vsm_role")
        if not (out == "NONE"):
            log_site("vsm_role", out)
            return out

    while True:
        u_input = raw_input("Select 1 or 2: ")
        if (u_input.isdigit()):
           u_input = int(u_input)
           if (u_input == 1):
               role = "standalone" 
               break
           elif (u_input == 2):
               role = "primary"
               break
           else:
               print "Valid values are 1 (Standalone) and 2 (primary). Try again"
               continue
        else:
            print "Valid values are 1 (Standalone) and 2 (primary). Try again"
            continue
    log_site("vsm_role", role)
    return role


def extractIP(ipStr):
    l = re.split('(.*)\.(.*)\.(.*)\.(.*)', ipStr)
    return l[1:-1]

def get_gb_def(cob_node_subnet):
    list = extractIP(cob_node_subnet)
    new_string = "%s." % list[0] + "%s." % list[1] + "%s." % list[2] + "%"
    return new_string

def get_password():
    print "Password you want to configure on the node (Default ubuntu)\n"
    while True:
        cleartext1 = getpass.getpass()
        if (cleartext1 == ""):
            cleartext2 = "ubuntu"
            break
        cleartext2 = getpass.getpass()
        if (cleartext1 != cleartext2):
            print "Passwords do not match. Try again"
            continue
        else:
            break
    return cleartext2

def log_site(log1, log2):
    site_pp_log.write(datetime.datetime.now().isoformat())
    site_pp_log.write(': User entered %s ' % log1)
    site_pp_log.write('to %s \n' % log2)
    site_data_file.write(log1)
    site_data_file.write(' %s \n' % log2)
    

def help(input):
    return {
        'ntp_servers': "NTP server for the nodes",
        'domain_name': "Domain name to be configured",
        'domain_id': "domain ID. Can be a random number. Default is 111",
        'admin_user': "User name yu ID. Can be a random number. Default is 111",
        'controller_hostname': "domain ID. Can be a random number. Default is 111",
        'public_interface': "Interface that connects to the outside world",
        'external_interface': "The external_interface is used for"\
                " external connectivity in association with the l3_agent"\
                " external router interface, providing floating IPs",
        'No_of_compute_nodes': "Number of compute nodes you want to configure",
        'vsm_primary_hostname': "Primary VSM hostname",
        'sec_kvm_host': "Secondary VSM Hostname",
        'vemimage': "Location and name of vem image",
        'vsmimage': "Location and name of vsm image",
        'controller_node_address': "Controller node IP address ",
        'controller_node_network': "Controller node network ",
        'controller_cimc': "Controller KVM console IP address ",
        'compute_node_ip': "IP address you want to configure on"\
                          " the compute node ",
        'compute_node_cimc': "Compute node KVM console IP address ",
        'ucs_node_cimc': "UCS node KVM console IP address ",
        'vsm_node_ip': "IP address you want to specify to vsm node",
        'vsm_node_cimc': "VSM node KVM console IP address ",
        'controller_mac': "Controller mac address ",
        'compute_mac': "Compute node mac address ",
        'ucs_mac': "ucs blade mac address",
        'vsm_pri_mac': "VSM MAC address of the cobbler node definition"\
                           " in site.pp. It is the MAC of the physical node ",
        'sec_vsm_mac': "Secondary VSM mac address ",
        'ucs_service_name': "ucs service name VSM ",
        'sec_vsm_service_name': "Secondary VSM service name ",
        'sec_vsm_ip': "Secondary VSM IP ",
        'sec_kvm_host': "Secondary KVM host ",
        'vsm_subgroup': "Subgroup of VSM node ",
        'vsm_service_name': "ucs service name for VSM ",
        'vsm_compute_pw': "VSM compute password ",
        }.get(input, "Help not provided yet")

def get_yes_no_plane_vanilla(question_str, default):
    out = 0
    while True:
        i = raw_input("%s" % question_str )
        if i.lower() in ('yes','y'):
            out = 1
            break
        elif i.lower() in ('no','n'):
            out = 0
            break
        elif default.lower() in ('yes', 'y'):
            out = 1
            break
    return out


# Read from the data file
def get_from_file(input_str, help_string):
    global stop_file_read
    if (stop_file_read == 1):
        return "NONE"
    data_file = file(inputfile, 'r')
    word = "NONE"
    for line in data_file:
        if help_string in line:
            word = line.split()[1]
            if (help_string == "total_compute_nodes" \
                            or help_string == "number_of_ucs_nodes" \
                            or help_string == "total_nw_nodes" \
                            or help_string == "nw_node_config" ):
                break 
            print "Got [%s] from file" % word + " for [%s]" % help_string
            if (interactive_mode == 0):
                user_result = get_yes_no_plane_vanilla("Do you want to"\
                          " accept it:[Y/N]? (Default Yes) ", "yes")
                if (user_result == 0):
                    word = "NONE"
            else:
                return word
            break
    data_file.close()
    return word


#Print the help strings
def print_help_str(help_str):
    print_string = help(help_str)
    print print_string


#Get user input either from a file or user
def get_user_input(input_str, help_str, default):
    if not (inputfile == ""):
        out = get_from_file(input_str,help_str)
        if not (out == "NONE"):
            if not (help_str == "domain_id" or \
                  help_str == "vemimage" or help_str == "vsmimage" \
                  or help_str == "gw_image_location"):
                log_site(help_str, out)
            return out
    while True:
        out = raw_input("%s" % input_str)
        if (out == '?'):
            print_help_str(help_str)
            continue
        if (out == ""):
            if not (default == "NONE"):
                out = default
                break
            else:
                print "Empty Input: Try again"
        else:
            break
    if not (help_str == "domain_id" or \
              help_str == "vemimage" or help_str == "vsmimage" \
              or help_str == "gw_image_location"):
        log_site(help_str, out)
    return out


# Check IP format
def ip_format_check(ip):
    return(re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$",ip))

def check_ip(ip):
    try:
        socket.inet_aton(ip)
        return 1
    except socket.error:
        return 0


def mac_format_check(mac):
    return re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", 
                                  mac.lower())

# Get valid IP address 
def get_valid_ip(ip_str, help_str, default):
    if not (inputfile == ""):
        out = get_from_file(ip_str,help_str)
        if not (out == "NONE"):
            log_site(help_str, out)
            return out
    print ""
    ip = raw_input("%s" % ip_str)
    ip = ip.strip()
    while True:
        if (ip == ""):
            if not (default == "NONE"):
                ip = default
                break
        if (ip == "?"):
           print_help_str(help_str)
           ip = raw_input("%s" % ip_str)
           ip = ip.strip()
           continue
        if (ip_format_check(ip) and (check_ip(ip) == 1)):
             break
        else:
            print ""
            print "IP address format 10.10.10.1"
            print("Wrong format given. Try again")
            print ""
            ip = raw_input("%s" % ip_str)
            ip = ip.strip()
            continue
    log_site(help_str, ip)
    return ip



# Get a valid MAC address
def get_valid_mac(mac_str, help_str, default):
    if not (inputfile == ""):
        out = get_from_file(mac_str,help_str)
        if not (out == "NONE"):
            log_site(help_str, out)
            return out
    mac = raw_input("%s" % mac_str)
    mac = mac.strip()
    while True:
        # If no output assign default
        if (mac == ""):
            if not (default == "NONE"):
                mac = default
                break
        if (mac == "?"):
           print_help_str(help_str)
           mac = raw_input("%s" % mac_str)
           mac = mac.strip()
           continue
        if(mac_format_check(mac)):
             break
        else:
            print("Wrong MAC format. Try again")
            mac = raw_input("%s" % mac_str)
            mac = mac.strip()
            continue
    log_site(help_str, mac)
    return mac

##############################################################
######## Beginning of the script. User inputs ################
##############################################################

print "      Welcome!!! This script will create the site.pp file"
print ""
print ""
print "      For help enter ? "
print "      All the information entered will be saved in "
print "      /home/n1kv/logs/site_data_file.txt file "
print ""
print " YOU HAVE TO BE A ROOT USER TO RUN THIS SCRIPT"
print ""
print " Please make sure you have the following ready before you start"
print "1. vsm and vem image locations and the images are actually present there"
print "2. You are aware of the Domain id to be used in the setup"
print "3. Make sure you have created an uplink port-profile (type Ethernet) in the VSM. (If the VSM is on N1010)"
print "4. Decide the external and physical interfaces of the COI nodes "

print ""

get_globals(sys.argv[1:])
stop_file_read = 0
# Open output file
check_if_file_exists_and_backup()
site_pp_log = file('/home/n1kv/logs/log_site_pp.txt', 'w')
site_pp_log.write('Script started at %s ' % datetime.datetime.now().isoformat())
site_pp_log.write('VERSION %s\n' % version)
site_data_file = file('/home/n1kv/logs/site_data_file.txt', 'w')
sitepp = file('site.pp.temp', 'w') 

print "=================================================================="
print('\nNTP server name: Format looks like this "ntp.esl.cisco.com"\n ')
print "==================================================================="
ntp_server = get_user_input("NTP Server: ", "ntp_servers", "NONE")

print "===================================================="
print('\n          Domain name format "cisco.com"\n')
print "This domain should be the same domain the build server is on"
print ""
print "===================================================="
domain_name = get_user_input("Domain name: ", "domain_name", "NONE")

print "==================================================================="
print('\nvem image location format ' )
print('"/home/image/nexus_1000v_vem-12.04-5.2.1.SK1.2.0.409.S0-16.deb" \n')
print "==================================================================="
while True:
    vem_image_location = get_user_input("vem image location. Provide full path"\
                               " along with file name: ", "vemimage", "NONE")
    vem_image_location = vem_image_location.strip()
    if (os.path.isfile('%s' % vem_image_location)):
        log_site("vemimage", vem_image_location)
        break
    else:
        print "File not present. Please check and provide the right location"
        continue

print "=========================================================="
print "        Build server configuration begins"
print ""
print " IP Address format 10.1.1.1"
print ""

cob_node_ip = get_valid_ip("Build server IP address: (Interface "\
                            "pointing towards the openstack network) ", 
                            "cobbler_node_ip",
                            "NONE")
cob_node_subnet = get_valid_ip("Build server network address "\
                          "(Network of COI nodes): ", "node_subnet",
                         "NONE")
 
cob_node_netmask = get_valid_ip("Build server subnet mask: "\
                           "(Default 255.255.255.0) ", 
                            "node_netmask", "255.255.255.0")

cob_node_gw = get_valid_ip("Subnet gateway (Gateway of COI nodes): ", 
                             "node_gateway", "NONE")

print "        End of Build server configuration "
print "=========================================================="
print ""

db_def_val = get_gb_def(cob_node_subnet)

print ""

login = get_user_input("Login user name that you want to setup for the"\
                      " COI nodes: (Default localadmin) ",
                      "admin_user", "localadmin")
print ""
cleartext = get_password()
password = crypt.crypt(cleartext, '$6$UfgWxrIv$')

#Interfaces
print "============================================================"
print "The public_interface will have an IP address reachable by"
print "all other nodes in the openstack cluster.  This address will"
print "be used for API Access, for the Horizon UI, and as an endpoint"
print "for the default GRE tunnel mechanism used in the OVS network"
print "configuration."
print "============================================================"
print ""

public_interface = get_user_input("Public interface (Default eth2): ", 
                                     "public_interface", "eth2")
print "============================================================"
print "The external interface is applicable for network nodes ONLY"
print "It used to provide a Layer2 path for"
print "the l3_agent external router interface.  It is expected that"
print "this interface be attached to an upstream device that provides"
print "a L3 router interface, with the default router configuration"
print "assuming that the first non \"network\" address in the external"
print "network IP subnet will be used as the default forwarding path"
print "if no more specific host routes are added."
print "============================================================"
print ""

external_interface = get_user_input("External interface (Default eth3): ",
                                    "external_interface", "eth3")
print ""
print "============================================================"
print "Uplink Interface: This port-profile is for data communication"
print "to and from the nodes, and the following"
print "Ethernet will be used on the compute nodes."
print "Uplink interface format is \"eth3:sys-uplink, eth4:sys-uplink\""
print "============================================================"
print ""
uplink_interface = get_user_input("Uplink interface (Default eth3:sys-uplink): ",
                                    "uplink", "eth3:sys-uplink")

#all_are_ucs_blades = get_yes_no("Are you configuring UCS blades "\
#                              "for your setup[Y/N]? ", "all_are_ucs_blades")
#if (all_are_ucs_blades == 1):
#    is_ucs_controller = 1
#    is_ucs_blade = 1
#    nw_node_is_ucs_blade = 1
#    vsm_is_ucs = 1
#    secvsm_is_ucs = 1
#else:
is_ucs_controller = 0
is_ucs_blade = 0
nw_node_is_ucs_blade = 0
vsm_is_ucs = 0
secvsm_is_ucs = 0

    
# Controller node configs
print ""
print "=================================================================="
print "Control node configuration begins "
print ""
is_ucs_controller = get_yes_no("Will your controller be a UCS blade:[Y/N]? ",
                            "is_ucs_controller")

controller_cimc = get_valid_ip("Controller CIMC address: ", 
                                  "controller_cimc", "NONE")
control_username = \
            get_user_input("Controller CIMC user login (Default admin): ", 
                             "control_username", "admin")
control_password = \
            get_user_input("Controller user password (Default password): ",
                             "control_password", "password")
if (is_ucs_controller == 1):
    ucs_control_service_name = get_user_input("Controller Service profile: ", 
                                 "ucs_control_service_name", "NONE")
    print "=============================================="
    print "If your service profile is not under root"
    print "provide the subgroup it is under"
    print "=============================================="
    control_subgroup = \
                   get_yes_no("Do you want to provide the subgroup [Y/N]? ", 
                              "control_subgroup")

    if (control_subgroup == 1):
        controller_subgroup_name = get_user_input("UCS Blade subgroup: ", 
                                     "controller_subgroup_name", "NONE")
    else:
        controller_subgroup_name = "NONE"
             
controller_ip = get_valid_ip("IP address of open stack controller: ", 
                               "controller_node_address", "NONE")
controller_network = get_valid_ip("Controller network address: ", 
                                  "controller_node_network", "NONE")
print ""
print "=================================================================="
print "All hostnames should be all lowercase."
print "Any uppercase letters entered will be changed to lower case"
print "=================================================================="
print""

controller_hostname = get_user_input("Controller hostname: ", 
                                "controller_hostname", "NONE")
controller_hostname = controller_hostname.lower()
print "=================================================================="
print "   Mac address format 11:22:33:44:55:66"
print "=================================================================="
print ""
controller_mac = get_valid_mac("Mac address of the controller node: ", 
                               "controller_mac", "NONE")
    
print ""
print ("End of control node configuration ")
print "=================================================================="
print ""

print ""
print " Compute nodes configuration begins"
print ""
print "==================================================================="       
    
#Compute nodes
c_mac_list = []
c_ip_list = []
c_host_list = []
cimc_ip_list = []
c_vtep_list = []
compute_vtep_diff_subnet_list = []
c_dhcp_enable_list = []
ucs_mac_list = []
ucs_ip_list = []
ucs_host_list = []
ucs_cimc_list = []
login_user_list = [] 
pw_list = []
ucs_service_name_list = []
ucs_pw_list = []
ucs_admin_user_list = [] 
ucs_subgroup_list = []
ucs_vtep_list = []
ucs_dhcp_enable_list = []
ucs_vtep_diff_subnet_list = []

from_file = 0
no_ucs = 0
ucs_subgroup = "NONE"
com = 0
new_nodes = 0
if (inputfile == ""):
    com = raw_input("How many compute nodes do you want to configure? ")
else:
    t_nodes_from_file = get_from_file("Compute Nodes", 
                                    "total_compute_nodes")
    if not (t_nodes_from_file == "NONE"):
        total_c_nodes = int(t_nodes_from_file)
        if (total_c_nodes > 0):
            ucs_from_file = get_from_file("number_of_ucs_nodes", 
                                               "number_of_ucs_nodes")
            if (ucs_from_file == "NONE"):
                no_ucs = 0
            else:
                no_ucs = int(ucs_from_file)

            actual_compute_nodes = total_c_nodes - no_ucs
            c_ip_list = get_list_from_file("compute_node_ip_list", 
                                              actual_compute_nodes)
            c_host_list = get_list_from_file("compute_node_host_list", 
                                           actual_compute_nodes)
            c_mac_list = get_list_from_file("compute_node_mac_list", 
                                            actual_compute_nodes)
            cimc_ip_list = get_list_from_file("compute_node_cimc_ip_list", 
                                          actual_compute_nodes)
            login_user_list = get_list_from_file("login_user_list", 
                                          actual_compute_nodes)
            pw_list = get_list_from_file("pw_list", actual_compute_nodes)
            c_dhcp_enable_list = get_list_from_file("c_dhcp_enable_list",
                                                    actual_compute_nodes)
            c_vtep_list = get_vtep_list_from_file("c_vtep_list", 
                                           actual_compute_nodes)
            compute_vtep_diff_subnet_list = get_vtep_list_from_file(\
                         "compute_vtep_diff_subnet_list", 
                         actual_compute_nodes)
            if (no_ucs > 0):
                ucs_cimc_list = get_list_from_file("ucs_cimc_list", no_ucs)
                ucs_host_list = get_list_from_file("ucs_host_list", no_ucs)
                ucs_service_name_list = \
                           get_list_from_file("ucs_service_name_list", no_ucs)
                ucs_pw_list = get_list_from_file("ucs_pw_list", no_ucs)
                ucs_admin_user_list = get_list_from_file("ucs_admin_user_list", 
                                                      no_ucs)
                ucs_mac_list = get_list_from_file("ucs_mac_list", no_ucs)
                ucs_ip_list = get_list_from_file("ucs_ip_list", no_ucs)
                ucs_subgroup_list = \
                     get_list_from_file("ucs_subgroup_list", no_ucs)
                ucs_vtep_list = get_vtep_list_from_file("ucs_vtep_list", no_ucs)
                ucs_dhcp_enable_list = \
                          get_list_from_file("ucs_dhcp_enable_list", no_ucs)
                ucs_vtep_diff_subnet_list = \
                          get_list_from_file("ucs_vtep_diff_subnet_list", 
                                            no_ucs)
                log_site("number_of_ucs_nodes", no_ucs)

            print "You can increase the number of compute nodes"
            print ""
            print "Found %s compute nodes in the data file." \
                               % total_c_nodes
            print ""
            add_new_nodes = \
                       get_yes_no_plane_vanilla("Do you want to add some more"\
                                     " compute nodes[Y/N]? ", "no")
            if (add_new_nodes == 1):
                while True:
                    no_of_new_nodes = raw_input("Number of new compute nodes "\
                                            "you want to configure: ")
                    if not (no_of_new_nodes.isdigit()):
                        print("Invalid input!! Please provide an integer ")
                        print ""
                        continue
                    else:
                        new_nodes = int(no_of_new_nodes)
                        break
        from_file = 1
    else:
        com = raw_input("How many compute nodes do you want to configure? ")

if (from_file == 0 or new_nodes > 0):
    if (new_nodes > 0):
        total_c_nodes = total_c_nodes + new_nodes
        n_com = int(new_nodes)
        stop_file_read = 1
    else:
        while True:
            if (com.isdigit()):
                total_c_nodes = int(com)
                n_com = int(com)
                break
            else:
                com = raw_input("Invalid input!! Please provide an integer ")
                continue

    n = 1
    while True:
        if (n_com == 0):
            if (stop_file_read == 1):
                stop_file_read = 0
            break
        print ("\n Compute Node values for Node %s\n" % n)
        is_ucs_blade = get_yes_no("Will this be a UCS blade:[Y/N]? ",
                                "is_ucs_blade")
        if not (is_ucs_blade):
            cimc_ip = get_valid_ip("Enter CIMC IP: ", 
                                    "compute_node_cimc", "NONE")
            cimc_ip_list.append(cimc_ip)
            compute_username = \
                    get_user_input("CIMC User login (Default admin): ", 
                       "compute_username", "admin") 
            login_user_list.append(compute_username)
            compute_pw = get_user_input("Password (Default password): ",
                                 "compute_pw", "password")
            pw_list.append(compute_pw)
            com_ip = get_valid_ip("Enter compute node IP: ", 
                                       "compute_node_ip", "NONE")
            c_ip_list.append(com_ip)
            com_host = get_user_input("Enter compute node hostname: ", 
                               "compute_hostname","compute-%s" % n)
            com_host = com_host.lower()
            c_host_list.append(com_host)
            com_mac = get_valid_mac("Enter compute node mac: ", 
                                         "compute_mac", "NONE")
            c_mac_list.append(com_mac)
            c_vtep_config = get_yes_no("Do you want to configure VTEP:[Y/N]? ",
                                "c_vtep_config")
            if (c_vtep_config == 1):
                print "===================================================="
                print "       VTEP Config FORMAT is as follows"
                print ""
                print "virt vmknic-int2 profile profint mode static"\
                      " address 192.168.1.91 netmask 255.255.255.0 mac"\
                      " 00:11:22:33:44:66"
                print ""
                print "===================================================="

                multiple_compute_vtep = get_yes_no("Do you want to configure"\
                             " multiple vteps on this node[Y/N]? ", 
                                 "multiple_compute_vtep")
                if (multiple_compute_vtep == 1):
                    compute_vtep_diff_subnet = get_yes_no("Are these VTEPs "\
                                     "going to be on same subnets[Y/N]? ",
                                     "compute_vtep_diff_subnet? ")

                    if (compute_vtep_diff_subnet == 1):
                        print ""
                        print " INFO: This action (i.e. if more than 1"
                        print " VTEP in same subnet) will change RPF check"
                        print " to loose mode"
                        print ""
                        compute_vtep_diff_subnet_list.append("1")
                    else:
                        compute_vtep_diff_subnet_list.append("NONE")

                else:
                    compute_vtep_diff_subnet_list.append("NONE")
                    
                vtep_config = get_user_input("VTEP configuration for "\
                                            "the compute node: ", "vtep_config",
                                             "NONE")
                c_vtep_list.append(vtep_config)
            else:
                c_vtep_list.append("NONE")
                compute_vtep_diff_subnet_list.append("NONE")

            c_dhcp_enable = get_yes_no("Do you want to enable dhcp agent on"\
                         " this node [Y/N]? ", "c_dhcp_enable")
            if (c_dhcp_enable == 1):
                c_dhcp_enable_list.append("true")
            else:
                c_dhcp_enable_list.append("false")
        # For UCS compute nodes
        else:
            ucs_cimc_ip = get_valid_ip("Enter CIMC IP: ", 
                                        "ucs_node_cimc", "NONE")
            ucs_cimc_list.append(ucs_cimc_ip)
            ucs_compute_username = \
                    get_user_input("User login (Default admin): ", 
                       "ucs_compute_username", "admin") 
            ucs_admin_user_list.append(ucs_compute_username)
            ucs_compute_pw = get_user_input("Password (Default password): ",
                                 "ucs_compute_pw", "password")
            ucs_pw_list.append(ucs_compute_pw)
            ucs_service_name = get_user_input("Enter UCS Service profile: ", 
                                          "ucs_service_name", "NONE")
            ucs_service_name_list.append(ucs_service_name)
            print "If your service profile is not under root"
            print "provide the subgroup it is under"
            diff_subgroup = \
                    get_yes_no("Do you want to provide the subgroup [Y/N]? ", 
                               "diff_subgroup")

            if (diff_subgroup == 1):
                ucs_subgroup = get_user_input("UCS Blade subgroup: ", 
                                      "ucs_sub_group", "0")
                ucs_subgroup_list.append(ucs_subgroup)
            else:
                ucs_subgroup_list.append("NONE")
             
            ucs_ip = get_valid_ip("Enter compute node IP: ", 
                                               "ucs_node_ip", "NONE")
            ucs_ip_list.append(ucs_ip)
            ucs_host = get_user_input("Enter compute node hostname: ", 
                               "ucs_hostname","compute-%s" % n)
            ucs_host = ucs_host.lower()
            ucs_host_list.append(ucs_host)
            ucs_mac = get_valid_mac("Enter compute node mac: ", 
                                                "ucs_mac", "NONE")
            ucs_mac_list.append(ucs_mac)
            ucs_vtep_config = get_yes_no("Do you want to configure VTEP on"\
                         " this node [Y/N]? ", "ucs_vtep_config")
            if (ucs_vtep_config == 1):
                print "========================================================"
                print "       VTEP Config FORMAT is as follows"
                print "virt vmknic-int2 profile profint mode static"\
                      " address 192.168.1.91 netmask 255.255.255.0 mac"\
                      " 00:11:22:33:44:66"
                print ""
                print "========================================================"
                ucs_multiple_vtep = get_yes_no("Do you want to configure"\
                             " multiple vteps on this node[Y/N]? ", 
                                 "ucs_multiple_vtep")
                if (ucs_multiple_vtep == 1):
                    ucs_vtep_diff_subnet = get_yes_no("Are these VTEPs "\
                                     "going to be on same subnets[Y/N]? ",
                                     "ucs_vtep_diff_subnet")

                    if (ucs_vtep_diff_subnet == 1):
                        print ""
                        print " INFO: This action (i.e. if more than 1"
                        print " VTEP in same subnet) will change RPF check"
                        print " to loose mode"
                        print ""
                        ucs_vtep_diff_subnet_list.append("1")
                    else:
                        ucs_vtep_diff_subnet_list.append("NONE")

                else:
                    ucs_vtep_diff_subnet_list.append("NONE")

                ucs_vtep_config = get_user_input("VTEP configuration for "\
                                        "the compute node: ", "ucs_vtep_config",
                                         "NONE")
                ucs_vtep_list.append(ucs_vtep_config)
            else:
                ucs_vtep_diff_subnet_list.append("NONE")
                ucs_vtep_list.append("NONE")

            ucs_dhcp_enable = get_yes_no("Do you want to enable dhcp agent on"\
                         " this node [Y/N]? ", "ucs_dhcp_enable")
            if (ucs_dhcp_enable == 1):
                ucs_dhcp_enable_list.append("true")
            else:
                ucs_dhcp_enable_list.append("false")

            no_ucs = no_ucs + 1
       
        n_com = n_com - 1
        n = n + 1

    if (no_ucs > 0):
        log_site("number_of_ucs_nodes", no_ucs)

log_site("total_compute_nodes", total_c_nodes)
if (total_c_nodes > 0):
    log_site("compute_node_ip_list", c_ip_list)
    log_site("compute_node_host_list", c_host_list)
    log_site("compute_node_mac_list", c_mac_list)
    log_site("compute_node_cimc_ip_list", cimc_ip_list)
    log_site("c_vtep_list", c_vtep_list)
    log_site("login_user_list", login_user_list)
    log_site("pw_list", pw_list)
    log_site("c_dhcp_enable_list", c_dhcp_enable_list)
    log_site("compute_vtep_diff_subnet_list", compute_vtep_diff_subnet_list)

if (no_ucs > 0):
    log_site("ucs_cimc_list", ucs_cimc_list)
    log_site("ucs_service_name_list",ucs_service_name_list)
    log_site("ucs_pw_list", ucs_pw_list)
    log_site("ucs_admin_user_list", ucs_admin_user_list)
    log_site("ucs_mac_list", ucs_mac_list)
    log_site("ucs_ip_list", ucs_ip_list)
    log_site("ucs_host_list", ucs_host_list)
    log_site("ucs_subgroup_list", ucs_subgroup_list)
    log_site("ucs_vtep_list", ucs_vtep_list)
    log_site("ucs_dhcp_enable_list", ucs_dhcp_enable_list)
    log_site("ucs_vtep_diff_subnet_list", ucs_vtep_diff_subnet_list)

print ""
print "Compute node configuration ends"
print "====================================================================="
print ""
print ""


print "Network nodes configuration begins"
print "====================================================================="

# Initialize the lists
nw_login_user_list = []
nw_node_passwd_list = []
nw_cimc_ip_list = []
nw_ip_list = []
nw_mac_list = []
nw_host_list = []
nw_dhcp_enable_list = []
nw_vtep_list = []
nw_node_ucs_list = []
nw_subgroup_list = []
nw_service_list = []
nw_vtep_diff_subnet_list =[]

get_nw_from_user = 0
total_nw_nodes = 0
# Check if this is present in the inputfile if provided
if not (inputfile == ""):
    nw_node_config = get_from_file("nw_node_config", "nw_node_config")
    if not (nw_node_config == "NONE"):
        nw_node_config = int(nw_node_config)
        if (nw_node_config == 1):
            nw_nodes_from_file = get_from_file("total_nw_nodes", 
                                             "total_nw_nodes")
            if not (nw_nodes_from_file == "NONE"):
                nw_nodes_from_file = int(nw_nodes_from_file)
                if (nw_nodes_from_file > 0):
                    # Populate lists from the file
                    total_nw_nodes = nw_nodes_from_file

                    nw_login_user_list =  \
                              get_list_from_file("nw_login_user_list",
                                          total_nw_nodes)
                    nw_node_passwd_list = \
                       get_list_from_file("nw_node_passwd_list",total_nw_nodes)
                    nw_cimc_ip_list = get_list_from_file("nw_cimc_ip_list",
                                                total_nw_nodes)
                    nw_ip_list = get_list_from_file("nw_ip_list", 
                                                      total_nw_nodes)
                    nw_mac_list = get_list_from_file("nw_mac_list", 
                                            total_nw_nodes)
                    nw_host_list = get_list_from_file("nw_host_list", 
                                          total_nw_nodes)
                    nw_dhcp_enable_list = \
                       get_list_from_file("nw_dhcp_enable_list",total_nw_nodes)
                    nw_vtep_list = get_vtep_list_from_file("nw_vtep_list", 
                                                     total_nw_nodes)
                    nw_vtep_diff_subnet_list = \
                           get_vtep_list_from_file("nw_vtep_diff_subnet_list", 
                                                     total_nw_nodes)
                    nw_node_ucs_list = get_list_from_file("nw_node_ucs_list", 
                                                   total_nw_nodes)
                    nw_subgroup_list = get_list_from_file("nw_subgroup_list", 
                                               total_nw_nodes)
                    nw_service_list = get_list_from_file("nw_service_list", 
                                                 total_nw_nodes)
                    log_site("nw_node_config", nw_node_config)
                    log_site("total_nw_nodes", total_nw_nodes) 
        else:
            print "Input file does not have network nodes"
            get_nw_from_user = 1
    else:
         get_nw_from_user = 1
        
if (inputfile == "" or get_nw_from_user == 1):
    nw_node_config = get_yes_no("Do you want to configure network"\
                                 " nodes [Y/N]? ", "nw_node_config")
    if (nw_node_config == 1):
        nw_nodes = raw_input("How many network nodes do you want to"\
                               " configure? ")
        while True:
            if (nw_nodes.isdigit()):
                total_nw_nodes = int(nw_nodes)
                break
            else:
                nw_nodes = raw_input("Invalid input!! Please provide an"\
                                            " integer ")
                continue

        log_site("total_nw_nodes", total_nw_nodes) 
        nw_count = total_nw_nodes
        while True:
            if (nw_count == 0):
                break
            print ("\n Network Node values for Node %s\n" % nw_count)
            print ""
            nw_node_is_ucs_blade = get_yes_no("Will this node be a UCS"\
                                " blade:[Y/N]? ",
                                "nw_node_is_ucs_blade")
            nw_node_ucs_list.append(nw_node_is_ucs_blade)
            nw_cimc_ip = get_valid_ip("Enter CIMC IP: ", 
                                      "nw_node_cimc", "NONE")
            nw_cimc_ip_list.append(nw_cimc_ip)
            nw_node_username = \
                    get_user_input("CIMC User login (Default admin): ", 
                       "nw_node_username", "admin") 
            nw_login_user_list.append(nw_node_username)
            nw_node_pw = get_user_input("Password (Default password): ",
                                 "nw_node_pw", "password")
            nw_node_passwd_list.append(nw_node_pw)
            if (nw_node_is_ucs_blade == 1):
                nw_service_name = get_user_input("Enter UCS Service profile: ",
                                     "nw_service_name", "NONE")
                nw_service_list.append(nw_service_name)
	        print ("If your service profile is not under root")
                print("provide the subgroup it is under")
                nw_diff_subgroup = \
                      get_yes_no("Do you want to provide the subgroup [Y/N]? ",
                               "diff_subgroup")
                if (nw_diff_subgroup == 1):
                    nw_subgroup = get_user_input("Subgroup is under: ",
                                            "nw_subgroup", "NONE")
                    nw_subgroup_list.append(nw_subgroup)
                else:
                    nw_subgroup_list.append("0")
            else:
                    nw_subgroup_list.append("0")
                    nw_service_list.append("0")
            nw_node_ip = get_valid_ip("Enter network node IP: ", 
                                    "nw_node_ip", "NONE")
            nw_ip_list.append(nw_node_ip)
            nw_host = get_user_input("Enter Network node hostname: ", 
                               "nw_hostname","NONE")
            nw_host = nw_host.lower()
            nw_host_list.append(nw_host)
            nw_node_mac = get_valid_mac("Enter network node mac: ", 
                                      "nw_node_mac", "NONE")
            nw_mac_list.append(nw_node_mac)
            nw_vtep_config = get_yes_no("Do you want to configure vtep "\
                                   "on this node [Y/N]? ", "nw_vtep_config")
            if (nw_vtep_config == 1):
                print "===================================================="
                print "       VTEP Config FORMAT is as follows"
                print ""
                print "virt vmknic-int2 profile profint mode static"\
                      " address 192.168.1.91 netmask 255.255.255.0 mac"\
                      " 00:11:22:33:44:66"
                print ""
                print "===================================================="
                multiple_nw_vtep = get_yes_no("Do you want to configure"\
                             " multiple vteps on this node[Y/N]? ", 
                                 "multiple_nw_vtep")
                if (multiple_nw_vtep == 1):
                    nw_vtep_diff_subnet = get_yes_no("Are these VTEPs "\
                                     "going to be on same subnets[Y/N]? ",
                                     "nw_vtep_diff_subnet")

                    if (nw_vtep_diff_subnet == 1):
                        print ""
                        print " INFO: This action (i.e. if more than 1"
                        print " VTEP in same subnet) will change RPF check"
                        print " to loose mode"
                        print ""
                        nw_vtep_diff_subnet_list.append("1")
                    else:
                        nw_vtep_diff_subnet_list.append("NONE")

                else:
                    nw_vtep_diff_subnet_list.append("NONE")

                nw_vtep_config = get_user_input("VTEP configuration for "\
                                        "this network node: ", "nw_vtep_config",
                                         "NONE")
                nw_vtep_list.append(nw_vtep_config)
            else:
                nw_vtep_diff_subnet_list.append("NONE")
                nw_vtep_list.append("NONE")


            nw_dhcp_enable = get_yes_no("Do you want to enable dhcp agent on"\
                         " this node [Y/N]? ", "nw_dhcp_enable")
            if (nw_dhcp_enable == 1):
                nw_dhcp_enable_list.append("true")
            else:
                nw_dhcp_enable_list.append("false")


            nw_count = nw_count -1

if (total_nw_nodes > 0):
    log_site("nw_login_user_list", nw_login_user_list)
    log_site("nw_node_passwd_list", nw_node_passwd_list)
    log_site("nw_login_user_list", nw_login_user_list)
    log_site("nw_node_passwd_list", nw_node_passwd_list)
    log_site("nw_cimc_ip_list",nw_cimc_ip_list)
    log_site("nw_ip_list", nw_ip_list)
    log_site("nw_mac_list", nw_mac_list)
    log_site("nw_host_list", nw_host_list)
    log_site("nw_dhcp_enable_list", nw_dhcp_enable_list)
    log_site("nw_vtep_list", nw_vtep_list) 
    log_site("nw_node_ucs_list", nw_node_ucs_list)
    log_site("nw_subgroup_list", nw_subgroup_list)
    log_site("nw_service_list", nw_service_list)
    log_site("nw_vtep_diff_subnet_list", nw_vtep_diff_subnet_list)

print "Network Node configuration ends"
print ""
print "================================================================"
print "Start VSM configuration"
print ""

print "========================================================="
print "    Domain ID is for VSM and compute node "  
print "   communication and is an integer between 1 - 1023"
print "========================================================="
while True:
    domain_id = get_user_input("DomainID: ", "domain_id", "NONE")
    if (domain_id.isdigit()):
        domain_id = int(domain_id)
        if (domain_id < 0 or domain_id > 1023):
            print "Invalid DomainID provided."\
                    " Please input a value between 1 - 1023)"
            continue
        else:
            log_site("domain_id", domain_id)
            break
    else:
        print "Invalid DomainID provided."\
                  " Please input a value between 1 - 1023)"
        continue

is_vsm_n110 = get_yes_no("Is your VSM going to be on a"\
                            " Nexus 1110/1010 [Y/N]? ",
                            "is_vsm_n110")
if (is_vsm_n110 == 1):
    #vsm_control_mac = get_valid_mac("Provide the control mac of"\
    #                                " the VSM: ",
    #                                 "n110_control_mac", "NONE")
    vsm_control_mac = "00:11:11:11:11:11"
    #vsm_ip  = get_valid_ip("Enter VSM public interface IP on the node: ", 
    #                          "n110_node_ip", "NONE")
    vsm_ip = "1.1.1.1"

    vsm_control_ip = get_valid_ip("Enter VSM management IP: ", 
                                 "n110_control_ip", "NONE")
    vsm_control_pw = get_user_input("VSM Password: ",
                                    "n110_control_pw", "NONE")
else:
    vsm_is_ucs = get_yes_no("Will your VSM be a UCS blade[Y/N]? ",
                            "vsm_is_ucs")
    vsm_cimc = get_valid_ip("Enter VSM node CIMC IP: ", "vsm_node_cimc", 
                            "NONE")
    vsm_admin_user = \
                   get_user_input("CIMC User login (Default admin): ", 
                       "vsm_compute_username", "admin") 
    vsm_admin_pw = get_user_input("Password (Default password): ",
                                 "vsm_compute_pw", "password")
    if (vsm_is_ucs == 1):
        vsm_service_name = get_user_input("Enter UCS Service profile: ", 
                                     "vsm_service_name", "NONE")
        print "============================================================"
        print "If your service profile is not under root"
        print "provide the subgroup it is under"
        print "============================================================"
        vsm_diff_subgroup = \
              get_yes_no("Do you want to provide the subgroup [Y/N]? ", 
                               "vsm_diff_subgroup")
        if (vsm_diff_subgroup == 1):
            vsm_subgroup = get_user_input("Subgroup VSM is under: ",
                                            "vsm_subgroup", "NONE")
    print "==========================================================="
    print "This IP address is the address of the node hosting the"
    print "VSM VM"
    print "==========================================================="
    print ""
    vsm_ip = get_valid_ip("Enter IP address of the node hosting VSM VM: ", 
                                "vsm_node_ip", "NONE")
    vsm_host = get_user_input("Enter VSM node hostname: ",
                       "vsm_primary_hostname", "NONE")
    vsm_host = vsm_host.lower()
    print""
    print "=================================================================="
    print "VSM boot interface mac of the VSM node"
    print "=================================================================="
    vsm_mac = get_valid_mac("Interface MAC address of the VSM node: ", 
                                     "vsm_pri_mac", "NONE")
    print ""
    print "=================================================================="
    print "The following inputs are for the actual VSM values"
    print "=================================================================="
    print ""
    
    print "==================================================================="
    print('\nvsm image location format ' )
    print('"/home/image/n1000v-dk9.5.2.1.SK1.2.0.409.iso" \n')
    print "==================================================================="
    while True:
        vsm_image_location = get_user_input("vsm image location."\
                            " Provide full path"\
                            " along with file name: ", "vsmimage", "NONE")
        vsm_image_location = vsm_image_location.strip()
        if (os.path.isfile('%s' % vsm_image_location)):
            log_site("vsmimage", vsm_image_location)
            break
        else:
            print "File not present. Please check and provide "\
                   "the right location"
            continue

    vsm_control_mac = get_valid_mac("Provide the control mac of"\
                                    " the VSM: ",
                                     "vsm_control_mac", "NONE")
    vsm_control_ip = get_valid_ip("Enter VSM management IP: ", 
                                "vsm_control_ip", "NONE")
    vsm_control_pw = get_user_input("VSM password: ",
                                    "vsm_control_pw", "NONE")
    vsm_role = get_vsm_role()

    kvm_secondary = 0
    if (vsm_role == "primary"):
        kvm_secondary = get_yes_no("Do you want to configure secondary"\
                                  " VSM [Y/N]? ",
                                "kvm_secondary")

        if (kvm_secondary == 1):
            secvsm_is_ucs = get_yes_no("Will your secondary VSM be a "\
                             " UCS blade[Y/N]? ",
                            "secvsm_is_ucs")

            sec_kvm_cimc = get_valid_ip("Enter Secondary VSM node CIMC: ", 
                           "sec_kvm_cimc", "NONE")
            sec_admin_user = \
                       get_user_input("CIMC User login (Default admin): ", 
                           "sec_username", "admin") 
            sec_admin_pw = get_user_input("CIMC Password (Default password): ",
                                 "sec_cimc_pw", "password")
            if (secvsm_is_ucs == 1):
                sec_vsm_service_name = get_user_input("Provide VSM secondary"\
                                                " service name: ", 
                                   "sec_vsm_service_name", "NONE")
                print "====================================================="
                print "If your service profile is not under root"
                print "provide the subgroup it is under"
                print "======================================================"
                secvsm_diff_subgroup = \
                  get_yes_no("Do you want to provide the subgroup [Y/N]? ", 
                                   "secvsm_diff_subgroup")
                if (secvsm_diff_subgroup == 1):
                    secvsm_subgroup = get_user_input("Subgroup VSM is under: ",
                                                   "secvsm_subgroup", "NONE")
            sec_kvm_host = get_user_input("Enter Secondary VSM node hostname: ",
                           "sec_kvm_host", "NONE")
            sec_kvm_host = sec_kvm_host.lower()

            sec_kvm_mac = get_valid_mac("Enter secondary VSM node Mac: ", 
                                     "sec_vsm_mac", "NONE")
            sec_vsm_ip = get_valid_ip("Enter Secondary VSM node IP address: ",
                               "sec_vsm_ip", "NONE")

print ""
print "End of VSM configuration"
print "================================================================"
print ""
print ""

in_gw_image = get_yes_no("Do you want to specify an image location "\
                          "for the VXLAN Gateway [Y/N]? ", "in_gw_image")
if (in_gw_image == 1):
    while True:
        gw_image_location = get_user_input("VXLAN Gateway image_location: ",
                                         "gw_image_location", "NONE")
        gw_image_location = gw_image_location.strip()
        if (os.path.isfile('%s' % gw_image_location)):
            log_site("gw_image_location", gw_image_location)
            break
        else:
            print "File not present. Please check and provide"\
                               " the right location"
            continue

print ""
     
                                         
############### Start of site.pp write section ####################


sitepp.write('# This document serves as an example of how to deploy\n')
sitepp.write('# basic multi-node openstack environments.\n')
sitepp.write('# In this scenario Quantum is using OVS with GRE Tunnels\n')
sitepp.write('\n')
sitepp.write('########### Proxy Configuration ##########\n')
sitepp.write('# If you use an HTTP/HTTPS proxy, uncomment this setting and specify the\n')
sitepp.write('# correct proxy URL.  If you do not use an HTTP/HTTPS proxy, leave this\n')
sitepp.write('# setting commented out.\n')
sitepp.write('#$proxy			= "http://proxy-server:port-number"\n')
sitepp.write('\n')
sitepp.write('########### package repo configuration ##########\n')
sitepp.write('#\n')
sitepp.write('# The package repos used to install openstack\n')
sitepp.write('$package_repo = \'cisco_repo\'\n')
sitepp.write('# Alternatively, the upstream Ubuntu package from cloud archive can be used\n')
sitepp.write('# $package_repo = \'cloud_archive\'\n')
sitepp.write('\n')
sitepp.write('# If you are behind a proxy you may choose not to use our ftp distribution, and\n')
sitepp.write('# instead try our http distribution location. Note the http location is not\n')
sitepp.write('# a permanent location and may change at any time.\n')
sitepp.write('#$location 		= "ftp://ftpeng.cisco.com/openstack/cisco"\n')
sitepp.write('# Alternate, uncomment this one, and comment out the one above.\n')
sitepp.write('$location               = "http://openstack-repo.cisco.com/openstack"\n')
sitepp.write('\n')
sitepp.write('# Cisco also maintains a supplemental repository of packages that aren\'t\n')
sitepp.write('# core to OpenStack itself and are not provided by operating system vendors.\n')
sitepp.write('# The supplemental repository is provided as a convenience for those wishing\n')
sitepp.write('# to reduce the count of repositories needed to bring up a cloud with\n')
sitepp.write('# particular features (such as Ceph or highly available databases).\n')
sitepp.write('# If you want to use the supplemental, uncomment one of the two lines\n')
sitepp.write('# below.  If you have a local cache or mirror of the supplemental repo, change\n')
sitepp.write('# the $supplemental_repo variable to the URL of your mirror.  If you don\'t\n')
sitepp.write('# need the supplemental repo and prefer not to configure it at all, simply\n')
sitepp.write('# comment out the line below.\n')
sitepp.write('$supplemental_repo = \'ftp://ftpeng.cisco.com/openstack/cisco_supplemental\'\n')
sitepp.write('#$supplemental_repo = \'http://openstack-repo.cisco.com/openstack/cisco_supplemental\'\n')
sitepp.write('\n')
sitepp.write('########### Build Node (Cobbler, Puppet Master, NTP) ######\n')
sitepp.write('# Change the following to the host name you have given your build node.\n')
sitepp.write('# This name should be in all lower case letters due to a Puppet limitation\n')
sitepp.write('# (refer to http://projects.puppetlabs.com/issues/1168).\n')
sitepp.write('$build_node_name        = "%s"\n\n' % socket.gethostname())
sitepp.write('\n')
sitepp.write('########### NTP Configuration ############\n')
sitepp.write('# Change this to the location of a time server in your organization accessible\n')
sitepp.write('# to the build server.  The build server will synchronize with this time\n')
sitepp.write('# server, and will in turn function as the time server for your OpenStack\n')
sitepp.write('# nodes.\n')
sitepp.write('$ntp_servers	= [\'%s\']\n' % ntp_server)
sitepp.write('\n')
sitepp.write('########### Build Node Cobbler Variables ############\n')
sitepp.write('# Change these 5 parameters to define the IP address and other network\n')
sitepp.write('# settings of your build node.  The cobbler node *must* have this IP\n')
sitepp.write('# configured and it *must* be on the same network as the hosts to install.\n')

sitepp.write('$cobbler_node_ip        = \'%s\'\n' % cob_node_ip)
sitepp.write('$node_subnet            = \'%s\'\n' % cob_node_subnet)
sitepp.write('$node_netmask           = \'%s\'\n' % cob_node_netmask)

sitepp.write('# This gateway is optional - if there\'s a gateway providing a default route,\n')
sitepp.write('# specify it here.  If not, comment this line out.\n')

sitepp.write('$node_gateway           = \'%s\'\n\n' % cob_node_gw)
sitepp.write('\n')
sitepp.write('\n')
sitepp.write('# This domain name will be the name your build and compute nodes use for the\n')
sitepp.write('# local DNS.  It doesn\'t have to be the name of your corporate DNS - a local\n')
sitepp.write('# DNS server on the build node will serve addresses in this domain - but if\n')
sitepp.write('# it is, you can also add entries for the nodes in your corporate DNS\n')
sitepp.write('# environment they will be usable *if* the above addresses are routeable\n')
sitepp.write('# from elsewhere in your network.\n')
sitepp.write('$domain_name             = \'%s\'\n' % domain_name)
sitepp.write('# This setting likely does not need to be changed.\n')
sitepp.write('# To speed installation of your OpenStack nodes, it configures your build\n')
sitepp.write('# node to function as a caching proxy storing the Ubuntu install files used\n')
sitepp.write('# to deploy the OpenStack nodes.\n')
sitepp.write('$cobbler_proxy 		= "http://${cobbler_node_ip}:3142/"\n')
sitepp.write('\n')
sitepp.write('####### Preseed File Configuration #######\n')
sitepp.write('# This will build a preseed file called \'cisco-preseed\' in\n')
sitepp.write('# /etc/cobbler/preseeds/\n')
sitepp.write('# The preseed file automates the installation of Ubuntu onto the OpenStack\n')
sitepp.write('# nodes.\n')
sitepp.write('#\n')
sitepp.write('# The following variables may be changed by the system admin:\n')
sitepp.write('# 1) admin_user\n')
sitepp.write('# 2) password_crypted\n')
sitepp.write('# 3) autostart_puppet -- whether the puppet agent will auto start\n')
sitepp.write('# Default user is: localadmin \n')
sitepp.write('# Default SHA-512 hashed password is "ubuntu": \n')
sitepp.write('# $6$UfgWxrIv$k4KfzAEMqMg.fppmSOTd0usI4j6gfjs0962.JXsoJRWa5wMz8yQk4SfInn4.WZ3L/MCt5u.62tHDGB36EhiKF1\n')
sitepp.write('# To generate a new SHA-512 hashed password, run the following replacing\n')
sitepp.write('# the word "password" with your new password. Then use the result as the\n')
sitepp.write('# $password_crypted variable.\n')
sitepp.write('# python -c "import crypt, getpass, pwd; print crypt.crypt(\'password\', \'\$6\$UfgWxrIv\$\')"\n')
sitepp.write('$admin_user 		= \'%s\'\n' % login)
#sitepp.write('$password_crypted 	= \'$6$UfgWxrIv$k4KfzAEMqMg.fppmSOTd0usI4j6gfjs0962.JXsoJRWa5wMz8yQk4SfInn4.WZ3L/MCt5u.62tHDGB36EhiKF1\'\n')
sitepp.write('$password_crypted 	= \'%s\'\n' % password)
sitepp.write('$autostart_puppet       = true\n')
sitepp.write('\n')
sitepp.write('# If the setup uses the UCS B-series blades, enter the port on which the\n')
sitepp.write('# ucsm accepts requests. By default the UCSM is enabled to accept requests\n')
sitepp.write('# on port 443 (https). If https is disabled and only http is used, set\n')
sitepp.write('# $ucsm_port = \'80\'\n')
sitepp.write('$ucsm_port = \'443\'\n')
sitepp.write('\n')
sitepp.write('########### OpenStack Variables ############\n')
sitepp.write('# These values define parameters which will be used to deploy and configure \n')
sitepp.write('# OpenStack once Ubuntu is installed on your nodes.\n')
sitepp.write('#\n')
sitepp.write('# Change these next 3 parameters to the network settings of the node which\n')
sitepp.write('# will be your OpenStack control node.  Note that the $controller_hostname\n')
sitepp.write('# should be in all lowercase letters due to a limitation of Puppet\n')
sitepp.write('# (refer to http://projects.puppetlabs.com/issues/1168).\n')
sitepp.write('$controller_node_address     = \'%s\'\n' % controller_ip)

sitepp.write('$controller_node_network     = \'%s\'\n' % controller_network)

sitepp.write('$controller_hostname         = \'%s\'\n' % controller_hostname)

sitepp.write('# Specify the network which should have access to the MySQL database on \n')
sitepp.write('# the OpenStack control node. Typically, this will be the same network as\n')
sitepp.write('# defined in the controller_node_network parameter above. Use MySQL network\n')
sitepp.write('# wild card syntax to specify the desired network.\n')
sitepp.write('$db_allowed_network            = \'%s\'\n' % db_def_val)
sitepp.write('# These next two values typically do not need to be changed. They define the\n')
sitepp.write('# network connectivity of the OpenStack controller.  This is the interface\n')
sitepp.write('# used to connect to Horizon dashboard.\n')
sitepp.write('$controller_node_public        = $controller_node_address\n')
sitepp.write('# This is the interface used for external backend communication.\n')
sitepp.write('$controller_node_internal      = $controller_node_address\n')
sitepp.write('\n')
sitepp.write('# Specify the address of the Swift proxy\n')
sitepp.write('# If you have multiple Swift proxy nodes, this should be the address\n')
sitepp.write('# of the VIP used to load-balance across the individual nodes. \n')
sitepp.write('# Uncommenting this variable will enable the keystone swift endpoint.\n')
sitepp.write('# $swift_proxy_address           = \'192.168.242.179\'\n')
sitepp.write('\n')
sitepp.write('# These next two parameters specify the networking hardware used in each node\n')
sitepp.write('# Current assumption is that all nodes have the same network interfaces and are\n')
sitepp.write('# cabled identically.  However, with the control node acting as network node,\n')
sitepp.write('# only the control node requires 2 interfaces.  For all other nodes, a single\n')
sitepp.write('# interface is functional with the assumption that:\n')
sitepp.write('#   a) The public_interface will have an IP address reachable by\n')
sitepp.write('#      all other nodes in the openstack cluster.  This address will\n')
sitepp.write('#      be used for API Access, for the Horizon UI, and as an endpoint\n')
sitepp.write('#      for the default GRE tunnel mechanism used in the OVS network\n')
sitepp.write('#      configuration.\n')
sitepp.write('#   b) The external_interface is used to provide a Layer2 path for \n')
sitepp.write('#      the l3_agent external router interface.  It is expected that\n')
sitepp.write('#      this interface be attached to an upstream device that provides\n')
sitepp.write('#      a L3 router interface, with the default router configuration\n')
sitepp.write('#      assuming that the first non "network" address in the external \n')
sitepp.write('#      network IP subnet will be used as the default forwarding path\n')
sitepp.write('#      if no more specific host routes are added.\n')
sitepp.write('#\n')
sitepp.write('# It is assumed that this interface has an IP Address associated with it\n')
sitepp.write('# and is available and connected on every host in the OpenStack cluster\n')

sitepp.write('$public_interface        	= \'%s\'\n' % public_interface)
sitepp.write('# The external_interface is used for external connectivity in association\n')
sitepp.write('# with the l3_agent external router interface, providing floating IPs\n')
sitepp.write('# (this is only required on the network/controller node)\n')
sitepp.write('$external_interface	 	= \'%s\'\n' % external_interface)
sitepp.write('\n')
sitepp.write('\n')
sitepp.write('# Uncomment and customize these next three variables to use a provider\n')
sitepp.write('# network model.\n')
sitepp.write('#\n')
sitepp.write('# $ovs_vlan_ranges is used to name a physical network and indicate the\n')
sitepp.write('# VLAN tag or # tags that should be associated with that network. The first\n')
sitepp.write('# parameter is the network name, while the second parameter is the starting\n')
sitepp.write('# tag # number and the third parameter is the ending tag number.\n')
sitepp.write('#$ovs_vlan_ranges = \'physnet1:1000:2000\'\n')
sitepp.write('#\n')
sitepp.write('# $ovs_bridge_uplinks is used to map an OVS bridge to a physical network\n')
sitepp.write('# interface. The first parameter is the OVS external bridge name, and the\n')
sitepp.write('# second parameter is the physical network interface which should be\n')
sitepp.write('# associated with it.\n')
sitepp.write('#\n')
sitepp.write('#$ovs_bridge_uplinks = [\'br-ex:eth0\']\n')
sitepp.write('# $ovs_bridge_mappings is used to map an OVS bridge to a physical network.\n')
sitepp.write('# The first parameter is the physical network name and the second parameter\n')
sitepp.write('# is the OVS external bridge name\n')
sitepp.write('#$ovs_bridge_mappings = [\'physnet1:br-ex\']\n')
sitepp.write('#\n')
sitepp.write('# To use vlan provider networks with OVS, you will also need to\n')
sitepp.write('# set the tenant network type to \'vlan\' instead of gre.  To\n')
sitepp.write('# do so, uncomment the line below.  This is also necessary if using\n')
sitepp.write('# the Cisco Nexus plugin.\n')
sitepp.write('# $tenant_network_type = \'vlan\'\n')
sitepp.write('\n')
sitepp.write('# Select the drive on which Ubuntu and OpenStack will be installed in each\n')
sitepp.write('# node. The current assumption is that all nodes will be installed on the\n')
sitepp.write('# same device name.\n')

sitepp.write('$install_drive           = \'/dev/sda\'\n')
sitepp.write('\n')
sitepp.write('########### OpenStack Service Credentials ############\n')
sitepp.write('# This block of parameters is used to change the user names and passwords\n')
sitepp.write('# used by the services which make up OpenStack. The following defaults should\n')
sitepp.write('# be changed for any production deployment.\n')
sitepp.write('\n')
sitepp.write('$admin_email             = \'root@localhost\'\n')
sitepp.write('$admin_password          = \'Cisco123\'\n')
sitepp.write('$keystone_db_password    = \'keystone_db_pass\'\n')
sitepp.write('$keystone_admin_token    = \'keystone_admin_token\'\n')
sitepp.write('$mysql_root_password     = \'mysql_db_pass\'\n')
sitepp.write('$nova_user               = \'nova\'\n')
sitepp.write('$nova_db_password        = \'nova_pass\'\n')
sitepp.write('$nova_user_password      = \'nova_pass\'\n')
sitepp.write('$libvirt_type            = \'kvm\'\n')
sitepp.write('$glance_db_password      = \'glance_pass\'\n')
sitepp.write('$glance_user_password    = \'glance_pass\'\n')
sitepp.write('$glance_sql_connection   = "mysql://glance:${glance_db_password}@${controller_node_address}/glance"\n')
sitepp.write('$cinder_user             = \'cinder\'\n')
sitepp.write('$cinder_user_password    = \'cinder_pass\'\n')
sitepp.write('$cinder_db_password      = \'cinder_pass\'\n')
sitepp.write('$quantum_user_password   = \'quantum_pass\'\n')
sitepp.write('$quantum_db_password     = \'quantum_pass\'\n')
sitepp.write('$rabbit_password         = \'openstack_rabbit_password\'\n')
sitepp.write('$rabbit_user             = \'openstack_rabbit_user\'\n')
sitepp.write('$swift_password          = \'swift_pass\'\n')
sitepp.write('$swift_hash              = \'swift_secret\'\n')
sitepp.write('# Nova DB connection\n')
sitepp.write('$sql_connection 	 = "mysql://${nova_user}:${nova_db_password}@${controller_node_address}/nova"\n')
sitepp.write('# Glance backend configuration, supports \'file\', \'swift\', or \'rbd\'.\n')
sitepp.write('$glance_backend = \'file\'\n')
sitepp.write('\n')
sitepp.write('# Set this option to true to use RBD-backed glance. This will store\n')
sitepp.write('# your glance images in your ceph cluster.\n')
sitepp.write('# $glance_ceph_enabled = true\n')
sitepp.write('# $glance_ceph_user    = \'admin\'\n')
sitepp.write('# $glance_ceph_pool    = \'images\'\n')
sitepp.write('\n')
sitepp.write('# If you are using a controller node as a ceph MON node then you\n')
sitepp.write('#   need to also set this to true to enable glance on ceph.\n')
sitepp.write('#   Also ensure that the controller node stanze contains the mon\n')
sitepp.write('#   class declarations.\n')
sitepp.write('# $controller_has_mon = true\n')
sitepp.write('\n')
sitepp.write('\n')
sitepp.write('# If you are using compute hosts as ceph OSD servers then you\n')
sitepp.write('#   need to set this to true\n')
sitepp.write('# $osd_on_compute = true\n')
sitepp.write('\n')
sitepp.write('# If you run additional mons on any of your compute nodes, this must\n')
sitepp.write('# be set to true, otherwise, leave it false. When using this scenario\n')
sitepp.write('# you should leave $osd_on_compute either false or commented out. Then\n')
sitepp.write('# you will explicitly declare the Ceph OSD configuration for each\n')
sitepp.write('# compute node that should run OSD.\n')
sitepp.write('# $computes_have_mons = false\n')
sitepp.write('\n')
sitepp.write('###### Quantum plugins #######\n')
sitepp.write('# Use either OVS (the default) or Cisco quantum plugin:\n')
sitepp.write('# $quantum_core_plugin = \'ovs\'\n')
sitepp.write('$quantum_core_plugin = \'cisco\'\n')
sitepp.write('# if neither is specified, OVS will be used\n')
sitepp.write('\n')
sitepp.write('# If using the Cisco plugin, use either OVS or n1k for virtualised l2\n')
sitepp.write('# $cisco_vswitch_plugin = \'ovs\'\n')
sitepp.write('$cisco_vswitch_plugin = \'n1k\'\n')
sitepp.write('# If neither is specified, OVS will be used\n')
sitepp.write('\n')
sitepp.write('# If using the Cisco plugin, Nexus hardware can be used for l2\n')
sitepp.write('# $cisco_nexus_plugin = \'nexus\'\n')
sitepp.write('# By default this will not be used\n')
sitepp.write('\n')
sitepp.write('# If using the nexus sub plugin, specify the hardware layout by\n')
sitepp.write('# using the following syntax:\n')
sitepp.write('# $nexus_config = { \'SWITCH_IP\' => { \'COMPUTE_NODE_NAME\' : \'PORT\' } }\n')
sitepp.write('#\n')
sitepp.write('# SWITCH_IP is the ip address of a nexus device\n')
sitepp.write('# COMPUTE_NODE_NAME is the hostname of an openstack compute node\n')
sitepp.write('# PORT is the port in the switch that compute node is plugged into\n')
sitepp.write('\n')
sitepp.write('# A more complete example with multiple switches and nodes:\n')
sitepp.write('#\n')
sitepp.write('# $nexus_config = {\'1.1.1.1\' =>   {\'compute1\' => \'1/1\',\n')
sitepp.write('#                                  \'compute2\' => \'1/2\' },\n')
sitepp.write('#                  \'2.2.2.2\' =>   {\'compute3\' => \'1/3\',\n')
sitepp.write('#                                  \'compute4\' => \'1/4\'}\n')
sitepp.write('#                 }\n')
sitepp.write('#\n')
sitepp.write('\n')
sitepp.write('# Set the nexus login credentials by creating a list\n')
sitepp.write('# of switch_ip/username/password strings as per the example below:\n')
sitepp.write('#\n')
sitepp.write('# $nexus_credentials = [\'1.1.1.1/nexus_username1/secret1\',\n')
sitepp.write('#                       \'2.2.2.2/nexus_username2/secret2\']\n')
sitepp.write('#\n')
sitepp.write('# At this time the / character cannot be used as a nexus\n')
sitepp.write('# password.\n')
sitepp.write('\n')
sitepp.write('# The nexus plugin also requires the ovs plugin to be set to\n')
sitepp.write('# vlan mode.  To do this, set $tenant_network_type = \'vlan\' above.\n')
sitepp.write('\n')

sitepp.write('\n')
sitepp.write('########### Test variables ############\n')
sitepp.write('# Variables used to populate test script:\n')
sitepp.write('# /tmp/test_nova.sh\n')
sitepp.write('#\n')
sitepp.write('# Image to use for tests. Accepts \'kvm\' or \'cirros\'.\n')
sitepp.write('$test_file_image_type = \'kvm\'\n')
sitepp.write('\n')
sitepp.write('# VSM related shared variables\n')
sitepp.write('$n1kinstall    = true\n')
sitepp.write('$vemimage      = "%s"\n' % vem_image_location)
if (is_vsm_n110 == 0):
    sitepp.write('$vsmimage      = "%s"\n' % vsm_image_location)
sitepp.write('$vsmip         = "%s"\n' % vsm_control_ip)
sitepp.write('$domainid      = "%s"\n' % domain_id)
sitepp.write('$ctrlmac       = "%s"\n' % vsm_control_mac)
#sitepp.write('$ctrlmac       = "00:02:3d:72:40:00"\n')
sitepp.write('$hostmgmtint   = "%s"\n'% public_interface)
sitepp.write('$uplinkint     = "%s"\n'% uplink_interface)
sitepp.write('\n')
sitepp.write('#VXLAN Gateway related shared variables\n')
sitepp.write('\n')
sitepp.write('#$vxlangwimage         = "/home/n1kv/tonic_407_GW.qcow2"\n')
sitepp.write('\n')
sitepp.write('#### end shared variables #################\n')
sitepp.write('\n')

if (in_gw_image == 1):
     sitepp.write('$gwimage         = "%s"\n' % gw_image_location)

sitepp.write('\n')
sitepp.write('# Storage Configuration\n')
sitepp.write('# Set to true to enable Cinder services.\n')
sitepp.write('$cinder_controller_enabled     = true\n')
sitepp.write('\n')
sitepp.write('# Set to true to enable Cinder deployment to all compute nodes.\n')
sitepp.write('$cinder_compute_enabled        = true\n')
sitepp.write('\n')
sitepp.write('# The cinder storage driver to use Options are iscsi or rbd(ceph). Default\n')
sitepp.write('# is \'iscsi\'.\n')
sitepp.write('$cinder_storage_driver         = \'iscsi\'\n')
sitepp.write('\n')
sitepp.write('# The cinder_ceph_enabled configures cinder to use rbd-backed volumes.\n')
sitepp.write('# $cinder_ceph_enabled           = true\n')
sitepp.write('\n')
sitepp.write('####### OpenStack Node Definitions #####\n')
sitepp.write('# This section is used to define the hardware parameters of the nodes \n')
sitepp.write('# which will be used for OpenStack. Cobbler will automate the installation\n')
sitepp.write('# of Ubuntu onto these nodes using these settings.\n')
sitepp.write('\n')
sitepp.write('# The build node name is changed in the "node type" section further down\n')
sitepp.write('# in the file. This line should not be changed here.\n')
sitepp.write('node \'build-node\' inherits master-node {\n')
sitepp.write('\n')
sitepp.write('# This block defines the control server. Replace "control-server" with the \n')
sitepp.write('# host name of your OpenStack controller, and change the "mac" to the MAC \n')
sitepp.write('# address of the boot interface of your OpenStack controller. Change the \n')
sitepp.write('# "ip" to the IP address of your OpenStack controller.  The power_address\n')
sitepp.write('# parameter specifies the address to use for device power management,\n')
sitepp.write('# power_user and power_password specify the login credentials to use for\n')
sitepp.write('# power management, and power_type determines which Cobbler fence script\n')
sitepp.write('# is used for power management.  Supported values for power_type are\n')
sitepp.write('# \'ipmitool\' for generic IPMI devices and UCS C-series servers in standalone\n')
sitepp.write('# mode or \'ucs\' for C-series or B-series UCS devices managed by UCSM.\n')
sitepp.write('\n')

if (is_ucs_controller == 0):
    sitepp.write('  cobbler_node { \'%s\':\n' % controller_hostname)
    sitepp.write('    mac => \'%s\',\n' % controller_mac)
    sitepp.write('    ip => \'%s\',\n' % controller_ip)
    sitepp.write('    power_address  => \'%s\',\n' % controller_cimc)
    sitepp.write('    power_user => \'%s\',\n' % control_username)
    sitepp.write('    power_password => \'%s\',\n' % control_password)
    sitepp.write('    power_type => \'ipmitool\'\n')
    sitepp.write('  }\n\n')
else:
    sitepp.write('cobbler_node { \'%s\':\n' % controller_hostname)
    sitepp.write('    mac => \'%s\',\n' % controller_mac)
    sitepp.write('    ip => \'%s\',\n' % controller_ip)
    if (control_subgroup == 0):
        sitepp.write('    power_address  => \'%s\',\n' % controller_cimc)
    else:
        con_subgroup_string = controller_cimc + ":org-" + controller_subgroup_name 
        sitepp.write('    power_address  => \'%s\',\n' % con_subgroup_string)
    sitepp.write('    power_id => \'%s\',\n' % ucs_control_service_name)
    sitepp.write('    power_type => \'ucs\',\n')
    sitepp.write('    power_user => \'%s\',\n' % control_username)
    sitepp.write('    power_password => \'%s\'\n' % control_password)
    sitepp.write('  }\n\n')


sitepp.write('# This block defines the first compute server. Replace "compute-server01" \n')
sitepp.write('# with the host name of your first OpenStack compute node (note: the hostname\n')
sitepp.write('# should be in all lowercase letters due to a limitation of Puppet; refer to\n')
sitepp.write('# http://projects.puppetlabs.com/issues/1168), and change the "mac" to the \n')
sitepp.write('# MAC address of the boot interface of your first OpenStack compute node. \n')
sitepp.write('# Change the "ip" to the IP address of your first OpenStack compute node.\n')
sitepp.write('\n')
sitepp.write('# Begin compute node\n')

k = total_c_nodes - no_ucs - 1
while True:
    if (k < 0):
        break
    sitepp.write('  cobbler_node { \'%s\':\n' % c_host_list[k] )
    sitepp.write('    mac => \'%s\',\n' % c_mac_list[k])
    sitepp.write('    ip => \'%s\',\n' % c_ip_list[k])
    sitepp.write('    power_address  => \'%s\',\n' % cimc_ip_list[k])
    sitepp.write('    power_user => \'%s\',\n' % login_user_list[k])
    sitepp.write('    power_password => \'%s\',\n' % pw_list[k])
    sitepp.write('    power_type => \'ipmitool\'\n')
    sitepp.write('  }\n\n')
    k = k - 1

x = no_ucs - 1
while True:
    if (x < 0):
        break
    sitepp.write('  cobbler_node { \'%s\':\n' % ucs_host_list[x])
    sitepp.write('    mac => \'%s\',\n' % ucs_mac_list[x])
    sitepp.write('    ip => \'%s\',\n' % ucs_ip_list[x])
    if (ucs_subgroup_list[x] == "NONE"):
        sitepp.write('    power_address  => \'%s\',\n' % ucs_cimc_list[x])
    else:
        subgroup_string = ucs_cimc_list[x] + ":org-" + ucs_subgroup_list[x]
        sitepp.write('    power_address  => \'%s\',\n' % subgroup_string)

    sitepp.write('    power_id => \'%s\',\n' % ucs_service_name_list[x])
    sitepp.write('    power_type => \'ucs\',\n')
    sitepp.write('    power_user => \'%s\',\n' %ucs_admin_user_list[x])
    sitepp.write('    power_password => \'%s\'\n' % ucs_pw_list[x])
    sitepp.write('  }\n')
    x = x -1

nw_n = total_nw_nodes - 1
while True:
    if (nw_n < 0):
        break
    sitepp.write('  cobbler_node { \'%s\':\n' % nw_host_list[nw_n] )
    sitepp.write('    mac => \'%s\',\n' % nw_mac_list[nw_n])
    sitepp.write('    ip => \'%s\',\n' % nw_ip_list[nw_n])
    if (nw_subgroup_list[nw_n] == "0"):
        sitepp.write('    power_address  => \'%s\',\n' % nw_cimc_ip_list[nw_n])
    else:
        subgroup_string = nw_cimc_ip_list[nw_n] + ":org-" + \
                                 nw_subgroup_list[nw_n]
        sitepp.write('    power_address  => \'%s\',\n' % subgroup_string)

    sitepp.write('    power_user => \'%s\',\n' % nw_login_user_list[nw_n])
    sitepp.write('    power_password => \'%s\',\n' % nw_node_passwd_list[nw_n])
    if not (nw_service_list[nw_n] == "0"):
        sitepp.write('    power_id => \'%s\',\n' % nw_service_list[nw_n])
        sitepp.write('    power_type => \'ucs\',\n')
    else:
        sitepp.write('    power_type => \'ipmitool\',\n')
        
    sitepp.write('  }\n\n')
    nw_n = nw_n - 1

sitepp.write('\n\n')

if (is_vsm_n110 == 0):
    if (vsm_is_ucs == 0):
        sitepp.write('  cobbler_node { \'%s\':\n' % vsm_host )
        sitepp.write('    mac => \'%s\',\n' % vsm_mac)
        sitepp.write('    ip => \'%s\',\n' % vsm_ip)
        sitepp.write('    power_address  => \'%s\',\n' % vsm_cimc)
        sitepp.write('    power_user     => \'%s\',\n' % vsm_admin_user)
        sitepp.write('    power_password => \'%s\',\n' % vsm_admin_pw)
        sitepp.write('    power_type     => \'ipmitool\',\n')
        sitepp.write('  }\n\n')
    else:
        sitepp.write('  cobbler_node { \'%s\':\n' % vsm_host)
        sitepp.write('    mac => \'%s\',\n' % vsm_mac)
        sitepp.write('    ip => \'%s\',\n' % vsm_ip)
        if (vsm_diff_subgroup == 0):
            sitepp.write('    power_address  => \'%s\',\n' % vsm_cimc)
        else:
            subgroup_string = vsm_cimc + ":org-" + vsm_subgroup 
            sitepp.write('    power_address  => \'%s\',\n' % subgroup_string)

        sitepp.write('    power_id => \'%s\',\n'% vsm_service_name)
        sitepp.write('    power_type => \'ucs\',\n')
        sitepp.write('    power_user => \'%s\',\n'% vsm_admin_user)
        sitepp.write('    power_password => \'%s\'\n' % vsm_admin_pw)

        sitepp.write('  }\n\n')


    if (kvm_secondary == 1):
        if (secvsm_is_ucs == 0):
            sitepp.write('  cobbler_node { \'%s\':\n' % sec_kvm_host)
            sitepp.write('    mac => \'%s\',\n' % sec_kvm_mac)
            sitepp.write('    ip => \'%s\',\n' % sec_vsm_ip)
            sitepp.write('    power_address  => \'%s\',\n' % sec_kvm_cimc)
            sitepp.write('    power_type     => \'ipmitool\',\n')
            sitepp.write('    power_user     => \'%s\',\n' % sec_admin_user)
            sitepp.write('    power_password => \'%s\',\n' % sec_admin_pw)
            sitepp.write('  }\n\n')
        else:
            sitepp.write('  cobbler_node { \'%s\':\n' % sec_kvm_host)
            sitepp.write('    mac => \'%s\',\n' % sec_kvm_mac)
            sitepp.write('    ip => \'%s\',\n' % sec_vsm_ip)
            sitepp.write('    power_id => \'%s\',\n'% sec_vsm_service_name)
            if (secvsm_diff_subgroup == 0):
                sitepp.write('    power_address  => \'%s\',\n' % sec_kvm_cimc)
            else:
                sec_subgroup_string = sec_kvm_cimc + ":org-" + secvsm_subgroup 
                sitepp.write('    power_address  => \'%s\',\n' % sec_subgroup_string)
            sitepp.write('    power_type => \'ucs\',\n')
            sitepp.write('    power_user => \'%s\',\n'% sec_admin_user)
            sitepp.write('    power_password => \'%s\'\n' % sec_admin_pw)
            sitepp.write('  }\n\n')
       
    sitepp.write('}\n\n')
else:
    sitepp.write('}\n\n')

sitepp.write('# Example with UCS blade power_address with a sub-group (in UCSM), and \n')
sitepp.write('# a ServiceProfile for power_id.\n')
sitepp.write('#  cobbler_node { "compute-server01":\n')
sitepp.write('#    mac => "11:22:33:44:66:77",\n')
sitepp.write('#    ip => "192.168.242.21",\n')
sitepp.write('#    power_address  => "192.168.242.121:org-cisco",\n')
sitepp.write('#    power_id => "OpenStack-1",\n')
sitepp.write('#    power_type => \'ucs\',\n')
sitepp.write('#    power_user => \'admin\',\n')
sitepp.write('#    power_password => \'password\'\n')
sitepp.write('#  }\n')
sitepp.write('# End compute node\n')
sitepp.write('\n')
sitepp.write('# Standalone cinder storage nodes. If cinder is enabled above,\n')
sitepp.write('# it is automatically installed on all compute nodes. The below definition\n')
sitepp.write('# allows the addition of cinder volume only nodes.\n')
sitepp.write('#  cobbler_node { "cinder-volume01":\n')
sitepp.write('#    mac => "11:22:33:44:55:66",\n')
sitepp.write('#    ip => "192.168.242.22",\n')
sitepp.write('#    power_address => "192.168.242.122",\n')
sitepp.write('#    power_user => "admin",\n')
sitepp.write('#    power_password => "password",\n')
sitepp.write('#    power_type => "ipmitool"\n')
sitepp.write('# }\n')
sitepp.write(' \n')
sitepp.write('\n')
sitepp.write('### Repeat as needed ###\n')
sitepp.write('# Make a copy of your compute node block above for each additional OpenStack\n')
sitepp.write('# node in your cluster and paste the copy in this section. Be sure to change\n')
sitepp.write('# the host name, mac, ip, and power settings for each node.\n')
sitepp.write('\n')
sitepp.write('# This block defines the first swift proxy server. Replace "swift-server01"\n')
sitepp.write('# with the host name of your first OpenStack swift proxy node (note: \n')
sitepp.write('# the hostname should be in all lowercase letters due to a limitation of\n')
sitepp.write('# Puppet; refer to http://projects.puppetlabs.com/issues/1168), and change\n')
sitepp.write('# the "mac" to the MAC address of the boot interface of your first OpenStack\n')
sitepp.write('# swift proxy node.  Change the "ip" to the IP address of your first\n')
sitepp.write('# OpenStack swift proxy node.\n')
sitepp.write('\n')
sitepp.write('# Begin swift proxy node\n')
sitepp.write('#  cobbler_node { "swift-proxy01":\n')
sitepp.write('#    node_type => "swift-proxy",\n')
sitepp.write('#    mac => "11:22:33:aa:bb:cc",\n')
sitepp.write('#    ip => "192.168.242.179",\n')
sitepp.write('#    power_address  => "192.168.242.12"\n')
sitepp.write('#  }\n')
sitepp.write('\n')
sitepp.write('# This block defines the first swift storage server. Replace "swift-storage01"\n')
sitepp.write('# with the host name of your first OpenStack swift storage node (note: the\n')
sitepp.write('# hostname should be in all lowercase letters due to a limitation of Puppet;\n')
sitepp.write('# refer to http://projects.puppetlabs.com/issues/1168), and change the "mac"\n')
sitepp.write('# to the MAC address of the boot interface of your first OpenStack swift\n')
sitepp.write('# storage node.  Change the "ip" to the IP address of your first OpenStack\n')
sitepp.write('# swift storage node.\n')
sitepp.write('\n')
sitepp.write('# Begin swift storage node\n')
sitepp.write('#  cobbler_node { "swift-storage01":\n')
sitepp.write('#    node_type => "swift-storage",\n')
sitepp.write('#    mac => "11:22:33:cc:bb:aa",\n')
sitepp.write('#    ip => "192.168.242.180",\n')
sitepp.write('#    power_address  => "192.168.242.13"\n')
sitepp.write('#  }\n')
sitepp.write('\n')
sitepp.write('### Repeat as needed ###\n')
sitepp.write('# Make a copy of your swift storage node block above for each additional\n')
sitepp.write('# node in your swift cluster and paste the copy in this section. Be sure \n')
sitepp.write('# to change the host name, mac, ip, and power settings for each node.\n')
sitepp.write('\n')
sitepp.write('### this block defines the ceph monitor nodes\n')
sitepp.write('### you will need to add a node type for each addtional mon node\n')
sitepp.write('### eg ceph-mon02, etc. This is due to their unique id requirements\n')
sitepp.write('#  cobbler_node { "ceph-mon01":\n')
sitepp.write('#    node_type     => "ceph-mon01",\n')
sitepp.write('#    mac           => "11:22:33:cc:bb:aa",\n')
sitepp.write('#    ip            => "192.168.242.180",\n')
sitepp.write('#    power_address => "192.168.242.13",\n')
sitepp.write('#  }\n')
sitepp.write('\n')
sitepp.write('### this block define ceph osd nodes\n')
sitepp.write('### add a new entry for each node\n')
sitepp.write('#  cobbler_node { "ceph-osd01":\n')
sitepp.write('#    node_type     => "ceph-osd01",\n')
sitepp.write('#    mac           => "11:22:33:cc:bb:aa",\n')
sitepp.write('#    ip            => "192.168.242.181",\n')
sitepp.write('#    power_address => "192.168.242.14",\n')
sitepp.write('#  }\n')
sitepp.write('\n')
sitepp.write('### End repeated nodes ###\n')
#sitepp.write('}\n')
sitepp.write('\n')
sitepp.write('### Node types ###\n')
sitepp.write('# These lines specify the host names in your OpenStack cluster and what the\n')
sitepp.write('# function of each host is.  internal_ip should be the same as what is\n')
sitepp.write('# specified as "ip" in the OpenStack node definitions above.\n')
sitepp.write('# This sets the IP for the private(internal) interface of controller nodes\n')
sitepp.write('# (which is predefined already in $controller_node_internal, and the internal\n')
sitepp.write('# interface for compute nodes.\n')
sitepp.write('# In this example, eth0 is both the public and private interface for the\n')
sitepp.write('# controller.\n')
sitepp.write('# tunnel_ip allows you to create a network specifically for GRE tunneled\n')
sitepp.write('# traffic between compute and network nodes. Generally, you will want to\n')
sitepp.write('# use "ip" from the OpenStack node definitions above.\n')
sitepp.write('# This sets the IP for the private interface of compute and network nodes.\n')
sitepp.write('\n')
sitepp.write('# Change build_server to the host name of your build node.\n')
sitepp.write('# Note that the hostname should be in all lowercase letters due to a\n')
sitepp.write('# limitation of Puppet (refer to http://projects.puppetlabs.com/issues/1168).\n')

sitepp.write('node %s inherits build-node { }\n' % socket.gethostname())
sitepp.write('\n')

sitepp.write('# Change control-server to the host name of your control node.  Note that the\n')
sitepp.write('# hostname should be in all lowercase letters due to a limitation of Puppet\n')
sitepp.write('# (refer to http://projects.puppetlabs.com/issues/1168).  If you wish\n')
sitepp.write('# to disable the L3, DHCP, or metadata agents on the control node,\n')
sitepp.write('# uncomment the appropriate parameters in the node definition below.  By\n')
sitepp.write('# default, all agents will run on the control node.\n')

sitepp.write('node \'%s\' inherits os_base {\n' % controller_hostname)
sitepp.write('  class { \'control\':\n')
sitepp.write('    enable_dhcp_agent     => false,\n')
sitepp.write('    enable_l3_agent       => false,\n')
sitepp.write('    enable_ovs_agent      => false,\n')
sitepp.write('    enable_metadata_agent => false,\n')

sitepp.write('  }\n')

sitepp.write('  quantum_plugin_cisco {\n')
sitepp.write('    \'N1KV:%s/username\' : value => \'admin\';\n' % vsm_control_ip)
sitepp.write('    \'N1KV:%s/password\' :' % vsm_control_ip)
sitepp.write(' value => \'%s\';\n' % vsm_control_pw)
sitepp.write('  }\n')
sitepp.write('\n')
sitepp.write(' quantum_plugin_cisco {\n')
sitepp.write('   \'CISCO_N1K/integration_bridge\' : value => \'br-int\';\n')
sitepp.write('   \'CISCO_N1K/tunnel_bridge\' : value => \'br-int\';\n')
sitepp.write('   \'CISCO_N1K/local_ip\' : value => \'%s\';\n' % controller_ip)
sitepp.write('   \'CISCO_N1K/tenant_network_type\' : value => \'local\';\n')
sitepp.write('   \'CISCO_N1K/bridge_mappings\' : value => \' \';\n')
sitepp.write('   \'CISCO_N1K/default_policy_profile\' : value => \'dhcp_pp\';\n')
sitepp.write('   \'CISCO_N1K/POLL_DURATION\' : value => \'10\';\n')
sitepp.write('   \'DATABASE/sql_connection\' : value => \'mysql://quantum:quantum_pass@127.0.0.1/quantum?charset=utf8\';\n')
sitepp.write(' }\n')
sitepp.write('\n')
sitepp.write('\n')
if (in_gw_image == 1):
    sitepp.write('     n1k-vxlangw {\'vxgwvm\':\n')
    sitepp.write('     gw_isoimage => $::gwimage,\n')
    sitepp.write('     os_password => $admin_password,\n')
    sitepp.write('     controller_ip => $controller_node_address,\n')
    sitepp.write('   }\n')
sitepp.write('}\n')
sitepp.write('  # If you want to run ceph mon0 on your controller node, uncomment the\n')
sitepp.write('  # following block. Be sure to read all additional ceph-related\n')
sitepp.write('  # instructions in this file.\n')
sitepp.write('  # Only mon0 should export the admin keys.\n')
sitepp.write('  # This means the following if statement is not needed on the additional\n')
sitepp.write('  # mon nodes.\n')
sitepp.write('  # if !empty($::ceph_admin_key) {\n')
sitepp.write('  #   @@ceph::key { \'admin\':\n')
sitepp.write('  #     secret       => $::ceph_admin_key,\n')
sitepp.write('  #     keyring_path => \'/etc/ceph/keyring\',\n')
sitepp.write('  #   }\n')
sitepp.write('  # }\n')
sitepp.write('\n')
sitepp.write('  # Each MON needs a unique id, you can start at 0 and increment as needed.\n')
sitepp.write('  # class {\'ceph_mon\': id => 0 }\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('# Change network-server01 to the host name of your first network node.\n')
sitepp.write('# Note that the hostname should be in all lowercase letters due to a\n')
sitepp.write('# limitation of Puppet (refer to http://projects.puppetlabs.com/issues/1168).\n')
sitepp.write('# As n1k uvem is being installed on network node, set enable_ovs_agent=false.\n')
sitepp.write('# Set true or false for enable_l3_agent and enable_dhcp_agent based on the requirement.\n')
sitepp.write('#node \'network-server01\' inherits os_base {\n')
sitepp.write('#  class { \'network\':\n')
sitepp.write('#    internal_ip => \'51.1.1.4\',\n')
sitepp.write('#    ovs_local_ip => \'51.1.1.4\' ,\n')
sitepp.write('#    enable_l3_agent => true,\n')
sitepp.write('#    enable_dhcp_agent => true,\n')
sitepp.write('#    enable_ovs_agent => false,\n')
sitepp.write('#    bridge_mappings => \'br-int:eth3\',\n')
sitepp.write('#  }\n')
sitepp.write('#  class {"n1k-vem":\n')
sitepp.write('#    vemimage => $vemimage,\n')
sitepp.write('#    vsmip => $vsmip,\n')
sitepp.write('#    domainid => $domainid,\n')
sitepp.write('#    hostmgmtint => $hostmgmtint,\n')
sitepp.write('#    uplinkint => $uplinkint,\n')
sitepp.write('#    vtepconfig => \'vmknic-int1 profint mode dhcp mac 00:01:22:33:44:66\',\n')
sitepp.write('#    n1kconfname => "ns1",\n')
sitepp.write('#  }\n')
sitepp.write('#}\n')

sitepp.write('# Change compute-server01 to the host name of your first compute node.\n')
sitepp.write('# Note that the hostname should be in all lowercase letters due to a\n')
sitepp.write('# limitation of Puppet (refer to http://projects.puppetlabs.com/issues/1168).\n')

sitepp.write('# If you want to run a dhcp agent on the compute node, uncomment the\n')
sitepp.write('# \'enable_dhcp_agent => true\' line below.  If you want to run an L3\n')
sitepp.write('# agent on the compute node, uncomment the \'enable_l3_agent => true" line\n')
sitepp.write('# below.  If you want to run an OVS agent on the compute node,\n')
sitepp.write('# uncomment the \'enable_ovs_agent => true\' line below.\n')

k = total_c_nodes - no_ucs - 1
while True:
    if (k < 0 ):
        break
    sitepp.write('node \'%s\' inherits os_base {\n' % c_host_list[k])
    sitepp.write('  class { \'compute\':\n')
    sitepp.write('    internal_ip   => \'%s\',\n' % c_ip_list[k])
    sitepp.write('    enable_dhcp_agent => %s,\n' % c_dhcp_enable_list[k])
    sitepp.write('    enable_ovs_agent => false,\n')
    sitepp.write('  }\n')
    sitepp.write('  class {"n1k-vem":\n')
    sitepp.write('     vemimage => $vemimage,\n')
    sitepp.write('     node_type => "compute",\n')
    sitepp.write('     vsmip => $vsmip,\n')
    sitepp.write('     domainid => $domainid,\n')
    sitepp.write('     hostmgmtint => $hostmgmtint,\n')
    sitepp.write('     uplinkint => $uplinkint,\n')
    if not (c_vtep_list[k] == "NONE"):
        sitepp.write('     vtepconfig => \'%s\',\n' % c_vtep_list[k])
    else:
        sitepp.write('     vtepconfig => \'no\',\n')

    if not (compute_vtep_diff_subnet_list[k] == "NONE"):
        sitepp.write('     isMultipleVtepInSameSubnet => \'true\',\n')
    else:
        sitepp.write('     isMultipleVtepInSameSubnet => \'false\',\n')

    sitepp.write('     n1kconfname => "%s",\n' % c_host_list[k] )
    sitepp.write('  }\n')
    sitepp.write('\n')
    sitepp.write('  if $::cinder_ceph_enabled {\n')
    sitepp.write('    class { \'coe::ceph::compute\':\n')
    sitepp.write('      poolname => $::cinder_rbd_pool,\n')
    sitepp.write('     }\n\n')
    sitepp.write('  }\n\n')

    sitepp.write('}\n\n')
    k = k - 1

x = no_ucs - 1
while True:
    if (x < 0):
        break
    sitepp.write('node \'%s\' inherits os_base {\n' % ucs_host_list[x])
    sitepp.write('  class { \'compute\':\n')
    sitepp.write('    internal_ip   => \'%s\',\n' % ucs_ip_list[x])
    sitepp.write('    enable_dhcp_agent => %s,\n' % ucs_dhcp_enable_list[x])
    sitepp.write('    enable_ovs_agent => false,\n')
    sitepp.write('  }\n')
    sitepp.write('  class {"n1k-vem":\n')
    sitepp.write('     vemimage => $vemimage,\n')
    sitepp.write('     node_type => "compute",\n')
    sitepp.write('     vsmip => $vsmip,\n')
    sitepp.write('     domainid => $domainid,\n')
    sitepp.write('     hostmgmtint => $hostmgmtint,\n')
    sitepp.write('     uplinkint => $uplinkint,\n')
    if not (ucs_vtep_list[x] == "NONE"):
        sitepp.write('     vtepconfig => \'%s\',\n' % ucs_vtep_list[x])
    else:
        sitepp.write('     vtepconfig => \'no\',\n')
    if not (ucs_vtep_diff_subnet_list[x] == "NONE"):
        sitepp.write('     isMultipleVtepInSameSubnet => \'true\',\n')
    else:
        sitepp.write('     isMultipleVtepInSameSubnet => \'false\',\n')

    sitepp.write('     n1kconfname => "%s",\n' % ucs_host_list[x])
    sitepp.write('  }\n')
    sitepp.write('\n')
    sitepp.write('  if $::cinder_ceph_enabled {\n')
    sitepp.write('    class { \'coe::ceph::compute\':\n')
    sitepp.write('      poolname => $::cinder_rbd_pool,\n')
    sitepp.write('    }\n\n')
    sitepp.write('   }\n\n')
    x = x - 1
    sitepp.write('}\n\n')

nw_n = total_nw_nodes - 1
while True:
    if (nw_n < 0):
        break

    sitepp.write('node \'%s\' inherits os_base {\n' % nw_host_list[nw_n])
    sitepp.write('  class { \'network\':\n')
    sitepp.write('    internal_ip => \'%s\',\n' % nw_ip_list[nw_n])
    sitepp.write('    ovs_local_ip =>  \'%s\',\n' % nw_ip_list[nw_n])
    sitepp.write('    enable_l3_agent => true,\n')
    sitepp.write('    enable_dhcp_agent => %s,\n' % nw_dhcp_enable_list[nw_n])
    sitepp.write('    enable_ovs_agent => false,\n')
    sitepp.write('    bridge_mappings => \'br-int:%s\',\n' % external_interface)
    sitepp.write('  }\n')
    sitepp.write('  class {"n1k-vem":\n')
    sitepp.write('    vemimage => $vemimage,\n')
    sitepp.write('    node_type => "network",\n')
    sitepp.write('    vsmip => $vsmip,\n')
    sitepp.write('    domainid => $domainid,\n')
    sitepp.write('    hostmgmtint => $hostmgmtint,\n')
    sitepp.write('    uplinkint => $uplinkint,\n')
    if not (nw_vtep_list[nw_n] == "NONE"):
        sitepp.write('    vtepconfig => \'%s\',\n' %  nw_vtep_list[nw_n])
    else:
        sitepp.write('    vtepconfig => \'no\',\n')

    if not (nw_vtep_diff_subnet_list[nw_n] == "NONE"):
        sitepp.write('    isMultipleVtepInSameSubnet => \'true\',\n')
    else:
        sitepp.write('    isMultipleVtepInSameSubnet => \'false\',\n')
        
    sitepp.write('    n1kconfname => "%s",\n' % nw_host_list[nw_n])
    sitepp.write('  }\n')
    sitepp.write('}\n\n\n')
    nw_n = nw_n -1


if (is_vsm_n110 == 0):
    sitepp.write('node %s {\n' %vsm_host)
    sitepp.write('     class { n1k-vsm:\n')
    sitepp.write('          # if you have a host with kvm/ovs configured already where you want to bring up\n')
    sitepp.write('          # the vsm, then comment the next 6 lines\n')
    sitepp.write('          configureovs => true,\n')
    sitepp.write('          ovsbridge => "br0",\n')
    sitepp.write('          physicalinterfaceforovs => "%s",\n' % public_interface)
    sitepp.write('          nodeip => "%s",\n' % vsm_ip)
    sitepp.write('          nodenetmask => "%s",\n' % cob_node_netmask)
    sitepp.write('          nodegateway => "%s",\n' % cob_node_gw)
    sitepp.write('          nodedns => $::node_dns,\n')

    sitepp.write('          ### The commented out parameters have a default value as specified, if you want it to be\n')
    sitepp.write('          ### different uncomment the parameter and change the value as required\n')
    sitepp.write('          ### memory is specified in KiB and disk size is in GB.\n')
    sitepp.write('\n')
    sitepp.write('          vcpu => \'2\',\n')
    sitepp.write('          memory => \'4096000\',\n')
    sitepp.write('          #disksize => \'4\'\n')
    sitepp.write('          #consolepts => \'2\',\n')
    sitepp.write('\n')
    sitepp.write('          vsmname => \'vsm-p\',\n')
    sitepp.write('          role => \'%s\',\n' % vsm_role)
    sitepp.write('          isoimage => $::vsmimage,\n')
    sitepp.write('          domainid => $::domainid,\n')
    sitepp.write('          adminpasswd => \'%s\',\n' % vsm_control_pw)
    sitepp.write('          mgmtip => $::vsmip,\n')
    sitepp.write('          mgmtnetmask => \'%s\',\n' % cob_node_netmask)
    sitepp.write('          mgmtgateway => \'%s\',\n' % cob_node_gw)
    sitepp.write('          ctrlinterface => [\'tap0\', $::ctrlmac, \'br0\' ],\n')
    sitepp.write('          mgmtinterface => [\'tap1\', \'00:02:3d:72:40:02\', \'br0\'],\n')
    sitepp.write('          pktinterface => [\'tap2\', \'00:02:3d:72:40:03\', \'br0\']\n')
    sitepp.write('     }\n')
    sitepp.write('}\n')
    sitepp.write('\n')

    if (kvm_secondary == 1):
        sitepp.write('node \'%s\' {\n' % sec_kvm_host)
        sitepp.write(' class { n1k-vsm:\n')
        sitepp.write('      configureovs => true,\n')
        sitepp.write('      ovsbridge => "br0",\n')
        sitepp.write('      physicalinterfaceforovs => "%s",\n' % public_interface)
        sitepp.write('      nodeip => "%s",\n' % sec_vsm_ip)
        sitepp.write('      nodenetmask => "%s",\n' % cob_node_netmask)
        sitepp.write('      nodegateway => "%s",\n' % cob_node_gw)
        sitepp.write('      nodedns => $::node_dns,\n')
        sitepp.write('      ####\n')
        sitepp.write('      vsmname => \'vsm-s\',\n')
        sitepp.write('      role => \'secondary\',\n')
        sitepp.write('      isoimage => $::vsmimage,\n')
        sitepp.write('      domainid => $::domainid,\n')
        sitepp.write('      adminpasswd => \'%s\',\n' % vsm_control_pw)
        sitepp.write('      mgmtip => \'0.0.0.0\',\n')
        sitepp.write('      mgmtnetmask => \'0.0.0.0\',\n')
        sitepp.write('      mgmtgateway => \'0.0.0.0\',\n')
        sitepp.write('      ctrlinterface => [\'tap0\', \'00:02:4d:72:40:01\', \'br0\' ],\n')
        sitepp.write('      mgmtinterface => [\'tap1\', \'00:02:4d:72:40:02\', \'br0\'],\n')
        sitepp.write('      pktinterface => [\'tap2\', \'00:02:4d:72:40:03\', \'br0\']\n')
        sitepp.write(' }\n')
        sitepp.write('}\n\n\n')

sitepp.write('\n')

sitepp.write('### Repeat as needed ###\n')
sitepp.write('# Copy the compute-server01 line above and paste a copy here for each\n')
sitepp.write('# additional OpenStack node in your cluster. Be sure to replace the\n')
sitepp.write('# \'compute-server01\' parameter with the correct host name for each\n')
sitepp.write('# additional node.\n')
sitepp.write('\n')
sitepp.write('# Uncomment the node definiton below to create a standalone\n')
sitepp.write('# network node.  Standalone network nodes provide Quantum services\n')
sitepp.write('# such as L3 and/or DHCP agents, but do not run nova-compute and\n')
sitepp.write('# therefore do not house instances.  They are often employed when\n')
sitepp.write('# for scalability reasons when you want to be able to dedicate\n')
sitepp.write('# a node\'s full resources to providing networking functions or\n')
sitepp.write('# want to split networking functions across nodes.\n')
sitepp.write('#node \'network01\' inherits os_base {\n')
sitepp.write('#  class { \'network\':\n')
sitepp.write('#    enable_dhcp_agent => true,\n')
sitepp.write('#    enable_l3_agent   => true,\n')
sitepp.write('#    internal_ip       => \'2.6.1.5\',\n')
sitepp.write('#  }\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('# Defining cinder storage nodes is only necessary if you want to run\n')
sitepp.write('# cinder volume servers aside from those already on the compute nodes. To\n')
sitepp.write('# do so, create a node entry for each cinder-volume node following this model.\n')
sitepp.write('#node \'cinder-volume01\' inherits os_base {\n')
sitepp.write('#  class { \'cinder_node\': }\n')
sitepp.write('  # The volume class can be changed to different drivers (eg iscsi, rbd)\n')
sitepp.write('  # you can only use one type per host. Be mindful of this if you use\n')
sitepp.write('  # different backends on different cinder-volume nodes.\n')
sitepp.write('\n')
sitepp.write('  # If you are using iscsi as your storage type, uncomment the following class\n')
sitepp.write('  # and use a facter readable address for the interface that iscsi should use\n')
sitepp.write('  # eg. $::ipaddress, or for a specific interface $::ipaddress_eth0 etc.\n')
sitepp.write('  #class { \'cinder::volume::iscsi\':\n')
sitepp.write('  #  iscsi_ip_address => $::ipaddress,\n')
sitepp.write('  #}\n')
sitepp.write('\n')
sitepp.write('  # If you are using rbd, uncomment the following ceph classes.\n')
sitepp.write('  #class { \'ceph::conf\':\n')
sitepp.write('  #  fsid            => $::ceph_monitor_fsid,\n')
sitepp.write('  #  auth_type       => $::ceph_auth_type,\n')
sitepp.write('  #  cluster_network => $::ceph_cluster_network,\n')
sitepp.write('  #  public_network  => $::ceph_public_network,\n')
sitepp.write('  #}\n')
sitepp.write('  #\n')
sitepp.write('  #class { \'ceph::osd\':\n')
sitepp.write('  #  public_address  => \'192.168.242.22\',\n')
sitepp.write('  #  cluster_address => \'192.168.242.22\',\n')
sitepp.write('  #}\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('# Swift Proxy\n')
sitepp.write('# Adjust the value of swift_local_net_ip to match the IP address\n')
sitepp.write('# of your first Swift proxy node.  It is generally not necessary\n')
sitepp.write('# to modify the value of keystone_host, as it will default to the\n')
sitepp.write('# address of your control node.\n')
sitepp.write('#node \'swift-proxy01\' inherits os_base {\n')
sitepp.write('#  class {\'openstack::swift::proxy\':\n')
sitepp.write('#    swift_local_net_ip     => $swift_proxy_address,\n')
sitepp.write('#    swift_proxy_net_ip     => $swift_proxy_address,\n')
sitepp.write('#    keystone_host          => $controller_node_address,\n')
sitepp.write('#    swift_user_password    => $swift_password,\n')
sitepp.write('#    swift_hash_suffix      => $swift_hash,\n')
sitepp.write('#    swift_memcache_servers => ["${swift_proxy_address}:11211"],\n')
sitepp.write('#    memcached_listen_ip    => $swift_proxy_address,\n')
sitepp.write('#  }\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('# Swift Storage\n')
sitepp.write('# Modify the swift_local_net_ip parameter to match the IP address of\n')
sitepp.write('# your Swift storage nodes.  Modify the storage_devices parameter\n')
sitepp.write('# to set the list of disk devices to be formatted with XFS and used\n')
sitepp.write('# for Swift storage.  Our deployment model requires a minimum of 3\n')
sitepp.write('# storage nodes, but it is recommended to use at least 5 storage nodes\n')
sitepp.write('# (to support 5 zones) for production deployments.\n')
sitepp.write('#node \'swift-storage01\' inherits os_base {\n')
sitepp.write('#  class {\'openstack::swift::storage-node\':\n')
sitepp.write('#    swift_zone         => \'1\',\n')
sitepp.write('#    swift_local_net_ip => \'192.168.242.71\',\n')
sitepp.write('#    storage_type       => \'disk\',\n')
sitepp.write('#    storage_devices    => [\'sdb\',\'sdc\',\'sdd\'],\n')
sitepp.write('#    swift_hash_suffix  => $swift_hash,\n')
sitepp.write('#  }\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('#node \'swift-storage02\' inherits os_base {\n')
sitepp.write('#  class {\'openstack::swift::storage-node\':\n')
sitepp.write('#    swift_zone         => \'2\',\n')
sitepp.write('#    swift_local_net_ip => \'192.168.242.72\',\n')
sitepp.write('#    storage_type       => \'disk\',\n')
sitepp.write('#    storage_devices    => [\'sdb\',\'sdc\',\'sdd\'],\n')
sitepp.write('#    swift_hash_suffix  => $swift_hash,\n')
sitepp.write('#  }\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('#node \'swift-storage03\' inherits os_base {\n')
sitepp.write('#  class {\'openstack::swift::storage-node\':\n')
sitepp.write('#    swift_zone         => \'3\',\n')
sitepp.write('#    swift_local_net_ip => \'192.168.242.73\',\n')
sitepp.write('#    storage_type       => \'disk\',\n')
sitepp.write('#    storage_devices    => [\'sdb\',\'sdc\',\'sdd\'],\n')
sitepp.write('#    swift_hash_suffix  => $swift_hash,\n')
sitepp.write('#  }\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('### Repeat as needed ###\n')
sitepp.write('# Copy the swift-storage01 node definition above and paste a copy here for\n')
sitepp.write('# each additional OpenStack swift storage node in your cluster.  Modify\n')
sitepp.write('# the node name, swift_local_net_ip, and storage_devices parameters\n')
sitepp.write('# accordingly.\n')
sitepp.write('\n')
sitepp.write('# Ceph storage\n')
sitepp.write('# For each OSD you need to specify the public address and the cluster address\n')
sitepp.write('# the public interface is used by the ceph client to access the service\n')
sitepp.write('# the cluster (management) interface can be the same as the public address\n')
sitepp.write('# if you have only one interface. It\'s recommended you have a separate\n')
sitepp.write('# management interface.  This will offload replication and heartbeat from\n')
sitepp.write('# the public network.\n')
sitepp.write('# When reloading an OSD, the disk seems to retain some data that needs to\n')
sitepp.write('# be wiped clean. Before reloading the node, you MUST remove the OSD from\n')
sitepp.write('# the running configuration. Instructions on doing so are located here:\n')
sitepp.write('# http://ceph.com/docs/master/rados/operations/add-or-rm-osds/#removing-osds-manual\n')
sitepp.write('# Once complete, reinstall the node. Then, before running the puppet agent\n')
sitepp.write('# on a reloaded OSD node, format the filesystem to be used by the OSD. Then\n')
sitepp.write('# delete the partition, delete the partition table, then dd /dev/zero to the\n')
sitepp.write('# disk itself, for a reasonable count to clear any remnant disk info.\n')
sitepp.write('# ceph MONs must be configured so a quorum can be obtained. You can have\n')
sitepp.write('# one mon, and three mons, but not two, since no quorum can be established.\n')
sitepp.write('# No even number of MONs should be used.\n')
sitepp.write('\n')
sitepp.write('# Configuring Ceph\n')
sitepp.write('#\n')
sitepp.write('# ceph_auth_type: you can specify cephx or none, but please don\'t actually\n')
sitepp.write('# use none.\n')
sitepp.write('#\n')
sitepp.write('# ceph_monitor_fsid: ceph needs a cluster fsid. This is a UUID ceph uses for\n')
sitepp.write('# monitor creation.\n')
sitepp.write('#\n')
sitepp.write('# ceph_monitor_secret: mon hosts need a secret. This must be generated on\n')
sitepp.write('# a host with ceph already installed.  Create one by running\n')
sitepp.write('# \'ceph-authtool --create /path/to/keyring --gen-key -n mon.:\'\n')
sitepp.write('#\n')
sitepp.write('# ceph_monitor_port: the port that ceph MONs will listen on. 6789 is default.\n')
sitepp.write('#\n')
sitepp.write('# ceph_monitor_address: corresponds to the facter IP info. Change this to\n')
sitepp.write('# reflect your public interface.\n')
sitepp.write('#\n')
sitepp.write('# ceph_cluster_network: the network mask of your cluster (management)\n')
sitepp.write('# network (can be identical to the public netmask).\n')
sitepp.write('#\n')
sitepp.write('# ceph_public_network: the network mask of your public network.\n')
sitepp.write('#\n')
sitepp.write('# ceph_release: specify the release codename to install the respective release.\n')
sitepp.write('# dumpling is the latest, but as of this writing dumpling has a known issue\n')
sitepp.write('# that causes ceph-backed glance to not function correctly.  This is due to a\n')
sitepp.write('# bug in ceph that will be resolved in the next dumpling point release.\n')
sitepp.write('#\n')
sitepp.write('# cinder_rbd_user: the user configured in ceph to allow cinder rwx access\n')
sitepp.write('# to the volumes pool.  This currently requires the name \'volumes\'. Do not\n')
sitepp.write('# change it.\n')
sitepp.write('#\n')
sitepp.write('# cinder_rbd_pool: the name of the pool in ceph for cinder to use for\n')
sitepp.write('# block device creation.  This currently requires the name \'volumes\'. Do\n')
sitepp.write('# not change it.\n')
sitepp.write('#\n')
sitepp.write('# cinder_rbd_secret_uuid: the uuid secret to allow cinder to communicate\n')
sitepp.write('# with ceph. If you change this your ceph installation will break.\n')
sitepp.write('\n')
sitepp.write('#$ceph_auth_type         = \'cephx\'\n')
sitepp.write('#$ceph_monitor_fsid      = \'e80afa94-a64c-486c-9e34-d55e85f26406\'\n')
sitepp.write('#$ceph_monitor_secret    = \'AQAJzNxR+PNRIRAA7yUp9hJJdWZ3PVz242Xjiw==\'\n')
sitepp.write('#$ceph_monitor_port      = \'6789\'\n')
sitepp.write('#$ceph_monitor_address   = $::ipaddress\n')
sitepp.write('#$ceph_cluster_network   = \'192.168.242.0/24\'\n')
sitepp.write('#$ceph_public_network    = \'192.168.242.0/24\'\n')
sitepp.write('#$ceph_release           = \'cuttlefish\'\n')
sitepp.write('#$cinder_rbd_user        = \'admin\'\n')
sitepp.write('#$cinder_rbd_pool        = \'volumes\'\n')
sitepp.write('#$cinder_rbd_secret_uuid = \'e80afa94-a64c-486c-9e34-d55e85f26406\'\n')
sitepp.write('\n')
sitepp.write('# This global path needs to be uncommented for puppet-ceph to work.\n')
sitepp.write('# Uncomment and define the proxy server if your nodes don\'t have direct\n')
sitepp.write('# access to the internet. This is due to apt needing to run a wget.\n')
sitepp.write('#Exec {\n')
sitepp.write('#  path        => \'/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\',\n')
sitepp.write('#  environment => "https_proxy=$::proxy",\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('\n')
sitepp.write('#node \'ceph-mon01\' inherits os_base {\n')
sitepp.write('  # Only mon0 should export the admin keys.\n')
sitepp.write('  # This means the following if statement is not needed on the additional\n')
sitepp.write('  # mon nodes.\n')
sitepp.write('#  if !empty($::ceph_admin_key) {\n')
sitepp.write('#    @@ceph::key { \'admin\':\n')
sitepp.write('#      secret       => $::ceph_admin_key,\n')
sitepp.write('#      keyring_path => \'/etc/ceph/keyring\',\n')
sitepp.write('#    }\n')
sitepp.write('#  }\n')
sitepp.write('\n')
sitepp.write('  # Each MON needs a unique id, you can start at 0 and increment as needed.\n')
sitepp.write('#  class {\'ceph_mon\': id => 0 }\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('# Model each additional MON after the following. Remember to increment the id.\n')
sitepp.write('# node \'ceph-mon02\' inherits os_base {\n')
sitepp.write('#  class { \'ceph_mon\': id => 1 }\n')
sitepp.write('# }\n')
sitepp.write('\n')
sitepp.write('# This is the OSD node definition example. You will need to specify the\n')
sitepp.write('# public and cluster IP for each unique node.\n')
sitepp.write('\n')
sitepp.write('#node \'ceph-osd01\' inherits os_base {\n')
sitepp.write('#  class { \'ceph::conf\':\n')
sitepp.write('#    fsid            => $::ceph_monitor_fsid,\n')
sitepp.write('#    auth_type       => $::ceph_auth_type,\n')
sitepp.write('#    cluster_network => $::ceph_cluster_network,\n')
sitepp.write('#    public_network  => $::ceph_public_network,\n')
sitepp.write('#  }\n')
sitepp.write('#  class { \'ceph::osd\':\n')
sitepp.write('#    public_address  => \'192.168.242.3\',\n')
sitepp.write('#    cluster_address => \'192.168.242.3\',\n')
sitepp.write('#  }\n')
sitepp.write('  # Specify the disk devices to use for OSD here.\n')
sitepp.write('  # Add a new entry for each device on the node that ceph should consume.\n')
sitepp.write('  # puppet agent will need to run four times for the device to be formatted,\n')
sitepp.write('  #   and for the OSD to be added to the crushmap.\n')
sitepp.write('#  ceph::osd::device { \'/dev/sdd\': }\n')
sitepp.write('#}\n')
sitepp.write('\n')
sitepp.write('\n')
sitepp.write('### End repeated nodes ###\n')
sitepp.write('\n')
sitepp.write('########################################################################\n')
sitepp.write('### All parameters below this point likely do not need to be changed ###\n')
sitepp.write('########################################################################\n')
sitepp.write('\n')
sitepp.write('### Advanced Users Configuration ###\n')
sitepp.write('# These four settings typically do not need to be changed.\n')
sitepp.write('# In the default deployment, the build node functions as the DNS and static\n')
sitepp.write('# DHCP server for the OpenStack nodes. These settings can be used if\n')
sitepp.write('# alternate configurations are needed.\n')


sitepp.write('$node_dns           = $cobbler_node_ip\n')
sitepp.write('$ip                 = $cobbler_node_ip\n')
sitepp.write('$dns_service        = \'dnsmasq\'\n')
sitepp.write('$dhcp_service       = \'dnsmasq\'\n')
sitepp.write('$time_zone          = \'UTC\'\n')
sitepp.write('$force_config_drive = false\n')
sitepp.write('\n')
sitepp.write('# Enable network interface bonding. This will only enable the bonding module\n')
sitepp.write('# in the OS. It won\'t actually bond any interfaces. Edit the networking\n')
sitepp.write('# interfaces template to set up interface bonds as required after setting\n')
sitepp.write('# this to true should bonding be required.\n')
sitepp.write('#$interface_bonding = \'true\' \n')
sitepp.write('\n')
sitepp.write('# Enable ipv6 router edvertisement.\n')
sitepp.write('#$ipv6_ra = \'1\'\n')
sitepp.write('\n')
sitepp.write('# Adjust Quantum quotas\n')
sitepp.write('# These are the default Quantum quotas for various network resources.\n')
sitepp.write('# Adjust these values as necessary. Set a quota to \'-1\' to remove all\n')
sitepp.write('# quotas for that resource. Also, keep in mind that Nova has separate\n')
sitepp.write('# quotas which may also apply as well.\n')
sitepp.write('#\n')
sitepp.write('# Number of networks allowed per tenant\n')
sitepp.write('$quantum_quota_network             = \'10\'\n')
sitepp.write('# Number of subnets allowed per tenant\n')
sitepp.write('$quantum_quota_subnet              = \'10\'\n')
sitepp.write('# Number of ports allowed per tenant\n')
sitepp.write('$quantum_quota_port                = \'50\'\n')
sitepp.write('# Number of Quantum routers allowed per tenant\n')
sitepp.write('$quantum_quota_router              = \'10\'\n')
sitepp.write('# Number of floating IPs allowed per tenant\n')
sitepp.write('$quantum_quota_floatingip          = \'50\'\n')
sitepp.write('# Number of Quantum security groups allowed per tenant\n')
sitepp.write('$quantum_quota_security_group      = \'10\'\n')
sitepp.write('# Number of security rules allowed per security group\n')
sitepp.write('$quantum_quota_security_group_rule = \'100\'\n')
sitepp.write('\n')
sitepp.write('# Configure the maximum number of times mysql-server will allow\n')
sitepp.write('# a host to fail connecting before banning it.\n')
sitepp.write('$max_connect_errors = \'10\'\n')
sitepp.write('\n')
sitepp.write('### modify disk partitioning ###\n')
sitepp.write('# set expert_disk to true if you want to specify partition sizes,\n')
sitepp.write('#  of which root and var are currently supported\n')
sitepp.write('# if you do not want a separate /var from /, set enable_var to false\n')
sitepp.write('# if you do not want extra disk space set aside in an LVM volume\n')
sitepp.write('#  then set enable_vol_space to false (you likely want this true if you\n')
sitepp.write('#  want to use iSCSI CINDER on the compute nodes, and you must set\n')
sitepp.write('#  expert_disk to true to enable this.\n')
sitepp.write('\n')
sitepp.write('$expert_disk           = true\n')
sitepp.write('$root_part_size        = 65536\n')
sitepp.write('$var_part_size         = 1048576\n')
sitepp.write('$enable_var            = true\n')
sitepp.write('$enable_vol_space      = true\n')
sitepp.write('\n')
sitepp.write('# Select vif_driver and firewall_driver for quantum and quantum plugin\n')
sitepp.write('# These two parameters can be changed if necessary to support more complex\n')
sitepp.write('# network topologies as well as some Quantum plugins.\n')
sitepp.write('# These default values are required for Quantum security groups to work\n')
sitepp.write('# when using Quantum with OVS.\n')
sitepp.write('#$libvirt_vif_driver      = \'nova.virt.libvirt.vif.LibvirtHybridOVSBridgeDriver\'\n')
sitepp.write('#$quantum_firewall_driver = \'quantum.agent.linux.iptables_firewall.OVSHybridIptablesFirewallDriver\'\n')
sitepp.write('# If you don\'t want Quantum security groups when using OVS, comment out the\n')
sitepp.write('# libvirt_vif_driver line above and uncomment the libvirt_vif_driver below\n')
sitepp.write('# instead\n')
sitepp.write('# $libvirt_vif_driver = \'nova.virt.libvirt.vif.LibvirtGenericVIFDriver\'\n')
sitepp.write('$libvirt_vif_driver = \'nova.virt.libvirt.vif.LibvirtGenericVIFDriver\'\n')
sitepp.write('\n')
sitepp.write('# If you want to ensure that a specific Ubuntu kernel version is installed\n')
sitepp.write('# and that it is the default GRUB boot selection when nodes boot for the\n')
sitepp.write('# first time, uncomment the line below and enter the name of the\n')
sitepp.write('# linux-image package you want to load.  Note that this feature has only\n')
sitepp.write('# been tested with Ubuntu\'s generic kernel images.\n')
#sitepp.write('$load_kernel_pkg = \'linux-image-3.5.0-55-generic\'\n')
sitepp.write('$load_kernel_pkg = \'linux-image-3.2.0-55-generic\'\n')

sitepp.write('\n')
sitepp.write('### Puppet Parameters ###\n')
sitepp.write('# These settings load other puppet components. They should not be changed.\n')
sitepp.write('import \'cobbler-node\'\n')
sitepp.write('import \'core\'\n')
sitepp.write('\n')
sitepp.write('## Define the default node, to capture any un-defined nodes that register\n')
sitepp.write('## Simplifies debug when necessary.\n')
sitepp.write('\n')
sitepp.write('node default {\n')
sitepp.write('  notify{\'Default Node: Perhaps add a node definition to site.pp\': }\n')
sitepp.write('}\n')


sitepp.close()
os.system ('cp site.pp.temp /etc/puppet/manifests/site.pp')
print "\n SUCCESS. Created site.pp file and it is at the following location"
print "  /etc/puppet/manifests"
print ""
print "All the values entered are saved in /home/n1kv/logs/site_data_file.txt"
print "You can do \"create_sitepp.py -f /home/n1kv/logs/site_data_file.txt\""
print ""
site_pp_log.write('Script ended at %s ' % datetime.datetime.now().isoformat())

os.system('rm site.pp.temp')
if (os.path.isfile("temp_input.txt")):
    os.system('rm temp_input.txt')
site_pp_log.close()
site_data_file.close()
exit()

