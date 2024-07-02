%author Aleksandar Demic
%
% Schrodinger equation solver class using dTMM method

classdef TMMSolver < handle
    properties
        solverType;
        G;          % Grid object
        V;
        meff;
        alpha;
        consts;
        nE;
    end
    methods
        %% Constructor
        function obj = TMMSolver(solverType,Grid,nEmax)
            obj.solverType=solverType;
            obj.G=Grid;
            obj.V=obj.G.get_bandstructure_potential;
            obj.meff=obj.G.get_effective_mass;
            obj.consts=ConstAndScales;
            if (obj.solverType=="Ekenberg")
                obj.alpha=obj.G.get_alphap_ekenberg;
            else
                obj.alpha=obj.G.get_alpha_kane;
            end
            obj.nE=nEmax;
        end
        %% Wavevector calculation function
        function k = get_wavevector(obj,j,E)
            switch obj.solverType
                case 'Parabolic'
                    k=sqrt(2.0*obj.meff(j)/obj.consts.hbar^2*(obj.V(j)-E));
                case 'Taylor'
                    k=sqrt(2.0*obj.meff(j)/obj.consts.hbar^2*(obj.V(j)-E)/(1.0-obj.alpha(j)*(E-obj.V(j))));
                case 'Kane'
                    k=sqrt(2.0*obj.meff(j)*(1.0+obj.alpha(j)*(E-obj.V(j)))/obj.consts.hbar^2*(obj.V(j)-E));
                case 'Ekenberg'
                    k=sqrt(obj.meff(j)/(obj.consts.hbar^2*obj.alpha(j)) * (sqrt(1.0+4.0*obj.alpha(j)*(obj.V(j)-E))-1.0));
            end
        end 
        %% Wavevector derivative calculation function
        function dk = get_wavevector_derivative(obj,j,E)
            kj = obj.get_wavevector(j,E);
            switch obj.solverType
                case 'Parabolic'
                    dk = - obj.meff(j) / (kj * obj.consts.hbar^2);
                case 'Taylor'
                    dk = - obj.meff(j) / (kj * obj.consts.hbar^2) / power(1.0-obj.alpha(j)*(E-obj.V(j)),2);
                case 'Kane'
                    dk =  - obj.meff(j) / (kj * obj.consts.hbar^2) * (1.0 + 2.0*obj.alpha(j)*(E-obj.V(j)));
                case 'Ekenberg'
                    dk = -obj.meff(j)/(obj.consts.hbar^2*kj)/(1.0 + obj.consts.hbar^2*obj.alpha(j)/obj.meff(j)*kj*kj);
            end
        end 
        %% qpq coefficient calculation funciton
        function qpq = get_coefficient(obj,j,E)
            p = obj.get_wavevector(j-1,E);
            q = obj.get_wavevector(j,E);
            switch obj.solverType
                case 'Parabolic'
                    qpq = obj.meff(j) / obj.meff(j - 1) * p / q;
                case 'Taylor'
                    qpq = obj.meff(j) / obj.meff(j - 1) / (1.0-obj.alpha(j)*(E-obj.V(j))) * (1.0-obj.alpha(j-1)*(E-obj.V(j-1))) * p / q;
                case 'Kane'
                    qpq = obj.meff(j) / obj.meff(j - 1) * (1.0+obj.alpha(j)*(E-obj.V(j))) / (1.0+obj.alpha(j-1)*(E-obj.V(j-1))) * p / q;
                case 'Ekenberg'
                    qpq = (obj.meff(j) / obj.meff(j - 1) * (1.0+obj.consts.hbar^2*obj.alpha(j-1)/obj.meff(j-1)*p*p) / (1.0+obj.consts.hbar^2*obj.alpha(j)/obj.meff(j)*q*q)	) * p / q;
            end
        end 
        %% qpq derivative (dqpq) calculation function
        function dqpq = get_coefficient_derivative(obj,j,E)
            p = obj.get_wavevector(j-1,E);
            q = obj.get_wavevector(j,E);
            dp = obj.get_wavevector_derivative(j-1,E);
            dq = obj.get_wavevector_derivative(j,E);
            switch obj.solverType
                case 'Parabolic'
                    dqpq = obj.meff(j) / obj.meff(j - 1) * (q*dp-p*dq)/(q * q);
                case 'Taylor'
                    dqpq = obj.meff(j) / obj.meff(j-1) *(1.0-obj.alpha(j-1)*(E-obj.V(j-1))) / (1.0-obj.alpha(j)*(E-obj.V(j)))* (q*dp-p*dq)/(q * q) + p/q * (obj.alpha(j)*obj.meff(j)/power(1.0-obj.alpha(j)*(E-obj.V(j)),2) / obj.meff(j-1)*(1.0-obj.alpha(j-1)*(E-obj.V(j-1))) - obj.meff(j)/(1.0-obj.alpha(j)*(E-obj.V(j)))/obj.meff(j-1)*obj.alpha(j-1));
                case 'Kane'
                    dqpq = obj.meff(j) / obj.meff(j-1) * (1.0+obj.alpha(j)*(E-obj.V(j)))/(1.0+obj.alpha(j-1)*(E-obj.V(j-1)))* (q*dp-p*dq)/(q * q) + p/q * obj.meff(j)/obj.meff(j-1)*(obj.alpha(j) - obj.alpha(j-1) + obj.alpha(j)*obj.alpha(j-1)*(obj.V(j) - obj.V(j-1))) / (1.0+obj.alpha(j-1)*(E-obj.V(j-1))) / (1.0+obj.alpha(j-1)*(E-obj.V(j-1)));
	            case 'Ekenberg'
                    dqpq = obj.meff(j) / obj.meff(j - 1) / (q+obj.consts.hbar^2*obj.alpha(j)/obj.meff(j)*q*q*q) * ((1.0 + 3.0 * obj.consts.hbar^2*obj.alpha(j-1)/obj.meff(j-1)*p*p) * dp - (1.0+obj.consts.hbar^2*obj.alpha(j-1)/obj.meff(j-1)*p*p) / (1.0+obj.consts.hbar^2*obj.alpha(j)/obj.meff(j)*q*q) * p / q * (1.0 + 3.0 * obj.consts.hbar^2*obj.alpha(j)/obj.meff(j)*q*q)*dq);
            end
        end 
        %% Transfer matrix calculation at position j (corresponding to z-axis postion z(j))
        function Mj = get_matrix_j(obj,j,E)
            Mj = eye(2,2);
            if (j>1)
                p = obj.get_wavevector(j-1,E);
                q = obj.get_wavevector(j,E);
                qpq = obj.get_coefficient(j,E);
                zj = obj.G.get_zj(j);
                Mj(1,1)=0.5*(1+qpq)*exp((p-q)*zj);
                Mj(1,2)=0.5*(1-qpq)*exp(-(p+q)*zj);
                Mj(2,1)=0.5*(1-qpq)*exp((p+q)*zj);
                Mj(2,2)=0.5*(1+qpq)*exp(-(p-q)*zj);
            end 
        end
        %% First derivative of transfer matrix calculation at position j (corresponding to z-axis postion z(j))
        function dMj = get_matrix_derivative_j(obj,j,E)
            dMj = eye(2,2);
            if (j>1)
                p = obj.get_wavevector(j-1,E);
                q = obj.get_wavevector(j,E);
                dp = obj.get_wavevector_derivative(j-1,E);
                dq = obj.get_wavevector_derivative(j,E);
                qpq=obj.get_coefficient(j,E);
                dqpq=obj.get_coefficient_derivative(j,E);
                zj = obj.G.get_zj(j);
                dMj(1,1)= 0.5*( dqpq + (1.0+qpq)*zj*(dp-dq))*exp((p-q)*zj);
                dMj(1,2)= 0.5*(-dqpq - (1.0-qpq)*zj*(dp+dq))*exp(-(p+q)*zj);
                dMj(2,1)= 0.5*(-dqpq + (1.0-qpq)*zj*(dp+dq))*exp((p+q)*zj);
                dMj(2,2)= 0.5*( dqpq - (1.0+qpq)*zj*(dp-dq))*exp(-(p-q)*zj);
            end
        end 
        %% Left cumulative product of transfer matrices calculation function 
        function TM_left = get_left_TMM_cumulative_sum(obj,E)
            nz=obj.G.get_nz;
            TM_left = zeros(2,2,nz);
            TM_left(:,:,1)=eye(2,2);
            for j=2:nz
                Mj=obj.get_matrix_j(j,E);
                TM_left(:,:,j)=Mj*TM_left(:,:,j-1);
            end
        end 
        %% Right cumulative product of transfer matrices calculation function 
        function TM_right = get_right_TMM_cumulative_sum(obj,E)
            nz=obj.G.get_nz;
            TM_right = zeros(2,2,nz);
            TM_right(:,:,nz)=obj.get_matrix_j(nz,E);
            for j=nz-1:-1:2
                Mj=obj.get_matrix_j(j,E);
                TM_right(:,:,j)=TM_right(:,:,j+1)*Mj;
            end
            TM_right(:,:,1)=TM_right(:,:,2);
        end 
        %% m11 element of transfer matrix calculation function 
        function m11 = get_m11(obj,E)
            nz=obj.G.get_nz;
            TM = eye(2,2);
            for j=2:nz
                Mj=obj.get_matrix_j(j,E);
                TM=Mj*TM;
            end
            m11=abs(TM(1,1));
        end 
        %% m11 element derivative (dm11) of transfer matrix calculation function 
        function dm11 = get_m11_derivative(obj,E)
            dTM = zeros(2,2);
            TM_left = obj.get_left_TMM_cumulative_sum(E);
            TM_right = obj.get_right_TMM_cumulative_sum(E);
            nz=obj.G.get_nz;
            for j=2:nz-1
                dMj=obj.get_matrix_derivative_j(j,E);
                A=TM_right(:,:,j+1);
                B=TM_left(:,:,j-1);
                dTM=dTM+A*dMj*B;
            end
            dTM=dTM+obj.get_matrix_derivative_j(nz,E)*TM_left(:,:,nz-1);
            m11 = TM_left(1,1,nz);
            dTM11=dTM(1,1);
            dm11=1.0/abs(m11)*(real(dTM11)*real(m11)+imag(dTM11)*imag(m11));
        end 
        %% Wavefunction calculation function
        function psi = get_wavefunction(obj,E)
            nz=obj.G.get_nz;
            A1B1 = zeros(2,1); 
            A1B1(1)=1.0;
            psi=zeros(1,nz);
            psi(1)=1.0;
            for j=2:nz
                qjzj = obj.get_wavevector(j,E) * obj.G.get_zj(j);
                Mj=obj.get_matrix_j(j,E);
                A1B1 = Mj*A1B1;
                psi(j)=real(A1B1(1)*exp(qjzj)+A1B1(2)*exp(-qjzj));  
            end
            norm_const=sqrt(1/trapz(abs(psi).^2)/obj.G.get_dz*obj.consts.angstrom);
            psi=norm_const*psi;  
        end 
        %% Bisection function (required when finding zeros of dm11)
        function [Ex,i,fx]=bisect(obj,f,Elo,Ehi,tol)
            a=Elo;
            b=Ehi;
            fa=f(a);
            for i=1:100
                Ex=(a+b)/2;
                fx=f(Ex);
                if abs(fx)<tol
                    break;
                end
                if (fx*fa<0)
                    b=Ex;
                else
                    a=Ex;
                end
            end
        end
        %% Main solver function, calculates all solutions (up to nE limit) of Schrodinger equation for the given potential profile
        function [energies,psis]=get_wavefunctions(obj)
            found=0;
            energies=[];
            psis=[];
            dE=obj.G.get_dE;
            Emax=max(obj.V);
            E=min(obj.V)+3*dE;
            m11_km1=obj.get_m11(E-dE);
            m11_km2=obj.get_m11(E-2*dE);
            while E<Emax
                m11_k=obj.get_m11(E);
                if ((m11_k>m11_km1) && (m11_km1<m11_km2))
                    found=found+1;
                    Elo = E-2*dE;
			        Ehi = E;
                    f=@(E) obj.get_m11_derivative(E);
                    %Ex=obj.bisect(f,Elo,Ehi,1e-16);
                    options=optimset('TolX',1e-300);
                    Ex=fzero(f,[Elo Ehi],options);
                    psi = obj.get_wavefunction(Ex);
                    energies=[energies Ex];
                    psis=[psis; psi];
                end
                m11_km2=m11_km1;
			    m11_km1=m11_k;
                E=E+dE;
                if (obj.nE>0) && (found==obj.nE)
                    break;
                end
            end
        end
    end
end