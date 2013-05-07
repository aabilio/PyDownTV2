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

import java.util.ArrayList;

public class DownloadControllerSingleton {
	
	private ArrayList<String> ids = new ArrayList<String>();
	
	protected DownloadControllerSingleton() {}
	
	private static class SingletonHolder { 
		private final static DownloadControllerSingleton INSTANCE = new DownloadControllerSingleton();
	}
	
	public static DownloadControllerSingleton getInstance() {
		return SingletonHolder.INSTANCE;
	}
	
	public void add(String id) {
		this.ids.add(id);
	}
	public void del(String id) {
		try {
			this.ids.remove(this.ids.indexOf(id));
		} catch (Exception e) {
			// TODO: ...
		}
	}
	public void remove(int pos) {
		try {
			this.ids.remove(pos);
		} catch (Exception e) {
			// TODO: ...
		}
	}
	public boolean isId(String id) {
		try {
			if (this.ids.indexOf(id) != -1) return true;
		} catch (Exception e) {
			// TODO: ...
		}
		return false;
	}
	
	
}
