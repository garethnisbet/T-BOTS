from collections import OrderedDict
def mac():
    fileread = open('MAC_Adresses','r')
    address = fileread.read()
    addresses = OrderedDict()
    l_curley_indicies = [n for n in range(len(address)) if address.find('{', n) == n]
    r_curley_indicies = [n for n in range(len(address)) if address.find('}', n) == n]
    for ii in range(len(l_curley_indicies)):
        addresses.update(eval(address[l_curley_indicies[ii]:r_curley_indicies[ii]+1]))
    print('Options:')
    print('1 Enter name from list.')
    print('2 Press Enter for most recent connection.')
    print('3 Enter new name for new device.')
    print('')
    key = input('Choose form '+str(list(addresses.keys()))+ ' or enter new name> ')
    if key in addresses:
        bd_addr = addresses[key]
    elif key == '':
        bd_addr = addresses[list(addresses.keys())[-1]]
    else:
        newkey = key
        mac = input('Enter MAC address >')
        addresses.update({newkey : mac})
        file = open('MAC_Adresses','a')
        entry = {newkey: mac}
        file.write(str(entry)+'\n') 
        file.close()
        bd_addr = addresses[list(addresses.keys())[-1]]

