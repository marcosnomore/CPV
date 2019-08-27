% Fichero de Preprocesado de Datos.

load('geonica2018.txt')

% Se eliminan las horas no productivas y las medidas incompletas.
geonica2018_resumido=geonica2018(1,:);
m=1;
for l=1:34560
    if timeofday(geonica2018{l,2})>'08:00:00' && timeofday(geonica2018{l,2})<'21:00:00' && (~ isnan(geonica2018{l,3}))
        geonica2018_resumido(m,:)=geonica2018(l,:);
        m=m+1;
    end
end

% Se unen los archivos de datos funcionales y meteorológicos.
vector_time = strcat(datestr(InsolightPreseriesoutdoormonitoringIESrooftopUPM{:,1}),{' '},datestr(InsolightPreseriesoutdoormonitoringIESrooftopUPM{:,2}, 'hh:mm:ss'));
vector_time_resumido=strings(10000,1);

t=hours(1/60);
complete_measurements=zeros(10000,24);
k=1;
n=1;
for i=1:24066
    for j=n:18259
        if InsolightPreseriesoutdoormonitoringIESrooftopUPM{i,1} == geonica2018_resumido{j,1}
            if InsolightPreseriesoutdoormonitoringIESrooftopUPM{i,2} - geonica2018{j,2} < t && InsolightPreseriesoutdoormonitoringIESrooftopUPM{i,2} - geonica2018{j,2} > 0
                  complete_measurements(k,3:11)=table2array(InsolightPreseriesoutdoormonitoringIESrooftopUPM(i,3:end));
                  complete_measurements(k,12:end)=table2array(geonica2018(j,3:end));
                  vector_time_resumido(k,1)=vector_time{i,1};
                  k=k+1;
                  n=j;
                  break;
            end
        end
    end
end

% Se exportan los datos unidos.
dlmwrite('insolight_data.txt',complete_measurements,'newline','pc')
writematrix(vector_time_resumido,'insolight_datestr.txt')