package com.example.myapplication

import android.os.Bundle
import androidx.preference.EditTextPreference
import androidx.preference.PreferenceFragmentCompat


class SettingsFragment : PreferenceFragmentCompat() {

    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        setPreferencesFromResource(R.xml.root_preferences, rootKey)
        val preference: EditTextPreference? = findPreference("pref_iModemRefreshInterval") as EditTextPreference?
        preference?.setOnPreferenceChangeListener { preference, newValue ->
            try
            {
                val newV = (newValue as String).toLong()
            }
            catch(t:Throwable){

            }
            true
        }
    }
}