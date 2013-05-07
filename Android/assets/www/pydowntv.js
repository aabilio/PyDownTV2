// GLOBALS:
var pydowntv_api_url = 'http://pydowntv.com/api?url=';
var cont = "cc";

// DEBUG:
var hola;
var url_example = 'http://www.antena3.com/videos/con-el-culo-al-aire/temporada-2/capitulo-2.html';

// Prototyping
// String.endsWith(String)
if (typeof String.prototype.endsWith !== 'function') {
    String.prototype.endsWith = function(suffix) {
        return this.indexOf(suffix, this.length - suffix.length) !== -1;
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
}

var onDownloadConfirmation = function(data_video) {
	//data_video = Lungo.Data.Cache.get(html_list.getAttribute('data-usercache'));
	data_video.html_list.lastElementChild.setAttribute("style", "display:true;"); //overflow-y
	
	// Pruebas para refrescar section:
	//alert($$('#video_results').height());
	//alert($$(data_video.html_list).height());
	//$$('#video_results').style('height', ($$('#video_results').height()+$$(data_video.html_list).height()).toString()+'px !important');
	//alert($$('#video_results').height());
	//$$('#video_results').height();
	//Lungo.Router.section("downloads");
	//current = Lungo.Element.Cache.section;
	//query = "section"+"#"+"main_search_main_view";
	//target = Lungo.dom("#main_search_main_view");
	//Lungo.Element.Cache.article.attr('id');
	//Lungo.dom('[data-view-article]').removeClass("active").filter("[data-view-article=#main_search_main_view]").addClass("active");
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
			overwrite: true,
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
	


	/* Not more tap event onVideoResultClick */
	/*Lungo.dom(thiss).off("tap", onCancelDonwloadPressed);*/
	
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
	data_video.html_list = this;
	Lungo.Data.Cache.set(this.getAttribute('data-usercache'), data_video);
	
    if (this.lastElementChild.getAttribute("data-isactive") == "false") {
    	Lungo.Notification.confirm({
		    icon: 'info',
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

				html = '<li data-image="'+api.videos[v].url_img+'" class="thumb video_result '+cont+'" data-usercache="'+'cache_'+api.videos[v].url_video[p]+'"> \
					<img src="'+api.videos[v].url_img+'" /> \
					<strong>'+api.titulos[v]+'</strong> \
					 <a href="#" class="right tag red">Parte '+(parseInt(p)+parseInt(1))+'</a> \
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
                    </div>';
				$$('#video_results').append(html);
			}
		}
		
		Lungo.dom('.video_result.'+cont).on("tap", onVideoResultClick);
		/*Lungo.dom('.video_result.'+cont).on("tap", function(event) {
		});*/
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
		$$('#Search4url').val(url_example); //TEMP !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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






