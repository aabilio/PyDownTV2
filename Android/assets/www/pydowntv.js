// GLOBALS:
var pydowntv_api_url = 'http://pydowntv.com/api?url=';
var whereIam = "home";
var cont = "cc";

// DEBUG:
var debug;
var url_example = 'http://www.antena3.com/videos/con-el-culo-al-aire/temporada-2/capitulo-2.html';

// Prototyping
// String.endsWith(String)
if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
    };
}
// String.startsWidth(String)
if (typeof String.prototype.startsWith != 'function') {
  // see below for better implementation!
  String.prototype.startsWith = function (str){
    return this.indexOf(str) == 0;
  };
}


// Pydowntv logic

var onCancelConfirmation = function(progress, data_video) {
	//en vez de borrar:
	//1.Poner a cero el progress y la etiqueta
	Lungo.Element.progress(data_video.html_list.lastElementChild.querySelector('.progress-normal'), 0, false);
	data_video.html_list.lastElementChild.querySelector('.left.tag.blue').textContent = "0%";
	//2.Volver a ocultar lo antterior
	data_video.html_list.lastElementChild.setAttribute("style", "display:none;");
	//3.Poner a false data-isactive
	data_video.html_list.lastElementChild.setAttribute("data-isactive", "false");

	downloadedAlert = "<a style='margin-left:2px;float:right;' href='#' class='left tag cancel'>Cancelado</a>";
	$$(data_video.html_list).prepend(downloadedAlert);

	//data_video.html_list.parentNode.removeChild(data_video.html_list);
	downloadmanager("cancel", {id: progress.id}, function(){}, function(){});
}

var onCancelDonwloadPressed = function(progress, data_video) {
	Lungo.Notification.confirm({
	    icon: 'info',
	    title: '¿Seguro que quieres cancelar la descarga?',
	    description: 'Si confirmas, la descarga del vídeo se cancelará y no se podrá reanudar.',
	    accept: {
	        icon: 'checkmark',
	        label: 'Sí',
	        callback: function() {
	        	onCancelConfirmation(progress, data_video);
	        }
	    },
	    cancel: {
	        icon: 'close',
	        label: 'No',
	        callback: function(){ /* Do nothing */ }
	    }
	});
}

var onDownloadProgress = function(progress, data_video) {
	Lungo.Element.progress(data_video.html_list.lastElementChild.querySelector('.progress-normal'), progress.progress, false);
	data_video.html_list.lastElementChild.querySelector('.left.tag.blue').textContent = progress.progress+"%";
	console.log("Descargando: "+progress.progress+"% ");
	if (progress.progress == 100) { // Descarga completada
		window.plugins.thumbnailer.createVideoThumbnail(progress.dir+progress.file, // Create thumbail
			function(thumbPath) { 
		   		//alert(thumbPath); // should alert created thumbnail image path
		 		if (thumbPath.toLowerCase().indexOf("file://")!=0){
					thumbPath ="file://"+thumbPath;
				}
		 		var thumbFileName = thumbPath.substring(thumbPath.lastIndexOf("/")+1);
		 		var origFileName = thumbFileName.substring(0,thumbFileName.lastIndexOf("."));
				var origFilePath = thumbPath.substring(0,thumbPath.lastIndexOf("."));
					
		 	}
		);
		Lungo.Notification.success(
		    "Enhorabuena",
		    "Vídeo descargado correctamente",
		    "check",
		    2,
		    null
		);

		//en vez de borrar:
		//1.Poner a cero el progress y la etiqueta
		Lungo.Element.progress(data_video.html_list.lastElementChild.querySelector('.progress-normal'), 0, false);
		data_video.html_list.lastElementChild.querySelector('.left.tag.blue').textContent = "0%";
		//2.Volver a ocultar lo antterior
		data_video.html_list.lastElementChild.setAttribute("style", "display:none;");
		//3.Poner a false data-isactive
		data_video.html_list.lastElementChild.setAttribute("data-isactive", "false");

		//document.querySelector('#down_buttom .count').textContent = parseInt(document.querySelector('#down_buttom .count').textContent) + 1;
		setTimeout(function() {
			Lungo.Router.section('downloads'); 
			setTimeout(function() {
				Lungo.Router.back();
			}, 500);
		}, 2000);

		downloadedAlert = "<a style='margin-left:2px;float:right;' href='#' class='left tag accept'>Descargado</a>";
		$$(data_video.html_list).prepend(downloadedAlert);
	}
}

var onDownloadConfirmation = function(data_video) {
	//data_video = Lungo.Data.Cache.get(html_list.getAttribute('data-usercache'));
	data_video.html_list.lastElementChild.setAttribute("style", "display:true;"); //overflow-y
	
	Lungo.Router.section('downloads'); // TEMPORAL FIX
	setTimeout(function() {
		Lungo.Router.back();
	}, 500);

	data_video.html_list.lastElementChild.setAttribute("data-isactive", "true");
	if (!data_video.fileName.endsWith(".mp4")) data_video.fileName = data_video.fileName + '.mp4';

	downloadmanager(
		"start",
		{
			url: data_video.url2down,
			filePath: "Pydowntv",
			fileName: data_video.fileName,
			overwrite: false,
			useNotificationBar: true,
        	startToast: "Preparando la descarga...",
        	endToast: "¡Descarga finalizada!",
        	ticker: data_video.titulo,
        	notificationTitle: data_video.titulo,
        	cancelToast: "¡Descarga Cancelada!"
		},
		function(progress) {
			Lungo.dom(data_video.html_list.lastElementChild.querySelector('.button.small.cancel')).on("tap",function() {
				onCancelDonwloadPressed(progress, data_video);});
			onDownloadProgress(progress, data_video);
		},
		function(error) {
			alert(error);
		}
	);

}

var onVideoResultClick = function(event) {
	data_video = Lungo.Data.Cache.get(this.getAttribute('data-usercache'));
	data_video.html_list = this;
	Lungo.Data.Cache.set(this.getAttribute('data-usercache'), data_video);
	
    if (this.lastElementChild.getAttribute("data-isactive") == "false") {
    	Lungo.Notification.confirm({
		    /*icon: 'info',*/
		    title: '<br />'+data_video.titulo,
		    description: data_video.desc,
		    accept: {
		        icon: 'checkmark',
		        label: 'Descargar el vídeo',
		        callback: function() {
		        	onDownloadConfirmation(data_video);
		        }
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
					fileName: api.videos[v].filename[p],
				};

				Lungo.Data.Cache.set('cache_'+api.videos[v].url_video[p], user_cache);

				html = '<li data-image="'+api.videos[v].url_img+'" class="thumb video_result selectable '+cont+'" data-usercache="'+'cache_'+api.videos[v].url_video[p]+'"> \
					<img style="margin-bottom: 1px;" src="'+api.videos[v].url_img+'" /> \
					<a href="#" class="right tag red">Parte '+(parseInt(p)+parseInt(1))+'</a> \
					<strong>'+api.titulos[v]+'</strong> \
					<small>'+api.descs[v]+'</small></div> \
					<div class="form" style="display:none;" data-isactive="false" data-first="true"> \
						<br /> \
						<span>Progreso:</span>\
                        <div class="progress-normal" data-progress="0%"> \
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
                    </div> \
                    </li>';
				$$('#video_results').append(html);
			}
		}
		
		Lungo.dom('.video_result.'+cont).on("tap", onVideoResultClick);
		cont = cont + "c";


	} else {
		Lungo.Notification.error(
		    "Error",
		    api.mensaje,
		    "cancel",
		    4,
		    null
		);
	}
		
};

Lungo.ready(function(){

});


Lungo.Events.init({
	'load section#main_search': function() {
		whereIam = "home";
	},

	'load section#downloads': function() {
		whereIam = "downloads";
		document.querySelector("#localVideoList").innerHTML = '';
		window.requestFileSystem(LocalFileSystem.PERSISTENT, 0, 
			function (fileSystem) {
				fileSystem.root.getDirectory("Download/Pydowntv", {create: false, exclusive: false}, 
					function(dirEntry) {
						var directoryReader = dirEntry.createReader();
						directoryReader.readEntries(
							function(entries) {
								var i;
								var count = 0;
							    for (i=0; i<entries.length; i++) {
							        if (entries[i].name.endsWith('.mp4') || entries[i].name.endsWith('.flv')) {
							        	html = 	'<li class="thumb video_result selectable arrow" style="word-wrap:break-word;overflow:hidden;"> \
								                    <div style="display:inline-block;float:left;"> \
								                        <img style="margin-bottom:1px;" src="'+entries[i].fullPath+".jpg"+'" /> \
								                    </div> \
								                    <div style="display:inline-block;float:left;width:70%;"> \
								                        <strong>'+entries[i].name+'</strong> \
								                        <small>'+entries[i].fullPath.replace("file://", "")+'</small> \
								                    </div> \
								                </li>';
										$$('#localVideoList').append(html);
										count++;
							        } 
							    }
							    document.querySelector('#down_buttom .count').textContent = count;
							   	$$('#localVideoList li').tap(function() {
							   		window.plugins.videoPlayer.play("file://"+this.querySelector('small').textContent);
								});
							},
							function() {
								alert("Error al leer los archivos de descarga");
							}
						);
					}, 
					function() {
						alert("No se encuentra el directorio");
					}
				);
			},
			function() {
				alert("Error al acceder al disco");
			}
		);
	},

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
		//$$('#Search4url').val(url_example);
		if ($$('#Search4url').val() === '') {
			Lungo.Notification.error(
			    "Error",
			    "Nos has introducido ninguna URL",
			    "cancel",
			    4,
			    null
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






