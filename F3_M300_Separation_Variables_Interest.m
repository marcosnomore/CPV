% Se obtienen los datos filtrados junto al Air Mass.

load('m300_data_filtered_complete.txt')

% Se representan los datos con el Air Mass calculado.
Isc_DNI_filtered = m300_data_filtered_complete(:,26);
Airmass=m300_data_filtered_complete(:,34);

plot(Airmass.',Isc_DNI_filtered.', 'gx');
title('Isc/DNI en función de la Masa de Aire')
xlabel('Masa de Aire Relativa (-)')
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
title('Isc/DNI en función de la Masa de Aire para Temperatura Ambiente fija')
xlabel('Masa de Aire Relativa (-)')
ylabel('Isc/DNI (A/(W/m2))')
figure;
dlmwrite('nontemp_measurements.txt',nontemp_measurements,'newline','pc')

% Se elimina la influencia del Air Mass.
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
title('Isc/DNI en función de la Temperatura Ambiente para Masa de Aire fija')
xlabel('Temperatura Ambiente (ºC)')
ylabel('Isc/DNI (A/(W/m2))')
figure;
dlmwrite('nonairmass_measurements.txt',nonairmass_measurements,'newline','pc')

