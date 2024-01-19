package com.example.myapplication

import android.os.Environment
import java.io.File

class LogsHandler(logFolder:String)
{
    private var mlogFolder:String = logFolder;

    public fun appendToMeasurements(storagePermission:Boolean, campaignName:String, toAppend:String)
    {
        if(!storagePermission)
        {
            return
        }
        val path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS);
        val folderName = File(path, mlogFolder)
        folderName.mkdirs()
        val file = File(folderName, campaignName + "_log.txt")
        file.appendText(toAppend + "\n")
    }

    public fun appendToSummary(storagePermission:Boolean, campaignName:String, toAppend:String)
    {
        if(!storagePermission)
        {
            return
        }
        val path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS);
        val folderName = File(path, mlogFolder)
        folderName.mkdirs()
        val file = File(folderName, campaignName + "_summary.txt")
        file.appendText(toAppend + "\n")
    }

    public fun appendToLocation(storagePermission:Boolean, campaignName:String, toAppend:String)
    {
        if(!storagePermission)
        {
            return
        }
        val path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS);
        val folderName = File(path, mlogFolder)
        folderName.mkdirs()
        val file = File(folderName, campaignName + "_location.txt")
        file.appendText(toAppend + "\n")
    }

    public fun appendToDebug(storagePermission:Boolean, fileName:String, toAppend:String)
    {
        if(!storagePermission || !SettingsHandler.Debug)
        {
            return
        }
        val path = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOCUMENTS);
        val folderName = File(path, mlogFolder)
        folderName.mkdirs()
        val file = File(folderName, fileName + "_debug.txt")
        file.appendText(toAppend + "\n")
    }
}