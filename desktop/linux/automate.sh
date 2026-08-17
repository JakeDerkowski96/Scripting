#!/bin/bash
# automate fresh installation, to include:
# 1. make terminal pretty, make aliases
# 2. install packages and applications && update
# 3. install snaps
# experiment with bash automation

SYSUSR=$USER # MAIN USER
CWD=$(pwd)
SCRIPTS="${CWD}/scripts"
PKGS="${SCRIPTS}/packages.sh"
SNAPS="${SCRIPTS}/snaps.sh"
TERM="${SCRIPTS}/bash.sh"
# DEBS="${SCRIPTS}/debs.sh"

FUNC=".functions.sh"

source $FUNC

# automate installaton
read -p "Automate installation? (Y/n)?  : " answer
while true; do
  case $answer in
    [Yy]* ) echo -e "ok, i got ya"; sleep 0.5;

            check_dir logs;
            echo -e "Details found in the 'logs' folder";

            echo -e "Beginning..."; sleep 0.5;

            # dispaly pretty terminal
            show_host_ip;

            bash $TERMIN
            bash $PKGS
            bash $SNAPS

            # check_dir "deb";

            break;;

    [Nn]* ) echo -e "why run this then?"
            exit;;

    * )     echo "Invalid input";
            echo -e "Enter (Y/n)";;
  esac
done
