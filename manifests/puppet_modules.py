#!/usr/bin/env python
# This script will get all puppet modules required
# for the deployment of the Cisco OpenStack Edition (COE).
# Set REPO_NAME below to the name of the yum or apt repository you want to use.
# Choices include:
#    * A main release repo.  This will include the latest tested and 
#      released modules.  This is the recommended choice for most users.
#      Example: "grizzly"
#    * A proposed repo.  This includes the latest code that developers have
#      committed.  It is considered bleeding edge and may not have been
#      fully vetted.  This is recommended only for developers.
#      Example: "grizzly-proposed"
#    * A specific maintenance release repo.  This allows you to download
#      modules from a specific release.  This is recomended option if you
#      have qualified only a specific release for your environment and do
#      not wish to (yet) use the latest stable updates.
#      Example: "grizzly/snapshots/2013.4.1"

import os
import sys
import optparse
import platform
import tempfile
import subprocess

#-------- Default Constants ---------------------

## ----- global variables that can be configurable via cmdline.
REPO_NAME = "grizzly-proposed"
#APT_REPO_URL = "ftp://ftpeng.cisco.com/openstack/cisco"
# uncomment this line if you prefer to use http
APT_REPO_URL = "http://openstack-repo.cisco.com/openstack/dfa"

## ------- Other Constants --------------------------
MODULE_FILE = "modules.list"
PUPPET_PATH = "/etc/puppet/"

# config file locations for yum and apt
APT_CONFIG_FILE = "/etc/apt/sources.list.d/cisco-openstack-mirror_grizzly.list"
YUM_CONFIG_FILE = "/etc/yum.repos.d/cisco-openstack-mirror.repo"

# gpg keys for yum and apt repos with which packages are signed
APT_REPO_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----
Version: GnuPG v1.4.11 (GNU/Linux)

mQINBFJUsHkBEADlDRSBi0PREZSN6iByY6OoAudJrcbC1WRWm5Sqn88mSIdeO0HZ
fgVpeiVqjiouUAvpgbJcspXd8suHqINgfA37OlCwwcdabbOiz9qNDSF0HoJ++nRn
w+deq/YnlzkFjQ1VUKJbA4lNySZ27ERu/PDMOWRmFDimMvF8LCRhimWBimy3x+Ab
em5PizN6/Gdnf8sjb2sprilGpHS349+7Pa9tkmt/tXIBP0W+510/hMpo3WBvoGj/
37gOMStIkhAuG/43+l3aCL0Z45nkiY5L0Mhc8pO/dD29fy9o+T1pAcWU+eY0mMAo
g779N4pcuznx7ne2ZWnc8aCV6URorHSmIg/ZTiXOR0MEpSKxBEJRMgtZZp9jIbYi
2YOsMg5jQbQbpf0FNfLPwG7jN1/NpM/hATvr5E+oxGALxzALgyNCfsJn89G7P18k
P3b/EA56Rs4z7joQnsKr0wQKtIFBHQDmK7iFgqB6Xi3bEmE/zNHCxcPZhQ+JtuvV
w0zw5hglv2HBG1JICkfVsRfEeBnDf1q64OatgFgWoSDuRSsrRdZUrzSVxGvRfrDS
SQ6EwE6hKpkiWlPFVl7vZFwrEyQH3kQzrBJ2tpf+5Bw08HmWsCm/HYQeaX8oPux0
4G0+zqls+P0mRu+HGJ8Umb6XoHzMgAMUmZuMU45OP4YwlJUM9Frgkjl0VwARAQAB
tA5kZmEgcmVwb3NpdG9yeYkCOAQTAQIAIgUCUlSweQIbLwYLCQgHAwIGFQgCCQoL
BBYCAwECHgECF4AACgkQj8Am2wrFmxpPlg//cVNqKQw4/igZ/olOHdcwEWDX/WAE
HCDgeyvhU5W9AxlE2OggDgevVEta3x75E4fPFKLBjtZsrr519Yis7jFJnJ4f9Orr
7LtsMSh287Jsylg/15tpAIrpArOHlQItiZshkZxX/0daivXlQshp2qzsQkKsZdQ+
j/8I890zhz3w5KC+lneOr5DEcJk5ujWIabdHFaJIJrsawPd1XYutbxhAn4T+IS7b
84sPKqaP/BfyG9wokNdbEUfij4BeB5bCFfMT3eJ2aNK6IgtgtNlNdi4pdq7Tfbx8
DanrHSzYvnETh8OiAsiA2b/yr8YkEilGPNZLkVZCRUSCmHchKkUmnl1zHRuHRC0W
jxXmH1Mu9XNgXB1ganLQQpqhwsQkmgzWziqggS0rL6SRxKx5uLnR5b/l54zjVu3Z
7EnZ/8v1sGRMcRwyTy/kvsQg6MUT8A/zpG4TfZms1Mi4WSllLT7r9dmCN1SM5Yq4
c0ChBl96/rNt3bfqP2lpAfRsgNCq7CDkSB5HrQy9kaQSf7TqqJ3u1jfRRo7e8ZSY
boN51zlYvQtXZYFej7Fs5w84Za0gBFD+J2mXse3/8G2EMdQI2ML0Bze4XU5LNn8l
mwMXjc5sOOUSINg+9LC1WNPgUQzQQWJbhIyxiZJho8dgSmP8ccYF0Kc5GJypJRz4
peSsfBcC3pxbgNy5BA0EUlSweRAQAMEAKlWjf16TEkgw1sL3XDNGMA8RToDSUrks
t7s0Otrz10W1Tr85fkAD+zNXCRmiALfN4jo3+WsIV+N9t1/CuGqX3NOHTJKLrv7y
BIgeJmkqTvusxRG+cH6jSkHwb3W8UgeH0/67TpVNLKxoie7pq+HoCuPCuDOzwVdf
p0mAYXUNbaYJI+VGnvRxSHpXSbsKrIRWbwdsqPCEUOzjqKxPncU8kOvxl3sFI1Ho
XF8UV6b3GdNN1NStwQwuSa+Y2nmDTTHxgA4OZVtK1VQ/i9zfLT3jyR6LZkpEdx2S
CINnvo9ZgnTLCrdfGBnrOhSckN7e5qtdLW64Oi2+UEK8EMaEo1qr97AYfT8rBD63
NLze8gloXpzQUJHbKZ7X+h1EKnw4fJK50jIE+3hkF1olK7zZ4/imVo4FSYcXmMgD
zgvIxh8rV6aLIXYFbU3Gv2U/aJhrG4XtVj81MLE21ayJQaWcF/1l5L3038emOmik
vwK5a/IGwwYmiWnaypaqqzPweENvq5BSznbhsYx04L34Tu8obB1/TuAvO2umntOa
a0cHmtEKMRqtuBDgQYR5ISaonOyaYoOUHcE7uiorHWbWFCV02YDV9RFdAJi0iee+
KJ4DbhjjfOwEg7NLVBWlDntEF+1wvfJeIt2RWymEg5nYkPVftCJmY03emBbEIMxJ
uTWXyM+TAAMGD/44pSnfz4g3pn4mmbxe09ejELnzIhB1bVr0VGXxy2ZqfARm6epe
y+dL+/tzUd1VcrB8bzAQaXGlWtoAaGFIt/Tr9rQw3Ayvdzfo+CuF5N8tDOBZWrEK
bWIiwfsQDAdDPYndaTYFZTaN7omUYe94f39XytHgPdV5OGwfXbJsMQvyKreMUs4U
5BQg5Hrem8Mx1fFUYXb1RyJWxgTi7r6Z8t3LiSGSk/rOaVEIfX9AOCxivsC9hB9x
nHo4zt7yT6qKhjAt/FyorOHgxo18iG9v6FLs7zoJtnz37ZS0v1JnhFrBZRoXp7jk
c1+Gyr+k+WRYpZgyRlb0kV5Um4Pa2VRiCeDFjJN0FfLbJIGuaubUvWN/7e9QebBa
3xWCmH7TVivyE6EbFereqe/M2PmxHo4AVs4DAhnGNI4JVj8e/veN5/IRvlC1ELXh
RzWLTERcQgTWq5hEOWG4LPT685iBsxJCu8U3MzCIr4tB9x4CNIQqHNN3cUSe96fo
gW/EICB5mETHPf13jldGcIHgXDwjq6HHWkjcuvj5EjOj0TE9Wv8Sv1LxUPDfIsrx
PLkwsYpf7CusP8FUy6+0l/VpvbIbBojq/ON3ie4ExVokdWZdUbjYfBiqANvn8/OV
txS6/jFzHCT8YtoAiU1zHO1+8kiojs7y8nGIeR6jQMOdciQ9T1Cj9Wwe84kCHwQY
AQIACQUCUlSweQIbDAAKCRCPwCbbCsWbGkDUD/4rsgGyQcki7lIAze8a6dycK/Zs
SGxOnY7cVdekPdOmZ2GqazAcexgT+L3bzN1wldjy8pHPq8F+jWoMkeEdXw9duReh
3mPBQ9P5Q+OQ1n7sHfWUZvjSmhhfu+7aRp7gqeu1fc3JwaQIGoTMhU55bCDGymuP
6ozXUv2Fxc8Pm21IPh7mk3Ygn1O/A35W0s0K3e0SPrpr5Oe6F6BRAIoz86QHBDOF
v3WzjzvxDqFWUqwTLc0Ovry6ZLEOLSkBnqkJWLt9soH9D365gmbgKP2Vmpvu8IQj
SOp65pIbfUwQcvi5c6mCJlavTb88eQbJj9L/+b8BfjQsXhTQMWSTwhFerdXNI6zr
WZ6jkJHzoG3haC3K1D3V6QSYtTEQH9MgmvE7LfqTdA2A8I2HGH+93Sj+wzv4IOSR
L8BK8I+aSBSuUICubaqaNboxCjUCzcXsavrjafUPcmi+rGG+K7ODnnUqISs2Rt88
uH4kubcr3loqICXDdxtFNWx9FAM7qynVwrbXGK/CHM4Iw8x1q2SPgQr6A5DQ86me
QMRBUH9PHf2hV7KcTUmVQ72tE35CpHzbReECliURL0/A+df6i2uDwFOLUkjOaFhP
etiI8VAoXSjccmYHuvu1rRcLL8l7DeeZwC2bbPBD1zgbt/jd33cNDfF5ZVupvEHt
vNlU7geM8bjNTkKJgA==
=QN2y
-----END PGP PUBLIC KEY BLOCK-----"""
##TODO: Once we have a gpg for red hat manifest packages, include it here.
YUM_REPO_KEY = """TBD"""

##TODO: replace this with right url location once in place. Ideally
# we want a generic url with type and dist info. For example:
# http://eng.cisco.com/openstack/cisco/$type/dist/$release/
# where $type = 'yum' or 'apt'; $release= 'folsom' or 'grizzly' etc.

# yum repo url and .repo file setup
YUM_REPO_URL = "ftp://ftpeng.cisco.com/openstack/cisco/fedora/dist/grizzly"
YUM_REPO_DATA = """
[cisco-openstack-mirror]
name=Cisco Openstack Repository
baseurl= %(repo_url)s
enabled=1
gpgcheck=0
gpgkey=%(repo_url)s/coe.pub
""" % {'repo_url': YUM_REPO_URL}

# --- helper calls to fetch and install packages ----------


def setup_apt_sources():
    """
    # APT repo url and source file setup
    """
    global REPO_NAME, APT_REPO_URL
    return """
# cisco-openstack-mirror_grizzly
deb %(repo_url)s %(repo_name)s main
deb-src %(repo_url)s %(repo_name)s main
""" % {'repo_url': APT_REPO_URL, 'repo_name': REPO_NAME}


def override_globals(options):
    """
    Override the global variables passed in via commandline
    """
    for opt_var in ["REPO_NAME", "APT_REPO_URL"]:
        if getattr(options, opt_var) is not None:
            # vars()[opt_var] = getattr(options, opt_var)
            globals().__setitem__(opt_var, getattr(options, opt_var))


def get_modules(modules_file=MODULE_FILE):
    """
     Read the module list file and get a list of all module names.
     We need to prepend the module name with "puppet-" to match the
     package names.
    """
    return ["puppet-" + line.strip() for line in open(modules_file)]


def get_distribution():
    """
     Get the distribution we're dealing with
    """
    return platform.dist()[0]


def setup_apt_repo():
    """
     Setup apt repo to install manifest packages via apt
    """
    if os.path.exists(APT_CONFIG_FILE):
        # could be outdated, lets remove and set it up fresh
        try:
            os.remove(APT_CONFIG_FILE)
        except IOError, OSError:
            raise Exception("Unable to remove the config " \
                            "file [%s]" % APT_CONFIG_FILE)
    # no config file found, lets set one up
    with open(APT_CONFIG_FILE, 'a') as f:
        f.write(setup_apt_sources())
    # add gpg key to apt
    apt_key_add()


def apt_key_add():
    """
     Add the gpg key to apt repository
    """
    with tempfile.NamedTemporaryFile() as temp:
        temp.write(APT_REPO_KEY)
        temp.flush()
        run_command(['apt-key', 'add', temp.name])


def apt_update():
    """
     Update apt repo
    """
    run_command(['apt-get', 'update'])


def apt_install(modules):
    """
     Install packages via apt
    """
    apt_update()
    run_command(['apt-get', 'install', '-y'] + modules)


def setup_yum_repo():
    """
     Setup yum repos to install package manifests via yum.
     We just download the .repo file from the yum repo url.
     Example yum repo file is as follows:
     [cisco-openstack-mirror]
     name=Cisco Openstack Repository
     baseurl=ftp://ftpeng.cisco.com/openstack/cisco/yum/dist/grizzly/
     enabled=1
     gpgcheck=1
     gpgkey=ftp://ftpeng.cisco.com/openstack/cisco/yum/dist/grizzly/coe.pub

    """
    if os.path.exists(YUM_CONFIG_FILE):
        # could be outdated, lets remove and set it up fresh
        try:
            os.remove(YUM_CONFIG_FILE)
        except IOError, OSError:
            raise Exception("Unable to remove the config file [%s]" \
                            % YUM_CONFIG_FILE)
    # no config found, let download from the repo url
    with open(YUM_CONFIG_FILE, 'wb') as repo_file:
        repo_file.write(YUM_REPO_DATA)


def yum_install(modules):
    """
     Install packages via yum
    """
    run_command(['yum', 'install', '-y'] + modules)


def run_command(command_args):
    """
    Execute system calls
    """
    proc = subprocess.Popen(command_args, shell=False)
    proc.communicate()


def main():
    """
     This main call does the following:
      - Parse the modules file and get list of packages
      - Check the distribution we're working with yum/apt
      - Perform repo setup for yum or apt repos
      - install necessary packages
    """
    
    #bail if not root or sudo
    if not os.getenv("USER") == 'root':
        print("Must run as root or sudo")
        sys.exit(1)
    
    # parse and get list of modules
    modules = get_modules(MODULE_FILE)
    # set up the repos and perform install
    distro = get_distribution().lower()
    if distro in ["redhat", "fedora"]:
        setup_yum_repo()
        yum_install(modules)
    elif distro in ["ubuntu", ]:
        setup_apt_repo()
        apt_install(modules)

if __name__ == '__main__':
    main()
