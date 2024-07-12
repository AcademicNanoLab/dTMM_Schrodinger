classdef GUI_Form < handle
    properties
        app
        setupVar
        params
        parentGrid
        labelCol
        inputCol
    end

    methods
        function obj = GUI_Form(Var_Constructor,app,parentGrid,labelCol,inputCol)
            % init params dict
            obj.app = app;
            obj.setupVar = Var_Constructor();
            obj.params = containers.Map();
            k = keys(obj.setupVar.setupParams);
            val = values(obj.setupVar.setupParams);
            for i = 1:length(k)
                if strcmp(val{i}{2},'rangeNumberInput')
                    for j = 3:5
                        obj.params(strcat(k{i},num2str(j))) = val{i}{j};
                    end
                else
                    obj.params(k{i}) = val{i}{3};
                end
            end

            % init UI info
            obj.parentGrid = parentGrid;
            obj.labelCol = labelCol;
            obj.inputCol = inputCol;
        end

        function labeledInputArea(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % draw label
            dTitle = uilabel(obj.parentGrid);
            dTitle.Layout.Row = setupParam{1};
            dTitle.Layout.Column = obj.labelCol;
            dTitle.Text = titleText;

            switch setupParam{2}
                case 'dropdown'
                    obj.dropdown(titleText);
                case 'depDropdown'
                    obj.depDropdown(titleText);
                case 'fileSelector'
                    obj.fileSelector(titleText);
                case 'numberInput'
                    obj.numberInput(titleText);
                case 'rangeNumberInput'
                    obj.rangeNumberInput(titleText);
                case 'axisLimitInput'
                    obj.axisLimitInput(titleText);
                case 'radio'
                    obj.radioInput(titleText);
                case 'text'
                    obj.textInput(titleText);
            end
        end

        function dropdown(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % draw dropdown
            dDropdown = uidropdown(obj.parentGrid);
            dDropdown.Layout.Row = setupParam{1};
            dDropdown.Layout.Column = obj.inputCol;
            dDropdown.Items = setupParam{4};
            dDropdown.Value = setupParam{3};
            obj.params(titleText) = setupParam{3};

            % callback function upon value change
            dDropdown.ValueChangedFcn = @(src, event) obj.dropdownValueChanged(src, titleText);
        end

        function dropdownValueChanged(obj, src, titleText)
            obj.params(titleText) = src.Value;
        end

        function depDropdown(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % draw dropdown
            dDropdown = uidropdown(obj.parentGrid);
            dDropdown.Layout.Row = setupParam{1};
            dDropdown.Layout.Column = obj.inputCol;

            % dependency
            dDropdown.Items = setupParam{5}(obj.params(setupParam{4}));
            dDropdown.Value = setupParam{3};
            obj.params(titleText) = setupParam{3};

            % callback function upon value change
            dDropdown.ValueChangedFcn = @(src, event) obj.dropdownValueChanged(src, titleText);
        end

        function fileSelector(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % draw input area
            fTextBox = uitextarea(obj.parentGrid);
            fTextBox.Layout.Row = setupParam{1};
            fTextBox.Layout.Column = obj.inputCol;
            fTextBox.Value = setupParam{3};
            obj.params(titleText) = setupParam{3};
            fTextBox.Editable = 'off';
            if (~verLessThan('matlab',"9.14"))
                fTextBox.WordWrap = 'off';
            end

            % draw button
            fButton = uibutton(obj.parentGrid);
            fButton.Layout.Row = setupParam{1};
            fButton.Layout.Column = obj.inputCol + 1;
            fButton.Text = 'Browse';

            % callback function upon button press
            fButton.ButtonPushedFcn = @(src, event) obj.fileButtonPressed(src, titleText, fTextBox);
        end

        function fileButtonPressed(obj, ~, titleText, fTextBox)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            obj.app.Visible = 'off';
            if (strcmp(setupParam{4},'dir'))
                location = '';
                file = uigetdir();
            else
                [file,location] = uigetfile(setupParam{4});
            end
            obj.app.Visible = 'on';
            if (file ~= 0)
                obj.params(titleText) = strcat(location,file);
                fTextBox.Value = obj.params(titleText);
            end
        end

        function numberInput(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % input number
            numericInput = uispinner(obj.parentGrid);
            numericInput.Layout.Row = setupParam{1};
            numericInput.Layout.Column = obj.inputCol;
            numericInput.Value = setupParam{3};
            obj.params(titleText) = setupParam{3};

            % parameters dependent on which item it is
            numericInput.Limits = setupParam{4};
            numericInput.Step = setupParam{5};
            numericInput.ValueDisplayFormat = setupParam{6};

            numericInput.ValueChangedFcn = @(src, event) obj.numericInputValueChanged(event, titleText);
        end

        function numericInputValueChanged(obj, event, titleText)
            obj.params(titleText) = event.Value;
        end

        function radioInput(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % button group
            bg = uibuttongroup(obj.parentGrid);
            bg.BackgroundColor = obj.app.Color;
            bg.BorderType = "none";
            bg.Layout.Row = setupParam{1};
            bg.Layout.Column = obj.inputCol;

            % individual buttons
            for i = 1:length(setupParam{4})
                rb = uiradiobutton(bg);
                rb.Text = setupParam{4}{i};
                rb.Position = [-145+i*150 5 150 15];
            end

            % callback function upon radio button press
            bg.SelectionChangedFcn = @(src, event) obj.radioInputPressed(event, titleText);
        end

        function radioInputPressed(obj, event, titleText)
            % edit value
            obj.params(titleText) = event.NewValue.Text;

            % reset non-parabolicity
            if (strcmp(titleText,'Solver'))
                setupParam = obj.setupVar.setupParams('Non-parabolicity');
                obj.labeledInputArea('Non-parabolicity');
                obj.params('Non-parabolicity') = setupParam{3};
            end
        end

        function rangeNumberInput(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % setup grid
            rangeGrid = uigridlayout(obj.parentGrid);
            rangeGrid.Layout.Row = setupParam{1};
            rangeGrid.Layout.Column = obj.inputCol;
            if (~verLessThan('matlab',"9.14"))
                rangeGrid.BackgroundColor = obj.app.Color;
            end
            rangeGrid.Padding = [0,0,0,0];
            rangeGrid.ColumnSpacing = 2;
            rangeGrid.RowHeight = {22};
            rangeGrid.ColumnWidth = {'3x',10,'3x',35,'2x'};

            % input number - start, end, step
            for i = 1:3
                numericInput = uispinner(rangeGrid);
                numericInput.Layout.Row = 1;
                numericInput.Layout.Column = 2*i - 1;
                numericInput.Value = setupParam{i + 2};
                obj.params(strcat(titleText,num2str(i))) = setupParam{i + 2};

                if (i < 3)
                    numericInput.Limits = setupParam{6};
                    numericInput.Step = setupParam{7};
                    numericInput.ValueDisplayFormat = setupParam{8};
                else
                    numericInput.Limits = setupParam{9};
                    numericInput.Step = setupParam{10};
                end
                numericInput.ValueChangedFcn = @(src, event) obj.rangeChangedFunction(event, titleText, i);
            end

            % additional labels
            rLabel = uilabel(rangeGrid);
            rLabel.Layout.Row = 1;
            rLabel.Layout.Column = 2;
            rLabel.Text = '~';
            rStep = uilabel(rangeGrid);
            rStep.Layout.Row = 1;
            rStep.Layout.Column = 4;
            rStep.Text = 'step:';
            rStep.HorizontalAlignment = 'right';
        end

        function rangeChangedFunction(obj, event, titleText, idx)
            obj.params(strcat(titleText,num2str(idx))) = event.Value;
            % disp(strcat(titleText,num2str(idx)));
            % disp(obj.params(strcat(titleText,num2str(idx))));
        end

        function axisLimitInput(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % setup grid
            rangeGrid = uigridlayout(obj.parentGrid);
            rangeGrid.Layout.Row = setupParam{1};
            rangeGrid.Layout.Column = obj.inputCol;
            if (~verLessThan('matlab',"9.14"))
                rangeGrid.BackgroundColor = obj.app.Color;
            end
            rangeGrid.Padding = [0,0,0,0];
            rangeGrid.ColumnSpacing = 2;
            rangeGrid.RowHeight = {22};
            rangeGrid.ColumnWidth = {10,'1x',10,'1x',35,'1x',10,'1x'};

            % input number - start, end, step
            for i = 1:4
                numericInput = uispinner(rangeGrid);
                numericInput.Layout.Row = 1;
                numericInput.Layout.Column = 2*i;
                numericInput.Value = setupParam{3}(i);
                obj.params(strcat(titleText,num2str(i))) = setupParam{3}(i);

                numericInput.Step = setupParam{4};
                numericInput.ValueChangedFcn = @(src, event) obj.rangeChangedFunction(event, titleText, i);
            end

            % additional labels
            xLabel = uilabel(rangeGrid);
            xLabel.Layout.Row = 1;
            xLabel.Layout.Column = 1;
            xLabel.Text = 'x:';
            xLabel.HorizontalAlignment = 'right';
            xLabel2 = uilabel(rangeGrid);
            xLabel2.Layout.Row = 1;
            xLabel2.Layout.Column = 3;
            xLabel2.Text = '~';
            yLabel = uilabel(rangeGrid);
            yLabel.Layout.Row = 1;
            yLabel.Layout.Column = 5;
            yLabel.Text = 'y:';
            yLabel.HorizontalAlignment = 'right';
            yLabel2 = uilabel(rangeGrid);
            yLabel2.Layout.Row = 1;
            yLabel2.Layout.Column = 7;
            yLabel2.Text = '~';
        end

        function axisLimitChangedFunction(obj, event, titleText, idx)
            obj.params(strcat(titleText,num2str(idx))) = event.Value;
            % disp(strcat(titleText,num2str(idx)));
            % disp(obj.params(strcat(titleText,num2str(idx))));
        end

        function textInput(obj, titleText)
            % access values
            setupParam = obj.setupVar.setupParams(titleText);

            % draw input area
            textBox = uitextarea(obj.parentGrid);
            textBox.Layout.Row = setupParam{1};
            textBox.Layout.Column = obj.inputCol;
            textBox.Value = setupParam{3};
            obj.params(titleText) = setupParam{3};
            if (~verLessThan('matlab',"9.14"))
                textBox.WordWrap = 'off';
            end

            % callback function upon text input
            textBox.ValueChangedFcn = @(src, event) obj.textChangedFunction(src, titleText);
        end

        function textChangedFunction(obj, src, titleText)
            obj.params(titleText) = src.Value{1};
        end
    end
end