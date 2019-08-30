% Fichero de Preprocesado de Datos.

% Se importan manualmente los archivos.

% Se aumentan en una hora las medidas meteorológicas para normalizar la TZ.
geonica2018{:,2} = geonica2018{:,2} + hours(1);

% Se unen los archivos de datos funcionales y meteorológicos.
vector_time = strcat(datestr(InsolightPreseriesoutdoormonitoringIESrooftopUPM{:,1}),{' '},datestr(InsolightPreseriesoutdoormonitoringIESrooftopUPM{:,2}, 'HH:MM'));
vector_time_conjunto = strings(10000,1);

complete_measurements = zeros(10000,24);
k=1;
n=1;
for i=1:24066
    for j=n:13517
        if InsolightPreseriesoutdoormonitoringIESrooftopUPM{i,1} == geonica2018{j,1}
            if InsolightPreseriesoutdoormonitoringIESrooftopUPM{i,2} == geonica2018{j,2}
                  complete_measurements(k,3:11)=table2array(InsolightPreseriesoutdoormonitoringIESrooftopUPM(i,3:end));
                  complete_measurements(k,12:end)=table2array(geonica2018(j,3:end));
                  vector_time_conjunto(k,1)=vector_time{i,1};
                  k=k+1;
                  n=j;
                  break;
            end
        end
    end
end

% Se exportan los datos unidos.
dlmwrite('insolight_data.txt',complete_measurements,'newline','pc')
writematrix(vector_time_conjunto,'insolight_datestr.txt')