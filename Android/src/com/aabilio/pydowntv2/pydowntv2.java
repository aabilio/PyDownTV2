/*
       Licensed to the Apache Software Foundation (ASF) under one
       or more contributor license agreements.  See the NOTICE file
       distributed with this work for additional information
       regarding copyright ownership.  The ASF licenses this file
       to you under the Apache License, Version 2.0 (the
       "License"); you may not use this file except in compliance
       with the License.  You may obtain a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

       Unless required by applicable law or agreed to in writing,
       software distributed under the License is distributed on an
       "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
       KIND, either express or implied.  See the License for the
       specific language governing permissions and limitations
       under the License.
 */

package com.aabilio.pydowntv2;

import android.os.Bundle;
import android.util.Log;

import org.apache.cordova.*;
import org.apache.cordova.plugins.GlobalFlags;

public class pydowntv2 extends DroidGap
{
    @Override
    public void onCreate(Bundle savedInstanceState)
    {
        super.onCreate(savedInstanceState);
        // Set by <content src="index.html" /> in config.xml
        super.loadUrl(Config.getStartUrl());
        //super.loadUrl("file:///android_asset/www/index.html")
    }
    
    @Override
    public void onStart(){
            super.onStart();
            int fromNotification = getIntent().getExtras().getInt("cancel_download", -1); // getIntE("com.package.from.notification", -1);
            if(fromNotification == 1){
            	Log.d("PhoneGapLog", "LE HE DADO A CANCELAR SISISISISISISISISIS LE HE DADO QUE YO LO VI =================");
                   //callSomeMethod();
                   //int x = y + z;
                   // Do whatever you want basically
            }
    }  
    /*@Override
    public void onStart(Bundle savedInstanceState)
    {
    	//Global variable from GlobalFlags:
		//Log.d("PhoneGapLog", "LE HE DADO A CANCELAR SISISISISISISISISIS LE HE DADO QUE YO LO VI =================");
		//GlobalFlags.CANCEL_DOWLOAD_FLAG = true;
    }*/
}

