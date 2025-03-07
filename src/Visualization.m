
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
        function f = plot_V_wf(obj,parent)
            nstates=length(obj.E);
            f=parent;
            z=obj.G.get_z/obj.consts.angstrom;
            ax=axes(f);
            plot(ax,z,obj.G.get_bandstructure_potential/obj.consts.meV,'k','LineWidth',3)
            hold(ax,"on");
            for i=1:nstates
                plot(ax,z,1000.*(abs(obj.psi(i,:)).^2)+obj.E(i)/obj.consts.meV,'LineWidth',3);
            end
            hold(ax,"off");
            title(ax,'Bandstructure profile');
            xlabel(ax,'z [$\textrm{\AA}$]','interpreter','latex');
            ylabel(ax,'V [meV]','interpreter','latex');
            set(ax,'FontSize',14);
        end
        %% Get bandstructure profile and wavefuncitons on two periods
        function f = plot_QCL(obj,parent,K,padding,isGIF,varargin)
            nstates=length(obj.E);
            f=parent;
            z=obj.G.get_z/obj.consts.angstrom;
            Lper=z(end)-padding;
            npad=floor(padding/(obj.G.get_dz/obj.consts.angstrom)/2)+1;
            ax=axes(f);
            hold(ax,"on");
            for p=1:2
                V=obj.G.get_bandstructure_potential/obj.consts.meV-1e-2*K*Lper*(p-2);
                plot(ax,z(npad:end-npad)+(p-1)*Lper,V(npad:end-npad),'k','LineWidth',3)
                for i=1:nstates
                    plot(ax,z(npad:end-npad)+(p-1)*Lper,1000.*(abs(obj.psi(i,(npad:end-npad))).^2)+obj.E(i)/obj.consts.meV-1e-2*K*Lper*(p-2),'LineWidth',3);
                end
            end
            hold(ax,"off");
            if (isGIF)
                title(ax,strcat('K = ',num2str(K)));
                axis(ax,varargin{1})
            else
                title(ax,'Bandstructure profile on two QCL periods');
            end
            xlabel(ax,'z [$\textrm{\AA}$]','interpreter','latex');
            ylabel(ax,'V [meV]','interpreter','latex')
            set(ax,'FontSize',14)
        end

        %% Get eigenvalue energies
        function f = plot_energies(obj,parent)
            f=parent;
            ax=axes(f);
            stem(ax,obj.E/obj.consts.meV,'--b','MarkerSize',10,'LineWidth',2)
            title(ax,'Bound state energies');
            xlabel(ax,'#');
            ylabel(ax,'E [meV]','interpreter','latex');
            grid(ax,"on");
            set(ax,'FontSize',14)
        end
        %% Get energy differences in THz
        function f = plot_energy_difference_in_terahertz(obj,parent)
            f=parent;
            ax=axes(f);
            deltaE=length(obj.E)-1;
            for i=1:deltaE
                if i<10
                    deltaE(i) = 11*i+10;
                else
                    deltaE(i) = i*101+100;
                end
            end % Neat trick to get lables on x axis as 21, 32, 43, ...
            stem(ax,diff(obj.E/obj.consts.meV)/4.1356,'--ro','MarkerSize',10,'LineWidth',2)
            title (ax,'Bound state energy differences');
            xlabel(ax,'${fi}$','interpreter','latex');
            ylabel(ax,'f [THz]','interpreter','latex');
            xticks(ax,1:length(deltaE));
            xticklabels(ax,num2cell(deltaE));
            set(ax,'FontSize',14)
        end
    end
end
