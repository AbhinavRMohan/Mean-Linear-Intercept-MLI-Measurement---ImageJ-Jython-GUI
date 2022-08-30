#MLI Measurement Program [beta version] (c) Abhinav Mohan, May 2021
from fiji.util.gui import GenericDialogPlus
from java.awt.event import ActionListener
from itertools import groupby
from ij import IJ
from ij import WindowManager as wm
from math import sqrt
import os

img_set = 0;
numlines = 0;
title_img = {};
imgDirectory = "";
txtDirectory = "";
global scale, getNumDatasets;

#-------------------- SET THE GUI AND VARIABLES -----------------------------------

class ButtonClic(ActionListener):
	def actionPerformed(self, event): 
        	Source = event.getSource(); 
        	if Source.label == "Help":
           		helpGui = GenericDialogPlus("Help");
            	helpGui.addMessage("The number of datasets is the number of animals you are analyzing.\nMAX: 10");
            	helpGui.showDialog();
         
class ButtonClic2(ActionListener):
	def actionPerformed(self, event2): 
        	Source2 = event2.getSource();
        	if Source2.label == "Help":
           		helpGui2 = GenericDialogPlus("Help");
            	helpGui2.addMessage("This program currently only works in conjunction with PhenochartTM from Akoya Biosciences.\nThis is because the methods required to process the H&E stained images may not be applicable to all methods.");
            	helpGui2.addMessage("*folder*: Select ONLY the folder where your images are located.");
            	helpGui2.addMessage("*micron-to-pixel ratio*: The conversion from pixel length to microns.\nFor 4x magnification this value is 0.45 µm/px, while for 10x this value is 0.9 µm/px.");
            	helpGui2.addMessage("*image batch title*: The uniform title given to the lung sections of each animal (e.g., H46_4x given as the uniform title for the lung sections of H46 taken at 4x magnification).\nMake sure that all titles are uniform and appropriate for ease of use.\nEnter the title of the image ONLY in the dialog box (e.g., if your images are titled \"H46_4x 1.tif, H46_4x 2.tif\", etc., enter only H46_4x.)");
            	helpGui2.addMessage("*images per dataset*: The number of images you took from each lung section for each animal.\nAdjust the slider appropriately.");
            	helpGui2.addMessage("*number of lines to draw*: The number of horizontal lines you want to draw across each image to evaluate the MLI.\nThe number of lines drawn by the program are evenly spaced top-to-bottom along the image.\nAdjust the slider appropriately.");
            	helpGui2.addMessage("*output directory*: The folder you want to save your results csv file to.");
            	helpGui2.showDialog();

gui = GenericDialogPlus("MLI Measurement Program [beta version] (c) Abhinav Mohan 2021");
gui.addNumericField("How many datasets are you working with? ", 2,0);
gui.addButton("Help", ButtonClic())
gui.showDialog();

if gui.wasOKed():
	getNumDatasets = int(gui.getNextNumber());
	gui2 = GenericDialogPlus("MLI Measurement Program [beta version] (c) Abhinav Mohan 2021");
	gui2.addDirectoryField("Which folder are all your images located in? ", "MLI");
	gui2.addNumericField("Enter the micron-to-pixel ratio: ", 0.45, 2);
	for inumdatasets in range(getNumDatasets):
		gui2.addStringField("Enter the image batch title: ", "H46_4x");
	gui2.addSlider("How many images per dataset? ", 2, 25, 10);
	gui2.addSlider("How many lines to draw across each image? ", 5, 25, 18);
	gui2.addDirectoryField("Where do you want to save the output csv file? ","MLI");
	gui2.addButton("Help", ButtonClic2())
	gui2.showDialog(); 
# ---------------------------------------------------------------------------

#------------------------- ACCEPT THE VARIABLES -------------------------------
if gui2.wasOKed():
	imgDirectory = gui2.getNextString();
	scale = gui2.getNextNumber(); 	
	for isetNumDatasets in range(getNumDatasets):
		title_img[isetNumDatasets] = gui2.getNextString();
	img_set = int(gui2.getNextNumber());
	numlines = int(gui2.getNextNumber());
	csvDirectory = gui2.getNextString();
# ----------------------------------------------------------------------------------------

#------------------------- PREPARE TEXT FILE ----------------------
mliFile = open(csvDirectory + '/' + 'MLI Results.csv','w');
#------------------------------------------------------------------

# --------------------------------- RUN: MLI -----------------------------
for a in range(len(title_img)):
	IJ.log("MLI " + title_img[a] + " (micrometers)");
	meanMLI = [i for i in range(img_set)];
	for i in range(img_set):

	#==========================================================#
	#================== PROCESSING THE IMAGE ==================#
	#==========================================================#
	
		IJ.open(imgDirectory + "/" + title_img[a] + " " + str(i + 1) + ".tif");
		IJ.run("Set Scale...", "distance=" + str(scale) + " known=1 pixel=1 unit=µm global");
		IJ.run("Duplicate...", "title=binary");
		IJ.run("Split Channels");
		IJ.selectWindow("binary (red)");
		imp = IJ.getImage();
		imp.close();
		IJ.selectWindow("binary (blue)");
		imp = IJ.getImage();
		imp.close();
		IJ.selectWindow("binary (green)");
		imp = IJ.getImage();
		imp.setTitle("binary");
		IJ.run("Enhance Contrast...", "saturated=15 normalize");
		IJ.setAutoThreshold(imp, "Percentile no-reset");
		IJ.setThreshold(0, 115); 
		IJ.run("Convert to Mask");
		IJ.run("Remove Outliers...", "radius=2.7 threshold=254 which=Bright");
		IJ.run("Close-");

	#====================================================================#
	#======================= MEASURING THE MLI ==========================#
	#====================================================================#
		
		IJ.selectWindow("binary");
		IJ.run("Duplicate...", "title=binary2");
		imp = IJ.getImage();
		l = imp.getWidth();
	
		k = range(numlines); 
	
		h = (imp.getHeight()/len(k)); 
		klengths = [n for n in k];
		upper = 12;
		lower = 2;
		for n in k:
			IJ.selectWindow("binary");
			IJ.makeLine(0,(h*n+h/2),l,(h*n+h/2), );
			# you can start measuring from any altitude you want by modifying the "+h/2" part. 
			# If you want to start at altitude of "0", simply delete the "+" portion
			IJ.run("Plot Profile");		
			IJ.selectWindow("binary2");
			imp = IJ.getImage();
			IJ.run('Colors...', 'foreground=black')
			IJ.makeLine(0,(h*n+h/2),l,(h*n+h/2));
			IJ.run(imp,"Draw","slice");
			IJ.selectWindow("Plot of binary");
			imp = IJ.getImage();
			imp.setTitle("Plot of binary" + " " + str(n+1));
			myPlot = wm.getWindow("Plot of binary" + " " + str(n+1));
			rt_plot = myPlot.getResultsTable();
			n_cols = rt_plot.getLastColumn();
			x_cols = range(0,n_cols,1);
			for c in x_cols: 
	   			xValues_c = rt_plot.getColumn(c); # get XValues of c_th line
				Y = rt_plot.getColumn(c+1); # get corresponding YValues
				for yyy in range(len(Y)):
					if Y[yyy] > 220:
						Y[yyy] = 1;
					else:
						Y[yyy] = 0;
	
			### THE CRITICAL DATASET ###
			
			Y = [int(yr) for yr in Y]

			############################### MODIFIED K-MEANS CLUSTERING #############################

			black_mat  = [sum(1 for zzz in b )  if gg==1 else float('NaN') for gg,b in groupby(Y)]
			blackmat_raw = [oneso for oneso in black_mat if str(oneso) != 'nan']
			white_mat = [sum(1 for zzz in b )  if gg==0 else float('NaN') for gg,b in groupby(Y)]
			whitemat_raw = [zeroso for zeroso in white_mat if str(zeroso) != 'nan']
			merge = [sum(1 for zzz in b )  if gg==1 else sum(1 for zzz in b ) for gg,b in groupby(Y)]
			
			BLMRavg = 0.0;
			for blmi in blackmat_raw:
				BLMRavg = BLMRavg + float(blmi);
			BLMRavg = BLMRavg/len(blackmat_raw);
			BLMRsd = 0;
			for blmsdi in blackmat_raw:
				BLMRsd += (float(blmsdi) - BLMRavg)**2;
			BLMRsd = sqrt(BLMRsd / (len(blackmat_raw) - 1));

			upper = abs(BLMRavg + BLMRsd);
			lower = abs(BLMRavg - BLMRsd);
			
			def algo(hi,lo):
				newlen = len(Y);
				count = len(blackmat_raw);
				for xlen in range(len(blackmat_raw) - 1):
					if blackmat_raw[xlen] > hi and blackmat_raw[xlen+1] > hi: 
						count = count - 2;
						newlen = newlen - blackmat_raw[xlen] - blackmat_raw[xlen+1] - whitemat_raw[xlen+1];
					if blackmat_raw[xlen] < lo:
						newlen = newlen - blackmat_raw[xlen];
						count = count - 1; 
				return newlen/count	
			
			klengths[n] = algo(upper,lower);

			#########################################################################################
		
			IJ.selectWindow("Plot of binary" + " " + str(n+1))
			imp = IJ.getImage();
			imp.close();
		
		################################ MLI VALUES #####################################

		meanMLI[i] = sum(klengths)/len(klengths);
		
		##############################################################################

		IJ.selectWindow("binary");
		imp = IJ.getImage();
		imp.changes = False;
		imp.close();
		
		IJ.selectWindow("binary2");
		imp = IJ.getImage();
		imp.changes = False;
		imp.close();
		
		IJ.selectWindow(title_img[a] + " " + str(i + 1) + ".tif");
		imp = IJ.getImage();
		imp.changes = False;
		imp.close();
		
	finalMeanMLI = sum(meanMLI)/len(meanMLI);
	IJ.log(str(finalMeanMLI/scale));
	IJ.log(" ");	

	#------------------ SAVE TO CSV FILE -----------------
	mliFile.write("MLI " + title_img[a] + " (micrometers)\n");
	mliFile.write(str(finalMeanMLI/scale));
	mliFile.write("\n\n");
mliFile.close();
IJ.log("Values are saved to: " + csvDirectory + "/MLI Results.csv");