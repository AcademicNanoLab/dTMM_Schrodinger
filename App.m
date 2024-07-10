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
        totalScreens = 3;
        screen = 1;
    end

    methods
        function obj = App
            fclose all;

            screen_size = get(0, 'ScreenSize');
            obj.x = mean( screen_size([1, 3]));         % app x-coordinate
            obj.y = mean( screen_size([2, 4]));         % app y-coordinate

            % draw the screen
            obj.app = uifigure();
            obj.app.Position = [obj.x - obj.app_w/2, obj.y - obj.app_h/2, obj.app_w, obj.app_h];
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

            % init title
            obj.title = uilabel(obj.grid);
            obj.title.Layout.Row = 1;
            obj.title.Layout.Column = 1;
            obj.title.Interpreter = "html";

            % init inner grid
            obj.innerGrid = uigridlayout(obj.grid);
            obj.innerGrid.Layout.Row = 2;
            obj.innerGrid.Layout.Column = 1;
            obj.innerGrid.BackgroundColor = obj.color;
            obj.innerGrid.Padding = [0,0,0,0];

            % init params dict
            obj.params = containers.Map();
            obj.params('Layer file') = pwd;
            obj.params('Material') = 'AlGaAs';
            obj.params('Solver') = 'TMM';
            obj.params('Non-parabolicity') = 'Parabolic';
            obj.params('K') = 1.9;
            obj.params('Nstmax') = 10;
            obj.params('dz') = 0.6;
            obj.params('Padding') = 400;

            % init screen
            obj.screen = 1;
        end

        function mainLayout(obj)
            titles = {'Set options', 'Create GIF', 'Complete'};
            obj.title.Text = strcat("<font style='font-size:20px; font-weight:bold; font-family:Helvetica, Verdana, Arial;'>",titles{obj.screen},"</font>");
            obj.app.Position = [obj.x - obj.app_w/2, obj.y - obj.app_h/2, obj.app_w, obj.app_h]; % TODO

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
                if (obj.screen < obj.totalScreens)
                    pButton.Text = 'Previous';
                else
                    pButton.Text = 'Restart';
                end
                pButton.ButtonPushedFcn = @(src, event) obj.prevButtonPressed();
            end

            % next button
            if (obj.screen <= obj.totalScreens)
                nButton = uibutton(buttonGrid);
                nButton.Layout.Row = 1;
                nButton.Layout.Column = 3;
                if (obj.screen < obj.totalScreens - 1)
                    nButton.Text = 'Next';
                elseif (obj.screen < obj.totalScreens)
                    nButton.Text = 'Finish';
                else
                    nButton.Text = 'Complete';
                end
                nButton.ButtonPushedFcn = @(src, event) obj.nextButtonPressed();
            end
        end

        function prevButtonPressed(obj)
            if (obj.screen < obj.totalScreens)
                obj.screen = obj.screen - 1;
            else
                obj.screen = 1;
            end
            obj.switchScreen();
        end

        function nextButtonPressed(obj)
            expression = '\w*.txt';
            if (isempty(regexp(obj.params('Layer file'),expression,'match')))
                errorFig = errordlg('You need to select a layer file', 'File error','modal');
                uiwait;
                figure(obj.app);
            else
                obj.screen = obj.screen + 1;
                obj.switchScreen();
            end
        end

        function switchScreen(obj)
            obj.innerGrid.Children.delete;
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
                case 4
                    close(obj.app);
            end
        end

        function step1(obj)
            obj.mainLayout();
            rowHeight = 22;
            obj.innerGrid.RowHeight = {rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight};
            obj.innerGrid.ColumnWidth = {'fit','1x',100};

            obj.labeledInputArea('Layer file', 1, 'fileSelector');
            obj.labeledInputArea('Material', 2, 'dropdown', obj.params('Material'));
            obj.labeledInputArea('Solver', 3, 'radio');
            obj.labeledInputArea('Non-parabolicity', 4, 'dropdown', obj.params('Non-parabolicity'));
            obj.labeledInputArea('K',       5, 'numberInput', obj.params('K'),      [0,5],      0.05,   '%.2f kV/cm');
            obj.labeledInputArea('Nstmax',  6, 'numberInput', obj.params('Nstmax'), [0,20],     1,      '%.0f');
            obj.labeledInputArea('dz',      7, 'numberInput', obj.params('dz'),     [0,5],      0.1,    '%.1f angstroms');
            obj.labeledInputArea('Padding', 8, 'numberInput', obj.params('Padding'),[100,400],  25,     '%.0f angstroms');
        end

        function step2(obj)
            obj.mainLayout();
        end

        function step3(obj)    
            % get the layout
            obj.mainLayout();
            big_w = obj.app_w;
            big_h = obj.app_h * 1.5;
            % obj.innerGrid.RowHeight = {(big_h-60)/2,(big_h-60)/2};
            % obj.innerGrid.ColumnWidth = {(big_w-30)/2,(big_w-30)/2};
            obj.innerGrid.RowHeight = {'fit','fit'};
            obj.innerGrid.ColumnWidth = {'fit','fit'};
            obj.app.Position = [obj.x - big_w/2, obj.y - big_h/2, big_w, big_h];
            allPlots = gobjects(2, 2);
            for r = 1:2
                for c = 1:2
                    curPlot = uipanel(obj.innerGrid);
                    curPlot.Layout.Row = r;
                    curPlot.Layout.Column = c;
                    curPlot.BackgroundColor = obj.color;
                    curPlot.BorderType = 'none';
                    allPlots(r, c) = curPlot;
                end
            end

            progressBar = waitbar(0,'Please Wait...');
            progressBar.Name = 'Loading figures';

            % MAIN CODE!!
            G=Grid(obj.params('Layer file'),obj.params('dz'),obj.params('Material'));
            G.set_K(obj.params('K'));
            waitbar(1/6,progressBar);

            if (obj.params('Solver') == "FDM")
                Solver=FDMSolver(obj.params('Non-parabolicity'),G,obj.params('Nstmax'));
            else
                Solver=TMMSolver(obj.params('Non-parabolicity'),G,obj.params('Nstmax'));
            end
            waitbar(2/6,progressBar);

            [energies,psis]=Solver.get_wavefunctions;
            % energies_meV = energies / (G.consts.e);
            V=Visualization(G,energies,psis);
            V.plot_V_wf(allPlots(1,1));
            waitbar(3/6,progressBar);
            V.plot_energies(allPlots(1,2));
            waitbar(4/6,progressBar);
            V.plot_energy_difference_in_terahertz(allPlots(2,1));
            waitbar(5/6,progressBar);
            V.plot_QCL(allPlots(2,2),obj.params('K'),obj.params('Padding'));
            waitbar(1,progressBar);
            pause(1);
            close(progressBar);

            % completed
            figure(obj.app);
            % completeText = uilabel(obj.innerGrid);
            % completeText.Layout.Row = 1;
            % completeText.Layout.Column = 1;
            % completeText.Text = 'The figures have been created. {Would you like to restart the wizard?}';
        end


        function labeledInputArea(obj, titleText, row, type, varargin)
            dTitle = uilabel(obj.innerGrid);
            dTitle.Layout.Row = row;
            dTitle.Layout.Column = 1;
            dTitle.Text = titleText;

            switch type
                case 'dropdown'
                    obj.dropdown(titleText, row, varargin);
                case 'fileSelector'
                    obj.fileSelector(titleText, row);
                case 'numberInput'
                    obj.numberInput(titleText, row, varargin{1}, varargin{2}, varargin{3}, varargin{4});
                case 'radio'
                    obj.radioInput(titleText, row);
            end
        end

        function dropdown(obj, titleText, row, initVal)
            dOptions = {};
            switch titleText
                case 'Material'
                    dOptions = {'AlGaAs','AlGaSb','InGaAs/InAlAs','InGaAs/GaAsSb'};
                case 'Non-parabolicity'
                    if (obj.params('Solver') == "FDM")
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
            dDropdown.Value = initVal;
            obj.params(titleText) = dDropdown.Value;

            % callback function upon value change
            dDropdown.ValueChangedFcn = @(src, event) obj.dropdownValueChanged(src, titleText);
        end

        function dropdownValueChanged(obj, src, titleText)
            obj.params(titleText) = src.Value;
        end

        function fileSelector(obj, titleText, row)
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

        function numberInput(obj, titleText, row, initVal, limits, step, valueDisplayFormat)
            % input number
            numericInput = uispinner(obj.innerGrid);
            numericInput.Layout.Row = row;
            numericInput.Layout.Column = 2;
            numericInput.Value = obj.params(titleText);

            % parameters dependent on which item it is
            numericInput.Limits = limits;
            numericInput.Step = step;
            numericInput.ValueDisplayFormat = valueDisplayFormat;

            numericInput.ValueChangedFcn = @(src, event) obj.numericInputValueChanged(event, titleText);
        end

        function numericInputValueChanged(obj, event, titleText)
            obj.params(titleText) = event.Value;
        end

        function radioInput(obj, titleText, row)
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
            if (obj.params('Non-parabolicity') == "Ekenberg")
                obj.labeledInputArea('Non-parabolicity', 4, 'dropdown', 'Parabolic');
            else
                obj.labeledInputArea('Non-parabolicity', 4, 'dropdown', obj.params('Non-parabolicity'));
            end
        end
    end
end