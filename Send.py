# Use tricia's .exp script to send files over network
import os
import json

def send(hostID, fileToSend):
    _hostFound = False

    # Get sender info
    with open('manifest.json') as f:
        _manifest = json.load(f)

    _senderIP = ''
    _senderPassword = ''
    for person in _manifest:
        # print('Checking person ' + person['id'])
        if person['id'] == hostID:
            # print('Sending package to ' + person['id'])
            _senderIP = person['ip']
            _senderPassword = person['password']
            _hostFound = True
            break

    # Get sender .exp script
    _wd = os.getcwd()
    _file = os.path.join(_wd, 'sendPackage.exp')

    if (_hostFound):
        # Execute script
        print('Sending now to ' + hostID + ' (' + fileToSend + ')')
        os.system(_file + ' ' + hostID + ' ' + _senderIP + ' ' + _senderPassword + ' ' + fileToSend)
    else:
        print("Machine not found (Did you forget to add it to the manifest?): " + hostID)