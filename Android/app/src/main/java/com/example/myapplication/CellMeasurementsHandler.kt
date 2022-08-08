package com.example.myapplication

import android.icu.text.SimpleDateFormat
import android.os.SystemClock
import android.telephony.CellInfo
import android.telephony.CellInfoLte
import android.telephony.CellInfoNr
import android.telephony.TelephonyManager
import com.example.myapplication.Constants.CELL_LOG_START_MARKER
import com.example.myapplication.Constants.CELL_LOG_STOP_MARKER
import java.util.*

class CellMeasurementsHandler {
    fun getInfo(telephonyManager: TelephonyManager, settings:SettingsHandler, stringFormat:String, bOnlyConnectedBS:Boolean, startNanoSec:Long):String
    {
        val allCellInfo = telephonyManager.allCellInfo
        var infoString:String = ""
        if(stringFormat ==  "csv")
        {
            infoString += CELL_LOG_START_MARKER + ","
            infoString += ((SystemClock.elapsedRealtimeNanos() - startNanoSec) / Math.pow(10.0, 9.0)).toString() + ","
            infoString += GeneralConnectionInfo(telephonyManager).toCSVString()
        }
        else if(stringFormat == "display")
        {
              val sdf = SimpleDateFormat("dd/M/yyyy hh:mm:ss")
              val currentDate = sdf.format(Date())
              infoString +=  currentDate + "\n\nNumber of base stations detected = " + allCellInfo.size.toString() + "\n"
            if(android.os.Build.VERSION.SDK_INT < Constants.MIN_NR_SIG_STRENGTH_API_VERSION)
            {
            infoString += "\n5G cellular info cannot be detected on this device. Support for API version >= ${Constants.MIN_NR_SIG_STRENGTH_API_VERSION} required.\n"
            }
        }
        if(!bOnlyConnectedBS)
        {
            val itr = allCellInfo.listIterator()
            while (itr.hasNext())
            {
                val cellInfo = itr.next()
                if(stringFormat == "csv")
                {
                    infoString += ","
                }
                else if(stringFormat == "display")
                {
                    infoString += "Number of base stations detected = " + allCellInfo.size.toString()
                    infoString += "\n---\n"
                }
                infoString += getCellInfo(cellInfo, settings, stringFormat, startNanoSec)
            }
            infoString += getNRSigStrengthInfo(telephonyManager, stringFormat)
        }
        else if(allCellInfo.size > 0)
        {
            val registeredCellInfo = getRegisteredCellInfo(allCellInfo)
            if(stringFormat == "display")
            {
                infoString += "\nFor the connected base station:"
                infoString += GeneralConnectionInfo(telephonyManager).toDisplayString()
            }
            infoString += getCellInfo(registeredCellInfo, settings, stringFormat, startNanoSec)
        }
        if(stringFormat == "csv"){
            infoString += "," + CELL_LOG_STOP_MARKER
        }
        return infoString
    }

    private fun getNRSigStrengthInfo(telephonyManager: TelephonyManager, stringFormat: String):String
    {
        var infoString = ""
        if (telephonyManager.signalStrength != null && android.os.Build.VERSION.SDK_INT >= Constants.MIN_SIG_STRENGTH_API_VERSION) {
            val nrSSInfo = NRSignalStrengthInfo(telephonyManager.signalStrength)
            if (nrSSInfo.nrType.isNotEmpty())
            {
                if(stringFormat == "csv") {
                    infoString += "," + nrSSInfo.toCSVString()
                }
                else if(stringFormat == "display") {
                    infoString += nrSSInfo.toDisplayString()
                }
            }
        }
        return infoString
    }

    private fun getCellInfo(cellInfo: CellInfo,  settings:SettingsHandler, stringFormat: String, startNanoSec:Long):String
    {
        var infoString = ""
        if (cellInfo is CellInfoLte)
        {
            val cellInfoLte = cellInfo as CellInfoLte
            val lteInfo = LTEInfo(cellInfoLte, startNanoSec)
            if(stringFormat == "csv")
            {
                infoString += lteInfo.toCSVString(settings)
            }
            else if(stringFormat == "display")
            {
                infoString += lteInfo.toDisplayString()
            }
        }
        else if (cellInfo is CellInfoNr && android.os.Build.VERSION.SDK_INT >= Constants.CELL_INFO_NR_MIN_API_VERSION)
        {
            val cellInfoNr = cellInfo as CellInfoNr
            val nrInfo = NRInfo(cellInfoNr, startNanoSec)
            if(stringFormat == "csv")
            {
                infoString += nrInfo.toCSVString()
            }
            else if(stringFormat == "display")
            {
                infoString += nrInfo.toDisplayString()
            }
        }
        return infoString
    }

    private fun getRegisteredCellInfo(allCellInfo: List<CellInfo>):CellInfo {
        var registeredCellInfo: CellInfo = allCellInfo.get(0)
        val itr = allCellInfo.listIterator()
        while (itr.hasNext()) {
            val cellInfo = itr.next()
            if (cellInfo.isRegistered) {
                registeredCellInfo = cellInfo
                return registeredCellInfo
            }
        }
        return registeredCellInfo
    }
}