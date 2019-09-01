% Fichero de Preprocesado de Datos.

% Se importa manualmente el archivo con las medidas.

Pmp_estim=InsolightMay1(:,16);

vector_time_may = datestr(InsolightMay1{:,1});
vector_time_may_preprocessed=strings(5000,1);

preprocessed_measurements=zeros(5000, 17);
j=1; 
for i=1:10586
    if (Pmp_estim{i,1} > 0.001)
        preprocessed_measurements(j,2:end)=table2array(InsolightMay1(i,2:end));
        vector_time_may_preprocessed(j,1)=vector_time_may(i,:);
        j=j+1;
    end
end

% Se exportan los datos preprocesados.
dlmwrite('insolight_data_may.txt',preprocessed_measurements,'newline','pc')
writematrix(vector_time_may_preprocessed,'insolight_datestr_may.txt')