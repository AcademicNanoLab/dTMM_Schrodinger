clear all
close all 
clc

%We set the structure parameters, grid spacing and electrical field
layer_file="Structure2_LO_InGaAs_InAlAs.txt";
material="InGaAs/InAlAs";
dz=0.6;                   % z-axis resolution in [angstroms]
K=10.0;                   % Electrical field in kV/cm
G=Grid(layer_file,dz,material);
G.set_K(K);

%We call 4 TMM solvers and 3 FDM solvers
SolverTMMParabolic=TMMSolver("Parabolic",G,4);
[energiesTMMParabolic,psisTMMParabolic]=SolverTMMParabolic.get_wavefunctions;
energiesTMMParabolic_meV = energiesTMMParabolic / G.consts.e*1e3;

SolverTMMKane=TMMSolver("Kane",G,4);
[energiesTMMKane,psisTMMKane]=SolverTMMKane.get_wavefunctions;
energiesTMMKane_meV = energiesTMMKane / G.consts.e*1e3;

SolverTMMTaylor=TMMSolver("Taylor",G,4);
[energiesTMMTaylor,psisTMMTaylor]=SolverTMMTaylor.get_wavefunctions;
energiesTMMTaylor_meV = energiesTMMTaylor / G.consts.e*1e3;

SolverTMMEkenberg=TMMSolver("Ekenberg",G,4);
[energiesTMMEkenberg,psisTMMEkenberg]=SolverTMMEkenberg.get_wavefunctions;
energiesTMMEkenberg_meV = energiesTMMEkenberg / G.consts.e*1e3;

SolverFDMParabolic=FDMSolver("Parabolic",G,4);
[energiesFDMParabolic,psisFDMParabolic]=SolverFDMParabolic.get_wavefunctions;
energiesFDMParabolic_meV = energiesFDMParabolic / G.consts.e*1e3;

SolverFDMKane=FDMSolver("Kane",G,4);
[energiesFDMKane,psisFDMKane]=SolverFDMKane.get_wavefunctions;
energiesFDMKane_meV = energiesFDMKane / G.consts.e*1e3;

SolverFDMTaylor=FDMSolver("Taylor",G,4);
[energiesFDMTaylor,psisFDMTaylor]=SolverFDMTaylor.get_wavefunctions;
energiesFDMTaylor_meV = energiesFDMTaylor / G.consts.e*1e3;

%We calculate the difference between the TMM and FDM solvers for the
%Parabolic, Kane and Taylor case
EnergyDifference_TMM_FDM_Parabolic=1000*(energiesTMMParabolic_meV-energiesFDMParabolic_meV);
EnergyDifference_TMM_FDM_Kane=1000*(energiesTMMKane_meV-energiesFDMKane_meV);
EnergyDifference_TMM_FDM_Taylor=1000*(energiesTMMTaylor_meV-energiesFDMTaylor_meV);


%We plot the conduction band diagram for the selected solver
V=Visualization(G,energiesTMMParabolic,psisTMMParabolic);
V.plot_V_wf;
V.plot_energies;
V.plot_energy_difference_in_terahertz;