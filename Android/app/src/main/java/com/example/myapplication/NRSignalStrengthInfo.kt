package com.example.myapplication

import android.os.Build
import android.telephony.CellInfo
import android.telephony.CellSignalStrengthLte
import android.telephony.CellSignalStrengthNr
import android.telephony.SignalStrength
import androidx.annotation.RequiresApi

class NRSignalStrengthInfo(signalStrength: SignalStrength?) {
    var nrType:String  = ""
    private var csi_rsrp: String = ""
    private var csi_rsrq: String = ""
    private var csi_sinr: String = ""

    private var ss_rsrp: String = ""
    private var ss_rsrq: String = ""
    private var ss_sinr: String = ""

    private var asu: String = ""
    private var dbm: String = ""
    private var level: String = ""

    init{
        if (signalStrength != null)
        {
            val lteSS = signalStrength.getCellSignalStrengths(CellSignalStrengthLte::class.java)
            val nrSS = signalStrength.getCellSignalStrengths(CellSignalStrengthNr::class.java)
            signalStrength.getCellSignalStrengths(CellSignalStrengthNr::class.java)
            if (nrSS.isNotEmpty() && lteSS.isNotEmpty())
            {
                this.nrType = Constants.NR_5G_NSA_LOG_STRING
            }
            else if (nrSS.isNotEmpty() && lteSS.isEmpty())
            {
                this.nrType = Constants.NR_5G_SA_LOG_STRING
            }
            if(nrSS.isNotEmpty())
            {
                this.csi_rsrp = nrSS[0].csiRsrp.toString()
                if(nrSS[0].csiRsrp == CellInfo.UNAVAILABLE)
                {
                    this.csi_rsrp = "Unavailable"
                }
                this.csi_rsrq = nrSS[0].csiRsrq.toString()
                if(nrSS[0].csiRsrq == CellInfo.UNAVAILABLE)
                {
                    this.csi_rsrq = "Unavailable"
                }
                this.csi_sinr = nrSS[0].csiSinr.toString()
                if(nrSS[0].csiSinr == CellInfo.UNAVAILABLE)
                {
                    this.csi_sinr = "Unavailable"
                }
                this.ss_rsrp = nrSS[0].ssRsrp.toString()
                if(nrSS[0].ssRsrp == CellInfo.UNAVAILABLE)
                {
                    this.ss_rsrp = "Unavailable"
                }
                this.ss_rsrq = nrSS[0].ssRsrq.toString()
                if(nrSS[0].ssRsrq == CellInfo.UNAVAILABLE)
                {
                    this.ss_rsrq = "Unavailable"
                }
                this.ss_sinr = nrSS[0].ssSinr.toString()
                if(nrSS[0].ssSinr == CellInfo.UNAVAILABLE)
                {
                    this.ss_sinr = "Unavailable"
                }
                this.asu = nrSS[0].asuLevel.toString()
                if(nrSS[0].asuLevel == CellInfo.UNAVAILABLE)
                {
                    this.asu = "Unavailable"
                }
                this.level = nrSS[0].level.toString()
                if(nrSS[0].level == CellInfo.UNAVAILABLE)
                {
                    this.level = "Unavailable"
                }
            }
        }
    }

    public fun toCSVString(): String{
        var csvString = ""
        if (this.nrType.isNotEmpty()) {
            csvString = (Constants.BS_INFO_START_MARKER +  ","
                    + this.nrType +  ","
                    + this.dbm + ","
                    + this.csi_rsrp + ","
                    + this.csi_rsrq+ ","
                    + this.csi_sinr + ","
                    + this.ss_rsrp + ","
                    + this.ss_rsrq + ","
                    + this.ss_sinr + ","
                    + this.level + ","
                    + this.asu + ","
                    + Constants.BS_INFO_STOP_MARKER)
        }
        return csvString
    }

    @RequiresApi(Build.VERSION_CODES.N)
    public fun toDisplayString(): String {
        var displayString = ""
        if (this.nrType.isNotEmpty()) {
             displayString = ("\nNR Type = " + this.nrType
                    + "\nNR dBm = " + this.dbm
                    + "\nNR CSI RSRP = " + this.csi_rsrp
                    + "\nNR CSI RSRQ = " + this.csi_rsrq
                    + "\nNR CSI SINR = " + this.csi_sinr
                    + "\nNR SS RSRP = " + this.ss_rsrp
                    + "\nNR SS RSRQ = " + this.ss_rsrq
                    + "\nNR SS SINR = " + this.ss_sinr
                    + "\nNR SS Level = " + this.level
                    + "\nNR ASU = " + this.asu)
        }
        return displayString
    }
  }