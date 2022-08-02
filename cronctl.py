#!/usr/bin/python3
import argparse
from genericpath import exists
import os
import re
import crontab
import getpass


#----------------------------------------------------------------------
#Argument proccessing
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-a", "--add", action="store_true", help='adding script to crontab, not work with remove, must be use with --type')
group.add_argument("-r", "--remove", action="store_true", help='delete script from crontab, not work with add')
group.add_argument("-c", "--check", action="store_true", help='check valid of all crons, run every time')
parser.add_argument("-t", "--type", choices=['P','T','D','I'],help='Specified type: production/test/devel/internal, must be use with --add')
parser.add_argument("--files", nargs='+', help='Path to script',required=False)
args = parser.parse_args()



#----------------------------------------------------------------------
#Input handle
if args.add == args.remove and not(args.check):
    raise ValueError("Specifie add, remove or check")
    
if args.add and args.type==None:
    raise ValueError("Missing type.")

filesexecutable = []
if args.add or args.remove:
    for file in args.files:
        if os.access(file, os.X_OK) and not(os.path.isdir(file)):
            filesexecutable.append(file)

    if 0 == len(filesexecutable):
        raise ValueError("No script is choose.")

#----------------------------------------------------------------------

def add_script(file, type):
    f = open(file, 'r')
    # Find lines for cron and right type
    cronlines = ''
    for cronsearch in f:
        if cronsearch.startswith('#') and re.search('cron', cronsearch) and re.search(type, cronsearch):
            cronlines += cronsearch
    f.close()

    #Parse string as list and grep time value from it
    cronlines = cronlines.replace('\n',':')
    cronlines = cronlines.split(':')
    crontime = []
    for cronsearch in cronlines:
        if cronsearch.startswith(tuple('0123456789*')):
            crontime.append(cronsearch)
    
    #Absolute and relative path handle
    path_to_script = ''
    if (file.startswith('/')):
        path_to_script = file
    else:
        path_to_script = os.getcwd() + '/' + file

    #Check if job with time exist, if don't, then create it
    cron = crontab.CronTab(user=getpass.getuser())
    for cront in crontime:
        exist = False
        
        #Exist check
        for cronsearch in cron:
            cronsearchstring = str(cronsearch)
            if cronsearchstring.startswith(cront) and cronsearchstring.endswith(file):
               exist = True
        #Add
        if not exist:
            print('Adding...  ' + cront + ' ' + path_to_script)
            job = cron.new(command=path_to_script) #Add command
            job.setall(cront) #Add time
            cron.write()
    
#----------------------------------------------------------------------

def delete_script(file):
    cron = crontab.CronTab(user=getpass.getuser())
    for cronsearch in cron:
        cronsearchstring = str(cronsearch)
        if cronsearchstring.endswith(file):
            print('Deleting...  ' + cronsearchstring)
            cron.remove(cronsearch)
            cron.write()

#----------------------------------------------------------------------

# Check if exiting script are executable and have valid path, otherwise delete
def check_existing_script():
    cron = crontab.CronTab(user=getpass.getuser())
    cronstringfield = str(cron).split("\n")
    relatedcols = []
    for croncol in cronstringfield:
        if not croncol.startswith('#') and croncol != '':
            scriptpath = croncol.split(' ')
            relatedcols.append(scriptpath[5])
    # Make output uniq
    relatedcols = list(dict.fromkeys(relatedcols))
    for col in relatedcols:
        if not exists(col) or not os.access(col, os.X_OK):   
            print('Not valid...' + col)
            delete_script(col)
        

#----------------------------------------------------------------------        


#Calling check 
print ('----------------------------------------------------------------------')
print ('Checking phase start...')
check_existing_script()
print ('Checking phase complete...')
print ('----------------------------------------------------------------------')
#Calling add or remove
for file in filesexecutable:
    if args.add:
        add_script(file, args.type)
    if args.remove:
        delete_script(file)


