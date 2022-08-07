#!/usr/bin/python3
import argparse
import os
import re
import crontab
from crontab import CronSlices


parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("-a", "--add", action="store_true", help='adding script to crontab, not work with remove, must be use with --type')
group.add_argument("-r", "--remove", action="store_true", help='delete script from crontab, not work with add')
group.add_argument("-c", "--check", action="store_true", help='check valid of all crons, run every time')
parser.add_argument("-t", "--type", choices=['P','T','D','I'],default=None ,help='Specified type: production/test/devel/internal, must be use with --add')
parser.add_argument("-f", "--files", nargs='+', help='Path to script',required=False)
args = parser.parse_args()




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

def add_script(file, type):
    f = open(file, 'r')
    cronlines = ''
    for cronsearch in f:
        if cronsearch.startswith('#') and re.search(':cron:', cronsearch) and re.search(type, cronsearch):
            cronlines += cronsearch
    f.close()

    cronlines = cronlines.replace('\n',':')
    cronlines = cronlines.split(':')
    crontime = []
    
    for cronsearch in cronlines:
        if  CronSlices.is_valid(cronsearch):
            crontime.append(cronsearch)
    
    path_to_script = ''
    if (file.startswith('/')):
        path_to_script = file
    else:
        path_to_script = os.getcwd() + '/' + file

    environ = os.environ
    
    cron = crontab.CronTab(user=environ.get('USER'))
    for cront in crontime:
        exist = False
        
        
        for cronsearch in cron:
            cronsearchstring = str(cronsearch)
            if cronsearchstring.startswith(cront) and cronsearchstring.endswith(file):
               exist = True
        
        if not exist:
            print('Adding...  ' + cront + ' ' + path_to_script)
            job = cron.new(command=path_to_script) 
            job.setall(cront) 
            cron.write()
    

def delete_script(file):
    environ = os.environ
    cron = crontab.CronTab(user=environ.get('USER'))
    
    for c in cron:
        if re.search(file, str(c)):
            print('Deleting...  ' + str(c))
            cron.remove(c)
            cron.write()



def check_existing_script():
    environ = os.environ
    cron = crontab.CronTab(user=environ.get('USER'))
    cronstringfield = str(cron).split("\n")
    relatedcols = []
    for croncol in cronstringfield:
        if croncol.startswith(tuple('0123456789*')):
            scriptpath = croncol.split(' ')
            relatedcols.append(scriptpath[5])
    relatedcols = set(relatedcols)

    os_path = environ.get('PATH')
    os_path = os_path.split(':')
    
    for col in relatedcols:
        script_valid = False
        if col.startswith('/'):
            if os.path.exists(col) and os.access(col, os.X_OK):   
                script_valid = True
        else:
            for p in os_path:
                path_for_check = p + '/' + col
                if os.path.exists(path_for_check) and os.access(path_for_check, os.X_OK):
                    script_valid = True
        if not script_valid:
            print ("Non-valid cron.... " + col)
            delete_script(col)



        



print ('----------------------------------------------------------------------')
print ('Checking phase start...')
check_existing_script()
print ('Checking phase complete...')
print ('----------------------------------------------------------------------')
for file in filesexecutable:
    if args.add:
        add_script(file, args.type)
    if args.remove:
        delete_script(file)


