%author Aleksandar Demic

% Structure grid object that sets multiple quantum well system defined in
% the corresponding <layers.txt> file. This class generates x axis,
% bandstructure potential profile, effective mass profile and
% nonparabolicity parameter profile. 
% These profiles are generated through interpolation of material system
% parameters that formulate wells and barriers. Interpolation is assumed to
% be linear, depending on the fraction of dopant material in the system.

% Class also contains scaling factors
% that allow solver to operate with energies in eV and z axis in angstroms
% (this reduces model's stiffness, which is relevant as transfer matrix
% model may suffer overflow).
classdef Grid < handle
    properties (Access = private)
        %% Grid properties
            material;   % Material system       
            dz;         % Resolution of z-axis 
            z;          % z axis
            x;          % Molar composition of barrier material (vs z)
            
            nz;         % Number of points on z-axis
            K;          % Applied external electric field potential bias in [kV/cm]
            dE;         % Resolution of energy grid for eigenvalue search
    end
    properties (Access = public)
            consts;     % Constants and scales
    end
    methods
    %% Constructor
        function obj = Grid(layer_file,dz,HeterostructureMaterial)
            obj.consts=ConstAndScales;
            obj.dz = dz*obj.consts.angstrom;
            S=load(layer_file);                         % Load layer file 
            layer_thickness=S(:,1);                     % Read layer thicknesses
            alloy_profile=S(:,2);                       % Read alloy composition of each layer
            obj.z=0:dz:sum(layer_thickness);             % Make z axis
            obj.nz=length(obj.z);
            obj.material=Material(HeterostructureMaterial);       % Generate material 
            % Alghorithm for alternating layers, we mainly need to create
            % alloy profile vs z (x(z)) and this will then be used to
            % create profiles of conduction band potential, effective mass
            % and nonparabolic parameters. Alghorithm mainly checks in
            % which layer we are by tracking cumulative sum of layer
            % thickness read from file.
            obj.x=zeros(1,obj.nz);                      % Interpolate alloy profile in nz points
            layer=1;                        
            cum_sum=layer_thickness(layer);
            for i=1:obj.nz
                if (obj.z(i)>=cum_sum) && (layer < length(layer_thickness))
                    layer = layer+1;
                    cum_sum = cum_sum + layer_thickness(layer);
                end
                obj.x(i)=alloy_profile(layer); 
            end
            obj.z=obj.z*obj.consts.angstrom;
            obj.K=0;
            obj.dE=0.1e-3;
        end
    %% Set methods
       function set_K(obj,val)
           obj.K=val;
       end
       function set_dE(obj,val)
           obj.dE=val;
       end
    %% Get methods
       function K=get_K(obj)
           K=obj.K/obj.consts.kVcm;
       end
        %% Get nz
        function nz = get_nz(obj)
            nz=obj.nz;
        end
        %% Get dz
        function dz = get_dz(obj)
            dz=obj.dz;
        end
        %% Get z
        function z = get_z(obj)
            z=obj.z;
        end
        %% Get z at j
        function zj = get_zj(obj,j)
            zj=obj.z(j);
        end
        %% Get alloy profile vs z
        function x = get_x(obj)
           x=obj.x;
        end
        %% Get energy step
        function dE = get_dE(obj) 
            dE=obj.dE*obj.consts.e; 
        end
        %% Get energy limit (bandstructure potential max)
        function Vmax = get_Vmax(obj,K) %assumes K in kV/cm
            Vmax=obj.consts.e*(max(obj.x)*obj.material.V.barr + max(obj.z) * K * obj.consts.kVcm);
        end        
        %% Get banstructure potential profile vs z
        function V = get_bandstructure_potential(obj)  %assumes K in kV/cm
            V=zeros(1,obj.nz);
            for i=1:obj.nz
                V(i)=obj.consts.e * obj.material.interpolate_parameter(obj.x(i),obj.material.V);
            end
            V=V-obj.consts.e * obj.K * obj.consts.kVcm * obj.z;
            V=V-min(V); %Applying bias will create negative potential, so we offset this so that the lowest energy is 0
        end
        %% Get effective mass profile vs z
        function m = get_effective_mass(obj)
            m=zeros(1,obj.nz);
            for i=1:obj.nz
                m(i)=obj.consts.m0 * obj.material.interpolate_parameter(obj.x(i),obj.material.m);
            end
        end     
        function alpha = get_alpha_kane(obj)
            alpha=zeros(1,obj.nz);
            for i=1:obj.nz
                alpha(i)=obj.material.get_alpha_kane(obj.x(i)) / obj.consts.e;
            end
        end
        %% Get alphap profile vs z (scaled non paroblic parameter in [eV^-1])
        function alphap = get_alphap_ekenberg(obj)
            alphap=zeros(1,obj.nz);
            for i=1:obj.nz
                alphap(i)=obj.material.get_alpha0gp(obj.x(i)) / obj.consts.e;
            end
        end
    end
end