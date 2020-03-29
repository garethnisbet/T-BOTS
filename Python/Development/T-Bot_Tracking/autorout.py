import cv2
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
plt.ion()

save = 0 # Save way points
usecam = 0
showconv = 1

if usecam:
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 405)
    success, im_rgb = cap.read()
    sleep(1)
    success, im_rgb = cap.read()
    cv2.imwrite('TrackTiles/fulltrack2.png',im_rgb)
    im_rgb = cv2.cvtColor(im_rgb, cv2.COLOR_BGR2RGB)
else:
    im_rgb = cv2.imread('TrackTiles/fulltrack.png')
    
track = cv2.cvtColor(im_rgb, cv2.COLOR_BGR2GRAY)
#track = cv2.resize(track,None,fx=0.95,fy=0.95)


#----------------------------------------------------------------------#
#------------- Function to determine the tile sequence ----------------#
#----------------------------------------------------------------------#

def tilesequence(last_tile,current_tile,tile_type):
    if (tile_type == 0) & (last_tile[0] < current_tile[0]): # RD
        vout = [0,1]
        sign = [0]
    elif (tile_type == 0) & (last_tile[1] > current_tile[1]): # RD
        vout = [-1,0]
        sign = [1]

    elif (tile_type == 1) & (last_tile[0] > current_tile[0]): # UR
        vout = [0,1]
        sign = [0]
    elif (tile_type == 1) & (last_tile[1] > current_tile[1]): # UR
        vout = [1,0]
        sign = [1]
        
    elif (tile_type == 2) & (last_tile[0] > current_tile[0]): # DR
        vout = [0,-1]
        sign = [0]
    elif (tile_type == 2) & (last_tile[1] < current_tile[1]): # DR
        vout = [1,0]
        sign = [1]
        
    elif (tile_type == 3) & (last_tile[0] < current_tile[0]): # RU
        vout = [0,-1]
        sign = [0]
    elif (tile_type == 3) & (last_tile[1] < current_tile[1]): # RU
        vout = [-1,0]
        sign = [1]
        
    elif (tile_type == 4) & (last_tile[0] < current_tile[0]): # HS
        vout = [1,0]
        sign = [0]
    elif (tile_type == 4) & (last_tile[0] > current_tile[0]): # HS
        vout = [-1,0]
        sign = [1]

    elif (tile_type == 5) & (last_tile[1] < current_tile[1]): # VS
        vout = [0,1]
        sign = [0]
    elif (tile_type == 5) & (last_tile[1] > current_tile[1]): # VS
        vout = [0,-1]
        sign = [1]
                
    return vout+current_tile, sign

#----------------------------------------------------------------------#
# -------------  Load image kernels for convolution  ------------------#
# ---------------------------------------------------------------------#

tile_RD = cv2.imread('TrackTiles/bend.png',0)
tile_UR = np.fliplr(tile_RD)
tile_DR = np.flipud(tile_UR)
tile_RU = np.flipud(tile_RD)
tile_HS = cv2.imread('TrackTiles/straight.png',0)
tile_VS = tile_HS.T
tile_cross = cv2.imread('TrackTiles/cross.png',0)
tile_zebraV = cv2.imread('TrackTiles/zebra.png',0)
tile_zebraH = tile_zebraV.T

w, h = tile_RD.shape[::-1]

#----------------------------------------------------------------------#
# -------------------  Find Tiles and Asign Type  ---------------------#
# ---------------------------------------------------------------------#

threshold = 0.85
positions = []
tilelist = [tile_RD,tile_UR,tile_DR,tile_RU,tile_HS,tile_VS,tile_cross,tile_zebraH,tile_zebraV]
colourstep = int(255/len(tilelist))
for ii in range(len(tilelist)):
    res = cv2.matchTemplate(track,tilelist[ii],cv2.TM_CCOEFF_NORMED)
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):
        positions.append(pt+(ii,))
        if showconv:
            cv2.rectangle(im_rgb,pt,(pt[0] + w, pt[1] + h), ((55),(ii*colourstep),(255)), 2)

plt.figure()
plt.imshow(im_rgb)
aa = np.array(positions)

#----------------------------------------------------------------------#
# -------------------  Determine grid for search  ---------------------#
# -------------------    Average over matching  -----------------------#
# ---------------------------------------------------------------------#

v=np.zeros(track.shape[0])
v[aa[:,1]]=100
h=np.zeros(track.shape[1])
h[aa[:,0]]=100
vgrid = np.nonzero(np.diff(v,1)>50)[0]
hgrid = np.nonzero(np.diff(h,1)>50)[0]
mgrid = np.meshgrid(range(5),range(3))
cgrid=np.reshape(mgrid,(2,15)).T
v1 = np.array([[]]*3).T

for ii in range(cgrid.shape[0]):
    vindex = cgrid[ii][1]
    hindex = cgrid[ii][0]
    bb = aa[np.nonzero((aa[:,1]>vgrid[vindex]) & (aa[:,1]<vgrid[vindex]+40)),:][0]
    cc = bb[np.nonzero((bb[:,0]>hgrid[hindex]) & (bb[:,0]<hgrid[hindex]+40)),:][0]
    cc = np.sum(cc,0)/cc.shape[0]
    v1 = np.vstack((v1,cc))
    

#----------------------------------------------------------------------#
# --------------  Overlay averaged results on image -------------------#
#----------------------------------------------------------------------#
 
plt.plot(v1[:,0],v1[:,1],'wo')
plt.plot(v1[:,0],v1[:,1],'.k')
patharray = np.array([[]]*3).T
signarray = np.array([[]]*1).T

if v1[:,2].max() == 8:
    starttile = cgrid[np.nonzero(v1[:,2]==8)[0][0],:]
    nexttile = starttile + np.array([1,0])
    patharray = np.vstack((patharray,v1[np.nonzero(v1[:,2]>6)[0][0]]))

    
elif v1[:,2].max() == 7:
    starttile = cgrid[np.nonzero(v1[:,2]==7)[0][0],:]
    nexttile = starttile + np.array([0,1])  
    patharray = np.vstack((patharray,v1[np.nonzero(v1[:,2]>6)[0][0]]))

sign = [0]
signarray = np.vstack((signarray,sign))    
  
for ii in range(cgrid.shape[0]-2):
    nindex = np.nonzero(np.all(cgrid-np.array([nexttile[0],nexttile[1]])==0,axis=1))[0][0]
    patharray = np.vstack((patharray,v1[nindex,:]))
    
    tiletype = v1[nindex,-1].astype(int)
    vectout, sign = tilesequence(starttile,nexttile,tiletype)
    signarray = np.vstack((signarray,sign))
    starttile = nexttile
    nexttile = vectout
    
print(patharray)

#----------------------------------------------------------------------#
# -------------------  Create way points ------------------------------#
#----------------------------------------------------------------------#


minipaths =[[[[10,50],[40,55],[50,80]],[[50,80],[40,55],[10,50]]],# RD
            [[[85,50],[55,55],[50,85]],[[50,85],[55,55],[85,50]]],# UR           
            [[[85,50],[60,40],[50,10]],[[50,10],[55,40],[85,50]]],# DR
            [[[10,50],[40,40],[50,10]],[[50,10],[40,40],[10,50]]],# RU
                        
            [[[10,45],[50,45],[90,45]],[[90,45],[50,45],[10,45]]],# HS
            [[[45,10],[45,50],[45,90]],[[45,90],[45,50],[45,10]]],# VS
            
            [[[50,50]],[[50,50]]],# Cross
            
            [[[50,50]],[[50,50]]],# Zebra
            [[[50,50]],[[50,50]]]]# Zebra


                
p2 = np.array([[]]*2).T
for ii in range(patharray.shape[0]):
    p2 = np.vstack((p2,patharray[ii,:2]+np.array(minipaths[int(patharray[ii,-1])][int(signarray[ii])])))
plt.plot(p2[:,0],p2[:,1],'ro')

if save:
    filename = 'pathpoints.dat'
    np.savetxt(filename,p2[:,:2])
    plt.savefig('TrackTiles/Overlay.svg',format='svg')
    cv2.imwrite('TrackTiles/Overlay.png',cv2.cvtColor(im_rgb, cv2.COLOR_RGB2BGR))

    
