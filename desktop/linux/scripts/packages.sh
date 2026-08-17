#!/bin/bash
# install packages from apt

APT_LOG="logs/packages.txt"

source .functions.sh

echo "More info @ ${HOME_DIR}/logs/packages.txt"


#update and upgrade
update() {
  sudo apt-get update && sudo apt-get upgrade -y >> $APT_LOG
}

# Install package manager
package_managers() {
  pprint "Package Managers"
  sudo apt-get install synaptic gdebi snapd -y >> $PT_LOG
}

# user settings
settings() {
  pprint "User Settings"
  sudo apt-get install gnome-tweak-tool autoconf -y >> $APT_LOG
  sudo apt-get install automake wget sassc pkg-config optipng -y >> $APT_LOG
  sudo apt-get install numix-icon-theme python3-pip -y >> $APT_LOG
}

# network
network() {
  pprint "network";
  sudo apt-get install net-tools nmap apt-transport-https hping3 -y >> $APT_LOG

  # internet
  pprint "Internet"
  # download google chrome
  wget -qO https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
  sudo dpkg -i google-chrome*.deb -y >> $APT_LOG
  #-----
  sudo apt-get install chrome-gnome-shell links bittorrent git -y >> $APT_LOG
}

# media
media(){
  pprint "Media"; sleep 1;
  sudo apt-get install vlc -y >> $APT_LOG
  # spotify
  # curl -sS https://download.spotify.com/debian/pubkey.gpg | sudo apt-key add -
  # echo "deb http://repository.spotify.com stable non-free" | sudo tee /etc/apt/sources.list.d/spotify.list
}

# programming
prgms() {
  pprint "Programming"; sleep 1;
  sudo apt-get install -y gcc g++ sqlitebrowser mariadb-client \
  mariadb-common openjdk-11-jdk python3-pip nodejs npm >> $APT_LOG
}

# system/utilities
utilities() {
  pprint "Utilities"
  sudo apt-get install afflib-tools netdiscover wireshark openssl -y
  sudo apt-get install htop gtkhash ghex -y >> $APT_LOG

}

# office
office() {
  pprint "Office"
  sudo apt-get install texmaker cherrytree -y > $APT_LOG
  pprint "ATOM"
  wget -qO - https://packagecloud.io/AtomEditor/atom/gpgkey | sudo apt-key add -
  sudo sh -c 'echo "deb [arch=amd64] https://packagecloud.io/AtomEditor/atom/any/ any main" > /etc/apt/sources.list.d/atom.list'
  sudo apt-get update >> $APT_LOG
  sudo apt-get install atom -y >> $APT_LOG

  # sublime
  pprint "SUBLIME"
  wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
  echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
  sudo apt-get update -y > $APT_LOG
  sudo apt-get install sublime-text -y >> $APT_LOG
}


# ask user to install separate scripts
docker(){
  bash .dockerio.sh
}

github_cli(){
  bash .github.sh
}

# fail 2 ban
fail2ban(){
  bash .fail2ban.sh
}


# make ask function
ask_user() {
  read -p "Do you want to install ${1}? (Y/n) : " answer
  while true
  do
    case $answer in
      [yY]* ) ${1};
              log_separater;
              break;;

      [nN]* ) exit;;

      * )     echo "Invalid input"
              echo -e "Enter (y/n)"
     esac
   done
}

install_packages() {
  # ask yes or now for each "genre" of packages
    ask_user update;
    ask_user package_managers;
    ask_user settings;
    ask_user network;
    ask_user media;
    ask_user prgms;
    ask_user utilities;
    ask_user office;

    ask_user docker;
    ask_user github_cli;
    ask_user fail2ban;
}




pprint Debian Packages
install_packages;
pprint Done;
