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
    private var dbm: Int = Int.MIN_VALUE
    private var rsrp: Int = Int.MIN_VALUE
    private var rssnr: Int =  Int.MIN_VALUE
    private var rssi: Int =  Int.MIN_VALUE
    private var ta: Int =  Int.MIN_VALUE
    private var rsrq: Int =  Int.MIN_VALUE
    private var asu: Int =  Int.MIN_VALUE
    private var cqi: Int =  Int.MIN_VALUE
    private var level: Int =  Int.MIN_VALUE

    private var cellIdentity: Int = Int.MIN_VALUE

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
        this.dbm = cellInfo.cellSignalStrength.dbm

        this.rsrp = cellInfo.cellSignalStrength.rsrp
        if (android.os.Build.VERSION.SDK_INT >= MIN_RSSI_BUILD)
        {
            this.rssi = cellInfo.cellSignalStrength.rssi
        }
//        else
//        {
//            this.rssi = "Not supported. API version >= $MIN_RSSI_BUILD required."
//        }
        this.ta = cellInfo.cellSignalStrength.timingAdvance
        this.rssnr = cellInfo.cellSignalStrength.rssnr
        this.rsrq = cellInfo.cellSignalStrength.rsrq
        this.asu = cellInfo.cellSignalStrength.asuLevel
        this.cqi = cellInfo.cellSignalStrength.cqi
        this.level = cellInfo.cellSignalStrength.level
        this.cellIdentity = cellInfo.cellIdentity.ci
        if (android.os.Build.VERSION.SDK_INT >= MIN_BANDS_BUILD)
        {
            for(band in cellInfo.cellIdentity.bands)
            {
                this.bands.add(band)
            }
        }

        this.earfcn = cellInfo.cellIdentity.earfcn.toString()
        if(cellInfo.cellIdentity.earfcn == Int.MIN_VALUE)
        {
            this.earfcn = "Unavailable"
        }
        this.pci = cellInfo.cellIdentity.pci.toString()
        if(cellInfo.cellIdentity.pci == Int.MIN_VALUE)
        {
            this.pci = "Unavailable"
        }
        this.tac = cellInfo.cellIdentity.tac.toString()
        if(cellInfo.cellIdentity.tac == Int.MIN_VALUE)
        {
            this.tac = "Unavailable"
        }
        this.bandwidth = cellInfo.cellIdentity.bandwidth.toString()
        if(cellInfo.cellIdentity.bandwidth == Int.MIN_VALUE)
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

    fun bandnumber_to_uplink_frequencies(bandNumber: Int): Pair<Double, Double> {
        return when (bandNumber) {
            1 -> Pair(1920.0, 1980.0)
            2 -> Pair(1850.0, 1910.0)
            3 -> Pair(1710.0, 1785.0)
            4 -> Pair(1710.0, 1755.0)
            5 -> Pair(824.0, 849.0)
            6 -> Pair(830.0, 840.0)
            7 -> Pair(2500.0, 2570.0)
            8 -> Pair(880.0, 915.0)
            9 -> Pair(1749.0, 1784.0)
            10 -> Pair(1710.0, 1770.0)
            11 -> Pair(1427.0, 1447.0)
            12 -> Pair(698.0, 716.0)
            13 -> Pair(777.0, 787.0)
            14 -> Pair(788.0, 798.0)
            17 -> Pair(704.0, 716.0)
            18 -> Pair(815.0, 830.0)
            19 -> Pair(830.0, 845.0)
            20 -> Pair(832.0, 862.0)
            21 -> Pair(1447.0, 1462.0)
            22 -> Pair(3410.0, 3500.0)
            23 -> Pair(2000.0, 2020.0)
            24 -> Pair(1626.5, 1660.5)
            25 -> Pair(1850.0, 1915.0)
            26 -> Pair(814.0, 849.0)
            27 -> Pair(807.0, 824.0)
            28 -> Pair(703.0, 748.0)
            29 -> Pair(717.0, 728.0)
            30 -> Pair(2305.0, 2315.0)
            31 -> Pair(452.5, 457.5)
            32 -> Pair(703.0, 748.0)
            33 -> Pair(1900.0, 1920.0)
            34 -> Pair(2010.0, 2025.0)
            35 -> Pair(1850.0, 1910.0)
            36 -> Pair(1930.0, 1990.0)
            37 -> Pair(1910.0, 1930.0)
            38 -> Pair(2570.0, 2620.0)
            39 -> Pair(1880.0, 1920.0)
            40 -> Pair(2300.0, 2400.0)
            41 -> Pair(2496.0, 2690.0)
            42 -> Pair(3400.0, 3600.0)
            43 -> Pair(3600.0, 3800.0)
            44 -> Pair(703.0, 803.0)
            45 -> Pair(1447.0, 1462.0)
            46 -> Pair(5150.0, 5925.0)
            47 -> Pair(5150.0, 5925.0)
            48 -> Pair(3550.0, 3700.0)
            49 -> Pair(3510.0, 3550.0)
            50 -> Pair(1432.0, 1517.0)
            51 -> Pair(1427.0, 1432.0)
            52 -> Pair(3300.0, 3800.0)
            53 -> Pair(2483.5, 2500.0)
            54 -> Pair(1880.0, 1920.0)
            55 -> Pair(1710.0, 1755.0)
            56 -> Pair(703.0, 803.0)
            57 -> Pair(1447.0, 1467.0)
            58 -> Pair(2810.0, 2860.0)
            59 -> Pair(3590.0, 3690.0)
            60 -> Pair(2300.0, 2400.0)
            61 -> Pair(1500.0, 1520.0)
            62 -> Pair(5150.0, 5925.0)
            63 -> Pair(1515.0, 1525.0)
            64 -> Pair(703.0, 803.0)
            65 -> Pair(1920.0, 2010.0)
            66 -> Pair(1710.0, 1780.0)
            else -> Pair((Int.MIN_VALUE).toDouble(), (Int.MIN_VALUE).toDouble())
        }
    }

    private fun bandnumber_to_downlink_frequencies(bandNumber: Int): Pair<Double, Double> {
        return when(bandNumber) {
            1 -> Pair(1920.0, 2110.0)
            2 -> Pair(1850.0, 1910.0)
            3 -> Pair(1710.0, 1785.0)
            4 -> Pair(1710.0, 1755.0)
            5 -> Pair(824.0, 849.0)
            6 -> Pair(830.0, 840.0)
            7 -> Pair(2500.0, 2690.0)
            8 -> Pair(880.0, 915.0)
            9 -> Pair(1749.0, 1784.0)
            10 -> Pair(1710.0, 1770.0)
            11 -> Pair(1427.0, 1447.9)
            12 -> Pair(699.0, 716.0)
            13 -> Pair(777.0, 787.0)
            14 -> Pair(788.0, 798.0)
            17 -> Pair(704.0, 716.0)
            18 -> Pair(815.0, 830.0)
            19 -> Pair(830.0, 845.0)
            20 -> Pair(832.0, 862.0)
            21 -> Pair(1447.9, 1462.9)
            22 -> Pair(3410.0, 3500.0)
            23 -> Pair(2000.0, 2020.0)
            24 -> Pair(1626.5, 1660.5)
            25 -> Pair(1850.0, 1915.0)
            26 -> Pair(814.0, 849.0)
            27 -> Pair(807.0, 824.0)
            28 -> Pair(703.0, 748.0)
            29 -> Pair(717.0, 728.0)
            30 -> Pair(2305.0, 2315.0)
            31 -> Pair(452.5, 457.5)
            32 -> Pair(1452.0, 1496.0)
            33 -> Pair(1900.0, 1920.0)
            34 -> Pair(2010.0, 2025.0)
            35 -> Pair(1850.0, 1910.0)
            36 -> Pair(1930.0, 1990.0)
            37 -> Pair(1910.0, 1930.0)
            38 -> Pair(2570.0, 2620.0)
            39 -> Pair(1880.0, 1920.0)
            40 -> Pair(2300.0, 2400.0)
            41 -> Pair(2496.0, 2690.0)
            42 -> Pair(3400.0, 3600.0)
            43 -> Pair(3600.0, 3800.0)
            44 -> Pair(703.0, 803.0)
            45 -> Pair(1447.9, 1462.9)
            46 -> Pair(5150.0, 5925.0)
            47 -> Pair(5855.0, 5925.0)
            48 -> Pair(3550.0, 3700.0)
            49 -> Pair(3550.0, 3700.0)
            50 -> Pair(1432.0, 1517.0)
            51 -> Pair(1427.0, 1432.0)
            52 -> Pair(3300.0, 3800.0)
            53 -> Pair(2496.0, 2690.0)
            54 -> Pair(1710.0, 1780.0)
            55 -> Pair(3550.0, 3700.0)
            56 -> Pair(3550.0, 3700.0)
            57 -> Pair(3550.0, 3700.0)
            58 -> Pair(3550.0, 3700.0)
            59 -> Pair(3550.0, 3700.0)
            60 -> Pair(3550.0, 3700.0)
            61 -> Pair(3550.0, 3700.0)
            62 -> Pair(3550.0, 3700.0)
            63 -> Pair(3550.0, 3700.0)
            64 -> Pair(3550.0, 3700.0)
            65 -> Pair(1920.0, 2010.0)
            66 -> Pair(1710.0, 1780.0)
            else -> Pair(Int.MIN_VALUE.toDouble(), Int.MIN_VALUE.toDouble())
        }
    }

    private fun band_num_to_description(band_numbers: ArrayList<Int>): String{
        var bands_description = ""
        for (band_number in band_numbers){
            val uplink_frequecies = bandnumber_to_uplink_frequencies(band_number)
            val downlink_frequencies  = bandnumber_to_downlink_frequencies(band_number)
            val band_description = "Band Number = ${band_number}, Uplink = ${uplink_frequecies.first} - ${uplink_frequecies.second} MHz, Downlink = ${downlink_frequencies.first} - ${downlink_frequencies.second} MHz";
            bands_description += band_description + " | "
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
        jsonObject.put("level", this.level)
        jsonObject.put("bandwidth", this.bandwidth)
        jsonObject.put("bands", this.bands)
        jsonObject.put("modes", this.get_modes(this.\bands))
        jsonObject.put("bands_description", this.band_num_to_description(this.bands))
        jsonObject.put("mcc", this.mcc)
        jsonObject.put("mnc", this.mnc)
        jsonObject.put("is_connected", this.bConnected)
        return jsonObject
    }

    @RequiresApi(Build.VERSION_CODES.N)
    public fun toDisplayString(): String
    {
        var displayString = "\ndBm = " + this.dbm.toString()
        displayString += "\nRSSNR = " + this.rssnr.toString()
        displayString += "\nRSRP = " + this.rsrp.toString()
        displayString += "\nRSRQ = " + this.rsrq.toString()
        displayString += "\nRSSI = " + this.rssi.toString()
        displayString += "\nCQI = " + this.cqi.toString()
        displayString += "\nASU = " + this.asu.toString()
        displayString += "\nPCI = " + this.pci
        displayString += "\nTiming advance = " + this.ta
        displayString += "\nEARFCN = " + this.earfcn
        displayString += "\nLevel = " + this.level
        displayString += "\nTracking area code = " + this.tac
        displayString += "\nCell identity = " + this.cellIdentity.toString()
        displayString += "\nBandwidth = " + this.bandwidth
        displayString += "\nModes = " + this.get_modes(this.bands).joinToString()
        displayString += "\nBands = " + this.band_num_to_description(this.bands)
        displayString += "\nMobile country code = " + this.mcc
        displayString += "\nMobile network code = " + this.mnc
        return displayString
    }
}



