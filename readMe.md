<h2>PawPrints, The AERPAW Cellular Logger</h2>

Development effort for this app is supported in part by the NSF award CNS-1939334 (AERPAW). 
<br><br>The approach for calculating 5G NSA signal strength measurements is derived from <cite><a target="_blank" href="https://people.cs.uchicago.edu/~muhiqbalcr/sigcap/">Sigcap</a></cite>, developed by Muhammad Iqbal Rochman. Thanks to Muhammad for sharing the source code.

<div id="content">
<ol>
    <li><strong>Overview</strong>
        <p>This page explains the usage, features, and implementation details of the cellular logger Android app. There are separate sections for the user and the developer. The objective of the app is to capture cellular parameters, either of 4G or 5G technology, as reported by Android APIs, and display and log the same.</p>
        <p>These measurements can be logged locally on the Android storage as a .csv file or may be streamed over a TCP socket to an external process, which can be on a compute node connected via USB to the Android device, as shown in Fig. 1. The app can also be controlled remotely through commands sent over a TCP socket.</p></li>
    <li><strong>System Architecture</strong><p>The Android App can be used standalone, in which case all measurements can be saved locally. This Android App can also work with a companion compute node, which is connected to it via USB as shown in Fig. 1.
        On the control path, a bash script on the compute node, called android remote control, is provided to interact with the Android App to start and stop the capture of measurements. This script can also configure the app, for instance, it can set the logging interval. The app listens at <code>commandPort</code> for such commands over a TCP socket. On the data path, the Android App can stream measurements over a TCP socket to a data process on the compute node. The data process is a python script that listens on a TCP port, called the <code>measurementPort</code>, for measurements from the app. The process also saves these measurements as a .csv file on the compute node. </p></li>
    <img src="architecture.svg">
    <li><strong>Source Code</strong><p><a target="_blank" href="https://github.com/ssinghjah/PawPrints">Link to GitHub repository</a></p></li>
    <li><strong>Latest APK</strong><p><a target="_blank" href="https://github.com/ssinghjah/PawPrints/tree/main/Android/Releases">Link to the GitHub folder, from which the apk can be downloaded.</a></p></strong></li>
    <li><strong>For Users</strong>
        <p>To use the App, first make sure it has the required permissions. The app requires permission to 1) write to external storage (to save logs), 2) to read the phone state, and 3) access fine and coarse location. After providing these permissions, launch the app. The app has two pages: the main page and the settings page. Configure the App by going to the settings page. Then, you can start the measurement campaign by providing a campaign name, <code>campaignName</code>, and clicking on the Start button in the main page. If the required permissions have not been granted, the app will request for the same.</p>
        <p>To stream measurements to the compute node over USB, enable developer mode on the Android device and then connect the Android device to the compute node through USB. The scripts for the compute node were tested on Linux Ubuntu 18.04 operating system. You can verify that the Android device has been detected by running <code>adb devices</code> from the compute node. Run the <code>dataProcess.py</code> python script at the compute node using the command <code>python3 dataProcess.py</code>. This script listens for measurements from the Android app at the <code>measurementPort</code> and saves these measurements to a .csv file at the compute node. The name of the .csv file is that of the measurement campaign. The Android app can also be remotely controlled from the compute node, by using the <code>remoteAndroidControl</code> script. This script can trigger the app to start a measurement campaign with a given <code>campaignName</code>, stop a campaign, or to update some settings.
            The list of supported commands and corresponding examples of usage is given below in Table 1.</p>
        <div style="overflow-x:auto;">
            <table>
                <caption>Table 1. Commands accepted by the Android app and their effect on app behaviour.</caption>
                <tr>
                    <th>Command string accepted by the app at the <code>commandPort</code> (case-sensitive).</th>
                    <th>Effect</th>
                    <th>A sample command, using the android remote control script at the compute node</th>
                </tr>
                <tr>
                    <td>start</td><td>The app starts reading, logging, and streaming measurements, as per the configured settings.</td><td>./androidRemoteControl start</td>
                </tr>
                <tr>
                    <td>start,<code>campaignName</code></td><td>The app sets the campaign name to <code>campaignName</code>, as provided in the command. The app then starts reading, logging, and streaming measurements, as per the configured settings. The sample command will set <code>campaignName</code> to "measurementsAtTheLake"</td><td>./androidRemoteControl start,measurementsAtTheLake</td>
                </tr>
                <tr>
                    <td>stop</td><td>The app stops reading, logging, and streaming measurements.</td><td>./androidRemoteControl stop</td>
                </tr>
                <tr>
                    <td>updateSettings,<code>settingName</code>=<code>settingValue</code></td><td>The app sets <code>settingName</code> to <code>settingValue</code>. The sample command sets the logging interval to 1.5 seconds.</td><td>./androidRemoteControl updateSettings,logInterval=1500</td>
                </tr>
            </table>
        </div>
        <div style="overflow-x:auto;">
            <table>
                <caption>Table 2. List of setting names accepted by the app, as part of the "updateSettings" command, and their significance. The data type of corresponding setting values and their default values are also listed.</caption>
                <tr>
                    <th>Setting name accepted by the "updateSettings" command (case-sensitive)</th>
                    <th>Data type of the setting's value</th>
                    <th>Default value</th>
                    <th>Significance</th>
                    <th>Sample command</th>
                </tr>
                <tr>
                    <td>logLocally</td>
                    <td>Boolean (true or false)</td>
                    <td>true</td>
                    <td>A boolean value that indicates whether measurements should be logged at the Android device. The app creates a new folder under the Documents folder, under which all logs are written.</td>
                    <td>./androidRemoteControl updateSettings,logLocally=false</td>
                </tr>
                <tr>
                    <td>logInterval</td>
                    <td>Integer (represents time interval in milliseconds)</td>
                    <td>1000</td>
                    <td>Time interval at which cellular and GPS (if configured) measurements are periodically read, logged, and streamed to the compute node.</td>
                    <td>./androidRemoteControl updateSettings,logInterval=1500</td>
                </tr>
                <tr>
                    <td>forceModemRefresh</td>
                    <td>Boolean (true or false)</td>
                    <td>true</td>
                    <td>A boolean value that indicates whether the modem of the Android device should be forced to re-calculate its cellular data periodically.</td>
                    <td>./androidRemoteControl updateSettings,forceModemRefresh=false</td>
                </tr>
                <tr>
                    <td>modemRefreshInterval</td>
                    <td>Integer (represents time interval in milliseconds)</td>
                    <td>1000</td>
                    <td>Time interval at which the modem of the device is periodically forced to re-calculate its cellular data.</td>
                    <td>./androidRemoteControl updateSettings,modemRefreshInterval=1500</td>
                </tr>
                <tr>
                    <td>logGPS</td>
                    <td>Boolean (true or false)</td>
                    <td>false</td>
                    <td>A boolean value that indicates whether GPS location data should be captured and logged periodically.</td>
                    <td>./androidRemoteControl updateSettings,logGPS=true</td>
                </tr>
                <tr>
                    <td>streamToComputeNode</td>
                    <td>Boolean (true or false)</td>
                    <td>false</td>
                    <td>A boolean value that indicates whether measurements should be streamed to the compute node over TCP, to the <code>measurementPort</code>. Requires a USB connection between the compute node and the Android. The Android device should have developer mode enabled, and the compute node should be running the <code>dataProcess.py</code> script.</td>
                    <td>./androidRemoteControl updateSettings,streamToComputeNode=true</td>
                </tr>
                <tr>
                    <td>debug</td>
                    <td>Boolean (true or false)</td>
                    <td>false</td>
                    <td>A boolean value that indicates whether exceptions thrown by the code should be logged to a <code>campaignName</code>_debug.txt log file. Commands received at the <code>commandPort</code> are also logged to this file.</td>
                    <td>./androidRemoteControl updateSettings,debug=true</td>
                </tr>
            </table>
        </div>
        <div style="overflow-x:auto;">
            <table>
                <caption>Table 3. Format of the cellular measurements log.</caption>
                <tr>
                    <th>Column description</th>
                    <td>CELL_INFO_START (Indicates start of the cellular measurements log)</td>
                    <td>Network operator name</td>
                    <td>SIM operator name</td>
                    <td>SIM carrier ID name</td>
                    <td>BS_INFO_START (Indicates starts of a base station measurement block)</td>
                    <td>4G or 5G base station measurement block</td>
                    <td>BS_INFO_STOP (Indicates end of a base station measurement block)</td>
                    <td>BS_INFO_START (One measurement block for each detected base station)</td>
                    <td>4G or 5G base station measurement block</td>
                    <td>BS_INFO_STOP</td>
                    <td>Base station measurement blocks continue</td>
                    <td>CELL_INFO_STOP (Indicates end of the cellular measurements log)</td>
                </tr>
                <tr>
                    <th>Units</th>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                </tr>
                <tr>
                    <th>Source API</th>
                    <td>N/A</td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/TelephonyManager#getNetworkOperatorName()">TelephonyManager#getNetworkOperatorName()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/TelephonyManager#getSimOperatorName()">TelephonyManager#getSimOperatorName()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/TelephonyManager#getSimCarrierIdName()">TelephonyManager#getSimCarrierIdName()</a></td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                </tr>
                <tr>
                    <th>Min required API level</th>
                    <td>N/A</td>
                    <td>1</td>
                    <td>1</td>
                    <td>28</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                </tr>
            </table>
        </div>
        <div style="overflow-x:auto;">
            <table>
                <caption>Table 4. Format of the 4G LTE measurements block.</caption>
                <tr>
                    <strong>
                    <th>Column description</th>
                    <td>Elapsed time between experiment start and instant at which information was captured at the modem.</td>
                    <td>Cellular technology of the base station</td>
                    <td>Is device connected to this base station?</td>
                    <td>Cell signal strength</td>
                    <td>Reference signal, signal to noise ratio (RSSNR)</td>
                    <td>Reference signal received power (RSRP)</td>
                    <td>Reference signal received quality (RSRQ)</td>
                    <td>Received signal strength indicator (RSSI)</td>
                    <td>Channel quality index (CQI)</td>
                    <td>RSRP in ASU</td>
                    <td>Absolute radio frequency Channel Number (EARFCN)</td>
                    <td>Physical cell id (PCI)</td>
                    <td>Timing advance</td>
                    <td>Cell Identity</td>
                    <td>Tracking area code</td>
                    <td>Mobile country code</td>
                    <td>Mobile network code</td>
                    </strong>
                </tr>
                <tr>
                    <th>Data type</th>
                    <td>Decimal</td>
                    <td>String</td>
                    <td>Boolean</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>String</td>
                    <td>String</td>
                </tr>
                <tr>
                    <th>Units</th>
                    <td>seconds</td>
                    <td>N/A</td>
                    <td>Boolean (true or false)</td>
                    <td>dBm</td>
                    <td>dB</td>
                    <td>dBm</td>
                    <td>dBm</td>
                    <td>N/A</td>
                    <td>dBm</td>
                    <td>N/A</td>
                    <td>Arbitrary strength unit</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                </tr>
                <tr>
                    <th>Range</th>
                    <td>N/A. Can be negative if modem information was captured before experiment start, which is mostly the case for the initial logs.</td>
                    <td>Always "4G" for this block</td>
                    <td>true or false</td>
                    <td>Not documented</td>
                    <td>-20 to 30</td>
                    <td>-140 to -43</td>
                    <td>Not documented</td>
                    <td>-113 to -51</td>
                    <td>0 to 15</td>
                    <td>0 to 97 or 255</td>
                    <td>18 bits</td>
                    <td>0 to 503</td>
                    <td>0 to 1282</td>
                    <td>28-bit</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                </tr>
                <tr>
                    <th>Source API</th>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellInfo#getTimestampMillis()">CellInfo#getTimestampMillis()</a></td>
                    <td>N/A</td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellInfo#isRegistered()">CellInfo#isRegistered()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthLte#getDbm()">CellSignalStrengthLte#getDbm()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthLte#getRssnr()">CellSignalStrengthLte#getRssnr()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthLte#getRsrp()">CellSignalStrengthLte#getRsrp()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthLte#getRsrq()">CellSignalStrengthLte#getRsrq()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthLte#getRssi()">CellSignalStrengthLte#getRssi()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthLte#getCqi()">CellSignalStrengthLte#getCqi()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthLte#getAsuLevel()">CellSignalStrengthLte#getAsuLevel()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityLte#getEarfcn()">CellIdentityLte#getEarfcn()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityLte#getPci()">CellIdentityLte#getPci()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthLte#getTimingAdvance()">CellSignalStrengthLte#getTimingAdvance()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityLte#getCi()">CellIdentityLte#getCi()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityLte#getTac()">CellIdentityLte#getTac()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityLte#getMccString()">CellIdentityLte#getMccString()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityLte#getMncString()">CellIdentityLte#getMncString()</a></td>
                </tr>
                <tr>
                    <th>Min required API level</th>
                    <td>17</td>
                    <td>N/A</td>
                    <td>17</td>
                    <td>17</td>
                    <td>26</td>
                    <td>26</td>
                    <td>26</td>
                    <td>29</td>
                    <td>26</td>
                    <td>17</td>
                    <td>24</td>
                    <td>17</td>
                    <td>17</td>
                    <td>17</td>
                    <td>17</td>
                    <td>28</td>
                    <td>28</td>
                </tr>
            </table>
        </div>
        <div style="overflow-x:auto;">
            <table>
                <caption>Table 5. Format of the 5G new radio (NR) stand alone (SA) measurements block.</caption>
                <tr>
                    <strong>
                        <th>Column description</th>
                        <td>Elapsed time between experiment start and instant at which information was captured at the modem.</td>
                        <td>Cellular technology of the base station</td>
                        <td>Is device connected to this base station?</td>
                        <td>Signal strength of the synchronization signal (SS)</td>
                        <td>RSRP of channel state information reference signal (CSI-RSRP)</td>
                        <td>RSRQ of CSI</td>
                        <td>SINR of CSI</td>
                        <td>RSRP of SS</td>
                        <td>RSRQ of SS</td>
                        <td>SINR of SS</td>
                        <td>Abstract level value of overall signal quality</td>
                        <td>RSRP in ASU</td>
                        <td>New radio cell identity (NCI)</td>
                        <td>New radio absolute radio frequency channel number (NRAFCN)</td>
                        <td>Physical cell id (PCI)</td>
                        <td>Tracking area code</td>
                        <td>Bands of the cell reference</td>
                        <td>Mobile country code</td>
                        <td>Mobile network code</td>
                    </strong>
                </tr>
                <tr>
                    <th>Data type</th>
                    <td>Decimal</td>
                    <td>String</td>
                    <td>Boolean</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer array</td>
                    <td>String</td>
                    <td>String</td>
                </tr>
                <tr>
                    <th>Units</th>
                    <td>seconds</td>
                    <td>N/A</td>
                    <td>Boolean (true or false)</td>
                    <td>dBm</td>
                    <td>dBm</td>
                    <td>dB</td>
                    <td>dB</td>
                    <td>dBm</td>
                    <td>dB</td>
                    <td>dB</td>
                    <td>N/A</td>
                    <td>Arbitrary strength unit</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>N/A</td>
                    <td>To Do</td>
                    <td>N/A</td>
                    <td>N/A</td>
                </tr>
                <tr>
                    <th>Range</th>
                    <td>N/A. Can be negative if modem information was captured before experiment start, which is mostly the case for the initial logs.</td>
                    <td>Always "4G" for this block</td>
                    <td>true or false</td>
                    <td>-140 to -44</td>
                    <td>-140 to -44</td>
                    <td>-20 to -3</td>
                    <td>-23 to 23</td>
                    <td>-140 to -40</td>
                    <td>-43 to 20</td>
                    <td>-23 to 40</td>
                    <td>N/A</td>
                    <td>0 to 97 or 255</td>
                    <td>36-bit integer, 0 to 68719476735</td>
                    <td>0 to 3279165</td>
                    <td>0 to 1007</td>
                    <td>24 bit integer, 0 to 16777215</td>
                    <td>To Do</td>
                    <td>N/A</td>
                    <td>N/A</td>
                </tr>
                <tr>
                    <th>Source API</th>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellInfo#getTimestampMillis()">CellInfo#getTimestampMillis()</a></td>
                    <td>N/A</td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellInfo#isRegistered()">CellInfo#isRegistered()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getDbm()">CellSignalStrengthNr#getDbm()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getCsiRsrp()">CellSignalStrengthNr#getCsiRsrp()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getCsiRsrq()">CellSignalStrengthNr#getCsiRsrq()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getCsiSinr()">CellSignalStrengthNr#getCsiSinr()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getSsRsrp()">CellSignalStrengthNr#getSsRsrp()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getSsRsrq()">CellSignalStrengthNr#getSsRsrq()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getSsSinr()">CellSignalStrengthNr#getSsSinr()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getLevel()">CellSignalStrengthNr#getLevel()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getAsuLevel()">CellSignalStrengthNr#getAsuLevel()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityNr#getNci()">CellIdentityNr#getNci()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityNr#getNrarfcn()">CellIdentityNr#getNrarfcn()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityNr#getPci()">CellIdentityNr#getPci()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityNr#getTac()">CellIdentityNr#getTac()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityNr#getBands()">CellIdentityNr#getBands()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityNr#getMccString()">CellIdentityNr#getMccString()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellIdentityNr#getMccString()">CellIdentityNr#getMncString()</a></td>
                </tr>
                <tr>
                    <th>Min required API level</th>
                    <td>17</td>
                    <td>N/A</td>
                    <td>17</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>30</td>
                    <td>29</td>
                    <td>29</td>
                </tr>
            </table>
        </div>
<!--        -->
        <div style="overflow-x:auto;">
            <table>
                <caption>Table 6. Format of the 5G NR non-standalone (NSA) measurements block.</caption>
                <tr>
                    <strong>
                        <th>Column description</th>
                        <td>Elapsed time between experiment start and instant at which information was captured at the modem.</td>
                        <td>Cellular technology of the base station</td>
                        <td>Is device connected to this base station?</td>
                        <td>Signal strength of the synchronization signal (SS)</td>
                        <td>RSRP of channel state information reference signal (CSI-RSRP)</td>
                        <td>RSRQ of CSI</td>
                        <td>SINR of CSI</td>
                        <td>RSRP of SS</td>
                        <td>RSRQ of SS</td>
                        <td>SINR of SS</td>
                        <td>Abstract level value of overall signal quality</td>
                        <td>RSRP in ASU</td>
                    </strong>
                </tr>
                <tr>
                    <th>Data type</th>
                    <td>Decimal</td>
                    <td>String</td>
                    <td>Boolean</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                    <td>Integer</td>
                </tr>
                <tr>
                    <th>Units</th>
                    <td>seconds</td>
                    <td>N/A</td>
                    <td>Boolean (true or false)</td>
                    <td>dBm</td>
                    <td>dBm</td>
                    <td>dB</td>
                    <td>dB</td>
                    <td>dBm</td>
                    <td>dB</td>
                    <td>dB</td>
                    <td>N/A</td>
                    <td>Arbitrary strength unit</td>
                </tr>
                <tr>
                    <th>Range</th>
                    <td>N/A. Can be negative if modem information was captured before experiment start, which is mostly the case for the initial logs.</td>
                    <td>Always "4G" for this block</td>
                    <td>true or false</td>
                    <td>-140 to -44</td>
                    <td>-140 to -44</td>
                    <td>-20 to -3</td>
                    <td>-23 to 23</td>
                    <td>-140 to -40</td>
                    <td>-43 to 20</td>
                    <td>-23 to 40</td>
                    <td>N/A</td>
                    <td>0 to 97 or 255</td>
                </tr>
                <tr>
                    <th>Source API</th>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellInfo#getTimestampMillis()">CellInfo#getTimestampMillis()</a></td>
                    <td>N/A</td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellInfo#isRegistered()">CellInfo#isRegistered()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getDbm()">CellSignalStrengthNr#getDbm()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getCsiRsrp()">CellSignalStrengthNr#getCsiRsrp()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getCsiRsrq()">CellSignalStrengthNr#getCsiRsrq()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getCsiSinr()">CellSignalStrengthNr#getCsiSinr()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getSsRsrp()">CellSignalStrengthNr#getSsRsrp()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getSsRsrq()">CellSignalStrengthNr#getSsRsrq()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getSsSinr()">CellSignalStrengthNr#getSsSinr()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getLevel()">CellSignalStrengthNr#getLevel()</a></td>
                    <td><a target="_blank" href="https://developer.android.com/reference/android/telephony/CellSignalStrengthNr#getAsuLevel()">CellSignalStrengthNr#getAsuLevel()</a></td>
                </tr>
                <tr>
                    <th>Min required API level</th>
                    <td>17</td>
                    <td>N/A</td>
                    <td>17</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                    <td>29</td>
                </tr>
            </table>
        </div>
    </li>
    <li><strong>For Developers</strong>
        <ul>
            <li>Android App <p>The Android App is developed using Kotlin, and consists of two activities: a main activity from which the user can start or stop measurements and which displays the captured measurements, and a settings activity from which the user can configure the app. The App starts collecting measurements when the start button is pushed, or when it receives a command through the command port. A measurement campaign name (referred to as <code>campaignName</code> here) may be provided before start through the UI or in a command to the <code>commandPort</code>. Otherwise, the app uses its current timestamp, in milliseconds from Unix epoch, as the <code>campaignName</code>. <code>campaignName</code> is used to name the logs.</p>
                    <ul>
                    <li>APIs<p> The Android App relies on the below two APIs to collect cellular information:
                        <li><code><a target="_blank" href="https://developer.android.com/reference/kotlin/android/telephony/TelephonyManager#getallcellinfo">getAllCellInfo</a></code>: This API is a member function of the TelephonyManager class and requires the device to support API versions 17 and above. The API returns a list of objects containing cellular measurements for each detected base station. The class of each object in the returned list indicates the cellular technology of that base station. The app supports parsing objects belonging to classes that contain 4G LTE and 5G NR information. However, the device must support a minimum API level of 29 to obtain 5G NR information. Further, 5G NR information is returned only if the base station is a 5G NR standalone (SA) base station. If the base station is of type 5G NR non-standalone (NSA), then the below API must be used. 5G NR NSA base stations use 4G LTE for the control plane and 5G NR for user data.</li>
                            <li><code><a target="_blank" href="https://developer.android.com/reference/kotlin/android/telephony/TelephonyManager#getsignalstrength">getSignalStrength</a></code>: This API is also a member function of the TelephonyManager class and and requires the device to support API versions 28 and above. The API returns a list of objects containing the signal strength measurements of the base station the device is connected to. For 5G NR NSA base stations, the API returns both LTE and 5G NR signal strength information. For 5G SA base stations, the API returns only 5G NR signal strength information, and for LTE base stations, the API returns only LTE signal strength information.</li>
                            <br>
                        </p>
                        </li>
                    <li>Logs<p>The app can display and log 4G LTE and 5G NR measurements, as obtained from the above two APIs. Each measurements has a minimum required API level, which must be supported by the device. The app logs measurements for all observed base stations, besides the one that the device is connected to. The logging interval is configurable.
                        </br></br>
                        The above two APIs return the latest available measurements at the device modem, but do not trigger the modem to recalculate these cellular measurements, i.e. the measurements may be stale. The modem can be triggered to recalculate cellular measurements by calling the <code>requestCellInfoUpdate</code> API. The app can be configured to force the modem to refresh its data through these re-calculations. The modem refresh interval is also configurable. Both of these configurations can be performed through the settings page.
                        </br></br>
                        The App can also be configured to log GPS readings, using the fused location provider of Google Play services. The option to log GPS and the GPS logging interval can be configured through the settings page. For higher accuracy, you may enable the Force full GNSS measurements setting on the device. This setting can be accessed once developer mode has been enabled on the device.
                        </br></br>
                        All logs of the app are created under a folder called "AERPAW" under the "Documents" folder of the external storage of the Android device.
                        </br></br>
                        The log format of the cellular measurements, at the android app, is specified in Tables 3-5. Information of all detected base stations is included. This log is named  "<code>campaignName</code>_log.txt".
                        </br></br>
                        GPS information is captured in another log, named "<code>campaignName</code>_locations.txt".  Its format is specified in Table 6.</p></li>
                        <li>Threads <p>The app may launch upto three threads, each of which runs in a loop periodically, after their respective time intervals, as per the configured settings. These three threads are as follows:
                            <ul>
                                <li>Log and stream measurements: This thread saves cellular measurements locally to a .csv file, if configured to do so, and streams measurements to the compute node over UDP and USB at the specified port, if configured to do so. The interval at which this thread loops (and hence, the rate at which the app logs and streams measurements) can be configured.</li>
                                <li>Display measurements: This thread displays measurements in the app UI. The interval at which this thread loops can be configured. This thread is always launched.
                                </li>
                                <li>Refresh modem: This thread refreshes the data in the modem, by calling the requestCellInfoUpdate API repeatedly, after the specified time interval. This thread is launched only if the app is configured to force modem refresh.</li></ul>Measurements are displayed and logged/streamed in two different threads since a human may want to view the measurements at a slower rate in real-time, while logging it at a much faster rate, for later analysis. E.g. the measurements may be logged hundreds of milliseconds apart, but the naked eye may not be able to make sense between such rapid changes. Choosing a slower UI display rate also reduces the computational burden on the app.</p></li>
                            </ul>
                    <li>Relevant Functions & Classes
                    <ul>
                        <li><code>MainActivity.kt</code>
                            <p>MainActivity.kt is the core of the app, this is where all the action starts. This file contains all functions that handle interactions of the user with the main page.
                                </br>The <code>start</code> function is called when the user clicks on the Start button, and the <code>stop</code> function is called when the user clicks on the Stop button.
                                </br>The <code>startCommandServer</code> function is responsible for listening at the <code>commandPort</code> and processing incoming commands. Since Android does not allow network operations in the main UI thread, this function runs in its own separate thread.
                                </br>The <code>mCaptureMeasurements</code> function is called periodically, in a thread. This thread is launched from within the <code>start</code> function. This function is responsible for logging (locally) and streaming (to the compute node) cellular and location measurements.
                                </br>The <code>logLocation</code> function is called periodically, in a thread. This thread is launched from within the <code>start</code> function. This function is responsible for requesting and logging GPS coordinates.
                                </br>The <code>streamToComputeNode</code> function is responsible for sending measurements over a TCP socket to the compute node.
                                </br>The <code>mDisplayMeasurements</code> function is called periodically, in a thread. This thread is launched from within the <code>start</code> function. This function is responsible for displaying cellular measurements in the app UI.
                                </br>The <code>mRefreshModem</code> function is called periodically, in a thread. This thread is launched from within the <code>start</code> function. This function is responsible for forcing the modem to re-calculate its cellular data.
                            </p>
                        </li>
                        <li><code>Constants.kt</code>
                        <p>
                            This file defines all the constants used by the app.
                        </p>
                        </li>
                        <li><code>CellMeasurementHandler.kt</code>
                            <p>
                                This class queries cellular measurements from the modem using the <code>getAllCellInfo</code> and <code>getSignalStrength</code> APIs, and returns either a comma separated string for logging / streaming, or a string formatted for display in the app UI. Called from within the <code>mCaptureMeasurements</code> and <code>mDisplayMeasurements</code> functions.
                            </p>
                        </li>
                        <li><code>LTEInfo.kt</code>
                            <p>
                                This class retrieves LTE cellular measurements from <code>CellInfoLTE</code> type objects. The measurements are processed if needed, and then combined into either a comma separated string, or a string formatted for display in the app UI.
                            </p>
                        </li>
                        <li><code>NRInfo.kt</code>
                            <p>
                            This class retrieves 5G NR SA cellular measurements from <code>CellInfoNR</code> type objects. The measurements are processed if needed, and then combined into either a comma separated string, or a string formatted for display in the app UI.
                            </p>
                        </li>
                        <li><code>NRSignalStrengthInfo.kt</code>
                            <p>
                                This class retrieves 5G NR NSA signal strength measurements by using the <code>getSignalStrength</code> API. The measurements are processed if needed, and then combined into either a comma separated string, or a string formatted for display in the app UI.
                            </p>
                        </li>
                        <li><code>GeneralConnectionInfo.kt</code>
                            <p>
                                This class retrieves general connection information directly available from the <code>TelephonyManager</code> class object. The measurements are processed if needed, and then combined into either a comma separated string, or a string formatted for display in the app UI.
                            </p>
                        </li>
                        <li><code>SettingsHandler.kt</code>
                            <p>
                                This class is responsible for updating settings based on commands received at the <code>commandPort</code>, or by user actions in the settings page of the app.
                            </p>
                        </li>
                        <li><code>LogHandler.kt</code>
                            <p>
                                This class is responsible for appending the provided csv strings to logs.
                            </p>
                        </li>
                    </ul>
                    </li>
            <li>Compute Node
                <p>
                    The compute node contains two scripts:
                    <ul>
                    <li>
                        <code>androidRemoteControl</code> is a python script, which sends the command provided as its argument to the <code>commandPort</code> of the android app.
                    </li>
                    <li>
                        <code>dataProcess.py</code> is a python script, which listens at the <code>measurementPort</code> for measurements from the app, and logs the same locally to a .csv file.
                    </li>
                </ul>
                </ul>
    <li><strong>Future Work</strong>
    <ol>
        <li>
            Stream measurements from the Android app to the compute node using IP over USB, bypassing the android debug bridge.
        </li>
        <li>
            Process the 5G NR cellular band information returned by the <code>getBands()</code> API, to display the frequency bands in Hz.
        </li>
        <li>
            Display GPS measurements in the Android UI. These are only logged locally and streamed to the compute node as of now.
        </li>
        <li>
            Display information of neighbouring cells in the Android UI. These are only logged locally and streamed to the compute node as of now.
        </li>
        <li>
            Display build version or build date in the app.
        </li>
        <li>
            Allow the <code>remoteAndroidControl</code> script to reset all settings to default.
        </li>
        <li>
            Allow reset to default from the settings page.
        </li>
        <li>
            Test with 5G SA base stations.
        </li>
        <li>
            Return, from the Android app to the remote control script, the result of processing commands.
        </li>
        <li>
            Support iPhone.
        </li>
        <li>
            Develop a log visualizer, that replays a log by showing measurements at various time instants, and if captured, GPS locations.
        </li>
    </ol>
    </li>
</ol>
</div>
