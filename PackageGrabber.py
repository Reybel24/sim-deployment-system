import json
import mysql.connector
import zipfile
import os
import shutil, errno


class PackageGrabber:
    # package-directory location
    global fileDirectory
    fileDirectory = 'package-directory.json'

    def __init__(self):
        pass

    # Grab dependencies after finding package
    def grabDependencyLocations(self, packageData):
        # Print package
        print(packageData['packageID'] + ' v' +
              str(packageData['packageVersion']))
        # print(packageData['packageData'])

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
        # print('Listing dependencies')
        _packageList = []
        _dependencies = packageData['packageData']['dependencies']
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
                'unpackLocation': dep['unpack-location']
            }

            # Add to list
            _packageList.append(_depData)

        return _packageList

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
        
        # Copy over packages
        for dep in dependencies:
            # print("({0} v{1}) Searching file system for folder {2}. Will extract to {3}".format(dep['id'], dep['version'], dep['fetchLocation'], dep['unpackLocation']))
            
            # Make sure folder exists in packages folder
            _pckgName = str(dep['id']) + '_v' + str(dep['version'])
            _pckgPath = os.path.join('packages', _pckgName)
            if (os.path.isdir(_pckgPath)):
                # Copy folder onto stage
                shutil.copytree(_pckgPath, os.path.join(_stageDir, _pckgName))
            else:
                print('Package folder {0} does not exist within the package directory! Skipping it...'.format(_pckgName))

        # Zip all folders inside stage and prepare for transport
        _dest = 'bin/'
        # Make sure directory exists. If not, create it
        if (os.path.isdir(_dest) == False):
            os.mkdir(_dest)

        shutil.make_archive(_dest + 'bundle', 'zip', _stageDir)

    # Find a requested package11
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


# Pass in a package ID to grab. Leave empty to grab latest version.
pck = PackageGrabber()
pck.findPackage('front-end', 1.1)
