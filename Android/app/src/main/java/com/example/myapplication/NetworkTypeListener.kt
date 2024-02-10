package com.example.myapplication

import android.telephony.TelephonyCallback
import android.telephony.TelephonyDisplayInfo
import android.telephony.TelephonyManager

import java.util.concurrent.Executors

class NetworkTypeListener {

    public var mNetworkType = ""
    public var mNetworkOverrideType = ""

    private var mCallback = object : TelephonyCallback(), TelephonyCallback.DisplayInfoListener {
        override fun onDisplayInfoChanged(telephonyDisplayInfo: TelephonyDisplayInfo) {

            mNetworkType = when(telephonyDisplayInfo.networkType){
                TelephonyManager.NETWORK_TYPE_UNKNOWN -> "Unknown"
                TelephonyManager.NETWORK_TYPE_GPRS -> "GPRS"
                TelephonyManager.NETWORK_TYPE_EDGE -> "EDGE"
                TelephonyManager.NETWORK_TYPE_UMTS -> "UMTS"
                TelephonyManager.NETWORK_TYPE_CDMA -> "CDMA"
                TelephonyManager.NETWORK_TYPE_HSDPA -> "HSDPA"
                TelephonyManager.NETWORK_TYPE_LTE -> "LTE"
                TelephonyManager.NETWORK_TYPE_NR -> "NR"
                TelephonyManager.NETWORK_TYPE_GSM -> "GSM"
                TelephonyManager.NETWORK_TYPE_TD_SCDMA -> "TD-SCDMA"
                TelephonyManager.NETWORK_TYPE_IWLAN -> "IWLAN"
                TelephonyManager.NETWORK_TYPE_EVDO_0 -> "EVDO-0"
                TelephonyManager.NETWORK_TYPE_EVDO_A -> "EVDO-A"
                TelephonyManager.NETWORK_TYPE_EVDO_B -> "EDVO-B"
                else -> "Unknown"


            }
            mNetworkOverrideType = when(telephonyDisplayInfo.overrideNetworkType){
                TelephonyDisplayInfo.OVERRIDE_NETWORK_TYPE_LTE_CA -> "LTE-CA"
                TelephonyDisplayInfo.OVERRIDE_NETWORK_TYPE_NONE -> "None"
                TelephonyDisplayInfo.OVERRIDE_NETWORK_TYPE_NR_NSA -> "NR-NSA"
                TelephonyDisplayInfo.OVERRIDE_NETWORK_TYPE_NR_ADVANCED -> "NR-Advanced"
                TelephonyDisplayInfo.OVERRIDE_NETWORK_TYPE_LTE_ADVANCED_PRO -> "LTE-Advanced-Pro"
                else -> "Unknown"
            }
        }
    }



    public fun registerListener(telephonyManager: TelephonyManager)
    {
        // The thread Executor used to run the listener. This governs how threads are created and
        // reused. W use a single thread.
        val exec = Executors.newSingleThreadExecutor()

        // Register the callback
        telephonyManager.registerTelephonyCallback(exec, mCallback)
    }

    public fun deregisterListener(telephonyManager: TelephonyManager)
    {
        //telephonyManager.listen(mCallback, 0)
    }


    public fun getDisplayString(): String
    {
        var mDisplayString = "\n"
        mDisplayString += "Network Type: " + mNetworkType + "\n"
        mDisplayString += "Network Override Type: " + mNetworkOverrideType + "\n"
        return mDisplayString
    }

}