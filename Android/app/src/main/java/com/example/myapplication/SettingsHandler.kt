package com.example.myapplication

import android.content.SharedPreferences
import com.example.myapplication.Constants.COMMAND_DELIM
import com.example.myapplication.Constants.DEBUG_COMMAND
import com.example.myapplication.Constants.LOG_GPS_COMMAND
import com.example.myapplication.Constants.LOG_INTERVAL_COMMAND
import com.example.myapplication.Constants.LOG_LOCALLY_COMMAND
import com.example.myapplication.Constants.MODEM_REFRESH_COMMAND
import com.example.myapplication.Constants.MODEM_REFRESH_INTERVAL_COMMAND
import com.example.myapplication.Constants.SETTING_VAL_DELIM
import com.example.myapplication.Constants.UPDATE_SETTINGS_COMMAND

object SettingsHandler{
    var ForceModemRefresh:Boolean = true
    var LogInterval:Long = 1000
    var ModemRefreshInterval:Long = 1000
    var UIRefreshInterval:Long = 1000
    var LogLocally:Boolean = true
    var LogGPS:Boolean = true
    var StreamToComputeNode:Boolean = false
    var Debug:Boolean = false
    var LTE_Log_dBm:Boolean = true
    var LTE_Log_RSRP:Boolean = true
    var LTE_Log_RSRQ:Boolean = true
    var LTE_Log_RSSI:Boolean = true
    var LTE_Log_CQI:Boolean = true
    var LTE_Log_EARFCN:Boolean = true
    var LTE_Log_ASU:Boolean = true
    var LTE_Log_PCI:Boolean = true
    var LTE_Log_CI:Boolean = true
    var LTE_Log_TA:Boolean = true

    fun updateSettingsFromCommand(command:String, prefManager:SharedPreferences):Boolean
    {
        var bValidCommand = true
        try {

            val settingInfo = command.substringAfter(UPDATE_SETTINGS_COMMAND + COMMAND_DELIM)
            val settingName = settingInfo.substringBefore(SETTING_VAL_DELIM)
            val settingValue = settingInfo.substringAfter(SETTING_VAL_DELIM)

            with(prefManager.edit())
            {
                when (settingName)
                {
                    LOG_LOCALLY_COMMAND ->
                    {
                        putBoolean("pref_bLogLocally", settingValue.toBooleanStrict())
                    }
                    LOG_INTERVAL_COMMAND ->
                    {
                        putString("pref_iLogInterval", settingValue.toString());
                        apply()
                        LogInterval = settingValue.toLong()
                    }
                    MODEM_REFRESH_INTERVAL_COMMAND ->
                    {
                        putString("pref_iModemRefreshInterval", settingValue.toString());
                        apply()
                        ModemRefreshInterval = settingValue.toLong()
                    }
                    LOG_GPS_COMMAND ->
                    {
                        putBoolean("pref_bLogGPS", settingValue.toBooleanStrict())
                        apply()
                        LogGPS = settingValue.toBooleanStrict()
                    }
                    MODEM_REFRESH_COMMAND ->
                    {
                        putBoolean("pref_bForceModemRefresh", settingValue.toBooleanStrict())
                        apply()
                        ForceModemRefresh = settingValue.toBooleanStrict()
                    }
                    DEBUG_COMMAND ->
                    {
                        putBoolean("pref_bDebug", settingValue.toBooleanStrict())
                        apply()
                        Debug = settingValue.toBooleanStrict()
                    }
                    else ->
                    {
                        bValidCommand = false
                    }
                    }
                }
            return bValidCommand
            }
        catch (t:Throwable)
        {
            return false
        }
    }

    fun updateSettingsFromUI(sp: SharedPreferences):String
    {
        var errors = ""
        LogLocally = sp.getBoolean("pref_bLogLocally", true)
        ForceModemRefresh = sp.getBoolean("pref_bForceModemRefresh", true)
        StreamToComputeNode = sp.getBoolean("pref_bStreamMeasurements", true)
        LogGPS = sp.getBoolean("pref_bLogGPS", false)
        Debug = sp.getBoolean("pref_bDebug", false)
       try
       {
            LogInterval = sp.getString("pref_iLogInterval", "1000")!!.toLong()
            ModemRefreshInterval = sp.getString("pref_iModemRefreshInterval", "1000")!!.toLong()
            UIRefreshInterval = sp.getString("pref_iUIRefreshInterval", "1000")!!.toLong()
       }
       catch(t:Throwable)
       {
           errors = t.toString()
       }
        LTE_Log_dBm = sp.getBoolean("pref_b_LTE_dBm", true)
        LTE_Log_RSRP = sp.getBoolean("pref_b_LTE_RSRP", true)
        LTE_Log_RSRQ = sp.getBoolean("pref_b_LTE_RSRQ", true)
        LTE_Log_RSSI = sp.getBoolean("pref_b_LTE_RSSI", true)
        LTE_Log_CQI = sp.getBoolean("pref_b_LTE_CQI", true)
        LTE_Log_TA = sp.getBoolean("pref_b_LTE_TA", true)
        LTE_Log_EARFCN = sp.getBoolean("pref_b_LTE_EARCN", true)
        LTE_Log_ASU = sp.getBoolean("pref_b_LTE_ASU", true)
        LTE_Log_PCI = sp.getBoolean("pref_b_LTE_PCI", true)
        LTE_Log_CI = sp.getBoolean("pref_b_LTE_CI", true)
        return errors
    }
}
