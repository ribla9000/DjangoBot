$(document).ready(function(){
  var form = $('#price_and_form');
  $(document).on('click', '.button-send',function(evnt){
    evnt.preventDefault();
    console.log("U gey")
  });

      var data = {};
      data.product_id = product_id;
      data.product_price = product_price;
      data.product_name = product_name;
      data.product_discount = product_discount;
      data.product_price_with_discount =product_price_with_discount;
      data.nmb = nmb;
      var csrf_token = $('#price_and_form [name = "csrfmiddlewaretoken"]').val();
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
          console.log(data.product_total_number);
          if (data.product_total_number) {
            $('#basket_total').text(data.product_total_number); 
          };
        };
      });
  });
  


