# Now using these: http://cloud-images.ubuntu.com/releases/precise/release-20121218/
# Via: http://cloud-images.ubuntu.com/locator/ec2/: "instance-store amd64 LTS 12.04"
# Current as of 12/20/2012
### Script provided by DataStax.
### Last Modified by Tito Panicker www.titopanicker.net


# Download and install repo keys
gpg --keyserver pgp.mit.edu --recv-keys 2B5C1B00
gpg --export --armor 2B5C1B00 | sudo apt-key add -
wget -O - http://installer.datastax.com/downloads/ubuntuarchive.repo_key | sudo apt-key add -
wget -O - http://debian.datastax.com/debian/repo_key | sudo apt-key add -


# Install Git
sudo apt-get -y update
sudo apt-get -y install git

# Git these files on to the server's home directory
git config --global color.ui auto
git config --global color.diff auto
git config --global color.status auto
#git clone git://github.com/riptano/ComboAMI.git datastax_ami
git clone https://github.com/titotp/ComboAMI.git datastax_ami
cd datastax_ami
git checkout $(head -n 1 presetup/VERSION)

# Install Java
sudo FORCE_ADD_APT_REPOSITORY=1 add-apt-repository ppa:webupd8team/java
sudo echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | sudo /usr/bin/debconf-set-selections
sudo apt-get update && sudo apt-get install oracle-jdk7-installer
sudo update-java-alternatives -s java-7-oracle

# Begin the actual priming
git pull
sudo python presetup/pre_2.py
sudo chown -R ubuntu:ubuntu . 
rm -rf ~/.bash_history 
history -c


# git pull && rm -rf ~/.bash_history && history -c
