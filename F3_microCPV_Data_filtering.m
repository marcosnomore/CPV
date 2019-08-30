% Fichero de Filtrado de Datos y de Separación de los Datos en Variables 
% de Interés.

load('insolight_data_complete.txt')

% Filtrado de Datos.
SMR_tm=insolight_data_complete(:,18)./insolight_data_complete(:,19);
DNI=insolight_data_complete(:,15);
WindSpeed=insolight_data_complete(:,12);
AirTemp = insolight_data_complete(:,9);
Airmass = insolight_data_complete(:,25);
Isc = insolight_data_complete(:,6);

insolight_filtered_measurements=zeros(3000, 25);
j=1; 
for i=1:23793
    if (SMR_tm(i,1) < 2.0)&&(SMR_tm(i,1) > 0.7)&&(DNI(i,1) > 600)&&(WindSpeed(i,1) < 10)&&(AirTemp(i,1) > 10)&&(Airmass(i,1) < 10)&&(Isc(i,1) > 0.3)
        insolight_filtered_measurements(j,:)=insolight_data_complete(i,:);
        j=j+1;
    end
end

% Se representan los datos filtrados.
Isc_DNI_filtered = insolight_filtered_measurements(:,6)./insolight_filtered_measurements(:,15);
AirTemp_filtered = insolight_filtered_measurements(:,9);
SMRtop_mid_filtered = insolight_filtered_measurements(:,18)./insolight_filtered_measurements(:,19);
Airmass_filtered = insolight_filtered_measurements(:,25);

plot(AirTemp_filtered.',Isc_DNI_filtered.', 'r+');
title('Isc/DNI en función de la Temperatura Ambiente')
xlabel('Temperatura Ambiente (ºC)')
ylabel('Isc/DNI (A/(W/m2))')
figure;

plot(SMRtop_mid_filtered.',Isc_DNI_filtered.', 'r+');
title('Isc/DNI en función de SMR (top-middle)')
xlabel('SMR (top-middle) (-)')
ylabel('Isc/DNI (A/(W/m2))')
figure;

plot(Airmass_filtered.',Isc_DNI_filtered.', 'gx');
title('Isc/DNI en función de la Masa de Aire')
xlabel('Masa de Aire Relativa (-)')
ylabel('Isc/DNI (A/(W/m2))')
figure;

% Se exportan los datos filtrados completos.
dlmwrite('insolight_data_filtered_complete.txt',insolight_filtered_measurements,'newline','pc')

% Separacion en Variables de Interés.
% Se elimina la influencia de la temperatura ambiente.
nontemp_measurements=zeros(1000, 25);
media_tempair=mean(AirTemp_filtered.');
j=1; 
for i=1:7798
    if (AirTemp_filtered(i,1) < media_tempair + 2)&&(AirTemp_filtered(i,1) > media_tempair - 3)
        nontemp_measurements(j,:)=insolight_filtered_measurements(i,:);
        j=j+1;
    end
end

% Se representan los datos para el rango de temperaturas fijado y se
% exportan dichos datos.
plot(nontemp_measurements(:,25).',(nontemp_measurements(:,6)./nontemp_measurements(:,15)).', 'gx');
title('Isc/DNI en función de la Masa de Aire para Temperatura Ambiente fija')
xlabel('Masa de Aire Relativa (-)')
ylabel('Isc/DNI (A/(W/m2))')
figure;
dlmwrite('insolight_nontemp_measurements.txt',nontemp_measurements,'newline','pc')

% Se elimina la influencia del Air Mass.
nonairmass_measurements=zeros(1000, 25);
media_airmass=mean(Airmass_filtered.');
j=1; 
for i=1:7798
    if (Airmass_filtered(i,1) < media_airmass + 0.5)&&(Airmass_filtered(i,1) > media_airmass - 0.8)
        nonairmass_measurements(j,:)=insolight_filtered_measurements(i,:);
        j=j+1;
    end
end

% Se representan los datos para el rango de Airmass fijado y se
% exportan dichos datos.
plot(nonairmass_measurements(:,9).',(nonairmass_measurements(:,6)./nonairmass_measurements(:,15)).', '.');
title('Isc/DNI en función de la Temperatura Ambiente para Masa de Aire fija')
xlabel('Temperatura Ambiente (ºC)')
ylabel('Isc/DNI (A/(W/m2))')
figure;
dlmwrite('insolight_nonairmass_measurements.txt',nonairmass_measurements,'newline','pc')
