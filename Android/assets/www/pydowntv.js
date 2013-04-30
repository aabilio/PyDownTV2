// GLOBALS:
var pydowntv_api_url = 'http://pydowntv.com/api?url=';
var cont = "cc";

// DEBUG:
var hola;
var url_example = 'http://www.mitele.es/series-online/aida/temporada-8/capitulo-145/';


var parsePydowntvAPI = function(api){
	//Lungo.Notification.hide();
	if (api.exito === true) {
		Lungo.Notification.success(
		    "Enhorabuena",
		    "Vídeo encontrado correctamente",
		    "check",
		    4,
		    null
		);

		
		for (v=0; v<api.num_videos; v++) {
			for (p=0; p<api.videos[v].partes; p++) {
				html = '<li data-image="'+api.videos[v].url_img+'" class="thumb video_result '+cont+'"> \
					<img src="'+api.videos[v].url_img+'" class="icon"/> \
					<strong>'+api.titulos[v]+'</strong> \
					 <a href="#" class="right tag red">Parte '+(parseInt(p)+parseInt(1))+'</a> \
					<small>'+api.descs[v]+'</small> \
					<div class="form" style="display:none;" data-isactive="false"> \
						<br /> \
						<span>Progreso:</span>\
                        <div id="progress-normal" data-progress="25%"> \
                            <div class="progress"> \
                                <span class="bar"> \
                                    <span class="value" style="width: 25%"></span> \
                                </span> \
                            </div> \
                        </div> \
                        <a href="#" class="left tag blue"> \
                        	24%\
                    	</a> \
                        <a href="#" class="button small cancel right"> \
                        	Cancelar \
                    	</a> \
                    	<br /><br /> \
                    </div>';
				$$('#video_results').append(html);
			}
		}
		

		Lungo.dom('.video_result.'+cont).on("tap", function(event) {
		    //Lungo.dom(this).toggleClass('light').toggleClass('dark');
	    	if (this.lastElementChild.getAttribute("data-isactive") === "false") {
		    	this.lastElementChild.setAttribute('style', 'display:block;');
		    	this.lastElementChild.setAttribute("data-isactive", "true");
		    } else {
		    	this.lastElementChild.setAttribute('style', 'display:none;');
		    	this.lastElementChild.setAttribute("data-isactive", "false");
		    }
		});
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
	}



});






