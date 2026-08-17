#!/bin/bash
# MakePretty.sh
# init script, called my main
# this will install what is needed to make this a aesthically pleasing program

# call this script from 'sys-update.sh' if the conditions not met

PRGINFO="WARNING: the use of the superuser is necessary for this script to run correctly, \
If you do not know the password, you havve no business using these scripts!"

pprint() { echo -e $1 | figlet | lolcat; }

update() {  
  sudo apt-get update > /dev/null
  sudo apt-get upgrade -y > /dev/null
}

make_pretty() {
  sudo apt-get install -y figlet toilet lolcat > /dev/null;
  printf "Pretty binaries installation complete.\n"; sleep 0.5;
}


echo $PRGINFO; sleep 1;

printf "\nBeginning setup\n"
update; sleep 0.5;

printf "\nInstalling binaries to make output pretty\n";
make_pretty; 

pprint "Setup complete"; sleep 1;

printf "Now returning to main\n"; sleep 1;
clear;
