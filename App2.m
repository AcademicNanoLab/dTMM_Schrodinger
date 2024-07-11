classdef App2 < handle
    properties
        app                             % app window
        GUI_Form
        GUI_Save_Form
        M
        MFigs
        imageType
        generateFigures=0               % default is don't generate figures
    end

    properties (Hidden)
        grid
        titles={'Choose your task','Set options', 'Complete', 'Save as'};
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
            obj.GUI_Form = GUI_Form(GUI_Var,obj.app,obj.innerGrid,1,2);

            % init screen
            obj.switchScreen();
        end

        function pButtonPressed(obj)
            if (obj.screen < obj.totalScreens)
                obj.screen = obj.screen - 1;
                obj.switchScreen();
            else
                saveParams = obj.GUI_Save_Form.params;
                fileName = strcat(saveParams('Directory'),'/',saveParams('File name'));
                if (strcmp(saveParams('Save as'),'MATLAB Figures')) % save figures - same for GIF and PNG
                    for i = 1:length(obj.MFigs)
                        set(obj.MFigs(i), 'CreateFcn', 'set(gcbo,''Visible'',''on'')');
                        saveas(obj.MFigs(i),strcat(fileName,num2str(i)),'fig');
                        close(obj.MFigs(i));
                    end
                elseif (strcmp(obj.imageType,'GIF'))
                    v = VideoWriter(fileName,"MPEG-4");
                    v.FrameRate = 4; % TODO: change frame rate as needed
                    open(v);
                    writeVideo(v,obj.M);
                    close(v);
                end
            end
        end

        function nButtonPressed(obj)
            expression = '\w*.txt';
            if (isempty(regexp(obj.GUI_Form.params('Layer file'),expression,'match')))
                errorFig = errordlg('You need to select a layer file', 'File error','modal');
                uiwait;
                figure(obj.app);
            elseif (obj.screen == obj.totalScreens - 2 && strcmp(obj.imageType,'GIF'))
                obj.screen = obj.totalScreens; % skip the showing screen for GIF
                obj.switchScreen();
            else
                obj.screen = obj.screen + 1;
                obj.switchScreen();
            end
        end

        function switchScreen(obj)
            if (obj.screen > obj.totalScreens)
                close(obj.app);
                obj.app = 0;
                return
            end
            obj.mainLayout();
            switch (obj.screen)
                case 1
                    obj.step1();
                case 2
                    obj.step2();
                case 3
                    obj.step3_PNG();
                case obj.totalScreens
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
                    obj.pButton.Text = 'Save';
                    obj.nButton.Text = 'Close';
                case 2
                    obj.pButton.Text = 'Previous';
                    obj.nButton.Text = 'Finish';
                    % case obj.totalScreens - 1
                    %     obj.pButton.Text = 'Previous';
                    %     obj.nButton.Text = 'Finish';
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

        function step3_PNG(obj)
            obj.innerGrid.RowHeight = {20,'1x',20};
            obj.innerGrid.ColumnWidth = {20,'1x',20};
        end

        function step4_GIF(obj)
            % obj.app.Visible = 'off';
            rowHeight = 22;
            obj.innerGrid.RowHeight = {rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight};
            obj.innerGrid.ColumnWidth = {'fit','1x',100};

            % main code
            params = obj.GUI_Form.params;
            G=Grid(params('Layer file'),params('dz'),params('Material'));

            % progress bar
            progressBar = waitbar(0,'Please Wait...');
            progressBar.Name = 'Loading figures';

            % M
            kValues = params('K_range1'):params('K_range3'):params('K_range2');
            M(length(kValues)) = struct('cdata',[],'colormap',[]);
            obj.M = M;
            obj.MFigs = gobjects(1,length(kValues));
            for i = 1:length(kValues)
                curFig = figure;
                curFig.Visible = 'off';

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
                V.plot_QCL(curFig,k,params('Padding'),1,axisLimits);
                obj.M(i) = getframe(curFig);
                obj.MFigs(i) = curFig;
                waitbar(i/length(kValues),progressBar);
            end

            pause(1);
            close(progressBar);

            % save options form
            obj.GUI_Save_Form = GUI_Form(GUI_Var_File,obj.app,obj.innerGrid,1,2);

            % save options ui
            k = keys(obj.GUI_Save_Form.setupVar.setupParams);
            for i = 1:length(k)
                obj.GUI_Save_Form.labeledInputArea(k{i})
            end

            % completed
            obj.app.Visible = 'on';
            f = figure;
            movie(f,obj.M,5,2);
            close(f); % TODO: if you DON'T want the figure to close immediately, just comment this out

            % focus on app
            if (obj.app ~= 0)
                figure(obj.app);
            end
        end
    end
end