#!/usr/bin/env python
### Script provided by DataStax.
### Last Modified by Tito Panicker www.titopanicker.net

import shlex
import subprocess
import time
import os

def exe(command, shellEnabled=False):
    print '[EXEC] %s' % command
    if shellEnabled:
        process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    else:
        process = subprocess.Popen(shlex.split(command), stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    output = process.communicate()

    if output[0]:
        print 'stdout:'
        print output[0]
    if output[1]:
        print 'stderr:'
        print output[1]

    return output

def pipe(command1, command2):
    # Helper function to execute piping commands and print traces of the commands and output for debugging/logging purposes
    print '[PIPE] %s | %s' % (command1, command2)
    p1 = subprocess.Popen(shlex.split(command1), stdout=subprocess.PIPE)
    p2 = subprocess.Popen(shlex.split(command2), stdin=p1.stdout)
    p1.stdout.close()  # Allow p1 to receive a SIGPIPE if p2 exits.
    output = p2.communicate()[0]
    return output

def install_software():
    # Setup Repositories
    pipe('echo "deb http://archive.canonical.com/ lucid partner"', 'sudo tee -a /etc/apt/sources.list.d/java.sources.list')
    exe('sudo apt-get -y update')
    time.sleep(5)
    exe('sudo apt-get -y update')

    while True:
        output = exe('sudo apt-get -y upgrade')
        if not output[1] and not 'err' in output[0].lower() and not 'failed' in output[0].lower():
            break

    # Install other recommended tools
    while True:
        output = exe('sudo apt-get -y install --fix-missing libjna-java htop emacs23-nox sysstat iftop binutils pssh pbzip2 xfsprogs zip unzip ruby openssl libopenssl-ruby curl maven2 ant liblzo2-dev ntp subversion python-pip tree unzip ruby xfsprogs')
        if not output[1] and not 'err' in output[0].lower() and not 'failed' in output[0].lower():
            break

    # Install these for a much faster instance startup time
    while True:
        output = exe('sudo apt-get -y install ca-certificates-java icedtea-6-jre-cacao java-common jsvc libavahi-client3 libavahi-common-data libavahi-common3 libcommons-daemon-java libcups2 libjna-java libjpeg62 liblcms1 libnspr4-0d libnss3-1d tzdata-java')
        if not output[1] and not 'err' in output[0].lower() and not 'failed' in output[0].lower():
            break

    # Install RAID setup
    while True:
        output = exe('sudo apt-get -y --no-install-recommends install mdadm')
        if not output[1] and not 'err' in output[0].lower() and not 'failed' in output[0].lower():
            break

    # Preinstall Maven packages as a convenience
    exe('sudo -u ubuntu mvn install')
    time.sleep(5)

    # Preinstall Cassandra from source to get all the dependencies for convenience
    home_path = os.getcwd()
    exe('git clone https://github.com/apache/cassandra.git')
    os.chdir('cassandra')
    exe('ant')
    os.chdir(home_path)
    exe('rm -rf cassandra/')


# Fixed in ds1:setup_profile() for AMI 2.4
def setup_profiles():
    # Setup a link to the motd script that is provided in the git repository
    file_to_open = '/home/ubuntu/.profile'
    exe('sudo chmod 777 ' + file_to_open)
    with open(file_to_open, 'a') as f:
        f.write("""
    python datastax_ami/ds4_motd.py
    """)
    exe('sudo chmod 644 ' + file_to_open)

    os.chdir('/root')
    file_to_open = '.profile'
    exe('sudo chmod 777 ' + file_to_open)
    with open(file_to_open, 'w') as f:
        f.write("""
    """)
    exe('sudo chmod 644 ' + file_to_open)
    os.chdir('/home/ubuntu')

def create_initd():
    # Create init.d script
    initscript = """#!/bin/sh

    ### BEGIN INIT INFO
    # Provides:
    # Required-Start:    $remote_fs $syslog
    # Required-Stop:
    # Default-Start:     2 3 4 5
    # Default-Stop:
    # Short-Description: Start AMI Configurations on boot.
    # Description:       Enables AMI Configurations on startup.
    ### END INIT INFO

    # Make sure variables get set

    # Setup system properties
    sudo su -c 'ulimit -n 32768'
    echo 1 | sudo tee /proc/sys/vm/overcommit_memory

    # Clear old ami.log
    echo "\n======================================================\n" >> ami.log
    cd /home/ubuntu/datastax_ami
    python ds0_updater.py
    """
    exe('sudo touch /etc/init.d/start-ami-script.sh')
    exe('sudo chmod 777 /etc/init.d/start-ami-script.sh')
    with open('/etc/init.d/start-ami-script.sh', 'w') as f:
        f.write(initscript)
    exe('sudo chmod 755 /etc/init.d/start-ami-script.sh')

    # Setup AMI Script to start on boot
    exe('sudo update-rc.d -f start-ami-script.sh start 99 2 3 4 5 .')

def fix_too_many_open_files():
    # Setup limits.conf
    pipe('echo "* soft nofile 32768"', 'sudo tee -a /etc/security/limits.conf')
    pipe('echo "* hard nofile 32768"', 'sudo tee -a /etc/security/limits.conf')

def clear_commands():
    # Clear everything on the way out.
    exe('sudo rm .ssh/authorized_keys')
    exe("sudo rm -rf /etc/ssh/ssh_host_dsa_key*", shellEnabled=True)
    exe("sudo rm -rf /etc/ssh/ssh_host_key*", shellEnabled=True)
    exe("sudo rm -rf /etc/ssh/ssh_host_rsa_key*", shellEnabled=True)

    exe("sudo rm -rf /tmp/*", shellEnabled=True)
    exe("sudo rm -rf /tmp/.*", shellEnabled=True)
    exe('rm -rf ~/.bash_history')

def allow_keyless_ssh():
    # Allow SSH within the ring to be easier (only for private AMIs)
    # exe('ssh-keygen')
    # exe('cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys')
    pass


install_software()
setup_profiles()
create_initd()
fix_too_many_open_files()
clear_commands()

# allow_keyless_ssh()

print "Image succesfully configured."

