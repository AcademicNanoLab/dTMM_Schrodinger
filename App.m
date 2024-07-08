classdef App < handle

    properties
        app                             % app window
        app_w = 600;
        app_h = 400;
        color = [0.6 0.8 1];
        x
        y
        params
        defaultNumericalParams
        totalScreens = 3;
    end

    properties (Hidden)
        grid
        innerGrid
        title
        screen
    end

    methods
        function obj = App
            fclose all;
            
            screen_size = get(0, 'ScreenSize');
            x = mean( screen_size([1, 3]));         % app x-coordinate
            y = mean( screen_size([2, 4]));         % app y-coordinate

            % draw the screen
            obj.app = uifigure();
            obj.app.Position = [x - obj.app_w/2, y - obj.app_h/2, obj.app_w, obj.app_h];
            obj.app.MenuBar = 'none';
            obj.app.Name = 'dTMM Wizard';
            obj.app.Color = obj.color;

            % add padding
            mainPanel = uipanel(obj.app);
            mainPanel.BorderType = 'none';
            padding = 20;
            mainPanel.Position = [padding, padding, obj.app_w - 2*padding, obj.app_h - 2*padding];

            % draw the grid
            obj.grid = uigridlayout(mainPanel);
            obj.grid.BackgroundColor = obj.color;
            obj.grid.RowHeight = {'fit','1x',22};
            obj.grid.ColumnWidth = {'1x'};

            obj.title = uilabel(obj.grid);
            obj.title.Layout.Row = 1;
            obj.title.Layout.Column = 1;
            obj.title.Interpreter = "html";

            % init params dict
            obj.params = containers.Map();
            obj.defaultNumericalParams = containers.Map();

            % init screen
            obj.screen = 1;
        end

        function mainLayout(obj)
            titles = {'Set options', 'Create GIF', 'Loading'};
            obj.title.Text = strcat("<font style='font-size:20px; font-weight:bold; font-family:Helvetica, Verdana, Arial;'>",titles{obj.screen},"</font>");

            % init inner grid
            obj.innerGrid = uigridlayout(obj.grid);
            obj.innerGrid.Layout.Row = 2;
            obj.innerGrid.Layout.Column = 1;
            obj.innerGrid.BackgroundColor = obj.color;

            % button grid
            buttonGrid = uigridlayout(obj.grid);
            buttonGrid.Layout.Row = 3;
            buttonGrid.Layout.Column = 1;
            buttonGrid.BackgroundColor = obj.color;
            buttonGrid.Padding = [0,0,0,0];
            buttonGrid.RowHeight = {22};
            buttonGrid.ColumnWidth = {'1x',100,100};
            
            % prev button
            if (obj.screen > 1)
                pButton = uibutton(buttonGrid);
                pButton.Layout.Row = 1;
                pButton.Layout.Column = 2;
                pButton.Text = 'Previous';
                pButton.ButtonPushedFcn = @(src, event) obj.prevButtonPressed();
            end

            % next button
            nButton = uibutton(buttonGrid);
            nButton.Layout.Row = 1;
            nButton.Layout.Column = 3;
            if (obj.screen < obj.totalScreens)
                nButton.Text = 'Next';
            else
                nButton.Text = 'Finish';
            end
            nButton.ButtonPushedFcn = @(src, event) obj.nextButtonPressed();
        end

        function prevButtonPressed(obj)
            if (obj.screen > 1)
                obj.screen = obj.screen - 1;
                obj.switchScreen();
            end
        end

        function nextButtonPressed(obj)
            if (obj.screen < obj.totalScreens)
                obj.screen = obj.screen + 1;
                obj.switchScreen();
            else
                % MAIN CODE!!
            obj.labeledInputArea('Layer file', 1, 'fileSelector');
            obj.labeledInputArea('Material', 2, 'dropdown', solver);
            obj.labeledInputArea('Solver', 3, 'radio', 'row');
            obj.labeledInputArea('Non-parabolicity', 4, 'dropdown');
            obj.labeledInputArea('K', 5, 'numberInput', solver);
            obj.labeledInputArea('Nstmax', 6, 'numberInput', solver);
            obj.labeledInputArea('dz', 7, 'numberInput', solver);

                G=Grid(obj.params('Layer file'),obj.params('dz'),obj.params('Material'));
                G.set_K(obj.params('K'));

                if (obj.params('Solver') == "FDM")
                    Solver=FDMSolver(obj.params('Non-parabolicity'),G,obj.params('Nstmax'));
                else
                    Solver=TMMSolver(nonparabolicityType,G,nstmax);
                end

                [energies,psis]=Solver.get_wavefunctions;
                energies_meV = energies / (G.consts.e);
                V=Visualization(G,energies,psis);
                V.plot_V_wf;
                V.plot_energies;
                V.plot_energy_difference_in_terahertz;
                V.plot_QCL(K,padding);
            end
        end

        function switchScreen(obj)
            switch (obj.screen)
                case 1
                    fprintf("1");
                    obj.step1();
                case 2
                    fprintf("2");
                    obj.step2();
                case 3
                    fprintf("3");
                    obj.step3();
            end
        end

        function step1(obj)
            obj.mainLayout();
            rowHeight = 22;
            obj.innerGrid.RowHeight = {rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight};
            obj.innerGrid.ColumnWidth = {'fit','1x',100};

            solver = "FDM";
            obj.labeledInputArea('Layer file', 1, 'fileSelector');
            obj.labeledInputArea('Material', 2, 'dropdown');
            obj.labeledInputArea('Solver', 3, 'radio', 'row');
            obj.labeledInputArea('Non-parabolicity', 4, 'dropdown',solver);
            obj.labeledInputArea('K', 5, 'numberInput');
            obj.labeledInputArea('Nstmax', 6, 'numberInput');
            obj.labeledInputArea('dz', 7, 'numberInput');
        end

        function step2(obj)
            obj.mainLayout();
            
        end

        function step3(obj)
            obj.mainLayout();
        end


        function labeledInputArea(obj, titleText, row, type, varargin)
            dTitle = uilabel(obj.innerGrid);
            dTitle.Layout.Row = row;
            dTitle.Layout.Column = 1;
            dTitle.Text = titleText;

            switch type
                case 'dropdown'
                    if (nargin == 5)
                        obj.dropdown(titleText, row, varargin{1});
                    else
                        obj.dropdown(titleText, row);
                    end
                case 'fileSelector'
                    obj.fileSelector(titleText, row);
                case 'numberInput'
                    obj.numberInput(titleText, row);
                case 'radio'
                    obj.radioInput(titleText, row);
            end
        end

        function dropdown(obj, titleText, row, varargin)
            dOptions = {};
            switch titleText
                case 'Material'
                    dOptions = {'AlGaAs','AlGaSb','InGaAs/InAlAs','InGaAs/GaAsSb'};
                case 'Non-parabolicity'
                    if (nargin == 4 && varargin{1} == "FDM")
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

            % callback function upon value change
            dDropdown.ValueChangedFcn = @(src, event) obj.dropdownValueChanged(src, titleText);
        end

        function dropdownValueChanged(obj, src, titleText)
            obj.params(titleText) = src.Value;
        end

        function fileSelector(obj, titleText, row)
            % initialize value
            obj.params(titleText) = pwd;

            fTextBox = uitextarea(obj.innerGrid);
            fTextBox.Layout.Row = row;
            fTextBox.Layout.Column = 2;
            fTextBox.Value = obj.params(titleText);
            fTextBox.Editable = 'off';
            fTextBox.WordWrap = 'off';

            % button
            fButton = uibutton(obj.innerGrid);
            fButton.Layout.Row = row;
            fButton.Layout.Column = 3;
            fButton.Text = 'Browse';

            % callback function upon button press
            fButton.ButtonPushedFcn = @(src, event) obj.fileButtonPressed(src, titleText, fTextBox);
        end

        function fileButtonPressed(obj, ~, titleText, fTextBox)
            obj.app.Visible = 'off';
            [file,location] = uigetfile('*.txt');
            obj.app.Visible = 'on';
            if file ~= 0
                obj.params(titleText) = strcat(location,file);
                fTextBox.Value = obj.params(titleText);
            end
        end

        function numberInput(obj, titleText, row)
            % initialize value
            obj.params(titleText) = 1;

            % input number
            numericInput = uispinner(obj.innerGrid);
            numericInput.Layout.Row = row;
            numericInput.Layout.Column = 2;
            numericInput.Value = obj.params(titleText);

            % parameters dependent on which item it is
            switch titleText
                case 'K'
                    numericInput.Limits = [0,5];
                    numericInput.Step = 0.05;
                    numericInput.ValueDisplayFormat = '%.2f kV/cm';
                case 'Nstmax'
                    numericInput.Limits = [0,20];
                    numericInput.Step = 1;
                    numericInput.ValueDisplayFormat = '%.0f';
                case 'dz'
                    numericInput.Limits = [0,5];
                    numericInput.Step = 0.1;
                    numericInput.ValueDisplayFormat = '%.1f angstroms';
            end

            numericInput.ValueChangedFcn = @(src, event) obj.numericInputValueChanged(event, titleText);

            % % internal grid
            % g = uigridlayout(obj.innerGrid, [1, 3]);
            % g.BackgroundColor = obj.color;
            % g.Padding = [0,0,0,0];
            % g.Layout.Row = row;
            % g.Layout.Column = 2;
            % g.ColumnWidth = {'1x',30,30};
            % 
            % % number input area
            % numericInput = uieditfield(g, 'numeric');
            % numericInput.Layout.Column = 1;
            % numericInput.Value = obj.params(titleText);
            % 
            % % buttons
            % plusButton = uibutton(g);
            % plusButton.Layout.Column = 2;
            % plusButton.Text = '+';
            % 
            % minusButton = uibutton(g);
            % minusButton.Layout.Column = 3;
            % minusButton.Text = '-';
        end

        function numericInputValueChanged(obj, event, titleText)
            obj.params(titleText) = event.Value;
        end

        function radioInput(obj, titleText, row)
            % initialize value
            obj.params(titleText) = "TMM";

            % button group
            bg = uibuttongroup(obj.innerGrid);
            bg.BackgroundColor = obj.color;
            % bg.Padding = [0,0,0,0]; % TODO
            bg.BorderType = "none";
            bg.Layout.Row = row;
            bg.Layout.Column = 2;

            % individual buttons
            rb1 = uiradiobutton(bg);
            rb2 = uiradiobutton(bg);
            rb1.Text = 'TMM';
            rb2.Text = 'FDM';
            rb1.Position = [5 5 91 15];
            rb2.Position = [100 5 91 15];

            % callback function upon radio button press
            bg.SelectionChangedFcn = @(src, event) obj.radioInputPressed(event, titleText);
        end

        function radioInputPressed(obj, event, titleText)
            obj.params(titleText) = event.NewValue.Text;
        end
    end
end