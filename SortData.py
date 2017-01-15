from Tkinter import Tk
import tkFileDialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os
#test git
#NUM_CHANNELS          = 16
NUM_READINGS_PER_INT  = 31
NUM_READINGS_PER_LINE = 50

sortedTable= [ [] for j in range(NUM_READINGS_PER_INT) ]


savedFileLocationDirectory = open('C:\\Users\\Public\\PR_SortData.txt' , 'a+')
savedFileName = savedFileLocationDirectory.read()
savedFileLocationDirectory.close()
if len(savedFileName) > 0:
    Tk().withdraw() 
    sourceFile = tkFileDialog.askopenfilename(initialdir=savedFileName)
else :
    Tk().withdraw() 
    sourceFile = tkFileDialog.askopenfilename()
       
        
openedFile = open(sourceFile) 
statinfo = os.stat (sourceFile)

extractedFile = open(sourceFile + '_extracted_Date' , 'w') 
extractedFile.write('CH1,' + 'CH2,' + 'CH3,' + 'CH4,' + 'CH5,' + 'CH6,' \
                        + 'CH7,' + 'CH8,' + 'CH9,' + 'CH10,' + 'CH11,' \
                        + 'CH12,' + 'CH13,' + 'CH14,' + 'CH15,' + 'CH16,');

savedFileLocationDirectory = open('C:\\Users\\Public\\PR_SortData.txt' , 'w+')
savedFileLocationDirectory.write(sourceFile)
savedFileLocationDirectory.close()

for line in openedFile:
    if len(line.split(",")) >= NUM_READINGS_PER_INT*NUM_READINGS_PER_LINE :
        vectoredLine = line.split(",") 
        for x in range(NUM_READINGS_PER_LINE-1):
            for channel in range (NUM_READINGS_PER_INT-1):
                sortedTable[channel].append(vectoredLine[x*NUM_READINGS_PER_INT + channel])

                
openedFile.close()   
extractedFile.close()

fig = plt.figure()
ax1 = fig.add_subplot(111)
#ax2 = fig.add_subplot(212)  
#ax1.grid(True)
#ax1.set_ylim(ymin = -2, ymax = 3)
#ax1.set_ylabel(' Status',fontsize = 10)
for i in range(NUM_READINGS_PER_INT-1):
    ax1.plot(sortedTable[i])#,'.')

plt.show()

print 'channel length: ' + str(len(sortedTable[0]) )




