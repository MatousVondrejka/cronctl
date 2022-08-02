# cronctl
Project created as showcase for Travelport GDS

How to use:
$ ./cronctl.py --help #Cheat sheet
$ ./cronctl.py --check #Check existing scripts, if are not valid, delete
$ ./cronctl.py --remove --files testing_examples/* #Delete all cron records related to scripts in folder
$ ./cronctl.py --add --type T --files testing_examples/script-1.sh #Add script to crontab with specific time based on selected type

Features:
-checking and fillter input for executable scripts
-checking cron records
-support mass adding and removing scripts
-follow schema of adding, grep from script columns like: #PT:cron:10 1,2,3,4 * * *