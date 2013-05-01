// GLOBALS:
var pydowntv_api_url = 'http://pydowntv.com/api?url=';
var cont = "cc";

// DEBUG:
var hola;
var url_example = 'http://www.mitele.es/series-online/aida/temporada-8/capitulo-145/';

//
if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}


function download(url, msg, filename, overwrite) {
	var downloader = cordova.require("cordova/plugin/downloader");
 	downloader.get({fileName: filename, message: msg, url: url, overwrite: overwrite},
  		function() {
   			//console.log("PhoneGap Plugin: Downloader: callback success");
  		},
  		function() {
   			console.log("PhoneGap Plugin: Downloader: callback error");
	   			Lungo.Notification.error(
			    "Error al descargar",                      //Title
			    'Lo sentimos, se ha producido un error al iniciar la descarga',     //Description
			    "cancel",                     //Icon
			    4,                            //Time on screen
			    null             //Callback function
			);
  		}
 	);
}
/*var onCancelDonwloadPressed = function(event) {
	alert("cancel download button pressed");
}

var videoDownload = function(result) {
	thiss = Lungo.Data.Cache.get('this_cache').thiss;
    Lungo.Element.progress(thiss.lastElementChild.querySelector('#progress-normal'), result.progress, true);
    thiss.lastElementChild.querySelector('.left.tag.blue').textContent = result.progress+"%";
    console.log(result.progress);
    if (result.progress == 20) {
    	console.log("intentando cargarme esto");
    	result.status = 1;
    }
}*/

var onDownloadConfirmation = function(event) {
	thiss = Lungo.Data.Cache.get('this_cache').thiss;
	url2down = Lungo.Data.Cache.get('this_cache').url2down;
	titulo = Lungo.Data.Cache.get('this_cache').titulo;
	fileName = Lungo.Data.Cache.get('this_cache').fileName;
	
	if (!fileName.endsWith(".mp4")) fileName = fileName + '.mp4';
	download(url2down, 'Descargando: '+titulo, fileName, false);
	/*window.downloader.downloadFile(url2down, {overwrite: true}, videoDownload, function(error) {
		Lungo.Notification.error(
		    "Error al descargar",                      //Title
		    error,     //Description
		    "cancel",                     //Icon
		    4,                            //Time on screen
		    null             //Callback function
		);
	});*/

	/* Not more tap event onVideoResultClick */
	/*Lungo.dom(thiss).off("tap", onCancelDonwloadPressed);
	Lungo.dom(thiss.lastElementChild.querySelector('.button.small.cancel')).on("tap", onCancelDonwloadPressed);*/
	/*  */

	/* DEPRECATED */
	/* Seguir aquí con la ejecución */
	/*if (thiss.lastElementChild.getAttribute("data-isactive") === "false") {
    	thiss.lastElementChild.setAttribute('style', 'display:block;');
    	thiss.lastElementChild.setAttribute("data-isactive", "true");
    } else {
    	thiss.lastElementChild.setAttribute('style', 'display:none;');
    	thiss.lastElementChild.setAttribute("data-isactive", "false");
    }*/


}

var onVideoResultClick = function(event) {
	data_video = Lungo.Data.Cache.get(this.getAttribute('data-usercache'));
	var user_cache = {
		thiss: this,
		url2down: data_video.url2down,
		titulo: data_video.titulo,
		fileName: data_video.fileName
	};
	Lungo.Data.Cache.set('this_cache', user_cache);
	hola = this;
    /* Ask for download */
    if (true) { /* Firs Time */
    	Lungo.Notification.confirm({
		    icon: 'info',
		    title: '<br />'+data_video.titulo,
		    description: data_video.desc,
		    accept: {
		        icon: 'checkmark',
		        label: 'Descargar el vídeo',
		        callback: onDownloadConfirmation
		    },
		    cancel: {
		        icon: 'close',
		        label: 'Cerrar',
		        callback: function(){ /* Do nothing */ }
		    }
		});
    } else {

    }
}

var parsePydowntvAPI = function(api){
	//Lungo.Notification.hide();
	if (api.exito === true) {
		Lungo.Notification.success(
		    "Enhorabuena",
		    "Vídeo encontrado correctamente",
		    "check",
		    2,
		    null
		);

		
		for (v=0; v<api.num_videos; v++) {
			for (p=0; p<api.videos[v].partes; p++) {
				var user_cache = {
					url_img: api.videos[v].url_img,
					titulo: api.titulos[v],
					desc: api.descs[v],
					url2down: api.videos[v].url_video[p],
					fileName: api.videos[v].filename[p]
				};

				Lungo.Data.Cache.set('cache_'+api.videos[v].url_video[p], user_cache);

				html = '<li data-image="'+api.videos[v].url_img+'" class="thumb video_result '+cont+'" data-usercache="'+'cache_'+api.videos[v].url_video[p]+'"> \
					<img src="'+api.videos[v].url_img+'" class="icon"/> \
					<strong>'+api.titulos[v]+'</strong> \
					 <a href="#" class="right tag red">Parte '+(parseInt(p)+parseInt(1))+'</a> \
					<small>'+api.descs[v]+'</small></div>';/* \
					<div class="form" style="display:none;" data-isactive="false"> \
						<br /> \
						<span>Progreso:</span>\
                        <div id="progress-normal" data-progress="0%"> \
                            <div class="progress"> \
                                <span class="bar"> \
                                    <span class="value" style="width: 0%"></span> \
                                </span> \
                            </div> \
                        </div> \
                        <a href="#" class="left tag blue"> \
                        	0%\
                    	</a> \
                        <a href="#" class="button small cancel right"> \
                        	Cancelar \
                    	</a> \
                    	<br /><br /> \
                    </div>';*/
				$$('#video_results').append(html);
			}
		}
		
		Lungo.dom('.video_result.'+cont).on("tap", onVideoResultClick);
		/*Lungo.dom('.video_result.'+cont).on("tap", function(event) {
		});*/
		cont = cont + "c";


	} else {
		Lungo.Notification.error(
		    "Error",                      //Title
		    api.mensaje,     //Description
		    "cancel",                     //Icon
		    4,                            //Time on screen
		    null             //Callback function
		);
	}
		
    //alert(result.videos[0].url_video[0])
};

Lungo.ready(function(){

	
	



	/*setTimeout(function(){
		Lungo.Element.count("section#main_search nav.right a", 1000);
	},2000);*/
	
	
	

});

Lungo.Events.init({

	'doubleTap section#main_search': function() {
		Lungo.Notification.confirm({
		    icon: 'user',
		    title: 'Prueba Doblre Tap',
		    description: '¿Funciona bien la prueba?',
		    accept: {
		        icon: 'checkmark',
		        label: 'Sí, muy bien',
		        callback: function(){  }
		    },
		    cancel: {
		        icon: 'close',
		        label: 'No (estaría yo aquí! :S)',
		        callback: function(){  }
		    }
		});
	},

	'tap #Search4urlButton': function() {
		//$$('#Search4url').val("http://www.mitele.es/series-online/aida/temporada-9/capitulo-185/"); //TEMP !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
		if ($$('#Search4url').val() === '') {
			Lungo.Notification.error(
			    "Error",                      //Title
			    "Nos has introducido ninguna URL",     //Description
			    "cancel",                     //Icon
			    4,                            //Time on screen
			    null             //Callback function
			);
		} else {
			Lungo.Notification.show();
			Lungo.Service.get(pydowntv_api_url+$$('#Search4url').val(), null, parsePydowntvAPI, "json");

		}
	},

	'swipeLeft section#main_search': function() {
		Lungo.Router.section("downloads");
	},
	'swipeRight section#downloads': function() {
		Lungo.Router.back();
	}

});






