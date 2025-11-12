%author Aleksandar Demic
%
% Material class containing parameters of material system typically used
% for muliple quantum well structures. Units are chosen as typically given
% in literature, the Grid class converts them to SI units for further use
% by the solvers.

classdef Material < handle
    properties
        m=struct('well',0,'barr',0);        % Effective mass [Fraction of m0]
        Eg=struct('well',0,'barr',0);       % Bandgap [eV]
        Egp=struct('well',0,'barr',0);      % L valley bandgap [eV]
        d0=struct('well',0,'barr',0);       % Spin-split bandgap [eV]
        P=struct('well',0,'barr',0);        % P Kane parameter [eV A]
        Q=struct('well',0,'barr',0);        % Q Kane parameter [eV A]
        V=struct('well',0,'barr',0);        % Conduction band potential [eV]
    end
    methods
        %% Constructor
        function obj = Material(HeterostructureMaterial)
            switch HeterostructureMaterial
                case 'AlGaAs'
                    obj.m.well    =  0.067;
                    obj.Eg.well   =  1.424;
                    obj.Egp.well   =  4.48;
                    obj.d0.well   =  0.341;
                    obj.P.well   =  9.88;
                    obj.Q.well   =  8.68;
                    obj.V.well = 0;

                    obj.m.barr  =  0.15;
                    obj.Eg.barr   = 2.777;
                    obj.Egp.barr   = 4.55;
                    obj.d0.barr   =  0.3;
                    obj.P.barr   =  8.88;
                    obj.Q.barr   =  8.07;

                    obj.V.barr = 0.67*(obj.Eg.barr-obj.Eg.well);

                case 'AlGaSb'
                    obj.m.well   =  0.041;  
                    obj.Eg.well   = 0.81;
                    obj.Egp.well   = 3.11;
                    obj.d0.well   =  0.76;
                    obj.P.well   =  9.69;
                    obj.Q.well   =  8.25;
                    obj.V.well = 0;

                    obj.m.barr   =  0.12;
                    obj.Eg.barr   = 1.7; 
                    obj.Egp.barr   = 3.53;
                    obj.d0.barr   =  0.67;
                    obj.P.barr   =  8.57;
                    obj.Q.barr   =  7.8;

                    obj.V.barr = 0.55*(obj.Eg.barr-obj.Eg.well);
                    
                case 'InGaAs/InAlAs'  %In_0.53Ga_0.47As/In_0.52Al_0.48As
                    obj.m.well  =  0.043;
                    obj.Eg.well   = 0.8161;
                    obj.Egp.well   = 4.508;
                    obj.d0.well   =  0.3617;
                    obj.P.well   =  9.4189;
                    obj.Q.well   =  8.1712;
                    obj.V.well = 0;
                                        
                    obj.m.barr   =  0.075;
                    obj.Eg.barr   = 1.5296; 
                    obj.Egp.barr   = 4.514;
                    obj.d0.barr   =  0.3416;
                    obj.P.barr   =  8.9476;
                    obj.Q.barr   =  7.888;

                    obj.V.barr = 0.73*(obj.Eg.barr-obj.Eg.well);
                    
                case 'InGaAs/GaAsSb'  %In_0.53Ga_0.47As/GaAs_0.51Sb_0.49
                    obj.m.well  =  0.043;
                    obj.Eg.well   = 0.8161;
                    obj.Egp.well   = 4.508;
                    obj.d0.well   =  0.3617;
                    obj.P.well   =  9.4189;
                    obj.Q.well   =  8.1712;
                    obj.V.well = 0;
                                        
                    obj.m.barr   =  0.045;
                    obj.Eg.barr   = 1.1786; 
                    obj.Egp.barr   = 3.8393;
                    obj.d0.barr   =  0.39637;
                    obj.P.barr   =  9.7869;
                    obj.Q.barr   =  8.4693;

                    obj.V.barr = 1*(obj.Eg.barr-obj.Eg.well);
            end
        end
        function [alpha0golubov, beta0golubov] = get_alpha0g(obj,x)
            Eg_alloy = obj.interpolate_parameter(x,obj.Eg);
            Egp_alloy = obj.interpolate_parameter(x,obj.Egp);
            d0_alloy = obj.interpolate_parameter(x,obj.d0);
            P_alloy = obj.interpolate_parameter(x,obj.P);
            Q_alloy = obj.interpolate_parameter(x,obj.Q);
            
            E0_alloy=Egp_alloy-Eg_alloy;
            ksi_alloy=P_alloy^4/9/Eg_alloy^3/(Eg_alloy+d0_alloy)^2; 
            hi_alloy=P_alloy^2*Q_alloy^2/9/E0_alloy/Eg_alloy^2/(Eg_alloy+d0_alloy)^2;

            alpha0golubov=-ksi_alloy*(3*Eg_alloy^2+4*Eg_alloy*d0_alloy+2*d0_alloy^2)*(3*Eg_alloy+2*d0_alloy)/(Eg_alloy+d0_alloy)-2*hi_alloy*d0_alloy^2;
            beta0golubov=-12*hi_alloy*(3*Eg_alloy^2+4*Eg_alloy*d0_alloy+d0_alloy^2);
        end 
        function [alpha0golubobp, beta0golubovp] = get_alpha0gp(obj,x)
            e=1.602176462e-19;          %elementary charge
            hbar=1.05457172647e-34;     %reduced Planck const
            m0=9.10938188e-31;          %electron mass
            u0=hbar/m0;                 %scaling parameter
            A=1e-10;                    %angsrom
            m_alloy = obj.interpolate_parameter(x,obj.m);
            [alpha0g, beta0g] = obj.get_alpha0g(x);
            alpha0golubobp=-(2*m_alloy*e*A^2/hbar/u0)^2*alpha0g;    %ev^-1 
            beta0golubovp=-(2*m_alloy*e*A^2/hbar/u0)^2*beta0g;      %ev^-1 
        end 
        function alpha = get_alpha_kane(obj,x)
            Eg_alloy = obj.interpolate_parameter(x,obj.Eg);
            alpha=1./Eg_alloy;
        end 
        function par = interpolate_parameter(obj,x,param)
            par = param.well + x * (param.barr-param.well);
        end 
    end
end