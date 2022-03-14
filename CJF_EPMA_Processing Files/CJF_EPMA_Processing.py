#!/usr/bin/env python
# coding: utf-8

# # CJF EPMA Processing

# In[1]:


#Imports packages necessary to store and plot data, perform analysis
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
import math


# In[2]:


#Defines the Mass Balance Analysis as a function reliant on 8 inputs
def MBA(alloy, elements,composition_location, epma_data,filter,WIRS_cutoff,MBA_cutoff,export_location):
    alloy_comp={}
    trimfs=WIRS_cutoff
    totalwtlow=98 
    totalwthigh=102

    #Defines the scheil equation for use later on in plotting
    def scheil(C0,k, fs):
        return k*C0*((1-fs)**(k-1))
    
    #Reads excel sheet with composition data and stores the nominal composition of the alloy of interest
    for i in elements:
        compositions=pd.read_excel(composition_location)
        index=compositions.index[compositions['Name']==alloy]
        alloy_comp[i]=compositions.iloc[index][i]
        
    #Reads excel sheet with EPMA data and applies the user-defined filter
    data= pd.read_excel(epma_data)
    print('Before Count Filter:',len(data))   

    primary=data[eval(filter)]
    print('After Count Filter:',len(primary))
    
    #Begins WIRS analysis by performing C bar calculations in accordance with the defined segregation directions
    columns=[]
    for i in elements:
        if (elements[i]=='Liquid'):
            primary[i+'_bar']=((primary[i+" Elemental Percents"] - primary[i+" Elemental Percents"].min())/
                               ((primary[i+' Percent Errors']/100)*primary[i+' Elemental Percents']))
        if(elements[i]=='Solid'):
            primary[i+'_bar']=((primary[i+" Elemental Percents"].max() - primary[i+" Elemental Percents"])/
                               ((primary[i+' Percent Errors']/100)*primary[i+' Elemental Percents']))
        columns.append(i+'_bar')

    primary['Avgbar'] = primary[columns].mean(axis=1)

    #Sorts grid points according to C-bar min to max
    primary_sort=primary.sort_values(by=['Avgbar'])
    primary_sort['Rank'] = primary_sort['Avgbar'].rank(ascending = 1)

    #Assigns each EPMA point a value of fraction solid depending on its C-bar rank
    primary_sort['Fsolid']=(primary_sort['Rank'] - 0.5)/primary_sort['Rank'].max()
    primary_sort=primary_sort.reset_index(drop=True)
    
    # Cuts sorted data to a specified fraction solid
    final_data= primary_sort[(primary_sort["Fsolid"]<trimfs)]
    
    #Selects the first 7.5% of EPMA points in the dendrite core and uses them to calculate k init for each element
    acore=int(len(primary_sort)*.075) 
    print('# of points in k calculation:', acore)

    kinit={}
    for i in elements:
        kinit[i]= final_data[i+' Elemental Percents'].iloc[0:acore].mean(axis=0) / alloy_comp[i]
    print('_____________________________________________________________________________________\n')
    print('Calculated Partition Cofficients:')
    print(kinit)
    print('\n_____________________________________________________________________________________')
    #_________________________________________________________________________________________________

    #Start of MBA Analysis
    mba_dict={}
    #Applies the MBA trim defined by the user
    mba_trim=MBA_cutoff
    final_data2= final_data[(primary_sort["Fsolid"]<mba_trim)]
    
    #Performs MBA analysis on each element, stores the data in a new dataframe
    for el in elements:
        mba=pd.DataFrame(columns=['k', 'fs', 'cs_at_fs', 'cl_at_fs'])
        fs_incr=final_data2['Fsolid'][2]-final_data2['Fsolid'][1]
        fs=0
        mass_el_in_solid=0 #assume 100% liquid to start
        mass_el_in_liq= alloy_comp[el] #CL=Co at FL=1
        for i in range (0, len(final_data2)):
            cs_at_fs= final_data2.iloc[i][el+' Elemental Percents']
            fs= fs+fs_incr
            fl= (1-fs)

            mass_el_in_solid= mass_el_in_solid+(fs_incr*cs_at_fs)
            mass_el_in_liq= (alloy_comp[el]- mass_el_in_solid)
            cl_at_fs= (mass_el_in_liq/(fl))
            k= (cs_at_fs/cl_at_fs)
            value=pd.DataFrame({'k':k, 'fs':fs, 'cs_at_fs':cs_at_fs, 'cl_at_fs':cl_at_fs})
            mba=mba.append(value,ignore_index=True)
        mba_dict[el]= mba
    
    #Creates up to three plots of the WIRS data depending on the magnitude of the nominal compositions of the elements
    plot1=[]
    plot2=[]
    plot3=[]
    for key in alloy_comp:
        if (float(alloy_comp[key])>=25):
            plot1.append(key)
        if ((float(alloy_comp[key])<25)&(float(alloy_comp[key])>=5)):
            plot2.append(key)
        if (float(alloy_comp[key])<5):
            plot3.append(key)

    plotlist=[plot1,plot2,plot3]
    for plot in plotlist:
        try:
            plt.figure(figsize=(6,6))
            for i in plot:
                plt.scatter(final_data['Fsolid'],final_data[i+' Elemental Percents'],label=i, s=30)
                plt.plot(final_data['Fsolid'],scheil(float(alloy_comp[i]),float(kinit[i]),final_data['Fsolid']), 
                         color='black', label='Scheil (k init)')
            plt.xlim(0,1.05)
            plt.xlabel('Fraction of Solid', fontsize=30)
            plt.ylabel('Concentration (wt.%)', fontsize= 30)
            plt.rc('xtick', labelsize=25) 
            plt.rc('ytick', labelsize=25)
            plt.legend(fontsize=25)
            plt.grid()
            plt.show()
        except:
            pass
    
    #Creates a plot for the partition coefficient vs. fraction solid for each element, also plots k init for comparison
    for el in elements:
        plt.figure(figsize=(6,6))
        plt.scatter(mba_dict[el]['fs'],mba_dict[el]['k'],label='k(fs)- '+el, s=30)
        plt.plot([0,0.95],[float(kinit[el]),float(kinit[el])], color='black', label='k init')
        plt.xlim(0,1.05)
        plt.ylim(0,3)
        plt.xlabel('Fraction of Solid', fontsize=30)
        plt.ylabel('k(fs)', fontsize= 30)
        plt.rc('xtick', labelsize=25) 
        plt.rc('ytick', labelsize=25)
        plt.legend(fontsize=25)
        plt.grid()
        plt.show()
    
    #Exports the WIRS and MBA data to excel
    with pd.ExcelWriter(export_location) as writer:
        for key in mba_dict:
            df=pd.DataFrame(data=mba_dict[key])
            df.to_excel(writer, sheet_name=key)
        final_data.to_excel(writer, sheet_name='WIRS Data')
            
            


# In[3]:


#Defines the WIRS Analysis as a function reliant on 7 inputs
def WIRS(alloy, elements,composition_location,epma_data,filter,fs_cutoff,export_location):
    alloy_comp={}
    trimfs=fs_cutoff
    totalwtlow=98 
    totalwthigh=102
    
    #Defines the scheil equation for use later on in plotting
    def scheil(C0,k, fs):
        return k*C0*((1-fs)**(k-1))
    
    #Reads excel sheet with composition data and stores the nominal composition of the alloy of interest
    for i in elements:
        compositions=pd.read_excel(composition_location)
        index=compositions.index[compositions['Name']==alloy]
        alloy_comp[i]=compositions.iloc[index][i]
    data= pd.read_excel(epma_data)
    print('Before Count Filter:',len(data))   

    primary=data[eval(filter)]
    print('After Count Filter:',len(primary))
    
    #Begins WIRS analysis by performing C bar calculations in accordance with the defined segregation directions
    columns=[]
    for i in elements:
        if (elements[i]=='Liquid'):
            primary[i+'_bar']=((primary[i+" Elemental Percents"] - primary[i+" Elemental Percents"].min())/
                               ((primary[i+' Percent Errors']/100)*primary[i+' Elemental Percents']))
        if(elements[i]=='Solid'):
            primary[i+'_bar']=((primary[i+" Elemental Percents"].max() - primary[i+" Elemental Percents"])/
                               ((primary[i+' Percent Errors']/100)*primary[i+' Elemental Percents']))
        columns.append(i+'_bar')
    primary['Avgbar'] = primary[columns].mean(axis=1)

    #Sorts grid points according to C-bar min to max
    primary_sort=primary.sort_values(by=['Avgbar'])
    primary_sort['Rank'] = primary_sort['Avgbar'].rank(ascending = 1)

    #Assigns each EPMA point a value of fraction solid depending on its C-bar rank
    primary_sort['Fsolid']=(primary_sort['Rank'] - 0.5)/primary_sort['Rank'].max()
    primary_sort=primary_sort.reset_index(drop=True)
    # Cut sorted data to a specified fraction solid
    final_data= primary_sort[(primary_sort["Fsolid"]<trimfs)]
    
    #Selects the first 7.5% of EPMA points in the dendrite core and uses them to calculate k init for each element
    acore=int(len(primary_sort)*.075) #number of points to average from start of sorted data
    print('# of points in k calculation:', acore)

    kinit={}
    for i in elements:
        kinit[i]= final_data[i+' Elemental Percents'].iloc[0:acore].mean(axis=0) / alloy_comp[i]
    print('_____________________________________________________________________________________\n')
    print('Calculated Partition Cofficients:')
    print(kinit)
    print('\n_____________________________________________________________________________________')

    #Creates up to three plots of the WIRS data depending on the magnitude of the nominal compositions of the elements
    plot1=[]
    plot2=[]
    plot3=[]
    for key in alloy_comp:
        if (float(alloy_comp[key])>=25):
            plot1.append(key)
        if ((float(alloy_comp[key])<25)&(float(alloy_comp[key])>=5)):
            plot2.append(key)
        if (float(alloy_comp[key])<5):
            plot3.append(key)

    plotlist=[plot1,plot2,plot3]
    for plot in plotlist:
        try:
            plt.figure(figsize=(6,6))
            for i in plot:
                plt.scatter(final_data['Fsolid'],final_data[i+' Elemental Percents'],label=i, s=30)
                plt.plot(final_data['Fsolid'],scheil(float(alloy_comp[i]),float(kinit[i]),final_data['Fsolid']), color='black')
            plt.xlim(0,1.05)
            plt.xlabel('Fraction of Solid', fontsize=30)
            plt.ylabel('Concentration (wt.%)', fontsize= 30)
            plt.rc('xtick', labelsize=25) 
            plt.rc('ytick', labelsize=25)
            plt.legend(fontsize=25)
            plt.grid()
            plt.show()
        except:
            pass

        #Exports the WIRS data to excel
        df=pd.DataFrame(data=final_data)
        df.to_excel(export_location)


# In[ ]:





# In[ ]:




