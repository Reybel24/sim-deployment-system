#!/usr/bin/env python
# Run this and leave running on deployment machine
import json
import mysql.connector
import zipfile
import os
import shutil, errno
import fnmatch
import pika
from RabbitConn import RabbitConn
import pexpect


class PackageBroker:
    # package-directory location
    global fileDirectory
    fileDirectory = 'package-directory.json'

    # Environment (0 for development, 1 for production)
    global env
    env = 0

    def __init__(self):
        pass

    def createMockDatabase(self):
        _db = [
            {
                "id": "vue-front-end",
                "version": 1.1,
                "location": "packages/vue-front-end_v1.1/",
                "health": 1
            },
            {
                "id": "web-back-end",
                "version": 1.4,
                "location": "packages/web-back-end_v1.4/",
                "health": 1
            },
        ]
        return _db

    # Create a metadata snippet for a single package piece
    def createMeta(self, pckg_id, pckg_version, pckg_folderName, pckg_unpackTo):
        # print("creating metadata...")
        _meta = {
            "package": pckg_id,
            "version": pckg_version,
            "folderName": pckg_folderName,
            "unpackTo": pckg_unpackTo
        }
        return _meta

    # Grab dependencies after finding package
    def grabDependencyLocations(self, packageData):
        # Print package
        print(packageData['packageID'] + ' v' +
              str(packageData['packageVersion']))
        # print(packageData['packageData'])

        # print('Listing dependencies')
        _packageList = []
        _dependencies = packageData['packageData']['dependencies']

        # Dev, prod
        if (env == 1):
            # Connect to database
            db = mysql.connector.connect(
                host='localhost',
                user='root',
                passwd='',
                database='deployment'
            )
            # print(db)
            dbCursor = db.cursor()

            # Loop through dependencies and locate in database
            for dep in _dependencies:
                # print(dep['id'])

                # Prepare and execute select statement
                _sql = """SELECT location FROM packages WHERE id = '%s'"""%(dep['id'])
                dbCursor.execute(_sql)

                # Get results
                _location = dbCursor.fetchall()

                # Empty result set?
                if (dbCursor.rowcount == 0):
                    print('Dependency ({0}) missing from database...'.format(dep['id']))
                    continue

                # Grab first result
                _location = _location[0][0]

                # Insert into array
                # Package information nicely
                _depData = {
                    'id': dep['id'],
                    'version': dep['version'],
                    'fetchLocation': _location,
                    'unpackLocation': dep['unpackLocation']
                }

                # Add to list
                _packageList.append(_depData)

            return _packageList
        else:
            print("Env is dev. Using mock database.")
            # Create and use mock database
            _mockDB = self.createMockDatabase()

            # Loop through dependencies and locate in database
            for dep in _dependencies:
                # print(dep['id'])

                # Get dependency location
                _location = ''
                for entry in _mockDB:
                    if (entry['id'] == dep['id']):
                        # Found
                        _location = entry['location']
                        # print('found location...{0}'.format(_location))
                        break

                # Dependency not found?
                if (_location == ''):
                    print('Dependency ({0}) missing from database...'.format(dep['id']))
                    continue

                # Insert into array
                # Package information nicely
                _depData = {
                    'id': dep['id'],
                    'version': dep['version'],
                    'fetchLocation': _location,
                    'unpackLocation': dep['unpackLocation']
                }

                # Add to list
                _packageList.append(_depData)

            return _packageList

    # Used as copytree() ignore parameter to exlude files and directories
    def ignore_patterns(self, patterns):
        def _ignore_patterns(path, names):
            ignored_names = []
            for pattern in patterns:
                ignored_names.extend(fnmatch.filter(names, pattern))
            return set(ignored_names)
        return _ignore_patterns
        
    def doBundle(self, dependencies):
        print('bundling...')
        # print(dependencies)

        # Stage directory
        _stageDir = 'stage/'
        
        # Delete if it already exists
        if (os.path.isdir(_stageDir)):
            shutil.rmtree(_stageDir)

        # Create stage
        os.mkdir(_stageDir)

        # Packages metadata
        _pckgMeta = []
        
        # Copy over packages
        for dep in dependencies:
            # print("({0} v{1}) Searching file system for folder {2}. Will extract to {3}".format(dep['id'], dep['version'], dep['fetchLocation'], dep['unpackLocation']))

            # Make sure folder exists in packages folder
            _pckgName = str(dep['id']) + '_v' + str(dep['version'])
            _pckgPath = dep['fetchLocation']
            if (os.path.isdir(_pckgPath)):
                # Does this directory contain a .sim-ignore file? If so, get list of files to be ignored when copying
                _ignoreFiles = []
                _simignorePath = _pckgPath + ".simignore"
                if (os.path.isfile(_simignorePath)):
                    # Read .simignore to get files to be ignored
                    with open(_simignorePath) as _simignore:
                        _line = _simignore.readline()
                        cnt = 1

                        while _line:
                            if (_line.strip()[0] == '#'):
                                # This is a commented line. Ignore it.
                                # print('Found comment: ' + _line)
                                pass
                            else:
                                # Add file or dir to list of ignored
                                _ignoreFiles.append(_line.strip())
                                # print("ignoring {}".format(_line))

                            _line = _simignore.readline()
                            cnt += 1

                # Copy folder onto stage
                shutil.copytree(_pckgPath, os.path.join(_stageDir, _pckgName), ignore=self.ignore_patterns(_ignoreFiles))

                # Metadata
                _pckgMeta.append(self.createMeta(dep['id'], dep['version'], _pckgName, dep['unpackLocation']))
            else:
                print('Package folder {0} does not exist within the package directory! Skipping it...'.format(_pckgName))

        # Add bundle metadata to file
        with open('stage/sim-meta.json', 'w') as json_file:
            json.dump(_pckgMeta, json_file, indent=4, sort_keys=False)

        # Prepare for bundling
        _dest = 'bin/'
        # Make sure directory exists. If not, create it
        if (os.path.isdir(_dest) == False):
            os.mkdir(_dest)

        # Bundle (zip, tar)
        shutil.make_archive(_dest + 'bundle', 'zip', _stageDir)

        # Clean up
        shutil.rmtree(_stageDir)

    # Find a requested package
    def findPackage(self, pck_id, pck_ver=None):
        # print("Looking for package by ID: {0} v{1}".format(pck_id, pck_ver))

        # Load in json
        with open(fileDirectory) as f:
            pckDir = json.load(f)

        # Search for package id in package-directory.json
        # print(pckDir)
        result = {
            'packageID': pck_id,
            'packageVersion': pck_ver,
            'packageNameFound': False,
            'packageVersionFound': False,
            'message': '',
            'packageData': None
        }

        _latestVersion = 0
        # Go through packages
        for package in pckDir:
            if (package == pck_id):
                result['packageNameFound'] = True
                # print('Found package. checking version now...')
                package = pckDir[package]

                # Go through versions
                for package_item in package:
                    # Check version
                    _version = package_item['version']

                    # Is this the latest version of this package found?
                    if (_version > _latestVersion):
                        _latestVersion = _version
                        # print('setting latest version to ' + str(_latestVersion))

                    if (pck_ver is not None):
                        if (_version == pck_ver):
                            # print('Version match!')
                            result['packageVersionFound'] = True
                            result['packageData'] = package_item
                            break

                # At this point, package_item will be the last item in the versions list
                if (pck_ver == None):
                    result['packageVersionFound'] = True
                    result['packageVersion'] = package_item['version']
                    result['packageData'] = package_item
                    # print('latest version found was: ' + str(_latestVersion))

        # Check the results of the lookup
        if (result['packageNameFound'] == False):
            # Was package name found?
            result['message'] = 'Package not found.'
        elif (result['packageNameFound'] == True and result['packageVersionFound'] == False):
            # Did package version match?
            result['message'] = 'Package was found but versions don\'t match! Latest version of this package is v' + \
                str(_latestVersion)
        else:
            # Package + matching version found
            result['message'] = "Matching package and version found."

        if (result['packageData'] is None):
            print(result['message'])
        else:
            _dependenciesData = self.grabDependencyLocations(result)

            # Pass into bundler script here
            # Bundler will use locations to grab dependencies and get them ready for transport
            self.doBundle(_dependenciesData)

pck = PackageBroker()

# Rabbit conneciton parameters
rabbit_conn = RabbitConn()
connection = pika.BlockingConnection(rabbit_conn.connectionParams)

channel = connection.channel()

channel.queue_declare(queue='dep')

# Message handler
def callback(ch, method, properties, body):
    # print(" [x] Received %r" % json.loads(body))

    # Get payload
    _payload = json.loads(body)
    _pckgName = _payload['packageName']
    _pckgVersion = _payload['packageVersion']
    _requestorID = _payload['requestorID']

    # Test print
    print('Looking for ' + str(_pckgName) + ' and ' + str(_pckgVersion))

    # Look for package
    pck.findPackage(_pckgName, _pckgVersion)

    # Send package using .exp script
    # os.system('ls')
    _wd = os.getcwd()
    _file = os.path.join(_wd, 'sendPackage.exp')
    # print(_file)

    # Get sender info
    with open('manifest.json') as f:
        _manifest = json.load(f)

    _senderIP = ''
    _senderPassword = ''
    for person in _manifest:
        # print('Checking person ' + person['id'])
        if person['id'] == _requestorID:
            print('Sending package to ' + person['id'])
            _senderIP = person['ip']
            _senderPassword = person['password']
            break


    os.system(_file + ' ' + _requestorID + ' ' + _senderIP + ' ' + _senderPassword + ' bin/bundle.zip')

    # Done message
    print('Done. Look inside bin/')

# Run callback on message consume
channel.basic_consume(
    queue='dep', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')

# Listen
channel.start_consuming()


# Pass in a package ID to grab. Leave empty to grab latest version.
# pck = PackageGrabber()
# pck.findPackage('front-end', 1.1)
# print('Done. Look inside bin/')