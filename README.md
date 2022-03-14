# Mass-Balance-Analysis
Code associated with "A Novel Approach to Determine Variable Solute Partition Coefficients" by C. J. Farnin, S. Orzolek, and J. N. DuPont published in Metallurgical and Materials Transactions A: https://doi.org/10.1007/s11661-020-05986-9

Welcome to my Github repository containing the EPMA data analysis code for the publication "A Novel Approach to Determine Variable Solute Partition Coefficients" published in Met. Trans. A. For those interested, the original code used for that publication are found in the "Mass Balance Analysis For Co-Cu Binary System.ipynb" file within the repository.

UPDATE MARCH 2022: This code was originally written back when my co-author (S. Orzolek) and I were new to coding, and as such it is very narrow in scope and has poor organization. Since gaining some additional experience with Python, I have decided to upload an overhauled version of the code that is much more applicable to different materials without having to make changes to the code. These updated files can be found in the "CJF_EPMA_Processing Files" folder. I did this by essentially black box'ing the WIRS and MBA calculations through the creation of a downloadable python module (saved as a .py file) that lets any user apply the analysis to their own data by calling a function and providing the following inputs:

1) Alloy name (As it is labelled in the excel sheets)
2) A dictionary that lists the elements of interest and the associated direction of expected segregation (Solid or Liquid)
3) The file location containing an excel sheet with the compositions of the alloys of interest
4) The file location of the EPMA data
5) A string defining a filter for the EPMA data (for example, if only datapoints with a total wt% between 98-102 would like to be included in the analysis)
6) The fraction solid cutoff for the WIRS processing (0.0-0.99)
7) The fraction solid cutoff for the MBA processing (0.0-0.99, recommended to be <=0.95)
8) The desired file location to store an exported excel sheet containing all of the sorted WIRS and MBA data.

Based on these rather simple inputs, the code will output the initial partition coefficient (k init) of each element, 1-3 solid concentration vs. fraction solid plots for all elements (some elements will share a plot based on the scale of their nominal compositions), one plot of the partition coefficient (k) vs. fraction solid for each element plotted alongside the k init value (shown as a horizontal line), and an excel sheet with the WIRS sorted EPMA data and MBA data (fs, k, solid concentration, and liquid concentration) of each element. The CJF_EPMA_Processing.py file can be saved to the same file location as all of the other python codes a user may have, and then imported into any code with a single line of text, identical to other packages such as numpy or pandas.

The CJF_EPMA_Processing module contains two functions, the WIRS function that exclusively conducts the WIRS data analysis, and the MBA function that does both the WIRS and MBA analyses in case a user would want to do one without the other. As I have it designed, the code should be able to accomodate any type of alloy, regardless of the number or type of elements involved without ANY necessary modifications as long as the 8 inputs are defined and formatted properly. An example file showing how the imported .py file and associated MBA() function can be used is shown in the file labelled "CJF_EPMA_Processing Example.ipynb". Excel sheets with the necessary formatting for the function to retrieve the alloy composition and EPMA data are also included. 

While the automation of these techniques will hopefully be convenient, I would NOT recommend relying solely on the module without any knowledge of how the code and calculations work. I did my best to make the program fool proof, but I do not claim to be a Python expert, and have only validated the functions using 2-3 different materials that I have data for. Also, as described in the partition coefficient paper, the MBA is a sensitive technique that requires pristine data to be accurate, and should not be applied in every circumstance.

If you have any questions, comments, or recommendations about the code and/or EPMA data analysis procedures, please do not hesitate to reach out to me over email at cjf219@lehigh.edu. And if you find the code useful in  your own research, please ensure to cite the proper publications that I will link below:

MBA- Farnin et. al: https://doi.org/10.1007/s11661-020-05986-9

WIRS- Ganesan et. al: https://doi.org/10.1007/s11661-005-0338-2 
