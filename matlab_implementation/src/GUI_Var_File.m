% TODO: adjust the parameters as needed
classdef GUI_Var_File < handle
    properties
        setupParams
    end

    methods
        function obj = GUI_Var_File
            obj.setupParams = containers.Map();
            obj.setupParams('Directory') = {1,'fileSelector',pwd,'dir'};
            obj.setupParams('File name') = {2,'text','dTMM_file'};
            obj.setupParams('Save as') = {3,'radio','Default (PNG/MP4)',{'Default (PNG/MP4)','MATLAB Figures'}};
        end
    end
end