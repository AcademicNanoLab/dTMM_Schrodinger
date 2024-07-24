# dTMM_Schrodinger
Schrodinger equation solvers via derivative transfer matrix method and finite difference method

Details on the solvers and methodology of this package is available at doi.org/xxxxxxxx

The package consists of six classes, implemented in MATLAB:
  - **ConstsAndScales** - contains common constants and scales required for solving Schrodinger equation under effective mass approximation
  - **Material** - contains material parameters of several material systems in which multiple quantum well heterostrucutres can be generated, namely GaAs/AlGaAs, GaSb/AlGaSb, InGaAs/InAlAs, InGaAs/GaAsSb, we encourage the user to add more material properties to this repository
  - **Grid** - contains methods that define the spatial axis z and material parameters profile
  - **FDMSolver** - contains methods that solve 1D Schrodinger equation under effective mass approximation via finite difference approach using three cases:
          - parabolic subband approximation,
          - full two band Kane nonparabolic subband approximation and
          - Taylor expansion of the two band Kane nonparabolic subband approximation
  - **TMMsolver** - contains methods that solve 1D Schrodinger equation under effective mass approximation via derivative transfer matrix approach using four cases: 
          - parabolic subband approximation,
          - full two band Kane nonparabolic subband approximation and
          - Taylor expansion of the two band Kane nonparabolic subband approximation
          - 14 kp band nonparabolicity treatement of Schrodinger equation as per work in  U.Ekenber et. al, Physical Review B 40 (1989) 7714
   -  **Visualisation** - contains methods that create figures that visualise the electron structure, currently 4 figures are supported: electron structure of the modelled device, eigenvalue energy graph, energy difference graph, electron structure on two periods if user was modelling a QCL device.

The main code contains GUI version (by running Main_GUI.m) and manual version (by running Main.m), user can select the following options:
   -  **layer_file** = ".....txt" - two column file containing multiple quantum well layer structure in format
       200  0.15
       200  0
       20   0.15
       200  0
       200  0.15
      The first column is width of the layers in angstorom (1e-10 meters) and the second column is molar composition of the barrier layer (interpolation is handled via Material class depending on chosen material system)
      We recommend users to add periods of superlattice starting by half of the injection barrier (so that the file ends and starts by the half of the width of the injection barrier).
      To obtain tight-binding solutions of Schrodinger equation, user should add extra padding of 100+ angstroms in their injection barrier layers
  - **material** = "AlGaAs" - string defining material systems, currently supported material systems are "AlGaAs", "AlGaSb", "InGaAs/InAlAs" and "InGaAs/GaAsSb"
  - **nstamx** - number of states to visualy present in the figures, rule of thumb is number of wells + 2
  - **solver** = "TMM" - string defining type of solver you wish to use, supported options are "TMM" and "FDM"
  - **nonparabolicityType** = "Taylor" - string defining specific treatment of nonparabolicity treatment in Schrodinger equations, supported options are "Parabolic", "Kane", "Taylor" and TMM solver has an extra option "Ekenberg" for the 14kp model by U.Ekenber et. al, Physical Review B 40 (1989) 7714
  - **dz** - resolution of z axis in angstroms
  - **padding** - total added padding in layer_file in angstroms, this option is only relevant for plotting the solutions on two periods and if user used tight binding approximation while calculating the electronic structure

The package contains a test folder in which there are three .m test files and three corresponding layer files = ".....txt" - containing the width of the layers in angstorom and the molar composition of the barrier layers for the three exemplary structures.

  - Structure 1 is a GaAs/AlGaAs Bound to continuum THz QCL descibed in: A. Demić et. al, IEEE Transactions on Terahertz Science and Technology 7 (2017) 368–377.
  - Structure 2 is a LO-phonon InGaAs/InAlAs THz QCL descibed in: C. Deutsch et. al, Acs Photonics 4 (2017) 957–962
  - Structure 3 is a LO-phonon InGaAs/GaAsSb THz QCL descibed in: C. Deutsch et. al, Applied Physics Letters 101 (2012).

In the .m test files the structure parameters, grid spacing and electrical field are set for the exemplary structures and all of the seven solvers (three FDM + four TMM) are called for calculating the quasi-bound state energies and wavefunctions which are saved to the corresponding variables.
The difference is calculated between the quasi-boung state energies calculated with the TMM and FDM solvers for the parabolic subband approximation (Parabolic), full two band Kane nonparabolic subband approximation (Kane) and the Taylor expansion of the two band Kane nonparabolic subband approximation (Taylor). Lastly the conduction band diagram is plotted using the Visualization.m class for the selected solver.

