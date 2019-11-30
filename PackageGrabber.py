import json
import mysql.connector


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
        _packageLocations = {}
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
            _packageLocations[dep['id']] = _location

        return _packageLocations

    def doBundle(self, dependenciesData):
        print('bundling...')
        
        for id, location in dependenciesData.items():
            print("({0}) Searching file system for {1}".format(id, location))

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
pck.findPackage('front-end', 1.10)
