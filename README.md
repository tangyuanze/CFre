# CFre
---
### Source code for Creep-fatigue reliability assessment plug-in for Abaqus
Developer: Yuanze Tang
Contact: yztangapr@gmail.com


# Introduction
---
CFre is an efficient Abaqus plug-in tool for probabilistic reliability assessment, combining uncertainty quantification, FE simulation, surrogate model reliability assessment methods, and visualization into one platform based on Python.
![alt text](image.png)
# Installation
---
1. The software package "CFre_ReleasedV*x*" should be placed in the Abaqus_plugins directory under the Abaqus parent directory. You can find ‘Creep-Fatigue Analysis - Reliability’ tab under the ‘Plug-ins’ toolbar once opening Abaqus CAE.
2. Two third-party Python libraries need to be placed in the path of the Abaqus Python library (for example, "D:\ABAQUS2020\win_b64\tools\SMApy\python2.7\Lib\site-packages"): "xlrd" and "xlwt".
- **File description:**
- CFre_ReleasedV1: Software package
- Python_Third-party_Library Dependencies: Third-party Python libraries
- Surrogate_Model_Source_Code: Source code encapsulated into the .exe file 
- Test_Model: Example of turbine. Finite element model (.cae) and result (.odb), assessment results (.xls and .png)
# Instructions for use
---
#### 1. FEM TAB
##### In box (I), choose the finite element model and the material. Enter the name of the job, the number of CPUs to be used, and the number of times the simulation to be conducted. 
* Users can also create custom material properties by selecting the ‘User Define’ option, in box c. 
* Checkbox 'Temp'. considers the uncertainty for temperature-dependent material properties in CAE. The property values will be read from CAE instead of database.
* Button 'Database' is for displaying the properties value for various materials in database. Modifications in the database will be synchronized to the plug-in.
##### In box (II), selecte reliability criteria for calculation of the final reliability. 
* Three reliability criteria are provided for single or multiple selections, including Load-life interference (LLI), strength-damage interference (SDI), and probabilistic damage interaction diagram with continuous envelope (PDID). Detailed expression for these criteria can be referred to https://doi.org/10.1016/j.ress.2022.108523.
* Each selected criterion produces a series of results in the subsequent calculations and visualizations.
##### In box (III), selecte variables that need to be discretized as the input for FEM. Uncertainty feature inputs are only valid for the parameters selected here.
* The ‘General’ category contains loading variables, geometric features, and material inherent properties, i.e., density (*dens.*), thermal conductivity (*T. cond.*), coefficient of thermal expansion (*T. expan.*), Young’s modulus (*E*), Poisson’s ratio (*u*). 
* The ‘Creep’ category contains parameters of the Strain Energy Density Exhaustion (*SEDE*) and Norton-Bailey (*NB*) models .
* The ‘Fatigue’ category contains parameters of the Critical Plane-based Method (*CPM*) and Ramberg-Osgood (*RO*) models. Detailed expression for these life models can be referred to https://doi.org/10.1016/j.ress.2022.108523.
* Recommendation: The group of *{sigmaf, epsilonf, E, n, m, n1, wfcrit}* are independent variables to be discretized for model parameters.

![alt text](image-1.png)
#### 2. Uncertainty TAB
##### Characterize the Material/Model parameters uncertainty in box (I)
* Select the probabilistic distributions in drop-down list, including normal distribution, lognormal distribution, two-parameter Weibull distribution
* The mean values of these distributions are determined by the material properties and parameters of deterministic creep-fatigue models, varying with the material selected in the FEM TAB
*  Enter coefficients of variation (CVs) for Material/Creep/Fatigue parameters.
##### Characterize the Geometry uncertainty in box (II)
* Appoint the sketch name and pick the key dimensions on the sketch. Multiple geometric dimensions are also supported (press the shift key and pick them).
* Enter the means and CVs for the key dimensions. Mean should be entered separately with commas if there is more than one.
* The mean of the depth for a 3D model can be entered if the depth is considered to be a random variable.
##### Characterize the Load uncertainty in box (III):
* Enter the name of the load with the mean and CV. The direction of the load should be selected in the drop-down list (It follows the same symbol definition as in Abaqus CAE. ‘Magnitude’ is for the amplitude, ‘CF*i*’ is the three directions of force, ‘U*i*’ and ‘UR*i*’ are the three translational and rotational degrees of freedom for displacement loading respectively (*i*=1, 2, 3). For example, if the load is a centrifugal force on rotating structures, users should select ‘Magnitude’ and enter the rotating speed as the mean.). 
* Enter the mean and the CV of hold time, and the name of the amplitude applied to the load in Abaqus, if hold time is considered to be a random variable.

![alt text](image-2.png)
#### 3. Surrogate Model TAB
##### Choose the training dataset source in box (I)
* The dataset can either be derived from the FEM results or provided by users in other Excel files, or just conduct FEM and no training. 
* The input and output data in the user-supplied Excel file should be separated by a column of blank cell (like the format of the dataSet.xls generated by the plug-in). 
##### Choose the surrogate model In box (II)
* Four surrogate modelling approaches can be chosen.
* Use SVR for sample expansion if needed and specify the size of the virtual data to be generated. 

![alt text](image-3.png)
#### 4. Result Analysis TAB
##### Damage and life evaluation
* Specify the node points to be evaluated, otherwise the maximum damage points will be focused on.
* Creep and fatigue damage accumulation and life evaluation diagram.
* MCS histogram and probability distribution function for damage and life.
* Pearson and MIC correlation analysis between varaibles and life.
##### Reliability assessment
* Desgin life - Failure probability curve based on hotspot (maximum total damage point) under LLI/SDI/PDID reliability criteria.
* Desgin life - Failure probability curve based on joint evaluation strategy (maximum creep/fatigue/total damage points) under PDID. 
* The hotspot-based strategy regards the reliability of the most critical locations as the structural reliability. While the joint failure evaluation strategy takes other potential failures into account.
##### Sensitivity analysis
* Curves of sensitivity versus reliability for all variables.
* Pie chart of sensitivity for all variables at specified reliability.
* Variance-based global sensitivity approach is adopted to measure the effects of the uncertainty on failure probability.
##### Influence of uncertainties
* Add one or two cases to compare results considering different sources of uncertainty, after the original calculation completing. Results of comparion will be displayed in graphical form.
* Take the checkbox, the corresponding variables in this source of uncertainty will be treated as a constant and other variables remain unchanged. The assessment process will be repeated. 
##### Multi-conditions
* Add more condition cases, after the original calculation completing.
* Choose the variable you want to change from drop-down list, and enter the mean value list for the variable in the form of 'start value, stop value, number of point'.
  
![alt text](image-4.png)
#### 5. Execution and output
* Finally, after selecting the desired options on the GUI, users click the ‘OK’ button at the bottom of the interface to initiate the execution of the kernel program. The process information is displayed in both Abaqus CAE message area and Abaqus command line window. 
* In the message area, users can find the information related to the FEM process, including the variable changes, detailed information for dangerous points, and the running time with a separation between CPU time and clock time (The CPU time refers to the total running time across all CPUs and the clock time represents the real-world time). The CPU time and the clock time of the total program are almost the same because the Python kernel program runs on a single CPU by default, differing from FEM where users can specify the number of CPUs to be used. 
* The information related to the surrogate modelling approach is displayed in the command line window, because this part of program is embedded within the main program in the form of an executable file. The information contains the model name, the optimal model parameters identified through the grid search algorithm, and the evaluation indicators obtained by the cross-validation method. 
* Upon completion of the job, three Excel files (dataSet.xls, mcsData.xls, time.xls), a certain number of figure results selected from the Visualization TAB, and a trained surrogate model file (model name.pkl) are saved in the working directory of Abaqus. 
 
![alt text](image-5.png)
* Here are some illustrative images that can be output:
![alt text](image-6.png)
--- 
**For more information on this work, please consult the paper.**
The reliability assessment plug-in for *ANSYS Workbench* is under development ...
