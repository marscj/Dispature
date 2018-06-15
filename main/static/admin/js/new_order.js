(function($) {
    'use strict';

    $(document).ready(function() {

        delivery($("#id_delivery_type").val());
        order($("#id_order_type").val());

        $("#id_delivery_type").change(function(){
            delivery($("#id_delivery_type").val());
        });

        $("#id_order_type").change(function(){
            order($("#id_order_type").val());
        });

        function delivery(type) {
            if (type == '0') {
                $('#id_home_delivery_addr').parent().parent().attr("style","display:none");
                $('#id_delivery_addr').parent().parent().attr("style","display:none");
            } else {
                $('#id_home_delivery_addr').parent().parent().attr("style","display:block");
                $('#id_delivery_addr').parent().parent().attr("style","display:block");
            }
        }

        function order(type) {
            switch (type) {
                case '0':
                    $('#id_staff').parent().parent().attr("style","display:block");
                    $('#id_vehicle').parent().parent().attr("style","display:none");
                break;

                case '1':
                    $('#id_staff').parent().parent().attr("style","display:none");
                    $('#id_vehicle').parent().parent().attr("style","display:block");
                break;

                case '2':
                    $('#id_staff').parent().parent().attr("style","display:block");
                    $('#id_vehicle').parent().parent().attr("style","display:none");
                break;
            }
        }
    });

    
}(django.jQuery));