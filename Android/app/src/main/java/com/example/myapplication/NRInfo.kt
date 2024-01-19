package com.example.myapplication

import android.os.Build
import android.telephony.CellIdentityNr
import android.telephony.CellInfo
import android.telephony.CellInfoNr
import android.telephony.CellSignalStrengthNr
import androidx.annotation.RequiresApi
import org.json.JSONObject

class NRInfo(cellInfo: CellInfoNr, refTime: Long) {
    var bConnected: String
    var nci: String
    var nrarfcn: String
    var pci: String
    var tac: String
    var bands: String
    var mcc: String?
    var mnc: String?

    var csi_rsrp: String
    var csi_rsrq: String
    var csi_sinr: String
//    val csi_cqi_report: List<Int>,
//    val csi_cqi_table_index: Int,

    var ss_rsrp: String
    var ss_rsrq: String
    var ss_sinr: String

    var asu: String
    var dbm: String
    var level: String

    var modemTime: String

    init {
        this.bConnected = cellInfo.isRegistered.toString()

        this.nci = (cellInfo.cellIdentity as CellIdentityNr).nci.toString()
        if((cellInfo.cellIdentity as CellIdentityNr).nci == CellInfo.UNAVAILABLE_LONG)
        {
            this.nci = "Unavailable"
        }

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

        this.csi_rsrp = (cellInfo.cellSignalStrength as CellSignalStrengthNr).csiRsrp.toString()
        if((cellInfo.cellIdentity as CellSignalStrengthNr).csiRsrp == CellInfo.UNAVAILABLE)
        {
            this.csi_rsrp = "Unavailable"
        }

        this.csi_rsrq = (cellInfo.cellSignalStrength as CellSignalStrengthNr).csiRsrq.toString()
        if((cellInfo.cellIdentity as CellSignalStrengthNr).csiRsrq == CellInfo.UNAVAILABLE)
        {
            this.csi_rsrq = "Unavailable"
        }

        this.csi_sinr = (cellInfo.cellSignalStrength as CellSignalStrengthNr).csiSinr.toString()
        if((cellInfo.cellIdentity as CellSignalStrengthNr).csiSinr == CellInfo.UNAVAILABLE)
        {
            this.csi_sinr = "Unavailable"
        }

        this.ss_rsrp = (cellInfo.cellSignalStrength as CellSignalStrengthNr).ssRsrp.toString()
        if((cellInfo.cellIdentity as CellSignalStrengthNr).ssRsrp == CellInfo.UNAVAILABLE)
        {
            this.ss_rsrp = "Unavailable"
        }

        this.ss_rsrq = (cellInfo.cellSignalStrength as CellSignalStrengthNr).ssRsrq.toString()
        if((cellInfo.cellIdentity as CellSignalStrengthNr).ssRsrq == CellInfo.UNAVAILABLE)
        {
            this.ss_rsrq = "Unavailable"
        }

        this.ss_sinr = (cellInfo.cellSignalStrength as CellSignalStrengthNr).ssSinr.toString()
        if((cellInfo.cellIdentity as CellSignalStrengthNr).ssSinr == CellInfo.UNAVAILABLE)
        {
            this.ss_sinr = "Unavailable"
        }

        this.asu = (cellInfo.cellSignalStrength as CellSignalStrengthNr).asuLevel.toString()
        if((cellInfo.cellIdentity as CellSignalStrengthNr).asuLevel == CellInfo.UNAVAILABLE)
        {
            this.asu = "Unavailable"
        }

        this.dbm = (cellInfo.cellSignalStrength as CellSignalStrengthNr).dbm.toString()
        if((cellInfo.cellIdentity as CellSignalStrengthNr).dbm == CellInfo.UNAVAILABLE)
        {
            this.dbm = "Unavailable"
        }

        this.level = (cellInfo.cellSignalStrength as CellSignalStrengthNr).level.toString()
        this.modemTime = ((cellInfo.timestampMillis - (refTime / Math.pow(10.0, 6.0))) / Math.pow(10.0, 3.0)).toString()
    }

    public fun toCSVString(): String{
        val csvString = (Constants.BS_INFO_START_MARKER
                + "," + this.modemTime
                + "," + Constants.NR_5G_SA_LOG_STRING
                + "," + this.bConnected
                + "," + this.dbm
                + "," + this.csi_rsrp
                + "," + this.csi_rsrq
                + "," + this.csi_sinr
                + "," + this.ss_rsrp
                + "," + this.ss_rsrq
                + "," + this.ss_sinr
                + "," + this.level
                + "," + this.asu
                + "," + this.nci
                + "," + this.nrarfcn
                + "," + this.pci
                + "," + this.tac
                + "," + this.bands
                + "," + this.mcc
                + "," + this.mnc
                + Constants.BS_INFO_STOP_MARKER)
        return csvString
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
        var displayString = "dBm = " + this.dbm
        displayString += "\nSS SINR = " + this.ss_sinr
        displayString += "\nSS RSRP = " + this.ss_rsrp
        displayString += "\nSS RSRQ = " + this.ss_rsrq
        displayString += "\nCSI SINR = " + this.csi_sinr
        displayString += "\nCSI RSRP = " + this.csi_rsrp
        displayString += "\nCSI RSRQ = " + this.csi_rsrq
        displayString += "\nRSRP in ASU = " + this.asu
        displayString += "\nPCI = " + this.pci
        displayString += "\nNRAFCN = " + this.nrarfcn
        displayString += "\nTracking area code = " + this.tac
        displayString += "\nNR cell id = " + this.nci
        displayString += "\nPhysical cell id = " + this.pci
        displayString += "\nBands = " + this.bands
        displayString += "\nMobile country code = " + this.mcc
        displayString += "\nMobile network code = " + this.mnc
        return displayString
    }
}