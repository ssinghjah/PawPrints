package com.example.myapplication

object Constants {
    const val LOG_FOLDER_NAME = "AERPAW"
    const val LOG_START_DELIM = ",logStarts,"
    const val BS_INFO_START_MARKER = "BS_INFO_START"
    const val BS_INFO_STOP_MARKER = "BS_INFO_STOP"
    const val CELL_LOG_START_MARKER = "CELL_LOG_START"
    const val CELL_LOG_STOP_MARKER = "CELL_LOG_STOP"
    const val GPS_LOG_START_MARKER = "GPS_LOG_START"
    const val GPS_LOG_STOP_MARKER = "GPS_LOG_STOP"
    const val START_COMMAND = "start"
    const val STOP_COMMAND = "stop"
    const val COMMAND_DELIM = ","
    const val SETTING_VAL_DELIM = "="
    const val UPDATE_SETTINGS_COMMAND = "updateSettings"
    const val LOG_LOCALLY_COMMAND = "logLocally"
    const val LOG_GPS_COMMAND = "logGPS"
    const val LOG_INTERVAL_COMMAND = "logInterval"
    const val MODEM_REFRESH_COMMAND = "forceModemRefresh"
    const val MODEM_REFRESH_INTERVAL_COMMAND = "modemRefreshInterval"
    const val DEBUG_COMMAND = "debug"
    const val COMPUTE_NODE_IP = "127.0.0.1";
    const val NR_5G_SA_LOG_STRING = "5G_NR_SA"
    const val NR_5G_NSA_LOG_STRING = "5G_NR_NSA"
    const val LTE_4G_LOG_STRING = "4G_LTE"
    const val MEASUREMENT_PORT = 12348;
    const val COMMAND_PORT = 12345;
    const val MIN_SIG_STRENGTH_API_VERSION = 29
    const val MIN_NR_SIG_STRENGTH_API_VERSION = 29
    const val CELL_INFO_NR_MIN_API_VERSION = 29

}