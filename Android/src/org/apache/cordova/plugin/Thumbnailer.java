package org.apache.cordova.plugin;

import org.apache.cordova.api.Plugin;
import org.apache.cordova.api.PluginResult;
import org.json.JSONArray;
import org.json.JSONException;
//import org.json.JSONObject;

//thumbnailer
import android.media.ThumbnailUtils;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.provider.MediaStore.Video.Thumbnails;
import 	java.io.FileOutputStream;

/**
 * This class echoes a string called from JavaScript.
 */
public class Thumbnailer extends Plugin {

    /**
     * Executes the request and returns PluginResult.
     *
     * @param action        The action to execute.
     * @param args          JSONArry of arguments for the plugin.
     * @param callbackId    The callback id used when calling back into JavaScript.
     * @return              A PluginResult object with a status and message.
     */
    public PluginResult execute(String action, JSONArray args, String callbackId) {
        try {
            if (action.equals("createVideoThumbnail")) {
	                String pvUrl = args.getString(0); 
	                if (pvUrl != null && pvUrl.length() > 0) { 
	                	//do smth with pvUrl
	                	
	
	                	// MINI_KIND: 512 x 384 thumbnail 
	                	Bitmap bmThumbnail = ThumbnailUtils.createVideoThumbnail(pvUrl, 
	                					Thumbnails.MINI_KIND);
	                	
	                	try {
	                	       FileOutputStream out = new FileOutputStream(pvUrl+".jpg");
	                	       bmThumbnail.compress(Bitmap.CompressFormat.JPEG, 55, out);
	                	} catch (Exception e) {
	                	       e.printStackTrace();
	                	}
	                	
	                    return new PluginResult(PluginResult.Status.OK, pvUrl+".jpg");
	                } else {
	                    return new PluginResult(PluginResult.Status.ERROR);
	                }
            } else {
                if (action.equals("createImageThumbnail")) {
		                String pvUrl = args.getString(0); 
		                if (pvUrl != null && pvUrl.length() > 0) { 
		                	//do smth with pvUrl
		                	
		                	Bitmap bitmap = BitmapFactory.decodeFile(pvUrl);
		                	
		                	Bitmap bmThumbnail = ThumbnailUtils.extractThumbnail(bitmap, 512, 384);
		                	
		                	try {
		                	       FileOutputStream out = new FileOutputStream(pvUrl+".jpg");
		                	       bmThumbnail.compress(Bitmap.CompressFormat.JPEG, 55, out);
		                	} catch (Exception e) {
		                	       e.printStackTrace();
		                	}
		                	
		                    return new PluginResult(PluginResult.Status.OK, pvUrl+".jpg");
		                } else {
		                    return new PluginResult(PluginResult.Status.ERROR);
		                }
	            } else {
                	return new PluginResult(PluginResult.Status.INVALID_ACTION);
	            }
        	}
            
            
        } catch (JSONException e) {
            return new PluginResult(PluginResult.Status.JSON_EXCEPTION);
        }
    }
}
