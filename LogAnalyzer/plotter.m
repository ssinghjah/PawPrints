close all;
clear all;

ROLL_MEAN_NEIGHBOURS = 1;

% Absolute timestamps
gps_times = csvread("../Data/gps_abs_time.csv");
pawprints_times = csvread("../Data/connected_bs_abs_time.csv");

% Start and end time
start_time = max(min(pawprints_times), min(gps_times));
end_time = min(max(pawprints_times), max(gps_times));
pawprints_start_index = find(pawprints_times >= start_time, 1); 
pawprints_end_index = find(pawprints_times >= end_time, 1);
t_pawprints = (pawprints_times(pawprints_start_index:pawprints_end_index) - start_time)./60000;
gps_start_index = find(gps_times >= start_time, 1); 
gps_end_index = find(gps_times >= end_time, 1); 
t_gps = (gps_times(gps_start_index:gps_end_index) - start_time)./60000;

% Cell parameter and altitude vs rel time
connected_rsrps = csvread("../Data/connected_bs_rsrp.csv");
connected_rsrqs = csvread("../Data/connected_bs_rsrq.csv");
connected_rssis = csvread("../Data/connected_bs_rssi.csv");
connected_asus = csvread("../Data/connected_bs_asu.csv");

% Altitude
altitudes = csvread("../Data/gps_altitude.csv");

% RSRP & RSSI & altitude vs elapsed time
figure;
yyaxis left;
plot(t_pawprints, movmean(connected_rsrps(pawprints_start_index:pawprints_end_index), ROLL_MEAN_NEIGHBOURS), 'DisplayName', 'RSRP of connected BS', 'LineWidth', 2);
hold on;
plot(t_pawprints, movmean(connected_rssis(pawprints_start_index:pawprints_end_index), ROLL_MEAN_NEIGHBOURS), 'DisplayName' , 'RSSI of connected BS', 'LineWidth', 2);
hold on;
yyaxis right;
plot(t_gps, altitudes(gps_start_index: gps_end_index), 'DisplayName','Altitude of HeliKite', 'LineWidth', 2);
grid on;
legend show;

% RSRQ & altitude vs elapsed time
figure;
yyaxis left;
plot(t_pawprints, movmean(connected_rsrqs(pawprints_start_index:pawprints_end_index), ROLL_MEAN_NEIGHBOURS), 'DisplayName', 'RSRQ of connected BS', 'LineWidth', 2);
hold on;
yyaxis right;
plot(t_gps, altitudes(gps_start_index: gps_end_index), 'DisplayName','Altitude of HeliKite', 'LineWidth', 2);
grid on;
legend show;

% ASU & altitude vs elapsed time
figure;
yyaxis left;
plot(t_pawprints, movmean(connected_asus(pawprints_start_index:pawprints_end_index),ROLL_MEAN_NEIGHBOURS), 'DisplayName', 'ASU of connected BS', 'LineWidth', 2);
hold on;
yyaxis right;
plot(t_gps, altitudes(gps_start_index: gps_end_index), 'DisplayName', 'Altitude of HeliKite', 'LineWidth', 2);
grid on;
legend show;

% Number of seen BSs and altitude vs elapsed time
num_seen_bss = csvread("../Data/num_seen_bs.csv");
figure;
yyaxis left;
plot(t_pawprints, num_seen_bss(pawprints_start_index:pawprints_end_index), 'DisplayName' , 'Count of detected BSs', 'LineWidth', 2);
hold on;
yyaxis right;
plot(t_gps, altitudes(gps_start_index: gps_end_index), 'DisplayName','Altitude of HeliKite', 'LineWidth', 2);
legend show;

% Histogram of seen time duration
bs_seen_duration = csvread("../Data/bs_seen_time.csv");
figure;
histogram(bs_seen_duration(:,2)./60.0, 'BinEdges', [0, 1, 30, 60, 90]);