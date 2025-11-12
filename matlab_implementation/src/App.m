% NOTE: if verLessThan causes errors in the future, please change to isMATLABReleaseOlderThan
classdef App < handle
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
        titles={'Choose your task','Set options', 'Results', 'Save as'};
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
        curFigCount = 1;
    end

    methods
        function obj = App
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
            if (~verLessThan('matlab',"9.14")) 
                obj.app.Color = obj.color;
            end

            % add padding
            mainPanel = uipanel(obj.app);
            mainPanel.BorderType = 'none';
            padding = 20;
            mainPanel.Position = [padding, padding, obj.app_w - 2*padding, obj.app_h - 2*padding];

            % draw the grid
            obj.grid = uigridlayout(mainPanel);
            if (~verLessThan('matlab',"9.14"))
                obj.grid.BackgroundColor = obj.color;
                obj.grid.RowHeight = {'fit','1x',22};
            else
                obj.grid.RowHeight = {40,'1x',22};
            end
            obj.grid.ColumnWidth = {'1x'};

            % init title
            obj.title = uilabel(obj.grid);
            obj.title.Layout.Row = 1;
            obj.title.Layout.Column = 1;
            if (~verLessThan('matlab',"9.14"))
                obj.title.Interpreter = "html";
            else
                obj.title.FontSize = 22;
                obj.title.FontWeight = 'bold';
            end

            % init inner grid
            obj.innerGrid = uigridlayout(obj.grid);
            obj.innerGrid.Layout.Row = 2;
            obj.innerGrid.Layout.Column = 1;
            if (~verLessThan('matlab',"9.14"))
                obj.innerGrid.BackgroundColor = obj.color;
            end
            obj.innerGrid.Padding = [0,0,0,0];

            % init button grid
            obj.buttonGrid = uigridlayout(obj.grid);
            obj.buttonGrid.Layout.Row = 3;
            obj.buttonGrid.Layout.Column = 1;
            if (~verLessThan('matlab',"9.14"))
                obj.buttonGrid.BackgroundColor = obj.color;
            end
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

            % init save options form
            obj.GUI_Save_Form = GUI_Form(GUI_Var_File,obj.app,obj.innerGrid,1,2);

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
                    end
                elseif (strcmp(obj.imageType,'GIF'))
                    v = VideoWriter(fileName,"MPEG-4");
                    v.FrameRate = 4; % TODO: change frame rate as needed
                    open(v);
                    writeVideo(v,obj.M);
                    close(v);
                elseif (strcmp(obj.imageType,'PNG'))
                    for i = 1:length(obj.MFigs)
                        set(obj.MFigs(i), 'CreateFcn', 'set(gcbo,''Visible'',''on'')');
                        saveas(obj.MFigs(i),strcat(fileName,num2str(i)),'png');
                    end
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
                for i = 1:length(obj.MFigs) % clean up figures
                    close(obj.MFigs(i));
                end
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
                        obj.step4_PNG();
                    end
            end
        end

        function mainLayout(obj)
            if (~verLessThan('matlab',"9.14"))
                obj.title.Text = strcat("<font style='font-size:20px; font-weight:bold; font-family:Helvetica, Verdana, Arial;'>",obj.titles{obj.screen},"</font>");
            else
                obj.title.Text = obj.titles{obj.screen};
            end
            obj.innerGrid.Children.delete;

            % button text
            obj.pButton.Visible = 'on';
            obj.nButton.Visible = 'on';
            switch (obj.screen)
                case 1
                    obj.pButton.Visible = 'off';
                    obj.nButton.Visible = 'off';
                case obj.totalScreens
                    obj.pButton.Text = 'Save';
                    obj.nButton.Text = 'Close';
                case 2
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
            text = {'Electronic Structure Calculation','Electronic Structure Animation (Bias Sweep)'};
            file = {'optionPng.png','optionGif.gif'};
            for i = 1:2
                imgButton = uibutton(obj.innerGrid);
                imgButton.Layout.Row = 2;
                imgButton.Layout.Column = i;
                imgButton.Text = {'',text{i}};
                imgButton.Icon = file{i};
                imgButton.IconAlignment = 'top';
                imgButton.FontSize = 20;
                imgButton.WordWrap = 'on';
                imgButton.ButtonPushedFcn = @(src, event) obj.imgButtonPressed(src);
            end
        end

        function imgButtonPressed(obj,src)
            if strcmp(src.Text{2},"Electronic Structure Calculation")
                obj.imageType = "PNG";
            else
                obj.imageType = "GIF";
            end
            obj.screen = obj.screen + 1;
            obj.switchScreen();
        end

        function step2(obj)
            rowHeight = 22;
            obj.innerGrid.RowHeight = {rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight};
            if (~verLessThan('matlab',"9.14"))
                obj.innerGrid.ColumnWidth = {'fit','1x',100};
            else
                obj.innerGrid.ColumnWidth = {100,'1x',100};
            end

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
            obj.app.Visible = 'off';
            obj.innerGrid.RowHeight = {20,'1x',20};
            obj.innerGrid.ColumnWidth = {40,'1x',40};

            % main code
            params = obj.GUI_Form.params;
            G=Grid(params('Layer file'),params('dz'),params('Material'));

            % progress bar
            progressBar = waitbar(0,'Please Wait...');
            progressBar.Name = 'Loading figures';

            % M
            obj.MFigs = gobjects(1,4);

            k = params('K');
            G.set_K(k);

            if (params('Solver') == "FDM")
                Solver=FDMSolver(params('Non-parabolicity'),G,params('Nstmax'));
            else
                Solver=TMMSolver(params('Non-parabolicity'),G,params('Nstmax'));
            end

            [energies,psis]=Solver.get_wavefunctions;
            V=Visualization(G,energies,psis);
            % plot_V_wf
            curFig1 = figure('Visible','off');
            V.plot_V_wf(curFig1);
            waitbar(3/6,progressBar);
            % plot_energies
            curFig2 = figure('Visible','off');
            V.plot_energies(curFig2);
            waitbar(4/6,progressBar);
            % plot_energy_difference_in_terahertz
            curFig3 = figure('Visible','off');
            V.plot_energy_difference_in_terahertz(curFig3);
            waitbar(5/6,progressBar);
            % plot_QCL
            curFig4 = figure('Visible','off');
            V.plot_QCL(curFig4,params('K'),params('Padding'),0);
            waitbar(1,progressBar);
            % done
            obj.MFigs = [curFig1,curFig2,curFig3,curFig4];

            % finished
            pause(0.5);
            close(progressBar);
            obj.app.Visible = 'on';

            % show figures
            curFigPanel = uipanel(obj.innerGrid);
            curFigPanel.Layout.Row = 2;
            curFigPanel.Layout.Column = 2;
            if (~verLessThan('matlab',"9.14"))
                curFigPanel.BackgroundColor = obj.color;
            end
            curFigPanel.BorderType = 'none';
            copyobj(get(obj.MFigs(obj.curFigCount),'Children'),curFigPanel);

            % carousel buttons
            pCButton = uibutton(obj.innerGrid);
            pCButton.Layout.Row = 2;
            pCButton.Layout.Column = 1;
            pCButton.Text = '<';
            pCButton.ButtonPushedFcn = @(src, event) obj.pCButtonPressed(curFigPanel);
            nCButton = uibutton(obj.innerGrid);
            nCButton.Layout.Row = 2;
            nCButton.Layout.Column = 3;
            nCButton.Text = '>';
            nCButton.ButtonPushedFcn = @(src, event) obj.nCButtonPressed(curFigPanel);
        end

        function pCButtonPressed(obj,curFigPanel)
            if obj.curFigCount > 1
                obj.curFigCount = obj.curFigCount - 1;
            else
                obj.curFigCount = 4;
            end
            obj.updateCurFigPanel(curFigPanel);
        end

        function nCButtonPressed(obj,curFigPanel)
            if obj.curFigCount < 4
                obj.curFigCount = obj.curFigCount + 1;
            else
                obj.curFigCount = 1;
            end
            obj.updateCurFigPanel(curFigPanel);
        end

        function updateCurFigPanel(obj,curFigPanel)
            delete(curFigPanel.Children);
            copyobj(get(obj.MFigs(obj.curFigCount),'Children'),curFigPanel);
        end

        function step4_PNG(obj)
            % save options ui
            obj.step4_shared();
        end

        function step4_GIF(obj)
            obj.app.Visible = 'off';

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

            pause(0.5);
            close(progressBar);

            % save options ui
            obj.step4_shared();

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

        function step4_shared(obj)
            % save options ui
            rowHeight = 22;
            obj.innerGrid.RowHeight = {rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight,rowHeight};
            if (~verLessThan('matlab',"9.14"))
                obj.innerGrid.ColumnWidth = {'fit','1x',100};
            else
                obj.innerGrid.ColumnWidth = {100,'1x',100};
            end

            k = keys(obj.GUI_Save_Form.setupVar.setupParams);
            for i = 1:length(k)
                obj.GUI_Save_Form.labeledInputArea(k{i})
            end
        end
    end
end
