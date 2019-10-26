import pyautogui as snap
from time import sleep
for ii in range(600):
	snap.screenshot('images/im%05d.png' % ii)
	
