clear all
close all 
clc

%% Setup
layer_file="test/Structure1_BTC_GaAs_AlGaAs.txt";   % Input file 
material="AlGaAs";                                  % Material system
K=1.9;                                              % Input bias in [kV/cm]
nstmax=10;                                          % Max number of states
solver="TMM";                                       % Solver
nonparabolicityType="Taylor";                       % Nonnparabolicity type
dz=0.6;                                             % z-axis step in [angstroms]
padding=400;                                        % Added padding in [angstroms] 

%Note: in the setup file, if you wish to force tight binding solutions, add
%padding symmetrically around the injection barrier, this will directly
%influence the QCL plot method in the visualisation class.


%% Main code
G=Grid(layer_file,dz,material);
G.set_K(K);

if (solver == "FDM)
    Solver=FDMSolver(nonparabolicityType,G,nstmax);
else 
    Solver=TMMSolver(nonparabolicityType,G,nstmax);
end

[energies,psis]=Solver.get_wavefunctions;
energies_meV = energies / (G.consts.e);
V=Visualization(G,energies,psis);
V.plot_V_wf;
V.plot_energies;
V.plot_energy_difference_in_terahertz;
V.plot_QCL(K,padding);
