% Primera Parte. Carga y Filtrado de Datos.

load('M300_data.mat')

Tot=m300.measurements.data(:,29);
SMR_tm=m300.measurements.data(:,21);
DNI=m300.measurements.data(:,17);
WindSpeed=m300.measurements.data(:,9);

filtered_measurements=zeros(10000, 33);
media_tot=mean(Tot.');
j=1; 
for i=1:31053
    if (Tot(i,1) < media_tot)&&(SMR_tm(i,1) < 1.10)&&(SMR_tm(i,1) > 0.70)&&(DNI(i,1) > 600)&&(WindSpeed(i,1) < 10)
        filtered_measurements(j,:)=m300.measurements.data(i,:);
        j=j+1;
    end
end

% Se representan los datos filtrados junto a los originales.
Isc_DNI = m300.measurements.data(:,26);
Isc_DNI_filtered = filtered_measurements(:,26);

AirTemp = m300.measurements.data(:,11);
AirTemp_filtered = filtered_measurements(:,11);

SMRtop_mid = m300.measurements.data(:,21);
SMRtop_mid_filtered = filtered_measurements(:,21);

plot(AirTemp.',Isc_DNI.', 'bx'); hold on; 
plot(AirTemp_filtered.',Isc_DNI_filtered.', 'r+');
title('Isc/DNI en función de la Temperatura Ambiente')
xlabel('Temperatura Ambiente (ºC)')
ylabel('Isc/DNI (A/(W/m2))')
legend('Datos Completos','Datos Filtrados')
figure;

plot(SMRtop_mid.',Isc_DNI.', 'bx'); hold on; 
plot(SMRtop_mid_filtered.',Isc_DNI_filtered.', 'r+');
title('Isc/DNI en función de SMR (top-middle)')
xlabel('SMR (top-middle) (-)')
ylabel('Isc/DNI (A/(W/m2))')
legend('Datos Completos','Datos Filtrados')
figure;

% Se exportan los datos filtrados. Se obtiene la fecha como cadena y se
% guarda en un nuevo archivo
dlmwrite('m300_data_filtered.txt',filtered_measurements,'newline','pc')

datetime1 = datetime(filtered_measurements(:,24),'ConvertFrom','datenum');
datetimestring = datestr(datetime1);
dlmwrite('m300_datetime.txt',datetimestring,'delimiter','','newline','pc')


% Segunda parte. Se obtienen los datos filtrados junto al Airmass.
load('m300_data_filtered_complete.txt')

% Se representan los datos con el Airmass calculado.
Isc_DNI_filtered = m300_data_filtered_complete(:,26);
Airmass=m300_data_filtered_complete(:,34);

plot(Airmass.',Isc_DNI_filtered.', 'gx');
title('Isc/DNI en función del Airmass Relativo')
xlabel('Airmass Relativo (-)')
ylabel('Isc/DNI (A/(W/m2))')
figure;

% Se elimina la influencia de la temperatura ambiente.
nontemp_measurements=zeros(100, 34);
media_tempair=mean(AirTemp_filtered.');
j=1; 
for i=1:13044
    if (AirTemp_filtered(i,1) < media_tempair + 1)&&(AirTemp_filtered(i,1) > media_tempair - 5)
        nontemp_measurements(j,:)=m300_data_filtered_complete(i,:);
        j=j+1;
    end
end

% Se representan los datos para el rango de temperaturas fijado y se
% exportan dichos datos.
plot(nontemp_measurements(:,34).',nontemp_measurements(:,26).', 'gx');
title('Isc/DNI en función del Airmass Relativo para Temperatura Ambiente fija')
xlabel('Airmass Relativo (-)')
ylabel('Isc/DNI (A/(W/m2))')
hold on;
x=[1:0.1:8];
y_1=0.000019933462737882277*x + 0.0032280807538916955;
y_2=-0.00003617135318826666*x + 0.0033568655422862065;
plot(x, y_1, x, y_2);
figure;
dlmwrite('nontemp_measurements.txt',nontemp_measurements,'newline','pc')

% Se elimina la influencia del Airmass.
nonairmass_measurements=zeros(100, 34);
media_airmass=mean(Airmass.');
j=1; 
for i=1:13044
    if (Airmass(i,1) < media_airmass + 0.25)
        nonairmass_measurements(j,:)=m300_data_filtered_complete(i,:);
        j=j+1;
    end
end

% Se representan los datos para el rango de Airmass fijado y se
% exportan dichos datos.
plot(nonairmass_measurements(:,11).',nonairmass_measurements(:,26).', '.'); hold on;
x=[10:1:40];
y_1=0.000003091130233690231*x + 0.0031994814153441433;
plot(x, y_1);
figure;
dlmwrite('nonairmass_measurements.txt',nonairmass_measurements,'newline','pc')

