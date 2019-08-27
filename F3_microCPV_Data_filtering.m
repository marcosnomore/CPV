% Fichero de Filtrado de Datos.

load('insolight_data_complete.txt')

SMR_tm=insolight_data_complete(:,18)./insolight_data_complete(:,19);
DNI=insolight_data_complete(:,15);
WindSpeed=insolight_data_complete(:,12);
Isc = insolight_data_complete(:,6);

insolight_filtered_measurements=zeros(1000, 25);
j=1; 
for i=1:13076
    if (SMR_tm(i,1) < 2.0)&&(SMR_tm(i,1) > 0.0)&&(DNI(i,1) > 600)&&(WindSpeed(i,1) < 10)&&(Isc(i,1) > 0.3)
        insolight_filtered_measurements(j,:)=insolight_data_complete(i,:);
        j=j+1;
    end
end

% Se representan los datos filtrados.
Isc_DNI_filtered = insolight_filtered_measurements(:,6)./insolight_filtered_measurements(:,15);
AirTemp_filtered = insolight_filtered_measurements(:,9);
SMRtop_mid_filtered = insolight_filtered_measurements(:,18)./insolight_filtered_measurements(:,19);
Airmass_filtered=insolight_filtered_measurements(:,25);

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

