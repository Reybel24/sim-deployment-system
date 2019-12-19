# Install bundles
import shutil
import os.path
import json

# Unzip to temp location
def installBundle():
    _recievedLocation = 'recieved/'
    if (os.path.exists(_recievedLocation + 'bundle.zip')):
        print('Unpacking bundle...')
        # Unpack to temporary location
        tempLocation = 'recieved/temp'
        shutil.unpack_archive('recieved/bundle.zip', tempLocation, 'zip')
        print('Unpacked successfully')

        # Read meta.json and move files to destiantions
        with open(tempLocation + '/sim-meta.json') as f:
            meta = json.load(f)
        
        root = 'env/'
        for package in meta:
            _folderName = package['folderName']
            _destination = package['unpackTo']
            print('Moving package ' + _folderName + ' to ' + _destination)
            shutil.move(tempLocation + '/' + _folderName, root + _destination)

        # Done
        print('Installation finished sucessfully.')
    else:
        print('No bundles recieved.')


# Run on command
installBundle()