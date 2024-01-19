package com.example.myapplication

import android.telephony.TelephonyManager
import org.json.JSONObject

class GeneralConnectionInfo(telephonyManager: TelephonyManager) {
    private val networkOperatorName:String
    private val simOperatorName:String
    private var simCarrierIdName:String
    private var cellTech: String = getNetworkType(telephonyManager.dataNetworkType)

    init {
        this.networkOperatorName = telephonyManager.networkOperatorName
        this.simOperatorName = telephonyManager.simOperatorName
        this.simCarrierIdName = "Unknown"
        if(!telephonyManager.simCarrierIdName.isNullOrBlank()){
            this.simCarrierIdName = telephonyManager.simCarrierIdName as String
        }
    }

    private fun getNetworkType(networkType:Int):String{
        return when (networkType) {
            TelephonyManager.NETWORK_TYPE_1xRTT -> "1xRTT"
            TelephonyManager.NETWORK_TYPE_CDMA -> "CDMA"
            TelephonyManager.NETWORK_TYPE_EDGE -> "EDGE"
            TelephonyManager.NETWORK_TYPE_EHRPD -> "eHRPD"
            TelephonyManager.NETWORK_TYPE_EVDO_0 -> "EVDO revision 0"
            TelephonyManager.NETWORK_TYPE_EVDO_A -> "EVDO revision A"
            TelephonyManager.NETWORK_TYPE_EVDO_B -> "EVDO revision B"
            TelephonyManager.NETWORK_TYPE_GPRS -> "GPRS"
            TelephonyManager.NETWORK_TYPE_GSM -> "GSM"
            TelephonyManager.NETWORK_TYPE_HSDPA -> "HSDPA"
            TelephonyManager.NETWORK_TYPE_HSPA -> "HSPA"
            TelephonyManager.NETWORK_TYPE_HSPAP -> "HSPA+"
            TelephonyManager.NETWORK_TYPE_HSUPA -> "HSUPA"
            TelephonyManager.NETWORK_TYPE_IDEN -> "iDen"
            TelephonyManager.NETWORK_TYPE_IWLAN -> "IWLAN"
            TelephonyManager.NETWORK_TYPE_LTE -> "LTE"
            TelephonyManager.NETWORK_TYPE_NR -> "NR"
            TelephonyManager.NETWORK_TYPE_TD_SCDMA -> "TD_SCDMA"
            TelephonyManager.NETWORK_TYPE_UMTS -> "UMTS"
            TelephonyManager.NETWORK_TYPE_UNKNOWN -> "Unknown"
            else -> "Unknown"
        }
    }

    public fun toCSVString(): String{
        var csvString:String = this.networkOperatorName + ","
        csvString += this.simOperatorName + ","
        csvString += this.simCarrierIdName
        return csvString
    }

    public fun toJSONObj(): JSONObject{
        val jsonObject = JSONObject()
        jsonObject.put("network_operator",this.networkOperatorName)
        jsonObject.put("sim_operator", this.simOperatorName)
        jsonObject.put("sim_carrier_id", this.simCarrierIdName)
        return jsonObject
    }

    public fun toDisplayString(): String{
        var displayString:String = "\nNetwork operator name = " + this.networkOperatorName
        displayString += "\nSIM operator name = " + this.simOperatorName
        displayString += "\nSIM carrier ID name = " + this.simCarrierIdName
        displayString += "\nCellular Technology = " + this.cellTech
        return displayString
    }
}


