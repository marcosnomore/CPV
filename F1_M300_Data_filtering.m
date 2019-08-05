% Fichero de Carga y Filtrado de Datos.

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
