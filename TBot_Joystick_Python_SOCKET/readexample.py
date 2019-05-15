from time import sleep
f2 = open('cmd.csv')
for ii in f2:
    aa = ii
    aa = aa.split(',')
    dtime = float(aa[0])
    cmsstr = aa[1]
    print(cmsstr)
    sleep(dtime)
f2.close()


def PlayCMD(filein):
    global Play
    ff = open(filein)
    for ii in ff:
        if Play:
            aa = ii
            aa = aa.split(',')
            dtime = float(aa[0])
            cmsstr = aa[1]
            sleep(dtime)
            send(cmsstr)
        else:
            break
    ff.close()
