var pydowntv_api_url = 'http://pydowntv.com/api?url=';

function getVideoInfo(url) {
	$.ajax({
		url: pydowntv_api_url+url,
		dataType: 'jsonp',
		jsonp: 'jsoncallback',
		timeout: 25000,
		success: function(data, status){
			//data loaded
			//alert(data.videos[0].url_video[0]);
			$('#loading').fadeOut();
			//$('#resultados').html('<a href="'+data.videos[0].url_video[0]+'">'+data.videos[0].url_video[0]+'</a>');
			$('.download_link').attr('link', data.videos[0].url_video[0])
			$('.download_link').text(data.titulos[0])
			$('#resultados').fadeIn();
		},
		error: function(){
			//error loading data
			alert('Ha habido un error al obtener el vídeo. Sorry.');
		}
	});
}