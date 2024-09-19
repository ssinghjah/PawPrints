package com.example.myapplication

import android.os.Build
import android.telephony.CellIdentityNr
import android.telephony.CellInfo
import android.telephony.CellInfoNr
import android.telephony.CellSignalStrengthNr
import androidx.annotation.RequiresApi
import org.json.JSONObject

@RequiresApi(Build.VERSION_CODES.Q)
class NRInfo(cellInfo: CellInfoNr, refTime: Long) {
    var bConnected: String
    var nci: Long = Int.MIN_VALUE.toLong()
    var nrarfcn: String
    var pci: String
    var tac: String
    var bands: String
    var mcc: String?
    var mnc: String?

    var csi_rsrp: Int = Int.MIN_VALUE
    var csi_rsrq: Int =  Int.MIN_VALUE
    var csi_sinr: Int =  Int.MIN_VALUE
//    val csi_cqi_report: List<Int>,
//    val csi_cqi_table_index: Int,

    var ss_rsrp: Int =  Int.MIN_VALUE
    var ss_rsrq: Int =  Int.MIN_VALUE
    var ss_sinr: Int =  Int.MIN_VALUE

    var asu: Int =  Int.MIN_VALUE
    var dbm: Int =  Int.MIN_VALUE
    var level: Int =  Int.MIN_VALUE

    var modemTime: String

    init {
        this.bConnected = cellInfo.isRegistered.toString()
        this.nci = (cellInfo.cellIdentity as CellIdentityNr).nci
        this.nrarfcn = (cellInfo.cellIdentity as CellIdentityNr).nrarfcn.toString()
        if((cellInfo.cellIdentity as CellIdentityNr).nrarfcn == CellInfo.UNAVAILABLE)
        {
            this.nrarfcn = "Unavailable"
        }

        this.pci = (cellInfo.cellIdentity as CellIdentityNr).pci.toString()
        if((cellInfo.cellIdentity as CellIdentityNr).pci == CellInfo.UNAVAILABLE)
        {
            this.pci = "Unavailable"
        }

        this.tac = (cellInfo.cellIdentity as CellIdentityNr).tac.toString()
        if((cellInfo.cellIdentity as CellIdentityNr).tac == CellInfo.UNAVAILABLE)
        {
            this.tac = "Unavailable"
        }

        this.mcc = (cellInfo.cellIdentity as CellIdentityNr).mccString
        if(mcc.isNullOrEmpty())
        {
            this.mcc = "Unavailable"
        }

        this.mnc = (cellInfo.cellIdentity as CellIdentityNr).mncString
        if(this.mnc.isNullOrEmpty())
        {
            this.mnc = "Unavailable"
        }
        this.bands = (cellInfo.cellIdentity as CellIdentityNr).bands.toString()
        this.csi_rsrp = (cellInfo.cellSignalStrength as CellSignalStrengthNr).csiRsrp
        this.csi_rsrq = (cellInfo.cellSignalStrength as CellSignalStrengthNr).csiRsrq
        this.csi_sinr = (cellInfo.cellSignalStrength as CellSignalStrengthNr).csiSinr
        this.ss_rsrp = (cellInfo.cellSignalStrength as CellSignalStrengthNr).ssRsrp
        this.ss_rsrq = (cellInfo.cellSignalStrength as CellSignalStrengthNr).ssRsrq
        this.ss_sinr = (cellInfo.cellSignalStrength as CellSignalStrengthNr).ssSinr
        this.asu = (cellInfo.cellSignalStrength as CellSignalStrengthNr).asuLevel
        this.dbm = (cellInfo.cellSignalStrength as CellSignalStrengthNr).dbm
        this.level = (cellInfo.cellSignalStrength as CellSignalStrengthNr).level
        this.modemTime = ((cellInfo.timestampMillis - (refTime / Math.pow(10.0, 6.0))) / Math.pow(10.0, 3.0)).toString()
    }


    public fun toJSON(): JSONObject{
        val jsonObject = JSONObject()
        // Add key-value pairs to the JSON object
        jsonObject.put("technology", Constants.NR_5G_SA_LOG_STRING)
        jsonObject.put("dbm", this.dbm)
        jsonObject.put("csi_rsrp", this.csi_rsrp)
        jsonObject.put("csi_rsrq", this.csi_rsrq)
        jsonObject.put("csi_sinr", this.csi_sinr)
        jsonObject.put("ss_rsrp", this.ss_rsrp)
        jsonObject.put("ss_rsrq", this.ss_rsrq)
        jsonObject.put("ss_sinr", this.ss_sinr)
        jsonObject.put("level", this.level)
        jsonObject.put("asu", this.asu)
        jsonObject.put("nci", this.nci)
        jsonObject.put("pci", this.pci)
        jsonObject.put("tac", this.tac)
        jsonObject.put("bands", this.bands)
        jsonObject.put("bands", this.bands)
        jsonObject.put("mcc", this.mcc)
        jsonObject.put("mnc", this.mnc)
        return jsonObject
    }


    @RequiresApi(Build.VERSION_CODES.N)
    public fun toDisplayString(): String{
        var displayString = "dBm = " + this.dbm.toString()
        displayString += "\nSS SINR = " + this.ss_sinr.toString()
        displayString += "\nSS RSRP = " + this.ss_rsrp.toString()
        displayString += "\nSS RSRQ = " + this.ss_rsrq.toString()
        displayString += "\nCSI SINR = " + this.csi_sinr.toString()
        displayString += "\nCSI RSRP = " + this.csi_rsrp.toString()
        displayString += "\nCSI RSRQ = " + this.csi_rsrq.toString()
        displayString += "\nRSRP in ASU = " + this.asu.toString()
        displayString += "\nNRAFCN = " + this.nrarfcn
        displayString += "\nTracking area code = " + this.tac
        displayString += "\nNR cell id = " + this.nci.toString()
        displayString += "\nPhysical cell id = " + this.pci
        displayString += "\nBands = " + this.bands
        displayString += "\nMobile country code = " + this.mcc
        displayString += "\nMobile network code = " + this.mnc
        return displayString
    }
}