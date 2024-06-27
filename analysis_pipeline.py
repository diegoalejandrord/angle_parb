"""
Created on Tue Dec  5 12:25:03 2023

@author: diegoalejandrord
"""

import numpy as np
from skimage.io import imread
from skimage import measure
from skimage.measure import label, regionprops
import math
import tifffile
import glob
import pandas as pd
#from skimage.morphology import disk
#import matplotlib.pyplot as plt
#from skimage import io
#import matplotlib.pyplot as plt
#import cv2

def analysis(f_mask,f_parb):
    
    mask = imread(f_mask)
    parb = imread(f_parb)
    labels = label(mask, background=0)
    props = regionprops(labels, mask)        
    internal=[]
    area = [] 
    angle= []
    major = []
    minor = []
    distance_par=[]
    angle_par=[]
    rows, cols = mask.shape   
    mask_area = np.zeros((rows, cols))
    mask_par = np.zeros((rows, cols))    
    
    for index in range(1,labels.max()):
      
        test = [labels ==index]
        
        test=np.uint8(np.array(test))[0,:,:]

        a=parb*test
        
        test=255*test
        
        labels_a = label(a, background=0)
        
        if labels_a.max()==2:
            
            #if (props[index-1].area > 30) and (props[index-1].area < 120):
    
            if (props[index-1].area >10) and (props[index-1].area < 0.1): # Parameters chose by user Dr. Aditya C. Bandekar
                
                props_a = measure.regionprops(labels_a, mask)
              
                y0, x0 = props_a[0].centroid
                
                y1, x1 = props_a[1].centroid
    
                internal.append(index)
                area.append(props[index-1].area)
                angle.append(180*(props[index-1].orientation)/math.pi+90)
                major.append(props[index-1].axis_major_length)
                minor.append(props[index-1].axis_minor_length)           
                distance_par.append(math.sqrt((x1-x0)**2+(y1-y0)**2))
                angle_par.append(abs(math.atan2(y0-y1,x0-x1)*180/math.pi))
           

            mask_area = mask_area + test
            mask_par = mask_par + a
         
    
    mask_area=np.uint8(mask_area)
    mask_par=np.uint8(mask_par)
    
    name_f_area=f_mask[0:-4]+'_area_filtered.tif'
    name_f_parb=f_parb[0:-4]+'_parb_filtered.tif'
    
    name_f_csv=f_mask[0:-4]+'_data.csv'

    tifffile.imwrite(name_f_area, mask_area)   
    tifffile.imwrite(name_f_parb, mask_par)   
    
    d = {'Internal': internal,'Area': area,'Angle': angle, 'Major axis': major, 'Minor axis': minor, 'Distance Foci': distance_par, 'Angle Foci': angle_par}
    df = pd.DataFrame(data=d)  
    df.to_csv(name_f_csv, sep=',', index=False, encoding='utf-8')
   
    return df

def iteration_folder(dir_path):
    
    res = glob.glob(dir_path)
    mask_f=res[0]
    parb_f=mask_f[0:-10]+'.tif'
    df = analysis(mask_f,parb_f)
    
    for i in range(1,len(res)):
    
        mask_f=res[i]
        parb_f=mask_f[0:-10]+'.tif'
        frame_up=analysis(mask_f,parb_f)
        df = pd.concat([df, frame_up], axis=0)

    return df


if __name__ == '__main__':
    
    # search all files inside a specific folder
    # *.* means file name with any extension
    dir_path = r'/Users/adityabandekar/Desktop/Adi long axis parB/*masks.tif*'
        
    df=iteration_folder(dir_path)
        
    name_f_csv=dir_path[0:-11]+'Total.csv'
    df.to_csv(name_f_csv, sep=',', index=False, encoding='utf-8')
       
            
       
 
            
        
        
        