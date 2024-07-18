
%author Aleksandar Demic

% Visualization object that plots outputs of SchrodingerNonparabolic solver
classdef Visualization < handle
    properties (Access = private)
        %% Grid properties
            E;          % Quasbound energies
            psi;        % Wavefunctions
            G;          % QCL structure grid
            consts;
    end
    methods
    %% Constructor
        function obj = Visualization(Grid,energies,psis)
            obj.G = Grid;
            obj.E = energies;
            obj.psi = psis;
            obj.consts=ConstAndScales;
        end
    %% plot methods
        %% Get bandstructure profile and wavefuncitons
        function f = plot_V_wf(obj)
            nstates=length(obj.E);
            f=figure;
            z=obj.G.get_z/obj.consts.angstrom;
            plot(z,obj.G.get_bandstructure_potential/obj.consts.meV,'k','LineWidth',3)
            hold all;
            for i=1:nstates
                plot(z,1000.*(abs(obj.psi(i,:)).^2)+obj.E(i)/obj.consts.meV,'LineWidth',3);
            end
            hold off
            title('Bandstructure profile');
            xlabel('z [$\textrm{\AA}$]','interpreter','latex');
            ylabel ('V [meV]','interpreter','latex')
            set(gca,'FontSize',14)
        end
        %% Get bandstructure profile and wavefuncitons on two periods
        function f = plot_QCL(obj,K,padding)
            nstates=length(obj.E);
            f=figure;
            z=obj.G.get_z/obj.consts.angstrom;
            Lper=z(end)-padding;
            npad=floor(padding/(obj.G.get_dz/obj.consts.angstrom)/2);
            hold all;
            for p=1:2
                V=obj.G.get_bandstructure_potential/obj.consts.meV-1e-2*K*Lper*(p-2);
                plot(z(npad:end-npad)+(p-1)*Lper,V(npad:end-npad),'k','LineWidth',3)
                for i=1:nstates
                    plot(z(npad:end-npad)+(p-1)*Lper,1000.*(abs(obj.psi(i,(npad:end-npad))).^2)+obj.E(i)/obj.consts.meV-1e-2*K*Lper*(p-2),'LineWidth',3);
                end
            end
            hold off
            title('Bandstructure profile on two QCL periods');
            xlabel('z [$\textrm{\AA}$]','interpreter','latex');
            ylabel ('V [meV]','interpreter','latex')
            set(gca,'FontSize',14)
        end
        %% Get eigenvalue energies
        function f = plot_energies(obj)
            f=figure;
            stem(obj.E/obj.consts.meV,'--b','MarkerSize',10,'LineWidth',2)
            title (['Bound state energies']);
            xlabel('#');
            ylabel ('E [meV]','interpreter','latex');
            grid on;
            set(gca,'FontSize',14)
        end
        %% Get energy differences in THz
        function f = plot_energy_difference_in_terahertz(obj)
            f=figure;
            deltaE=length(obj.E)-1;
            for i=1:deltaE
                if i<10
                    deltaE(i) = 11*i+10;
                else
                    deltaE(i) = i*101+100;
                end
            end % Neat trick to get lables on x axis as 21, 32, 43, ...
            stem(diff(obj.E/obj.consts.meV)/4.1356,'--ro','MarkerSize',10,'LineWidth',2)
            title ('Bound state energy differences');
            xlabel('${fi}$','interpreter','latex');
            xticks(1:deltaE);
            xticklabels(num2cell(deltaE));
            ylabel ('f [THz]','interpreter','latex');
            set(gca,'FontSize',14)
        end 
    end
end
