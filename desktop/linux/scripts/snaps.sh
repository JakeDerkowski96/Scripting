#!/bin/bash
# install snaps
# ===========================================
HOME_DIR="$(cd .. && pwd)"
SNAP_LOG="${HOME_DIR}/logs/snaps.txt"
# ===========================================

source .functions.sh

echo "More info @ ${HOME_DIR}/logs/snaps.txt"

install_snaps(){
  # sudo snap install bitwarden
  sudo snap install code --classic
  # sudo snap install discord
  # sudo snap install eclipse --classic
  sudo snap install john-the-ripper
  # sudo snap install postgresql10
  # sudo snap install powershell --classic
  # sudo snap install simplenote
  sudo snap install cherrytree
  # sudo snap install hplip-printer-app --edge
  sudo snap install sublime-text --classic
  sudo snap install atom --classic
  sudo snap install eclipse --classic
  sudo snap install postman
  sudo snap install notepad-plus-plus
  sudo snap install slack --classic


}

get_ans snaps install_snaps;
figlet "Oh Snap"; sleep 2;

# start_install Snaps;
# install_snaps;
# figlet "Oh Snap"; sleep 2;
# finish_install;
