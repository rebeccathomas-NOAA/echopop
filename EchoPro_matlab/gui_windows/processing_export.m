function h1 = processing_export()
% This is the machine-generated representation of a Handle Graphics object
% and its children.  Note that handle values may change when these objects
% are re-created. This may cause problems with any callbacks written to
% depend on the value of the handle at the time the object was saved.
% This problem is solved by saving the output as a FIG-file.
% 
% To reopen this object, just type the name of the M-file at the MATLAB
% prompt. The M-file and its associated MAT-file must be on your path.
% 
% NOTE: certain newer features in MATLAB may not have been saved in this
% M-file due to limitations of this format, which has been superseded by
% FIG-files.  Figures which have been annotated using the plot editor tools
% are incompatible with the M-file/MAT-file format, and should be saved as
% FIG-files.



appdata = [];
appdata.GUIDEOptions = struct(...
    'active_h', [], ...
    'taginfo', struct(...
    'figure', 2, ...
    'activex', 3, ...
    'pushbutton', 15, ...
    'popupmenu', 7, ...
    'listbox', 2, ...
    'text', 20, ...
    'axes', 2, ...
    'uipanel', 22, ...
    'slider', 2, ...
    'radiobutton', 42, ...
    'edit', 6), ...
    'override', 0, ...
    'release', 13, ...
    'resize', 'none', ...
    'accessibility', 'callback', ...
    'mfile', 0, ...
    'callbacks', 1, ...
    'singleton', 1, ...
    'syscolorfig', 1, ...
    'blocking', 0, ...
    'lastFilename', 'C:\Projects\EchoPro\EchoProGUI_Current\gui_windows\processing.fig');
appdata.lastValidTag = 'Processing';
appdata.GUIDELayoutEditor = [];
appdata.initTags = struct(...
    'handle', [], ...
    'tag', 'Processing');

h1 = figure(...
'Units','characters',...
'PaperUnits','points',...
'Color',[0.831372549019608 0.815686274509804 0.784313725490196],...
'Colormap',[0 0 0.5625;0 0 0.625;0 0 0.6875;0 0 0.75;0 0 0.8125;0 0 0.875;0 0 0.9375;0 0 1;0 0.0625 1;0 0.125 1;0 0.1875 1;0 0.25 1;0 0.3125 1;0 0.375 1;0 0.4375 1;0 0.5 1;0 0.5625 1;0 0.625 1;0 0.6875 1;0 0.75 1;0 0.8125 1;0 0.875 1;0 0.9375 1;0 1 1;0.0625 1 1;0.125 1 0.9375;0.1875 1 0.875;0.25 1 0.8125;0.3125 1 0.75;0.375 1 0.6875;0.4375 1 0.625;0.5 1 0.5625;0.5625 1 0.5;0.625 1 0.4375;0.6875 1 0.375;0.75 1 0.3125;0.8125 1 0.25;0.875 1 0.1875;0.9375 1 0.125;1 1 0.0625;1 1 0;1 0.9375 0;1 0.875 0;1 0.8125 0;1 0.75 0;1 0.6875 0;1 0.625 0;1 0.5625 0;1 0.5 0;1 0.4375 0;1 0.375 0;1 0.3125 0;1 0.25 0;1 0.1875 0;1 0.125 0;1 0.0625 0;1 0 0;0.9375 0 0;0.875 0 0;0.8125 0 0;0.75 0 0;0.6875 0 0;0.625 0 0;0.5625 0 0],...
'DockControls','off',...
'IntegerHandle','off',...
'InvertHardcopy',get(0,'defaultfigureInvertHardcopy'),...
'MenuBar','none',...
'Name','processing',...
'NumberTitle','off',...
'PaperPosition',[60 500 580 450],...
'PaperSize',[612 792],...
'Position',[150 18.6153846153846 120 43.3846153846154],...
'HandleVisibility','callback',...
'UserData',[],...
'Tag','Processing',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'uipanel_processing_base_window';

h2 = uipanel(...
'Parent',h1,...
'Units','characters',...
'FontSize',20,...
'FontWeight','light',...
'ForegroundColor',[0 0 1],...
'Title','Processing Parameters',...
'Tag','uipanel_processing_base_window',...
'Clipping','on',...
'Position',[14.1428571428571 2.25 99.2857142857143 39.85],...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'popup_proc_scale';

h3 = uicontrol(...
'Parent',h2,...
'Units','normalized',...
'BackgroundColor',[1 1 1],...
'Callback',@(hObject,eventdata)processing('popup_proc_scale_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',12,...
'FontWeight','bold',...
'Position',[0.372469635627531 0.667567125260481 0.546558704453442 0.085667215815486],...
'String',{  'Interval'; 'EchoView region '; 'Transect'; 'Leg'; 'Geographic region'; 'Country' },...
'Style','popupmenu',...
'Value',1,...
'CreateFcn', {@local_CreateFcn, @(hObject,eventdata)processing('popup_proc_scale_CreateFcn',hObject,eventdata,guidata(hObject)), appdata} ,...
'Tag','popup_proc_scale');

appdata = [];
appdata.lastValidTag = 'uipanel_proc_country';

h4 = uibuttongroup(...
'Parent',h2,...
'Units','characters',...
'FontUnits','normalized',...
'FontSize',-1,...
'Title',blanks(0),...
'Tag','uipanel_proc_country',...
'Clipping','on',...
'Position',[6.4 29.3846153846154 51.2 7],...
'SelectedObject',[],...
'SelectionChangeFcn',[],...
'OldSelectedObject',[],...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'radio_extrapolation';

h5 = uicontrol(...
'Parent',h4,...
'Units','characters',...
'FontUnits','normalized',...
'Callback',@(hObject,eventdata)processing('radio_extrapolation_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',0.418300653594771,...
'FontWeight','bold',...
'Position',[6.4 3.07692307692308 32.4 3.15384615384615],...
'String','Extrapolation',...
'Style','radiobutton',...
'Tag','radio_extrapolation',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'radio_no_extrapolation';

h6 = uicontrol(...
'Parent',h4,...
'Units','characters',...
'FontUnits','normalized',...
'Callback',@(hObject,eventdata)processing('radio_no_extrapolation_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',0.418300653594771,...
'FontWeight','bold',...
'Position',[5.4 0.692307692307692 33.6 3.15384615384615],...
'String','No Extrapolation',...
'Style','radiobutton',...
'Value',1,...
'Tag','radio_no_extrapolation',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'edit_start_transect_num';

h7 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'BackgroundColor',[1 1 1],...
'Callback',@(hObject,eventdata)processing('edit_start_transect_num_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',12,...
'FontWeight','bold',...
'ForegroundColor',[1 0 0],...
'Position',[20 13.15 15.8571428571429 2.55],...
'String','1',...
'Style','edit',...
'CreateFcn', {@local_CreateFcn, @(hObject,eventdata)processing('edit_start_transect_num_CreateFcn',hObject,eventdata,guidata(hObject)), appdata} ,...
'Tag','edit_start_transect_num');

appdata = [];
appdata.lastValidTag = 'edit_end_transect_num';

h8 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'BackgroundColor',[1 1 1],...
'Callback',@(hObject,eventdata)processing('edit_end_transect_num_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',12,...
'FontWeight','bold',...
'ForegroundColor',[1 0 0],...
'Position',[20 9.29999999999999 15.8571428571429 2.85],...
'String','70',...
'Style','edit',...
'CreateFcn', {@local_CreateFcn, @(hObject,eventdata)processing('edit_end_transect_num_CreateFcn',hObject,eventdata,guidata(hObject)), appdata} ,...
'Tag','edit_end_transect_num');

appdata = [];
appdata.lastValidTag = 'text_proc_start';

h9 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'FontSize',14,...
'FontWeight','bold',...
'HorizontalAlignment','right',...
'Position',[5.85714285714286 13.15 10.1428571428571 2.45],...
'String','Start',...
'Style','text',...
'Tag','text_proc_start',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'text_proc_end';

h10 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'FontSize',14,...
'FontWeight','bold',...
'HorizontalAlignment','right',...
'Position',[5 9.29999999999999 10.4285714285714 2.4],...
'String','End',...
'Style','text',...
'Tag','text_proc_end',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'popup_proc_stratification';

h11 = uicontrol(...
'Parent',h2,...
'Units','normalized',...
'BackgroundColor',[1 1 1],...
'Callback',@(hObject,eventdata)processing('popup_proc_stratification_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',12,...
'FontWeight','bold',...
'Position',[0.372997711670481 0.567071260083102 0.549199084668193 0.0834951456310679],...
'String',{  'Post-Stratification (KS-based)'; 'Pre-Stratification (geographically definded)'; 'Customized'; blanks(0) },...
'Style','popupmenu',...
'Value',1,...
'CreateFcn', {@local_CreateFcn, @(hObject,eventdata)processing('popup_proc_stratification_CreateFcn',hObject,eventdata,guidata(hObject)), appdata} ,...
'Tag','popup_proc_stratification');

appdata = [];
appdata.lastValidTag = 'pb_quit';

h12 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'FontUnits','normalized',...
'Callback',@(hObject,eventdata)processing('pb_quit_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',0.4,...
'FontWeight','bold',...
'Position',[70.5714285714285 0.899999999999989 24.7142857142857 3.05],...
'String','Quit',...
'Tag','pb_quit',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'pb_start';

h13 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'FontUnits','normalized',...
'Callback',@(hObject,eventdata)processing('pb_start_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',0.4,...
'FontWeight','bold',...
'Position',[70.5714285714285 4.09999999999999 24.7142857142857 3.05],...
'String','Start',...
'Tag','pb_start',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'radio_proc_mix_region';

h14 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'Callback',@(hObject,eventdata)processing('radio_proc_mix_region_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',12,...
'FontWeight','bold',...
'Position',[72.2 17.7730769230769 24 2.61538461538462],...
'String','Mix Region',...
'Style','radiobutton',...
'Tag','radio_proc_mix_region',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'text_proc_EI_unit';

h15 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'FontSize',14,...
'FontWeight','bold',...
'HorizontalAlignment','right',...
'Position',[15.8 25.85 17.6 2.38461538461538],...
'String','EI Unit',...
'Style','text',...
'Tag','text_proc_EI_unit',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'text_proc_stratification';

h16 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'FontSize',14,...
'FontWeight','bold',...
'HorizontalAlignment','right',...
'Position',[9.00000000000001 22.3115384615385 24.4 1.92307692307692],...
'String','Stratification',...
'Style','text',...
'Tag','text_proc_stratification',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'text_proc_leg';

h17 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'FontSize',14,...
'FontWeight','bold',...
'HorizontalAlignment','right',...
'Position',[15.6 17.6961538461538 17.8 2.30769230769231],...
'String','Varible',...
'Style','text',...
'Tag','text_proc_leg',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'popup_proc_variable';

h18 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'BackgroundColor',[1 1 1],...
'Callback',@(hObject,eventdata)processing('popup_proc_variable_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',12,...
'FontWeight','bold',...
'Position',[36.8 17.85 27.4 2.30769230769231],...
'String',{  'Biomass'; 'NASC'; 'Abundance' },...
'Style','popupmenu',...
'Value',1,...
'Tag','popup_proc_variable',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'pb_proc_advanced';

h19 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'Callback','processing(''pb_proc_advanced_Callback'',gcbo,[],guidata(gcbo))',...
'FontSize',12,...
'FontWeight','bold',...
'Position',[62.2 32.6153846153846 33.2 3.69230769230769],...
'String','Construct NASC',...
'Tag','pb_proc_advanced',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'radio_kriging_proc';

h20 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'Callback',@(hObject,eventdata)processing('radio_kriging_proc_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',16,...
'FontWeight','bold',...
'Position',[8.85714285714286 4.14999999999999 59.7142857142857 2.6],...
'String','Biomass using Geostatistics ',...
'Style','radiobutton',...
'Value',1,...
'Tag','radio_kriging_proc',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'uipanel18';

h21 = uibuttongroup(...
'Parent',h2,...
'Units','characters',...
'Title',blanks(0),...
'Tag','uipanel18',...
'Clipping','on',...
'Position',[3.57142857142857 1.54999999999999 66.1428571428571 5.3],...
'SelectedObject',[],...
'SelectionChangeFcn',[],...
'OldSelectedObject',[],...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'radio_default_para';

h22 = uicontrol(...
'Parent',h21,...
'Units','characters',...
'Callback',@(hObject,eventdata)processing('radio_default_para_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',16,...
'FontWeight','bold',...
'Position',[5.14285714285714 0.849999999999978 45.8571428571429 1.75],...
'String','Default Parameters',...
'Style','radiobutton',...
'Value',1,...
'Tag','radio_default_para',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'uipanel19';

h23 = uibuttongroup(...
'Parent',h2,...
'Units','characters',...
'FontSize',16,...
'FontWeight','bold',...
'Title','Transect',...
'Tag','uipanel19',...
'Clipping','on',...
'Position',[3.6 7.13846153846156 92 11.1538461538462],...
'SelectedObject',[],...
'SelectionChangeFcn',[],...
'OldSelectedObject',[],...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'edit_transect_reduction_fraction';

h24 = uicontrol(...
'Parent',h23,...
'Units','characters',...
'BackgroundColor',[1 1 1],...
'Callback',@(hObject,eventdata)processing('edit_transect_reduction_fraction_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',10,...
'Position',[40.0000000000001 5.15384615384615 14.8 1.61538461538462],...
'String','0',...
'Style','edit',...
'Tag','edit_transect_reduction_fraction',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'uipanel_reduction';

h25 = uibuttongroup(...
'Parent',h23,...
'Units','characters',...
'FontSize',12,...
'FontWeight','bold',...
'Title','Reduction (%)',...
'Tag','uipanel_reduction',...
'Clipping','on',...
'Position',[36.4 1.23076923076923 25.6 7.76923076923077],...
'SelectedObject',[],...
'SelectionChangeFcn',[],...
'OldSelectedObject',[],...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'popup_transect_reduction_mode';

h26 = uicontrol(...
'Parent',h25,...
'Units','characters',...
'BackgroundColor',[1 1 1],...
'Callback',@(hObject,eventdata)processing('popup_transect_reduction_mode_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',10,...
'Position',[3 0.384615384615387 19.8 2.23076923076923],...
'String',{  'Regular'; 'Random' },...
'Style','popupmenu',...
'Value',1,...
'CreateFcn', {@local_CreateFcn, @(hObject,eventdata)processing('popup_transect_reduction_mode_CreateFcn',hObject,eventdata,guidata(hObject)), appdata} ,...
'Tag','popup_transect_reduction_mode');

appdata = [];
appdata.lastValidTag = 'uipanel_bootstrap';

h27 = uibuttongroup(...
'Parent',h23,...
'Units','characters',...
'FontSize',12,...
'FontWeight','bold',...
'Title','Bootstrap #',...
'Tag','uipanel_bootstrap',...
'Clipping','on',...
'Position',[65.4 1.23076923076923 23.8 7.76923076923077],...
'SelectedObject',[],...
'SelectionChangeFcn',[],...
'OldSelectedObject',[],...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'edit_bootstrap_limit';

h28 = uicontrol(...
'Parent',h27,...
'Units','characters',...
'BackgroundColor',[1 1 1],...
'Callback',@(hObject,eventdata)processing('edit_bootstrap_limit_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',10,...
'Position',[3.4 2.61538461538462 14.6 2.23076923076923],...
'String','1',...
'Style','edit',...
'Tag','edit_bootstrap_limit',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );

appdata = [];
appdata.lastValidTag = 'radio_agedata';

h29 = uicontrol(...
'Parent',h2,...
'Units','characters',...
'FontUnits','normalized',...
'Callback',@(hObject,eventdata)processing('radio_agedata_Callback',hObject,eventdata,guidata(hObject)),...
'FontSize',0.470588235294118,...
'FontWeight','bold',...
'Position',[68 29.4615384615385 20 2.61538461538462],...
'String','Age Data',...
'Style','radiobutton',...
'Value',1,...
'Tag','radio_agedata',...
'CreateFcn', {@local_CreateFcn, blanks(0), appdata} );



% --- Set application data first then calling the CreateFcn. 
function local_CreateFcn(hObject, eventdata, createfcn, appdata)

if ~isempty(appdata)
   names = fieldnames(appdata);
   for i=1:length(names)
       name = char(names(i));
       setappdata(hObject, name, getfield(appdata,name));
   end
end

if ~isempty(createfcn)
   if isa(createfcn,'function_handle')
       createfcn(hObject, eventdata);
   else
       eval(createfcn);
   end
end
