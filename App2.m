classdef App2 < handle
    properties
        app                             % app window
        GUI_Form
        imageType
        generateFigures=0               % default is don't generate figures
    end

    properties (Hidden)
        grid
        titles={'Choose your task','Set options', 'What to generate', 'Complete'};
        title
        innerGrid
        buttonGrid
        pButton
        nButton
        x
        y
        app_w = 600;
        app_h = 500;
        screen = 1;
        totalScreens = 4;
        color = [0 0.4470 0.7410];
    end

    methods
        function obj = App2
            fclose all;
            clc;

            % get screen coordinates
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

            % init button grid
            obj.buttonGrid = uigridlayout(obj.grid);
            obj.buttonGrid.Layout.Row = 3;
            obj.buttonGrid.Layout.Column = 1;
            obj.buttonGrid.BackgroundColor = obj.color;
            obj.buttonGrid.Padding = [0,0,0,0];
            obj.buttonGrid.RowHeight = {22};
            obj.buttonGrid.ColumnWidth = {'1x',100,100};

            % init buttons
            obj.pButton = uibutton(obj.buttonGrid);
            obj.pButton.Layout.Row = 1;
            obj.pButton.Layout.Column = 2;
            obj.pButton.ButtonPushedFcn = @(src, event) obj.pButtonPressed();
            obj.nButton = uibutton(obj.buttonGrid);
            obj.nButton.Layout.Row = 1;
            obj.nButton.Layout.Column = 3;
            obj.nButton.ButtonPushedFcn = @(src, event) obj.nButtonPressed();

            % init Form object
            obj.GUI_Form = GUI_Form(obj.app,obj.innerGrid,1,2);

            % init screen
            obj.switchScreen();
        end

        function pButtonPressed(obj)
            if (obj.screen < obj.totalScreens)
                obj.screen = obj.screen - 1;
            else
                obj.screen = 1;
            end
            obj.switchScreen();
        end

        function nButtonPressed(obj)
            expression = '\w*.txt';
            if (isempty(regexp(obj.GUI_Form.params('Layer file'),expression,'match')))
                errorFig = errordlg('You need to select a layer file', 'File error','modal');
                uiwait;
                figure(obj.app);
            else
                obj.screen = obj.screen + 1;
                obj.switchScreen();
            end
        end

        function switchScreen(obj)
            obj.mainLayout();
            switch (obj.screen)
                case 1
                    obj.step1();
                case 2
                    obj.step2();
                case obj.totalScreens + 1
                    close(obj.app);
                case 3
                    obj.step3();
                case 4
                    if strcmp(obj.imageType,'GIF')
                        obj.step4_GIF();
                    else
                    end
            end
        end

        function mainLayout(obj)
            obj.title.Text = strcat("<font style='font-size:20px; font-weight:bold; font-family:Helvetica, Verdana, Arial;'>",obj.titles{obj.screen},"</font>");
            obj.innerGrid.Children.delete;

            % button text
            obj.pButton.Visible = 'on';
            obj.nButton.Visible = 'on';
            switch (obj.screen)
                case 1
                    obj.pButton.Visible = 'off';
                    obj.nButton.Visible = 'off';
                    % case 2
                    % obj.pButton.Visible = 'off';
                    % obj.nButton.Text = 'Next';
                case obj.totalScreens
                    obj.pButton.Text = 'Restart';
                    obj.nButton.Text = 'Complete';
                case obj.totalScreens - 1
                    obj.pButton.Text = 'Previous';
                    obj.nButton.Text = 'Finish';
                otherwise
                    obj.pButton.Text = 'Previous';
                    obj.nButton.Text = 'Next';
            end
        end

        function step1(obj)
            obj.innerGrid.RowHeight = {10,'1x'};
            obj.innerGrid.ColumnWidth = {'1x','1x'};

            % init
            text = {'GIF','PNG'};
            file = {'optionGif.gif', 'optionPng.jpeg'};
            for i = 1:2
                imgButton = uibutton(obj.innerGrid);
                imgButton.Layout.Row = 2;
                imgButton.Layout.Column = i;
                imgButton.Text = {'',text{i}};
                imgButton.Icon = file{i};
                imgButton.IconAlignment = 'top';
                imgButton.ButtonPushedFcn = @(src, event) obj.imgButtonPressed(src);
            end
        end

        function imgButtonPressed(obj,src)
            obj.imageType = src.Text{2};
            obj.screen = obj.screen + 1;
            obj.switchScreen();
        end

        function step2(obj)
            rowHeight = 22;
            obj.innerGrid.RowHeight = {rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight};
            obj.innerGrid.ColumnWidth = {'fit','1x',100};

            % draw input
            k = keys(obj.GUI_Form.setupVar.setupParams);
            for i = 1:length(k)
                if strcmp(obj.imageType, "GIF") && strcmp(k{i}, "K")
                    continue
                elseif strcmp(obj.imageType, "PNG") && strcmp(k{i}, "Axis limits")
                    continue
                elseif strcmp(obj.imageType, "PNG") && strcmp(k{i}, "K_range")
                    continue
                end
                obj.GUI_Form.labeledInputArea(k{i})
            end
        end

        function step3(obj)
            obj.innerGrid.RowHeight = {22*2};
            obj.innerGrid.ColumnWidth = {'fit'};

            % button group
            bg = uibuttongroup(obj.innerGrid);
            bg.BackgroundColor = obj.app.Color;
            bg.BorderType = "none";
            bg.Layout.Row = 1;
            bg.Layout.Column = 1;

            % individual buttons
            options = {'Generate PNG only','Also generate MATLAB figures'};
            for i = 1:length(options)
                rb = uiradiobutton(bg);
                rb.Text = options{i};
                rb.Position = [5 -i*22+49 300 15];
            end

            bg.SelectionChangedFcn = @(src, event) obj.radioInputPressed(event);
        end

        function radioInputPressed(obj, event)
            % choose to generate figures
            obj.generateFigures = strcmp(event.NewValue.Text,'Also generate MATLAB figures');
        end

        function step4_GIF(obj)
            obj.innerGrid.RowHeight = {20,'1x',20};
            obj.innerGrid.ColumnWidth = {20,'1x',20};

            % main code
            params = obj.GUI_Form.params;
            G=Grid(params('Layer file'),params('dz'),params('Material'));

            % progress bar
            progressBar = waitbar(0,'Please Wait...');
            progressBar.Name = 'Loading figures';
            
            % M
            f = figure;
            f.Visible = 'off';
            kValues = params('K_range1'):params('K_range3'):params('K_range2');
            M(length(kValues)) = struct('cdata',[],'colormap',[]);
            for i = 1:length(kValues)
                k = kValues(i);
                disp(k);
                G.set_K(k);

                if (params('Solver') == "FDM")
                    Solver=FDMSolver(params('Non-parabolicity'),G,params('Nstmax'));
                else
                    Solver=TMMSolver(params('Non-parabolicity'),G,params('Nstmax'));
                end

                [energies,psis]=Solver.get_wavefunctions;
                V=Visualization(G,energies,psis);
                axisLimits = [params('Axis limits1'),params('Axis limits2'),params('Axis limits3'),params('Axis limits4')];
                V.plot_QCL(f,k,params('Padding'),1,axisLimits);
                M(i) = getframe(f);
                clf(f);
                waitbar(i/length(kValues),progressBar);
            end
            
            pause(1);
            close(progressBar);

            % completed
            u = uipanel(obj.innerGrid);
            u.Layout.Row = 2;
            u.Layout.Column = 2;
            u.Visible = 'off';
            movie(u,M,500,2);
            figure(obj.app);
        end
    end
end