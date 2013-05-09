/*
	CordovaPlugin (Android): Download Manager (Notification Bar Support)
	Author: aabilio - aabilio[at]gmail.com (@aabilio)
	
	[Based on the following implementations:
		- http://teusink.blogspot.com.es/2013/04/phonegap-android-downloader-plugin.html
		- http://www.toforge.com/2011/02/phonegap-android-plugin-for-download-files-from-url-on-sd-card/
	]

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

package org.apache.cordova.plugins.DownloadManager;

import com.aabilio.pydowntv2.R;
import org.apache.cordova.plugins.DownloadManager.Downloader;
import org.apache.cordova.plugins.DownloadManager.DownloadControllerSingleton;

import org.apache.cordova.api.CallbackContext;
import org.apache.cordova.api.CordovaPlugin;
import org.apache.cordova.api.PluginResult;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import android.os.Environment;
import android.util.Log;

import java.util.Random;

public class DownloadManager extends CordovaPlugin {
	
	DownloadControllerSingleton downloading_ids = DownloadControllerSingleton.getInstance();

	@Override
	public boolean execute(String action, final JSONArray args, final CallbackContext callbackContext) {
		if (action.equals("start")) {
			cordova.getThreadPool().execute(new Runnable() {
				public void run() {
					try {
						/* Get OPTIONS */
						JSONObject params = args.getJSONObject(0);
						String fileUrl    = params.getString("url");
						Boolean overwrite = params.getBoolean("overwrite");
						String fileName   = params.has("fileName") ? 
											params.getString("fileName"):
											fileUrl.substring(fileUrl.lastIndexOf("/")+1);
						String filePath   = params.has("filePath") ? 
											params.getString("filePath"):
											cordova.getActivity().getString(R.string.app_name);
						String startToast = params.has("startToast") ? 
											params.getString("startToast"):
											"Download Start!";
						String ticker	  = params.has("ticker") ?
											params.getString("ticker") :
											"Downloading...";
						String endToast   = params.has("endToast") ?
											params.getString("endToast") :
											"Download Complete!";
						String cancelToast= params.has("cancelToast") ?
											params.getString("cancelToast") :
											"Download canceled!";
						Boolean useNotificationBar = params.has("useNotificationBar") ?
													 params.getBoolean("useNotificationBar") : true;
						String notificationTitle   = params.has("notificationTitle") ?
													 params.getString("notificationTitle") :
													 "Downloading: "+fileName;
						
						String dirName = Environment.getExternalStorageDirectory().getAbsolutePath() + "/Download/"+ filePath +"/";
						
						// Get an ID:
						int downloader_id = new Random().nextInt(10000);
						String downloader_id_str = String.valueOf(downloader_id); 
						
						// Instantiate Downloader with the ID:
						Downloader downloadFile = new Downloader(
																downloader_id_str,
																fileUrl,
																dirName,
																fileName,
																overwrite,
																startToast,
																ticker,
																notificationTitle,
																endToast,
																cancelToast,
																useNotificationBar,
																callbackContext,
																cordova,
																webView
																);
						// Store ID: ATT! GLobal Here!
						//DownloadControllerGlobals.ids.add(downloader_id_str);
						downloading_ids.add(downloader_id_str);
						
						// Start Download
						downloadFile.run();
					} catch (JSONException e) {
						e.printStackTrace();
						Log.e("PhoneGapLog", "DownloaderMaganager Plugin: Error: " + PluginResult.Status.JSON_EXCEPTION);
						callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.JSON_EXCEPTION));
					} catch (InterruptedException e) {
						e.printStackTrace();
						Log.e("PhoneGapLog", "Downloader Plugin: Error: " + PluginResult.Status.ERROR);
						callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.ERROR));
					}
				}
			});
			return true;
		} else if (action.equals("cancel")) {
			cordova.getThreadPool().execute(new Runnable() {
				public void run() {
					try {
						JSONObject params = args.getJSONObject(0);
						String cancelID	  = params.has("id") ? params.getString("id") : null;
						Log.d("PhoneGapLog", "Este es el ID que me llega para cancelar: "+cancelID);
						
						if (cancelID == null) {
							callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.ERROR, "ID not found"));
						}
						//if (DownloadControllerGlobals.ids.indexOf(cancelID) == -1) {
						if (!downloading_ids.isId(cancelID)) {
							callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.ERROR, "The id has no download associated"));
						} else {
							//DownloadControllerGlobals.ids.remove(DownloadControllerGlobals.ids.indexOf(cancelID));
							downloading_ids.del(cancelID);
						}
					} catch (JSONException e) {
						e.printStackTrace();
						Log.e("PhoneGapLog", "DownloaderMaganager Plugin: Error: " + PluginResult.Status.JSON_EXCEPTION);
						callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.JSON_EXCEPTION));
					}
				}
			});
			return true;
		} else if (action.equals("isdownloading")) {
			cordova.getThreadPool().execute(new Runnable() {
				public void run() {
					try {
						JSONObject params = args.getJSONObject(0);
						String cancelID	  = params.has("id") ? params.getString("id") : null;
						Log.d("PhoneGapLog", "Este es el ID que me llega para cancelar: "+cancelID);
						
						if (cancelID == null) {
							callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.ERROR, "Error checking id"));
						}
						if (!downloading_ids.isId(cancelID)) {
							callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.OK, false));
						} else {
							callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.OK, true));
						}
					} catch (JSONException e) {
						e.printStackTrace();
						Log.e("PhoneGapLog", "DownloaderMaganager Plugin: Error: " + PluginResult.Status.JSON_EXCEPTION);
						callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.JSON_EXCEPTION));
					}
				}
			});
			return true;
		} else {
			Log.e("PhoneGapLog", "Downloader Plugin: Error: " + PluginResult.Status.INVALID_ACTION);
			callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.INVALID_ACTION));
			return false;
		}
	}
	
}


