
'''
A script to find out the locking information about a file on
VMFS datastore.

Script involves gettting host name and MAC address mapping by talking back to
Virtual Center Server using Property Collectors
'''

import sys
import os
from subprocess import getstatusoutput
import atexit  #退出处理程序
from pyVmomi import vim, SoapStubAdapter, vmodl
from pyVim.connect import Connect, Disconnect
from getpass import getpass
from optparse import OptionParser
from time import clock
from xml.dom import minidom

SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_VERSION = "1.0"

START = clock()

def CollectHostProperties(si, viewRef, objType,
                          pathSet=None, includeMors=False):
    '''
    Collect properties for managed objects from a view ref
    Check the vSphere API documentation for example on retrieving
    object properties using PropertyCollector

    Args:
        si          (ServiceInstance): ServiceInstance connection
        viewRef  (pyVmomi.vim.view.*): Starting point of inventory navigation
        objType       (pyVmomi.vim.*): Type of managed object
        pathSet                (list): List of properties to retrieve
        includeMors            (bool): If True include the managed objects
                                       refs in the result
    Returns:
        A list of properties for the managed objects
    '''
    propertyCollector = si.content.propertyCollector
    '''
    Create object specification to define the starting point of
    inventory navigation
    '''
    objSpec = vmodl.query.PropertyCollector.ObjectSpec()
    objSpec.obj = viewRef
    objSpec.skip = True

    # Create a traversal specification to identify the path for collection
    traversalSpec = vmodl.query.PropertyCollector.TraversalSpec()
    traversalSpec.name = 'traverseEntities'
    traversalSpec.path = 'view'
    traversalSpec.skip = False
    traversalSpec.type = viewRef.__class__
    objSpec.selectSet = [traversalSpec]

    # Identify the properties to the retrieved
    propertySpec = vmodl.query.PropertyCollector.PropertySpec()
    propertySpec.type = objType

    if not pathSet:
        propertySpec.all = True

    propertySpec.pathSet = pathSet

    # Add the object and property specification to the
    # property filter specification
    filterSpec = vmodl.query.PropertyCollector.FilterSpec()
    filterSpec.objectSet = [objSpec]
    filterSpec.propSet = [propertySpec]

    # Retrieve properties
    props = propertyCollector.RetrieveContents([filterSpec])

    data = []
    for obj in props:
        properties = {}
        for prop in obj.propSet:
            properties[prop.name] = prop.val

        if includeMors:
            properties['obj'] = obj.obj

        data.append(properties)
    return data


def GetContainerView(si, objType, container=None):
    """
    Get a vSphere Container View reference to all objects of type 'objType'
    It is up to the caller to take care of destroying the View when no longer
    needed.
    Args:
        objType (list): A list of managed object types
    Returns:
        A container view ref to the discovered managed objects
    """
    if not container:
        container = si.content.rootFolder
        viewRef = si.content.viewManager.CreateContainerView(
              container=container,
              type=objType,
              recursive=True
              )
    return viewRef

def endit():
    """
    time :  how long it took for this script to run.
    :return:
    """
    end = clock()
    total = end - START
    print("Total time taken : {0} seconds.".format(total))

def GetLockModeAndOwnersList(output) :
    '''
    Parse the output of 'vmkfstools -D' into 'lockMode' and
    list of 'owners'
    '''
    owners = list()
    lockMode = int(output[output.find("mode") + 5])
    if lockMode == 0 :
        return lockMode, owners
    elif lockMode == 1 :
        owners.append(output[output.find("owner"):].split()[1])
        return lockMode, owners
    elif lockMode == 2 or lockMode == 3 :
        for line in output.split('\n') :
            if ("RO Owner" in line) or ("MW Owner" in line) :
                owners.append(line.split()[-1])
        return lockMode, owners
    return None, None


def ConvertToMACAddress(macAddress) :
    '''
        Format the MAC address from the Owner field in 'vmkfstools -D'
        output to standard MAC address format
    '''
    n = 2
    formattedMacAddress = ""
    for i in range(0, len(macAddress), n) :
        formattedMacAddress = formattedMacAddress + macAddress[i:i+n] + ":"
    formattedMacAddress = formattedMacAddress[:-1]
    return formattedMacAddress

def GetLockingInfo(absFilePath) :
    '''
    Captures 'vmkfstools -D' output for the file
    '''
    status, output =  getstatusoutput("vmkfstools -D " + "\"" \
                                              + absFilePath + "\"")


    if status :
        print ("Failed to get the lock owners for", absFilePath)
        print ("Reason :", output)
        sys.exit(0)
    return output

def FindHostNameUsingFDM(fdmBinartPath, lockOwnerMACAddress) :
    lockingHostNames = []
    status, output =  getstatusoutput(fdmBinartPath + " hostlist")
    if status :
        print ("Failed to get host list from Fault Domain Manager")
    else :
        try :
            xmlStartIndex = output.index('<')
            root = minidom.parseString(output[xmlStartIndex:])
            lockOwnerLookupLeft = len(lockOwnerMACAddress)
            hosts = root.getElementsByTagName('host')
            print("-" * 70)
            print("Found {0} ESX hosts using Fault Domain Manager.".format(len(hosts)))
            print("-" * 70)

            for host in hosts :
                hostName = host.getElementsByTagName('hostName')[0].childNodes[0].data
                print ("Searching on Host {0}".format(hostName))
                for macAddress in host.getElementsByTagName('mac') :
                    mac = macAddress.childNodes[0].data
                    if mac in lockOwnerMACAddress :
                        print("MAC Address : {0}".format(mac))
                        lockingHostNames.append(hostName)
                        lockOwnerLookupLeft -= 1
                        break;
                if lockOwnerLookupLeft == 0 :
                     break;
        except :
            print ("Failed to parse XML information from Fault Domain Manager")
    return lockingHostNames

def CheckFirewallRule() :
    '''
    check if httpClient Rule is enabled otherwise we will fail to
    connect to Virtual Center Server
    '''

    cmd = "esxcli network firewall ruleset list"
    status, output =  getstatusoutput(cmd)
    if status :
        print ("Failed to check firewall rule information")
        print ("Reason :", output)
        sys.exit(0)
    for line in output.split('\n'):
        rule, value = line.split()
        if rule == "httpClient" :
            if value == "true" :
                return True
            else :
                return False
            break;
    return False

def ConnectToVC(vcHostName, vcAdminUser, shaThumbPrint) :
    '''
    Connects to Given Virtual Center Server with given Admin user
    '''
    try :
        print ("Connecting to", vcHostName, "with user", vcAdminUser)
        si = Connect(host=vcHostName, port=443, user=vcAdminUser,
                     pwd=getpass(), thumbprint=shaThumbPrint)
        atexit.register(Disconnect, si)
    except Exception as error:
        print ("Could not connect to host : {0}".format(error))
        sys.exit(0)
    return si;


def main():
    FDM_BINARY_PATH = "/opt/vmware/fdm/fdm/prettyPrint.sh"

    usage = "usage: %prog -p <file path> -v <vc host name>"

    parser = OptionParser(usage=usage)

    parser.add_option("-p", "--filepath",
                      dest="filePath",
                      metavar="filepath",
                      help="Path to the file on VMFS datastore")
    parser.add_option("-v", "--vchostname",
                      dest="vcHostName",
                      metavar="vcserverip",
                      help="Name/IP address of the Virtual Center Server")
    parser.add_option("-u", "--vcadminuser",
                      dest="vcAdminUser",
                      metavar="username",
                      help="Admin user name of the Virtual Center Server")
    parser.add_option("-t", "--thumbprint",
                      dest="shaThumbprint",
                      metavar="SHA thumbprint",
                      help="SHA-1 thumbprint required for Connecting to \
                            Virtual Center Server")

    (options, args) = parser.parse_args()

    if not options.filePath :
        print ("Please provide a valid File path")
        parser.print_help()
        sys.exit(0)

    try :
        absFilePath = os.path.abspath(options.filePath);
        if not os.path.exists(absFilePath) :
            print ("Could not find file", options.filePath, "or", absFilePath)
            sys.exit(0)
    except Exception as error :
        print ("Could not find file", options.filePath, ":", error)
        sys.exit(0)

    atexit.register(endit)

    lockingModes = {
                     0 : "Free",
                     1 : "Exclusive",
                     2 : "Read-Only",
                     3 : "Multi-writer"
                   }
    fileName = "\"" + os.path.basename(absFilePath) + "\""

    print ("Looking for lock owners on", fileName)
    lockingInfo = GetLockingInfo(absFilePath)
    lockMode, owners = GetLockModeAndOwnersList(lockingInfo)
    lockOwnerMACAddress = list()

    if lockMode is None :
        print ("Failed to find the locking mode for", fileName)
        sys.exit(0)

    if lockMode == 0 :
        print (fileName, "is not locked by any ESX host and is Free")
        sys.exit(0)
    elif lockMode == 1 or lockMode == 2 or lockMode == 3:
        for owner in owners :
            lockOwnerMACAddress.append(ConvertToMACAddress(owner.split('-')[3]))
        print (fileName, "is locked in", lockingModes[lockMode], \
              "mode by host having mac address", lockOwnerMACAddress)
    else :
        print ("Invalid Lock mode ", lockMode, \
              "Don't know what to do. Quitting...")

    lockingHostNames = list()

    # First try to fetch info from Fault Domain Manager if configured
    if os.path.exists(FDM_BINARY_PATH) :
        print("Trying to make use of Fault Domain Manager")
        lockingHostNames = FindHostNameUsingFDM(FDM_BINARY_PATH, lockOwnerMACAddress)

    if not lockingHostNames or lockingHostNames[0] is None or \
       len(lockingHostNames) != len(lockOwnerMACAddress) :
        if (os.path.exists(FDM_BINARY_PATH)) :
            print ("Could not get information from Fault domain manager")

        # Check if the firewall rule is enabled to connect to VC
        firewallEnabled = CheckFirewallRule()

        if (not firewallEnabled) :
            print ("Please configure ESXi firewall to connect to Virtual Center")
            sys.exit(0)

        if options.vcHostName is None :
            options.vcHostName = raw_input("Please provide Host Name or IP address for Virtual Center Server : ").strip()

        if options.vcAdminUser is None :
            user = raw_input("Admin user for Virtual Center "\
                             + options.vcHostName + \
                             " [default : administrator@vsphere.local] : ")
            if user is "" :
                options.vcAdminUser = "administrator@vsphere.local"
            else :
                options.vcAdminUser = user.strip()

        si = ConnectToVC(options.vcHostName, options.vcAdminUser,
                         options.shaThumbprint)
        hostProperties = ["name", "config.network.pnic"]
        view = GetContainerView(si, objType=[vim.HostSystem])
        hostsData = CollectHostProperties(si, viewRef=view,
                                      objType=vim.HostSystem,
                                      pathSet=hostProperties,
                                      includeMors=True)
        lockOwnerLookupLeft = len(lockOwnerMACAddress)

        print("-" * 70)
        print("Found {0} ESX hosts from Virtual Center Server.".format(len(hostsData)))
        print("-" * 70)
        for host in hostsData :
            hostName = host["name"]
            print("Searching on Host {0}".format(hostName))
            for nic in host["config.network.pnic"] :
                if nic.mac in lockOwnerMACAddress :
                    print("    MAC Address : {0}".format(nic.mac))
                    lockingHostNames.append(hostName)
                    lockOwnerLookupLeft -= 1
                    break;
            if lockOwnerLookupLeft == 0 :
                break;

    print ("\n")
    if not lockingHostNames or lockingHostNames[0] is None :
        print ("Count not find the host name having mac address", lockOwnerMACAddress)
    else :
        for name in lockingHostNames :
            print ("Host owning the lock on the vmdk is", name + ", lockMode :",\
                  lockingModes[lockMode])

# Start program
if __name__ == "__main__":
    print (SCRIPT_NAME + " Version " + SCRIPT_VERSION)
    main()
