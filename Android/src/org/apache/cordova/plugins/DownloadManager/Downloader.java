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

import org.apache.cordova.plugins.DownloadManager.DownloadControllerSingleton;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Random;


import org.apache.cordova.CordovaWebView;
import org.apache.cordova.api.CallbackContext;
import org.apache.cordova.api.PluginResult;
import org.apache.cordova.api.CordovaInterface;

import org.json.JSONException;
import org.json.JSONObject;

import android.app.Activity;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Intent;
import android.support.v4.app.NotificationCompat;
import android.util.Log;
import android.widget.Toast;

import com.aabilio.pydowntv2.R;

public class Downloader {
	String id;
	String fileUrl;
	String dirName;
	String fileName;
	boolean overwrite;
	boolean useNotificationBar;
	String startToast;
	String cancelToast;
	String ticker;
	String notificationTitle;
	String endToast;
	CallbackContext callbackContext;
	CordovaInterface cordova;
	CordovaWebView webView;
	
	DownloadControllerSingleton downloading_ids = DownloadControllerSingleton.getInstance();
	
	public Downloader(	String id,
						String fileUrl,
						String dirName,
						String fileName,
						boolean overwrite,
						String startToast,
						String ticker,
						String notificationTitle,
						String endToast,
						String cancelToast,
						boolean useNotificationBar,
						CallbackContext callbackContext,
						CordovaInterface cordova,
						CordovaWebView webView
					 ) {
		this.id 				= id;
		this.fileUrl 			= fileUrl;
		this.dirName 			= dirName;
		this.fileName 			= fileName;
		this.overwrite 			= overwrite;
		this.useNotificationBar = useNotificationBar;
		this.startToast 		= startToast;
		this.ticker 			= ticker;
		this.notificationTitle	= notificationTitle;
		this.endToast			= endToast;
		this.cancelToast		= cancelToast;
		this.callbackContext 	= callbackContext;
		this.cordova 			= cordova;
		this.webView			= webView;
	}
	
	public Boolean run() throws InterruptedException, JSONException {
		cordova.getThreadPool().execute(new Runnable() {
			public void run() {
				NotificationManager mNotifyManager;
				NotificationCompat.Builder mBuilder;
				Intent intent;
				PendingIntent pend;
				int mNotificationId;
				
				Log.d("PhoneGapLog", "dirName:  " + dirName);
				Log.d("PhoneGapLog", "fileName: " + fileName);
				try {
					
					File dir = new File(dirName);
					if (!dir.exists()) {
						dir.mkdirs();
					}
					
					File file = new File(dirName, fileName);
					if (file.exists() && !overwrite) {
						String temp_filename; 
						int i;
						for (i=1;;i++) { // test.txt -> test_1.txt -> test_2.tx -> ... while(file.exists())
							temp_filename = fileName.substring(0, fileName.lastIndexOf('.'))+"_"+String.valueOf(i)+fileName.substring(fileName.lastIndexOf('.'));
							file = new File(dirName, temp_filename);
							if (!file.exists()) {
								fileName = temp_filename;
								break;
							}
						}
					}
					else if (file.exists() && overwrite) {
						file.getCanonicalFile().delete(); //Delete
						file = new File(dirName, fileName); //Declare the same
					}
					
					intent = new Intent ();
					intent.putExtra("cancel_download", 1);
					intent.addFlags (Intent.FLAG_ACTIVITY_NEW_TASK);
					pend = PendingIntent.getActivity(cordova.getActivity(), 0, intent, PendingIntent.FLAG_UPDATE_CURRENT);
					
					mNotifyManager = (NotificationManager) cordova.getActivity().getSystemService(Activity.NOTIFICATION_SERVICE);
					mBuilder = new NotificationCompat.Builder(cordova.getActivity())
						.setSmallIcon(R.drawable.ic_stat_notification)
						.setContentTitle(notificationTitle)
						/*.setSubText("Tap to CANCEL")*/
						.setTicker(ticker)
						.setContentIntent(pend)
						.setContentText("0% - " + fileName);
					
					mNotificationId = new Random().nextInt(10000); 
					
					URL url = new URL(fileUrl);
					HttpURLConnection ucon = (HttpURLConnection) url.openConnection();
					ucon.setRequestMethod("GET");
					ucon.connect();
					InputStream is = ucon.getInputStream();
					byte[] buffer = new byte[1024];
					int readed = 0, progress = 0, totalReaded = 0, fileSize = ucon.getContentLength();
					
					// First Notification (id to Javascript) (not necessary necessary): 
					informProgress(id, true, fileSize, 0, dirName, fileName, callbackContext);
					
					FileOutputStream fos = new FileOutputStream(file);
					showToast(startToast,"short");
					int step = 0;
					while ((readed = is.read(buffer)) > 0 && downloading_ids.isId(id)) {
						fos.write(buffer, 0, readed);
						totalReaded += readed;
						int newProgress = (int) (totalReaded*100/fileSize);
						if (newProgress != progress & newProgress > step) {
							if (useNotificationBar) {
								mBuilder.setProgress(100, newProgress, false);
								mBuilder.setContentText(step + "% - " + fileName);
								mBuilder.setContentIntent(pend);
								mNotifyManager.notify(mNotificationId, mBuilder.build());
							}
							informProgress(id, true, fileSize, step, dirName, fileName, callbackContext);
							step = step + 1;
						}
					}
					// Download canceled??
					if (!downloading_ids.isId(id)) {
						showToast(cancelToast,"short");
						
						fos.flush();
						fos.close();
						is.close();
						ucon.disconnect();
						
						if (useNotificationBar) {
							mBuilder.setContentText("Download of \"" + fileName + "\" canceled").setProgress(0,0,false);
							mNotifyManager.notify(mNotificationId, mBuilder.build());
							
							try {
								Thread.sleep(1000);
			                } catch (InterruptedException e) {
			                	Log.d("PhoneGapLog", "Downloader Plugin: Thread sleep error: " + e);
			                }
							
							mNotifyManager.cancel(mNotificationId);
						}
						
						// Delete file:
						file.getCanonicalFile().delete();
						
						
						callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.OK, "Download properly canceled"));
					} else {
						// Download Normal END (continue)
						if (useNotificationBar) {
							mBuilder.setContentText("Download of \"" + fileName + "\" completed").setProgress(0,0,false);
							mNotifyManager.notify(mNotificationId, mBuilder.build());
						}
						showToast(endToast,"short");
						informProgress(id, false, fileSize, step, dirName, fileName, callbackContext);
						downloading_ids.del(id);
					}
					
					fos.flush();
					fos.close();
					is.close();
					ucon.disconnect();
					
					mNotifyManager.cancel(mNotificationId);
					
					
					if(!file.exists()) {
						showToast("Download went wrong, please try again or contact the developer.","long");
						Log.e("PhoneGapLog", "Downloader Plugin: Error: Download went wrong.");
					}
					//callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.OK));
				} catch (FileNotFoundException e) {
					showToast("File does not exists or cannot connect to webserver, please try again or contact the developer.","long");
					Log.e("PhoneGapLog", "Downloader Plugin: Error: " + PluginResult.Status.ERROR);
					e.printStackTrace();
					callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.ERROR));
				} catch (IOException e) {
					showToast("Error downloading file, please try again or contact the developer.","long");
					Log.e("PhoneGapLog", "Downloader Plugin: Error: " + PluginResult.Status.ERROR);
					e.printStackTrace();
					callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.ERROR));
				} catch (JSONException e) {
					e.printStackTrace();
					callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.JSON_EXCEPTION, e.getMessage()));
				} catch (InterruptedException e) {
					e.printStackTrace();
					callbackContext.sendPluginResult(new PluginResult(PluginResult.Status.ERROR, e.getMessage()));
				}
			}
		});
		return true;
	}
	
	private void showToast(final String message, final String duration) {
		cordova.getActivity().runOnUiThread(new Runnable() {
			public void run() {
				Toast toast;
				if(duration.equals("long")) {
					toast = Toast.makeText(cordova.getActivity(), message, Toast.LENGTH_LONG);
				} else {
					toast = Toast.makeText(cordova.getActivity(), message, Toast.LENGTH_SHORT);
				}
				toast.show();
			}
		});
	}
	
	private void informProgress(
			String id,
			boolean isDownloading,
			int fileSize,
			int progress,
			String dirName,
			String fileName,
			CallbackContext callbackContext
		  ) throws InterruptedException, JSONException {

		JSONObject obj = new JSONObject();
		obj.put("id", id);
		obj.put("downloading", isDownloading);
		obj.put("total", fileSize);
		obj.put("file", fileName);
		obj.put("dir", dirName);
		obj.put("progress", progress);
		
		
		PluginResult res = new PluginResult(PluginResult.Status.OK, obj);
		res.setKeepCallback(true);		
		webView.sendPluginResult(res, callbackContext.getCallbackId());
	}
}
