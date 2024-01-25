package com.example.myapplication

import android.os.Build
import android.os.SystemClock
import android.telephony.CellInfo
import android.telephony.CellInfoLte
import androidx.annotation.RequiresApi
import org.json.JSONObject

@RequiresApi(Build.VERSION_CODES.Q)
class LTEInfo(cellInfo:CellInfoLte, refTime: Long) {
    private val MIN_RSSI_BUILD = 29
    private val MIN_BANDS_BUILD = 29
    private val MIN_MODEM_TIME_BUILD = 30
    private var bConnected: String =  ""
    private var dbm: String =  ""
    private var rsrp: String =  ""
    private var rssnr: String =  ""
    private var rssi: String =  ""
    private var ta: String =  ""
    private var rsrq: String =  ""
    private var asu: String =  ""
    private var cqi: String =  ""
    private var level: String =  ""

    private var cellIdentity: String = ""
    private var bands: ArrayList<Int> = ArrayList()
    private var earfcn: String = ""
    private var pci: String = ""
    private var tac: String = ""
    private var bandwidth: String = ""
    private var mcc: String? = ""
    private var mnc: String? = ""
    private var modemTime: String = ""
    private var elapsedTime: String =  ""

    init {
        this.bConnected = cellInfo.isRegistered.toString()
        this.dbm = cellInfo.cellSignalStrength.dbm.toString()

        this.rsrp = cellInfo.cellSignalStrength.rsrp.toString()
        if(cellInfo.cellSignalStrength.rsrp == CellInfo.UNAVAILABLE)
        {
            this.rsrp = "Unavailable"
        }
        if (android.os.Build.VERSION.SDK_INT >= MIN_RSSI_BUILD)
        {
            this.rssi = cellInfo.cellSignalStrength.rssi.toString()
            if(cellInfo.cellSignalStrength.rssi == CellInfo.UNAVAILABLE)
            {
                this.rssi = "Unavailable"
            }
        }
        else
        {
            this.rssi = "Not supported. API version >= $MIN_RSSI_BUILD required."
        }
        this.ta = cellInfo.cellSignalStrength.timingAdvance.toString()
        if(cellInfo.cellSignalStrength.timingAdvance == CellInfo.UNAVAILABLE)
        {
            this.ta = "Unavailable"
        }
        this.rssnr = cellInfo.cellSignalStrength.rssnr.toString()
        if(cellInfo.cellSignalStrength.rssnr == CellInfo.UNAVAILABLE)
        {
            this.rssnr = "Unavailable"
        }
        this.rsrq = cellInfo.cellSignalStrength.rsrq.toString()
        if(cellInfo.cellSignalStrength.rsrq == CellInfo.UNAVAILABLE)
        {
            this.rsrq = "Unavailable"
        }
        this.asu = cellInfo.cellSignalStrength.asuLevel.toString()
        if(cellInfo.cellSignalStrength.asuLevel == CellInfo.UNAVAILABLE)
        {
            this.asu = "Unavailable"
        }
        this.cqi = cellInfo.cellSignalStrength.cqi.toString()
        if(cellInfo.cellSignalStrength.cqi == CellInfo.UNAVAILABLE)
        {
            this.cqi = "Unavailable"
        }
        this.level = cellInfo.cellSignalStrength.level.toString()
        this.cellIdentity = cellInfo.cellIdentity.ci.toString()
        if(cellInfo.cellIdentity.ci == CellInfo.UNAVAILABLE)
        {
            this.cellIdentity = "Unavailable"
        }
        if (android.os.Build.VERSION.SDK_INT >= MIN_BANDS_BUILD)
        {
            for(band in cellInfo.cellIdentity.bands)
            {
                this.bands.add(band)
            }
        }

        this.earfcn = cellInfo.cellIdentity.earfcn.toString()
        if(cellInfo.cellIdentity.earfcn == CellInfo.UNAVAILABLE)
        {
            this.earfcn = "Unavailable"
        }
        this.pci = cellInfo.cellIdentity.pci.toString()
        if(cellInfo.cellIdentity.pci == CellInfo.UNAVAILABLE)
        {
            this.pci = "Unavailable"
        }
        this.tac = cellInfo.cellIdentity.tac.toString()
        if(cellInfo.cellIdentity.tac == CellInfo.UNAVAILABLE)
        {
            this.tac = "Unavailable"
        }
        this.bandwidth = cellInfo.cellIdentity.bandwidth.toString()
        if(cellInfo.cellIdentity.bandwidth == CellInfo.UNAVAILABLE)
        {
            this.bandwidth = "Unavailable"
        }
        this.mcc = cellInfo.cellIdentity.mccString
        if(cellInfo.cellIdentity.mccString.isNullOrEmpty())
        {
            this.mcc = "Unavailable"
        }
        this.mnc = cellInfo.cellIdentity.mncString
        if(cellInfo.cellIdentity.mncString.isNullOrEmpty())
        {
            this.mnc = "Unavailable"
        }
        if (android.os.Build.VERSION.SDK_INT >= MIN_MODEM_TIME_BUILD)
        {
            this.modemTime = (cellInfo.timestampMillis - refTime / Math.pow(10.0, 6.0) / Math.pow(10.0, 3.0)).toString()
        }
        else
        {
            this.modemTime = ((cellInfo.timeStamp - refTime)/Math.pow(10.0, 9.0)).toString()
            //this.modemTime = "Not supported. API version >= $MIN_MODEM_TIME_BUILD required."
        }
        this.elapsedTime = ((SystemClock.elapsedRealtimeNanos() - refTime) / Math.pow(10.0, 9.0)).toString()
    }

    private fun get_modes(band_numbers: ArrayList<Int>): ArrayList<String>{
        val modes = ArrayList<String>()
        for (band_number in band_numbers){
            var mode = "TDD"
            if((band_number >= 1 && band_number <= 32) || (band_number >= 65 && band_number <= 85))
            {
                mode = "FDD"
            }
            modes.add(mode)
        }
        return modes
    }

    private fun band_num_to_description(band_numbers: ArrayList<Int>): String{
        var bands_description = ""
        for (band in band_numbers){
           val band = when (band) {
                1 -> "Band 1: FDD, 2100 MHz (Uplink: 1920 - 1980 MHz, Downlink: 2110 - 2170 MHz)"
                2 -> "Band 2: FDD, 1900 MHz (Uplink: 1850 - 1910 MHz, Downlink: 1930 - 1990 MHz)"
                3 -> "Band 3: FDD, 1800 MHz (Uplink: 1710 - 1785 MHz, Downlink: 1805 - 1880 MHz)"
                4 -> "Band 4: FDD, 1700 MHz (Uplink: 1710 - 1755 MHz, Downlink: 2110 - 2155 MHz)"
                // Add more cases for other bands
                else -> "Unknown Band"
        }
            bands_description += band + " | "
        }
        if (!bands_description.isEmpty()) {
            bands_description = bands_description.substring(0, bands_description.length - 2)
        }
        return bands_description
    }

    public fun toCSVString(settingsHandler: SettingsHandler): String{
        var csvString = (Constants.BS_INFO_START_MARKER + "," + Constants.LTE_4G_LOG_STRING  + ","  + this.bConnected + "," + this.elapsedTime + "," + this.modemTime)
        if(settingsHandler.LTE_Log_dBm)
        {
            csvString += "," + this.dbm
        }
        csvString += "," + this.rssnr
        if(settingsHandler.LTE_Log_RSRP)
        {
            csvString += "," + this.rsrp
        }
        if(settingsHandler.LTE_Log_RSRQ)
        {
            csvString += "," + this.rsrq
        }
        if(settingsHandler.LTE_Log_RSSI)
        {
            csvString += "," + this.rssi
        }
        if(settingsHandler.LTE_Log_CQI)
        {
            csvString += "," + this.cqi
        }
        if(settingsHandler.LTE_Log_ASU)
        {
            csvString += "," + this.asu
        }
        if(settingsHandler.LTE_Log_EARFCN)
        {
            csvString += "," + this.earfcn
        }
        if(settingsHandler.LTE_Log_PCI)
        {
            csvString += "," + this.pci
        }
        if(settingsHandler.LTE_Log_TA)
        {
            csvString += "," + this.ta
        }
        if(settingsHandler.LTE_Log_CI)
        {
            csvString += "," + this.cellIdentity
        }
        csvString += "," + this.tac
        csvString += "," + this.bandwidth
        csvString += "," + this.mcc
        csvString += "," + this.mnc
        csvString += "," + Constants.BS_INFO_STOP_MARKER
        return csvString
    }

    public fun toJSON(): JSONObject{
        val jsonObject = JSONObject()

        // Add key-value pairs to the JSON object
        jsonObject.put("technology", Constants.LTE_4G_LOG_STRING)
        jsonObject.put("dbm", this.dbm)
        jsonObject.put("rssnr", this.rssnr)
        jsonObject.put("rsrp", this.rsrp)
        jsonObject.put("rsrq", this.rsrq)
        jsonObject.put("rssi", this.rssi)
        jsonObject.put("cqi", this.cqi)
        jsonObject.put("asu", this.asu)
        jsonObject.put("earfcn", this.earfcn)
        jsonObject.put("pci", this.pci)
        jsonObject.put("ta", this.ta)
        jsonObject.put("ci", this.cellIdentity)
        jsonObject.put("tac", this.tac)
        jsonObject.put("bandwidth", this.bandwidth)
        jsonObject.put("bands", this.bands)
        jsonObject.put("modes", this.get_modes(this.bands))
        jsonObject.put("bands_description", this.band_num_to_description(this.bands))
        jsonObject.put("mcc", this.mcc)
        jsonObject.put("mnc", this.mnc)
        return jsonObject
    }

    @RequiresApi(Build.VERSION_CODES.N)
    public fun toDisplayString(): String
    {
        var displayString = "\ndBm = " + this.dbm
        displayString += "\nRSSNR = " + this.rssnr
        displayString += "\nRSRP = " + this.rsrp
        displayString += "\nRSRQ = " + this.rsrq
        displayString += "\nRSSI = " + this.rssi
        displayString += "\nCQI = " + this.cqi
        displayString += "\nASU = " + this.asu
        displayString += "\nPCI = " + this.pci
        displayString += "\nTiming advance = " + this.ta
        displayString += "\nEARFCN = " + this.earfcn
        displayString += "\nTracking area code = " + this.tac
        displayString += "\nCell identity = " + this.cellIdentity
        displayString += "\nBandwidth = " + this.bandwidth
        displayString += "\nModes = " + this.get_modes(this.bands).joinToString()
        displayString += "\nBands = " + this.band_num_to_description(this.bands)
        displayString += "\nMobile country code = " + this.mcc
        displayString += "\nMobile network code = " + this.mnc
        return displayString
    }
}



