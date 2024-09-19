package com.example.myapplication

import android.Manifest
import android.content.Intent
import android.content.SharedPreferences
import android.content.pm.PackageManager
import android.location.Location
import android.os.*
import android.telephony.CellInfo
import android.telephony.TelephonyManager
import android.text.method.ScrollingMovementMethod
import android.view.View
import android.widget.*
import androidx.annotation.RequiresApi
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.preference.PreferenceManager
import com.example.myapplication.Constants.COMMAND_DELIM
import com.example.myapplication.Constants.GPS_LOG_START_MARKER
import com.example.myapplication.Constants.GPS_LOG_STOP_MARKER
import com.example.myapplication.Constants.LOG_FOLDER_NAME
import com.example.myapplication.Constants.LOG_START_DELIM
import com.example.myapplication.Constants.START_COMMAND
import com.example.myapplication.Constants.STOP_COMMAND
import com.example.myapplication.Constants.UPDATE_SETTINGS_COMMAND
import com.example.myapplication.ControlLink
import com.google.android.gms.location.*
import com.google.android.gms.tasks.CancellationToken
import com.google.android.gms.tasks.CancellationTokenSource
import com.google.android.gms.tasks.OnTokenCanceledListener
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.net.ServerSocket
import java.net.Socket
import kotlin.concurrent.thread
import kotlin.math.roundToInt

class MainActivity : AppCompatActivity(), MessageListener {
    private val mHandler =  Handler();
    private val mUIHandler =  Handler();
    private val mModemRefreshHandler =  Handler();
    private var mMeasurementCampaignName = System.currentTimeMillis().toString();
    private var mLogHandler = LogsHandler(LOG_FOLDER_NAME)
    private var mDebugLogFile = System.currentTimeMillis().toString();
    private var mIsRunning = false;
    private var mExpStartElapsedNanoSec: Long = -1;
    private var mMeasurementSocket = Socket();
    private var mControlLink: ControlLink? = null;
    private var mIMEI = ""
    private var mTelephonyManager: TelephonyManager? =  null;
//    private var COMPUTE_NODE_IP: String = ""
//    private var MEASUREMENT_PORT: Int = -1

    // Permissions
    private var mStorageWritePermission = false;
    private var mLocationPermission = false;
    private var mPhoneStateReadPermission = false;
    private var mWiFiStatePermission = false;
    private var mNetworkTypeListener = NetworkTypeListener()

    private fun streamToComputeNode(messageString: String){
        try
        {
            if(this.mMeasurementSocket.isClosed() || !this.mMeasurementSocket.isConnected)
            {
                this.mMeasurementSocket = Socket(SettingsHandler.Companion_IP, SettingsHandler.Companion_Port)
            }
            this.mMeasurementSocket.outputStream?.write(messageString.toByteArray())
            this.mMeasurementSocket.outputStream?.flush()
        }
        catch(t:Throwable)
        {
            // mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, t.toString())
            if (t.message == "Broken pipe"){
                // The companion closed its socket. Close PawPrint's socket as well, so that the connection can be retried.
                this.mMeasurementSocket.close()
            }

        }
    }

    private fun getIMEI(): String {
        val ts = TELEPHONY_SERVICE
        val mTelephonyMgr = getSystemService(ts) as TelephonyManager
        val imei = mTelephonyMgr.deviceId
        return imei
    }


    private fun updatePermissions()
    {
        mLocationPermission = (ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED) && (ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED)
        mStorageWritePermission = ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.WRITE_EXTERNAL_STORAGE) == PackageManager.PERMISSION_GRANTED
        mPhoneStateReadPermission = ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.READ_PHONE_STATE) == PackageManager.PERMISSION_GRANTED
        mWiFiStatePermission = ContextCompat.checkSelfPermission(this@MainActivity, Manifest.permission.ACCESS_WIFI_STATE) == PackageManager.PERMISSION_GRANTED
    }

    private fun requestPermissions()
    {
        var permissionArray:MutableList<String> = emptyList<String>().toMutableList()
        if(!mLocationPermission)
        {
            permissionArray.add(Manifest.permission.ACCESS_COARSE_LOCATION)
            permissionArray.add(Manifest.permission.ACCESS_FINE_LOCATION)
        }
        if(!mStorageWritePermission)
        {
            permissionArray.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
        }
        if(!mPhoneStateReadPermission)
        {
            permissionArray.add(Manifest.permission.READ_PHONE_STATE)
        }
        if(!mWiFiStatePermission)
        {
            permissionArray.add(Manifest.permission.ACCESS_WIFI_STATE)
        }
        if(permissionArray.size > 0)
        {
            ActivityCompat.requestPermissions(this@MainActivity, permissionArray.toTypedArray(), 100)
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int,
                                            permissions: Array<String>,
                                            grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        updatePermissions()
    }

    private fun createControlLink()
    {
        val url = "wss://127.0.0.1:8080"
        this.mControlLink  = ControlLink(url)
        this.mControlLink?.connect()

        // Send a message
        // tlsServerWebSocket.sendMessage("Hello, server!")

        // Disconnect
        // tlsServerWebSocket.disconnect()
    }

    private fun startCommandServer()
    {
        try {
            val sock = ServerSocket(Constants.COMMAND_PORT)
            while (true) {
                val client = sock.accept()
                mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile,"Client connected : ${client.inetAddress.hostAddress}")
                val command = BufferedReader(InputStreamReader(client.inputStream)).readLine().trim()
                mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile,"Received command from ${client.inetAddress.hostAddress}: $command")
                if (command == START_COMMAND && !mIsRunning)
                {
                    start();
                }
                else if (command == STOP_COMMAND && mIsRunning)
                {
                    stop();
                }
                else if (command.contains(START_COMMAND + COMMAND_DELIM) && !mIsRunning)
                {
                    val campaignName = command.substringAfter(START_COMMAND + COMMAND_DELIM)
                    mMeasurementCampaignName = campaignName
                    runOnUiThread({
                        val editText: EditText = findViewById(R.id.campaignName)
                        editText.setText(mMeasurementCampaignName)
                        start()
                    })
                }
                else if (command.contains(UPDATE_SETTINGS_COMMAND))
                {
                    val bValidCommand = SettingsHandler.updateSettingsFromCommand(command, PreferenceManager.getDefaultSharedPreferences(applicationContext))
                    if(!bValidCommand)
                    {
                        mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, "Invalid command: $command")
                    }
                }
                client.getOutputStream().write("command received".toByteArray())
            }
        }
        catch(t:Throwable)
        {
            mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, t.toString())
            //startCommandServer()
        }
    }

    fun getRandomString(string_length:Int): String {
        val allowedChars = ('A'..'Z') + ('a'..'z') + ('0'..'9')
        var string = ""
        for (i in (1..string_length)) {
            string += allowedChars[(Math.random() * (allowedChars.size - 1)).roundToInt()]
        }
        return string
    }

    private fun createRandomString(){


    }

    private val mCaptureMeasurements: Runnable = object : Runnable {
        @RequiresApi(Build.VERSION_CODES.Q)
        override fun run()
        {
            if(!mIsRunning)
            {
                return;
            }
            thread {
                kotlin.run {
                    try
                      {
                         mHandler.postDelayed(this, SettingsHandler.LogInterval)
                          if(SettingsHandler.LogGPS)
                          {
                              thread {
                                  logLocation()
                              }
                          }
                          val telephonyManager = getSystemService(TELEPHONY_SERVICE) as TelephonyManager
                          var jsonLog = CellMeasurementsHandler().getInfo(telephonyManager, SettingsHandler, "json", mMeasurementCampaignName, mIMEI, mExpStartElapsedNanoSec )

                          if (SettingsHandler.LogLocally)
                          {
                              thread {
                                  mLogHandler.appendToMeasurements(
                                      mStorageWritePermission,
                                      mMeasurementCampaignName,
                                      jsonLog
                                  )
                              }
                          }
                          if (SettingsHandler.StreamToComputeNode)
                          {
                              thread {
                                  streamToComputeNode(jsonLog)
                              }
                          }
                    }
                    catch(t: Throwable)
                    {
                        mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, t.toString())
                    }
                }
            }
        }
    }

    private val mDisplayMeasurements: Runnable = object : Runnable {
        @RequiresApi(Build.VERSION_CODES.Q)
        override fun run()
        {
            if(!mIsRunning)
            {
                return;
            }
            kotlin.run {
                try {
                    mUIHandler.postDelayed(this, SettingsHandler.UIRefreshInterval);
                    val textView: TextView = findViewById(R.id.textView)
                    var displayString = ""
                    val telephonyManager = getSystemService(TELEPHONY_SERVICE) as TelephonyManager
                    displayString += CellMeasurementsHandler().getInfo(telephonyManager, SettingsHandler, "display",  mMeasurementCampaignName, mIMEI, mExpStartElapsedNanoSec)
                    displayString += mNetworkTypeListener.getDisplayString()
                    textView.text = displayString
                    textView.setMovementMethod(ScrollingMovementMethod());
                }
                catch(t: Throwable)
                {
                    mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, t.toString())
                }
            }

        }
    }

    private val mRefreshModem: Runnable = object : Runnable {
        @RequiresApi(Build.VERSION_CODES.Q)
        override fun run() {
            if(!mIsRunning){
                return;
            }
            kotlin.run {
                try
                {
                    mModemRefreshHandler.postDelayed(this, SettingsHandler.ModemRefreshInterval);
                    if (SettingsHandler.ForceModemRefresh)
                    {
                        val telephonyManager = getSystemService(TELEPHONY_SERVICE) as TelephonyManager
                        telephonyManager.requestCellInfoUpdate(
                            applicationContext.mainExecutor,
                            object : TelephonyManager.CellInfoCallback() {
                                override fun onCellInfo(activeCellInfo: MutableList<CellInfo>) {
                                }
                            })
                    }
                }
                catch(t: Throwable){
                    mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, t.toString())                }
            }
        }
    }

    @RequiresApi(Build.VERSION_CODES.N)
    private fun logLocation()
    {
        if(!mIsRunning){
            return
        }
        var fusedLocationProviderClient = LocationServices.getFusedLocationProviderClient(this)
        if (ActivityCompat.checkSelfPermission(
                this,
                Manifest.permission.ACCESS_FINE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(
                this,
                Manifest.permission.ACCESS_COARSE_LOCATION
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.
            return
        }
        fusedLocationProviderClient.getCurrentLocation(Priority.PRIORITY_HIGH_ACCURACY, object :CancellationToken(){
            override fun onCanceledRequested(p0: OnTokenCanceledListener) = CancellationTokenSource().token

            override fun isCancellationRequested() = false
        }).addOnSuccessListener { location: Location? ->
            if (location == null)
            //                Toast.makeText(this, "Cannot get location.", Toast.LENGTH_SHORT).show()
            else
            {
                val fixElapsedNanoSec = (location.elapsedRealtimeNanos - mExpStartElapsedNanoSec)/Math.pow(10.0, 9.0);
                val nowElapsed = (SystemClock.elapsedRealtimeNanos() - mExpStartElapsedNanoSec)/Math.pow(10.0, 9.0)

                val gpsJSON =  JSONObject()
                gpsJSON.put("device_name", SettingsHandler.Device_Name)
                gpsJSON.put("campaign_name", mMeasurementCampaignName)
                gpsJSON.put("abs_time", System.currentTimeMillis())
                gpsJSON.put("rel_time", nowElapsed)
                gpsJSON.put("rel_fix_time", fixElapsedNanoSec)
                gpsJSON.put("latitude", location.latitude)
                gpsJSON.put("longitude", location.longitude)
                gpsJSON.put("altitude", location.altitude)
                gpsJSON.put("accuracy", location.accuracy)
                gpsJSON.put("hasBearing", location.hasBearing())
                gpsJSON.put("bearing", location.bearing)
                gpsJSON.put("hasSpeed", location.hasSpeed())
                gpsJSON.put("speed", location.speed)
                gpsJSON.put("hasSpeedAccuracy", location.hasSpeedAccuracy())
                gpsJSON.put("speedAccuracy", location.speedAccuracyMetersPerSecond)
                gpsJSON.put("hasBearingAccuracy", location.hasBearingAccuracy())
                gpsJSON.put("bearingAccuracy", location.bearingAccuracyDegrees)

                mLogHandler.appendToLocation(mStorageWritePermission, mMeasurementCampaignName, gpsJSON.toString())
                if (SettingsHandler.StreamToComputeNode) {
                    thread {
                        streamToComputeNode(gpsJSON.toString())
                    }
                }
            }
        }
    }

    @RequiresApi(Build.VERSION_CODES.O)
    override fun onResume()
    {
            super.onResume()
            updatePermissions()
            val errors = SettingsHandler.updateSettingsFromUI(PreferenceManager.getDefaultSharedPreferences(applicationContext) )
            if (errors.isNotEmpty())
            {
                mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, errors)
            }
    }

    private fun start(){
        try {
            //            createControlLink()
            updatePermissions()
            requestPermissions()
            mNetworkTypeListener.registerListener(this.mTelephonyManager!!)
            runOnUiThread({
            val startBtn: Button = findViewById(R.id.startBtn)
            val editText: EditText = findViewById(R.id.campaignName)
                mMeasurementCampaignName = editText.text.toString()
                if(mMeasurementCampaignName.isEmpty())
                {
                    mMeasurementCampaignName =  System.currentTimeMillis().toString();
                }
            //                editText.focusable = View.NOT_FOCUSABLE;

            mIsRunning = true
            mExpStartElapsedNanoSec = SystemClock.elapsedRealtimeNanos();
            //            mIMEI = this.getIMEI()
            startBtn.text = "Stop"
            thread{
                kotlin.run {
                    mHandler.postDelayed(mCaptureMeasurements, SettingsHandler.LogInterval);
                }
                if(SettingsHandler.ForceModemRefresh) {
                    kotlin.run {
                        mHandler.postDelayed(mRefreshModem, SettingsHandler.ModemRefreshInterval);
                    }
                }
            }

            kotlin.run {
                mUIHandler.postDelayed(mDisplayMeasurements, SettingsHandler.UIRefreshInterval);
            }
            })
        }
        catch(t:Throwable){
            mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, t.toString())
        }
    }

    private fun stop()
    {
        this.mNetworkTypeListener.deregisterListener(this.mTelephonyManager!!)
        runOnUiThread({
            val startBtn: Button = findViewById(R.id.startBtn)
            val editText: EditText = findViewById(R.id.campaignName)
//            editText.focusable = View.FOCUSABLE
            editText.setText("")
            editText.hint = "Experiment Name"
            mIsRunning = false
            startBtn.text = "Start"
            val textView: TextView = findViewById(R.id.textView)
            textView.text = "Measurement Log:"
        })
        if(this.mMeasurementSocket != null)
        {
            this.mMeasurementSocket.close()
        }
    }

    @RequiresApi(Build.VERSION_CODES.O)
    override fun onCreate(savedInstanceState: Bundle?)
    {
        try {
            super.onCreate(savedInstanceState)
            this.mTelephonyManager = getSystemService(TELEPHONY_SERVICE) as TelephonyManager
            setContentView(R.layout.activity_main)  
            val buildDateTextView: TextView = findViewById(R.id.buildOn) // Replace R.id.buildDateTextView with the actual ID of your TextView
            buildDateTextView.text = getString(R.string.build_date, BuildConfig.BUILD_DATE)

            thread {
                startCommandServer();
            }

            val startBtn: Button = findViewById(R.id.startBtn)
            startBtn.setOnClickListener {
                try {
                    val preferences: SharedPreferences =
                        PreferenceManager.getDefaultSharedPreferences(applicationContext)
                    if (!mIsRunning) {
                        start()
                    } else {
                        stop()
                    }
                } catch (t: Throwable) {
                    mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, t.toString())
                }
            }

            val settingsBtn: Button = findViewById(R.id.settingsBtn);
            settingsBtn.setOnClickListener({
                // opening a new intent to open settings activity.
                val i = Intent(this@MainActivity, SettingsActivity::class.java)
                startActivity(i)
            })
        }
        catch(t:Throwable){
            mLogHandler.appendToDebug(mStorageWritePermission, mDebugLogFile, t.toString())
        }
    }

    override fun onConnectSuccess()
    {
    }

    override fun onConnectFailed()
    {
    }

    override fun onClose()
    {

    }

    override fun onMessage(text: String?) {
    }

    override fun onDestroy() {
        super .onDestroy ()
        this.mControlLink?.disconnect()
//        if(this.mMeasurementSocket != null)
//        {
//            this.mMeasurementSocket.close()
//        }
    }
}