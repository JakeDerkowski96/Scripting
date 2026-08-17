#!/bin/bash

snapList = "OneNote Skype "

function yes_or_no {
    while true; do
        read -p "$* [y/n]: " yn
        case $yn in
            [Yy]*) printf "install snap"
                   return 0  ;;
            [Nn]*) echo "Aborted" ; return  1 ;;
        esac
    done
}


function askUser(snapList){
  for item in snapList; do
    printf "Do you want to install $var"


}


# sudo snap install skype
sudo snap install microsoft-todo-unofficial
sudo snap install teams-insiders
sudo snap install teams
sudo snap install code
sudo snap install azure-cli-johanburati
sudo snap install p3x-onenote
