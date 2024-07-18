%author Aleksandar Demic
%
% Schrodinger equation solver class using dTMM method

classdef FDMSolver < handle
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
        function obj = FDMSolver(solverType,Grid,nEmax)
            obj.solverType=solverType;
            obj.G=Grid;
            obj.V=obj.G.get_bandstructure_potential;
            obj.meff=obj.G.get_effective_mass;
            obj.consts=ConstAndScales;
            obj.alpha=obj.G.get_alpha_kane;
            obj.nE=nEmax;
        end
        function A = construct_system_matrix(obj)
            switch obj.solverType
                case 'Parabolic'
                    A=obj.construct_parabolic_matrix();
                case 'Kane'
                    A=obj.construct_Kane_matrix();
                case 'Taylor'
                    A=obj.construct_Taylor_matrix();
            end
        end 
        function A = construct_parabolic_matrix(obj)
            nz=obj.G.get_nz;
            A = zeros(nz,nz);
            scale = (obj.consts.hbar/obj.G.get_dz)^2/4.0;
            for i=1:nz
                if (i~=1)
                    A(i,i-1) =  -scale * (1.0/obj.meff(i-1)+1.0/obj.meff(i));
                end
                if (i~=nz)
                    A(i,i+1) =  -scale * (1.0/obj.meff(i+1)+1.0/obj.meff(i));
                end
                if ((i~=1) && (i~=nz))
                    A(i,i) = obj.V(i) + scale * (1.0/obj.meff(i+1) + 2.0/obj.meff(i) + 1.0/obj.meff(i-1));
                end
            end
		    A(1,1)=A(2,2);
		    A(nz,nz)=A(nz-1,nz-1);
        end 
        function A = construct_Kane_matrix(obj)
            nz=obj.G.get_nz;
            A = zeros(4*nz,4*nz);
            scale = power(obj.consts.hbar/obj.G.get_dz,2)/4.0;
            for i=1:nz			
			    A_i = 1.0/ obj.alpha(i);
			    M_i = A_i / obj.meff(i);
			    V_i = obj.V(i);
                if ((i==1) || (i==nz))
                    A_plus = 1.0/obj.alpha(i);
				    A_minus = A_plus;
                    M_plus = A_minus/obj.meff(i);
				    M_minus = M_plus;
                    V_plus = obj.V(i);
				    V_minus = V_plus;
			    else
				    A_minus = 1.0/obj.alpha(i-1);
				    A_plus =  1.0/obj.alpha(i+1);
				    M_minus = A_minus/obj.meff(i-1);
				    M_plus = A_plus/obj.meff(i+1);
				    V_minus = obj.V(i-1);
				    V_plus = obj.V(i+1);
                end
			    B_minus =  A_minus*A_i;
			    B_0 = A_minus*A_plus;
			    B_plus = A_plus*A_i;
			
			    % Add subdiagonals of A0, A1 and A2
                if (i~=1)
				    A(3*nz+i,i-1) =	-scale * (1.0-V_plus/A_plus)*(M_minus*B_plus*(1.0 - V_i/A_i) + M_i*B_0*(1.0-V_minus/A_minus)); 	% A0
				    A(3*nz+i,nz+i-1) = -scale * (M_i*(A_minus+A_plus-V_minus-V_plus)+M_minus*(A_plus+A_i-V_i-V_plus));				% A1
				    A(3*nz+i,2*nz+i-1) = -scale * (M_minus+M_i);																	% A2
                end
			    % Add superdiagonals of A0, A1 and A2
                if (i~=nz)
				    A(3*nz+i,i+1) = -scale * (1.0-V_minus/A_minus)*(M_plus*B_minus*(1.0 - V_i/A_i) + M_i*B_0*(1.0-V_plus/A_plus));  	% A0
				    A(3*nz+i,nz+i+1) =  -scale * (M_i*(A_minus+A_plus-V_minus-V_plus)+M_plus*(A_minus+A_i-V_i-V_minus));				% A1
				    A(3*nz+i,2*nz+i+1) = -scale * (M_plus+M_i); 																		% A2
                end
			    % Add diagonal of A0 block
			    A(3*nz+i,i) = -scale * (V_i * (M_plus*A_minus+M_minus*A_plus) + V_minus * (M_plus*A_i+2.0*M_i*A_plus) + V_plus * (M_minus*A_i+2.0*M_i*A_minus) - M_plus*V_i*V_minus - M_minus*V_i*V_plus - 2.0*M_i*V_plus*V_minus - M_plus*B_minus - 2.0*M_i*B_0 - M_minus*B_plus) + V_i * (1.0-V_i/A_i) * (A_i*B_0 - B_plus*V_minus - B_minus*V_plus + A_i*V_minus*V_plus);
			    % Add diagonal of A1 block
			    A(3*nz+i,nz+i) = -scale * (M_plus*(V_i+V_minus-A_i-A_minus) + M_minus*(V_i+V_plus-A_i-A_plus) + 2.0*M_i*(V_minus+V_plus-A_minus-A_plus)) - V_i*V_i*(A_plus+A_minus) + V_i * (B_minus+2.0*B_0+B_plus) + V_minus*B_plus + V_plus*B_minus - V_i*V_minus*(2.0*A_plus+A_i) - V_i*V_plus*(2.0*A_minus+A_i) - A_i*V_minus*V_plus + V_i*V_i*(V_minus+V_plus) + 2.0*V_i*V_minus*V_plus - A_i*B_0;
			    % Add diagonal of A2 block
			    A(3*nz+i,2*nz+i) = scale * (M_plus+2.0*M_i+M_minus) - B_plus - B_0 - B_minus + A_plus*(2.0*V_i+V_minus) + A_minus*(2.0*V_i+V_plus) + A_i*(V_i+V_minus+V_plus) - V_i*V_i - 2.0*V_i*(V_minus+V_plus) - V_minus*V_plus;
			    % Add diagonal of A3 block
			    A(3*nz+i,3*nz+i) = V_plus+2.0*V_i+V_minus-A_plus-A_i-A_minus;
			    % Insert identity matrices
			    A(i,nz+i) = 1.0;
			    A(nz+i,2*nz+i) = 1.0;
			    A(2*nz+i,3*nz+i) = 1.0;
            end
        end 
        function A = construct_Taylor_matrix(obj)
            nz=obj.G.get_nz;
            A = zeros(nz,nz);
		    B = A;	
            scale = power(obj.consts.hbar/obj.G.get_dz,2)/4.0;
            for i=1:nz
			    if (i~=1)
				    B(i,i-1) = - scale * (obj.alpha(i) / obj.meff(i) + obj.alpha(i-1) / obj.meff(i-1));
				    A(i,i-1) =  -scale * ((1.0+obj.alpha(i-1)*obj.V(i-1))/obj.meff(i-1)+(1.0+obj.alpha(i)*obj.V(i))/obj.meff(i));
			    end
			    if (i~=nz)
				    B(i,i+1) = - scale * (obj.alpha(i) / obj.meff(i) + obj.alpha(i+1) / obj.meff(i+1) );
				    A(i,i+1) =  -scale * ((1.0+obj.alpha(i+1)*obj.V(i+1))/obj.meff(i+1)+(1.0+obj.alpha(i)*obj.V(i))/obj.meff(i));
			    end
			    if ((i~=1) && (i~=nz))
				    B(i,i) = 1.0 + scale * (obj.alpha(i+1) / obj.meff(i+1) + 2.0 * obj.alpha(i) / obj.meff(i) + obj.alpha(i-1) / obj.meff(i-1));
				    A(i,i) = obj.V(i) + scale * ((1.0+obj.alpha(i+1)*obj.V(i+1))/obj.meff(i+1) + 2.0 * (1.0+obj.alpha(i)*obj.V(i))/obj.meff(i) + (1.0+obj.alpha(i-1)*obj.V(i-1))/obj.meff(i-1));
			    end
            end
		    A(1,1)=A(2,2);
		    A(nz,nz)=A(nz-1,nz-1);
		    B(1,1)=B(2,2);
		    B(nz,nz)=B(nz-1,nz-1);
		    B = inv(B);
		    A = B*A;		
        end  
        function Eid=sort_and_filter_eigenvalues(obj,eigenvalues)
            Vmin = min(obj.V);
		    Vmax = max(obj.V);
		    %  We store how many eigenvalues in Vmin-Vmax we can find	   
            Efound=[];
		    iEfound=[];
            for i=1:length(eigenvalues)
		        Er = real(eigenvalues(i));
                if ( (Er > Vmin) && (Er < Vmax))
				    iEfound = [iEfound i];
				    Efound = [Efound Er];
                end
            end
		    % 	We sort found energies and calculate their indices in the unsorted Efound array
		    [~,indices] = sort(Efound);
		    %	We return iEfound(indices) - These are indicies in the eigval array that correspond to sorted eigenvalues in Vmin-Vmax range
		    Eid=iEfound(indices);
        end
        function [energies,psis]=get_wavefunctions(obj)
            psis=[];
            energies=[];
		    A = obj.construct_system_matrix();
		    [eigenvectors,eigenvalues] = eig(A);
            eigvals=diag(eigenvalues);
            Eid=obj.sort_and_filter_eigenvalues(eigvals);

		    nz=obj.G.get_nz();
            nE=obj.nE;
            if (nE<=0) || (nE>length(Eid))
                nE=length(Eid);
            end
		    for i=1:nE
                E=real(eigvals(Eid(i)));
		        energies=[energies E];
			    psiWhole = real(eigenvectors(:,Eid(i)));
			    psi = psiWhole(1:nz);
                norm_const=sqrt(1/trapz(abs(psi).^2)/obj.G.get_dz*obj.consts.angstrom);
                psi=norm_const*psi;  
                psis=[psis; psi'];
            end
        end
    end
end
