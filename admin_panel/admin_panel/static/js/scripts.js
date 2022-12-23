$(document).ready(function(){
	var form = $('#form_btn');
	console.log(form);
	// var shoping_cart_btn = $('#btn-send')
	// form.on('.submit', function(btn_submitted){
	// 	btn_submitted.preventDefault();
	// 	console.log('Submitted');
		// var submit_btn =  $('#btn-send');
		// var product_id = submit_btn.data("product_id");
	$(document).on('click', '.btn_mes',function(evnt){
		evnt.preventDefault();
		console.log("U gey")
	

			var data = {};
			 var csrf_token = $('#form_btn [name = "csrfmiddlewaretoken"]').val();
			 data["csrfmiddlewaretoken"] = csrf_token;
			var url = form.attr("action");
			console.log(data)
			
			
			$.ajax({
			    url: url,
				type: 'POST',
				data: data,
				cache: true,
				success: function (data) {
					console.log("OK");
					if (data.product_total_number) {
						$('#basket_total').text(data.product_total_number);	
					}
					

				}
				/*error: function() {console.log("ERROR")}*/
			})

		
	});

	


})