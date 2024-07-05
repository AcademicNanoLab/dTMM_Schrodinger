classdef App < handle

    properties
        app                             % app window
        app_w = 600;
        app_h = 400;
        color = [0.6 0.8 1];
        x
        y
        params
    end

    properties (Hidden)
        grid
        innerGrid
        title
    end

    methods
        function obj = App
            screen_size = get(0, 'ScreenSize');
            x = mean( screen_size([1, 3]));         % app x-coordinate
            y = mean( screen_size([2, 4]));         % app y-coordinate

            % draw the screen
            obj.app = uifigure();
            obj.app.Position = [x - obj.app_w/2, y - obj.app_h/2, obj.app_w, obj.app_h];
            obj.app.MenuBar = 'none';
            obj.app.Name = 'dTMM Wizard';

            % draw the grid
            obj.grid = uigridlayout(obj.app);
            obj.grid.BackgroundColor = obj.color;
            obj.grid.RowHeight = {'fit','1x',22};
            obj.grid.ColumnWidth = {'1x'};

            obj.title = uilabel(obj.grid);
            obj.title.Layout.Row = 1;
            obj.title.Layout.Column = 1;
            obj.title.Interpreter = "html";
            
            % init params dict
            obj.params = containers.Map();
        end

        function mainLayout(obj, screen)
            titles = {'Set options', 'Create GIF', 'Loading'};
            obj.title.Text = strcat("<font style='font-size:24px; font-weight:bold; font-family:Helvetica, Verdana, Arial;'>",titles{screen},"</font>");
        end

        function step1(obj)
            obj.mainLayout(1);

            obj.innerGrid = uigridlayout(obj.grid);
            obj.innerGrid.Layout.Row = 2;
            obj.innerGrid.Layout.Column = 1;
            obj.innerGrid.BackgroundColor = obj.color;
            obj.innerGrid.RowHeight = {'fit','fit','fit','fit','fit','fit','fit','fit'};
            obj.innerGrid.ColumnWidth = {'fit','1x',40};

            solver = "FDM";
            obj.dropdown('Material', 2, solver)
            obj.dropdown('Non-parabolicity', 6, solver)
        end

        function inputArea(obj, titleText, row, type, solver)

        end

        function dropdown(obj, titleText, row, solver)
            dTitle = uilabel(obj.innerGrid);
            dTitle.Layout.Row = row;
            dTitle.Layout.Column = 1;
            dTitle.Text = titleText;

            dOptions = {};
            switch titleText
                case 'Material'
                    dOptions = {'AlGaAs','AlGaSb','InGaAs/InAlAs','InGaAs/GaAsSb'};
                case 'Non-parabolicity'
                    if (solver == "FDM")
                        dOptions = {'Parabolic','Taylor','Kane'};
                    else
                        dOptions = {'Parabolic','Taylor','Kane','Ekenberg'};
                    end
            end
            dDropdown = uidropdown(obj.innerGrid);
            dDropdown.Layout.Row = row;
            dDropdown.Layout.Column = 2;
            dDropdown.Items = dOptions;

            % initialize value
            obj.params(titleText) = dDropdown.Value;
            fprintf(obj.params(titleText));

            % callback function upon value change
            dDropdown.ValueChangedFcn = @(src, event) obj.dropdownValueChanged(src, titleText);
        end

        function dropdownValueChanged(obj, src, titleText)
            obj.params(titleText) = src.Value;
            fprintf(obj.params(titleText));
        end

         
    end
end

% % Layer file
% % [file,location] = uigetfile('*.txt');
%
%
% end
%
% step0();