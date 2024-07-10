% TODO: adjust the parameters as needed
classdef GUI_Var < handle
    properties
        setupParams
    end

    methods
        function obj = GUI_Var
            obj.setupParams = containers.Map();
            % file selector - init
            obj.setupParams('Layer file') = {1,'fileSelector','/Users/hyuna/Desktop/dTMM_Schrodinger/test/Structure1_BTC_GaAs_AlGaAs.txt'};
            % obj.setupParams('Layer file') = {1,'fileSelector',pwd};
            % dropdown, radio - init, options
            obj.setupParams('Material') = {2,'dropdown','AlGaAs',{'AlGaAs','AlGaSb','InGaAs/InAlAs','InGaAs/GaAsSb'}};
            obj.setupParams('Solver') = {3,'radio','TMM',{'TMM','FDM'}};
            % dependent dropdown - init, dependency, options per
            % independent variable
            dependentOptions = containers.Map();
            dependentOptions('TMM') = {'Parabolic','Taylor','Kane','Ekenberg'};
            dependentOptions('FDM') = {'Parabolic','Taylor','Kane'};
            obj.setupParams('Non-parabolicity') = {4,'depDropdown','Parabolic','Solver',dependentOptions};
            % range - init, start, end, step, min-max, step (for slider),
            % units
            obj.setupParams('K_range')  = {5,'rangeNumberInput', 1, 1.5, 0.5, [0,5], 0.05, '%.2f kV/cm', [0,5], 0.05};
            % obj.setupParams('K_range')  = {5,'rangeNumberInput', 1, 3, 0.1, [0,5], 0.05, '%.2f kV/cm', [0,5], 0.05};
            % numerical - init, min-max, step, units
            obj.setupParams('K')        = {5,'numberInput', 1.9, [0,5],      0.05,   '%.2f kV/cm'};
            obj.setupParams('Nstmax')   = {6,'numberInput', 10,  [0,20],     1,      '%.0f'};
            obj.setupParams('dz')       = {7,'numberInput', 0.6, [0.5,5],    0.1,    '%.1f angstroms'};
            obj.setupParams('Padding')  = {8,'numberInput', 400, [100,400],  25,     '%.0f angstroms'};
            % axis limits
            obj.setupParams('Axis limits')  = {9,'axisLimitInput', [0 2000 0 120],  25};
        end
    end
end