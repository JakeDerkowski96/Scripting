#!/bin/bash
# automate update and upgrade
#  BUT PRETTY

#***NOTE TO SELF: Print out the statistics of the upgrade, but not all of the output
# ?tail the output stream.. or store in log and then grab last line

check_fig() {
  FIG="/usr/bin/figlet";
  if [ ! f "$FIG" ]; then
    sudo apt-get install -y figlet > /dev/null;
  fi
}

check_cat() {
  LOL="/usr/games/lolcat"
  if [ ! -f "$LOL" ]; then
    sudo apt-get install -y lolcat > /dev/null;
  fi
}

pprint() { echo -e $1 | figlet | lolcat; }

comp() { sleep 0.5; printf "\nDone.\n"; sleep 1; clear; }

upD() { sudo apt-get update > /dev/null; }

upG() { sudo apt-get -y upgrade > /dev/null; }

remove() { sudo apt-get -y autoremove > /dev/null; }

usroff() {
  printf "System will be turned off in 5s\n"; 		sleep 0.5;
  printf "Press 'ctrl + C' now to stop and exit\n";	sleep 0.5;
  sudo shutdown > /dev/null;
}

reboot(){
  read -p "Would you like to restart the system? (Y/n): " ANS

  if [[ "$ANS" = "y" || "$ANS" == "Y" ]]; then
    usroff;
  else
    printf "\nMachine has now been updated\n";	sleep 0.3;
    printf "Reboot may be necessary for these changes to take effect.\n";
    sleep 0.3; clear;
    exit;
  fi
}


printf "\n\n\t~~~Checking system~~~\n\n";
check_fig;
check_cat;

pprint "Updating...";   sleep 0.5;
clear;
# --------------------------------------------
pprint "Updating";    	sleep 0.2;
pprint "Repositories";  sleep 0.2;
upD;	                  comp;
# --------------------------------------------

# --------------------------------------------
pprint "Upgrading";	   sleep 0.2;
pprint "Packages"; 	   sleep 0.2;
upG; 	                 comp;
# --------------------------------------------

# --------------------------------------------
pprint "Removing"; 	   sleep 0.2;
pprint "Unnecessary";  sleep 0.2;
pprint "Packages"; 	   sleep 0.2;
remove;                comp;
# --------------------------------------------
reboot;
