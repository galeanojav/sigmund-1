xcrit = 819;
ycrit = 625;

Min1 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral570_ycentral1300_numpoints30_nexper_400.txt',0,1400,'H');
Min2 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral580_ycentral1232_numpoints33_nexper_400.txt',0,1400,'H');
Min3 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral600_ycentral1165_numpoints33_nexper_400.txt',0,1400,'H');
Min4 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral640_ycentral1098_numpoints40_nexper_300_years_100.txt',0,1400,'H');
Min5 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral655_ycentral1030_numpoints40_nexper_300_years_100.txt',0,1400,'H');
Min6 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral670_ycentral962_numpoints40_nexper_300_years_100_H.txt',0,1400,'H');
Min7 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral700_ycentral895_numpoints40_nexper_300_years_100_H.txt',0,1400,'H');
Min8 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral720_ycentral828_numpoints40_nexper_300_years_100_H.txt',0,1400,'H');
Min9 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral755_ycentral760_numpoints40_nexper_300_years_100_H.txt',0,1400,'H');
Min10 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral790_ycentral692_numpoints40_nexper_300_years_100_H.txt',0,1400,'H');
Min11 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral819_ycentral625_numpoints40_nexper_600_years_100_H.txt',0,1400,'H');
Min12 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral800_ycentral650_numpoints40_nexper_300_years_100_H.txt',0,1400,'H');
Min13 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral800_ycentral660_numpoints40_nexper_300_years_100_H.txt',0,1400,'H');
Min20 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral850_ycentral607_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min21 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral935_ycentral565_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min22 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral877_ycentral590_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min23 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral935_ycentral565_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min24 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral993_ycentral535_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min25 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral1051_ycentral510_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min26 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral1168_ycentral460_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min27 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral1226_ycentral440_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min28 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral1284_ycentral420_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min29 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral1342_ycentral400_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min30 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral1400_ycentral380_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min31 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral1051_ycentral510_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min32 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral825_ycentral610_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');
Min33 = lee_prob_slice('probslice_nexper_1x1_Binary_Logistic_abs_xcentral1100_ycentral482_numpoints40_nexper_300_years_100_V.txt',0,1300,'V');

Mintot = vertcat(Min1,Min2,Min3,Min4,Min5,Min6,Min7,Min8,Min9,Min10,Min11,Min12,Min13,Min20,Min21,Min22,Min23,Min24,Min25,Min26,Min27,Min28,Min29,Min30,Min31,Min32,Min33);
for i=0:xcrit-1
    Mintot = vertcat([i (round( i* (ycrit-1) / (xcrit-1))) 0.0],Mintot);
end
%pcolor(Mintot,'EdgeColor','Jet');
%imagesc(flipud(a));
x = Mintot(:,1);
y = Mintot(:,2);
z = Mintot(:,3);

% Settings
xres = 800; % Resolution, the higher, the smoother
yres = 800;         
cm = 'default'; % Colormap

% Axes Limits
xmin = 0; 
ymin = 0;
xmax = 1400; 
ymax = 1300; 
xi = linspace(xmin, xmax, xres);
yi = linspace(ymin, ymax, yres);

% Figure
myfig = figure('Position', [200 200 800 600]);

rotate3d off

% Create 13-level blue/red diverging color map:
level = 13; n = ceil(level/2);
cmap1 = [linspace(1, 1, n); linspace(0, 1, n); linspace(0, 1, n)]';
cmap2 = [linspace(1, 0, n); linspace(1, 0, n); linspace(1, 1, n)]';
cmap = [cmap1; cmap2(2:end, :)];
colormap(vivid(cmap, [.8, .8]));
[XI, YI] = meshgrid(xi, yi);

ZI = griddata(x, y, z, XI, YI, 'linear');
%mesh(XI,YI,ZI);

%contour(XI,YI,ZI);
%view(2);

surf(XI, YI, ZI,'EdgeColor', 'None');
colormap bone

zlim=[0 1.01];
xlim=[0 1400];
ylim=[0 1300];
%view(30, 30);
shading lines;
%light;
%lighting phong;
grid on;

%view(2);
 
%{
minX = min(Mintot(:,1));
maxX = max(Mintot(:,1));
minY = min(Mintot(:,2));
maxY = max(Mintot(:,2));
[X,Y]= meshgrid(1:1400,[895]);

figure;
j=895;
Z=[]

for i=1:1400
    index = find(Mintot(:,1)==i & Mintot(:,2)==j);
    %Z(i,1) = i;
    %Z(i,2) = j;
    Z = vertcat(Z,[i j Mintot(index(1),3)]);
end

mesh(Z','EdgeColor','Jet');
%}