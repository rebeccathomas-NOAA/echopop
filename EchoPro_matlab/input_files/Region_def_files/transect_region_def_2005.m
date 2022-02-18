function [tx0,tx1,tx_out1,tx_out2]=transect_region_def_2005(region)

tx0=[];
tx1=[];
tx_out1=[];
tx_out2=[];
if region == 1
%% region 1: paralell transects to latitudes from south of SCB to west of QC IS
    tx0=1;    % southern most transect number
    tx1=108;  % northern most transect number
    %% #.1 = west end of transect
    %% #.4 = east end of transect
    %% left (west) bound
    tx_l=[[tx0:106 tx1]+0.1 ];
    %% right (east) bound
    tx_r=[[tx0:93 107 97:106 tx1]+0.4];
    tx_out1=tx_l;
    tx_out2=tx_r;
elseif region == 2
%% region 2: transects paralell to longitudes north of QCI
    tx0=108;  % east most transect number
    tx1=111;  % west most transect number
%% specifies lower (south) and upper (north) region boundaries based on the transects
    %% #.1 = west end of transect
    %% #.4 = east end of transect
    %% #.6 = south end of transect
    %% #.9 = north end of transect
    tx_l=[108.1 [109 111]+0.6];
    tx_u=[108.4 [109 111]+0.9];
    tx_out1=tx_l;
    tx_out2=tx_u;
elseif region == 3
    %% region 3: paralell transects to latitudes west of QC IS
    tx0=97;    % southern most transect number
    tx1=113;    % northern most transect number
    %% specifies left (west) and right (east) region boundaries based on the transects
    %% #.1 = west end of transect
    %% #.4 = east end of transect
    %% #.6 = south end of transect
    %% #.9 = north end of transect
    tx_l=[113:2:123 97]+0.1;
    tx_r=[113.4 111.9 111.6 [115:2:123]+0.4 97.4];
    tx_out1=tx_l;
    tx_out2=tx_r;
end

return