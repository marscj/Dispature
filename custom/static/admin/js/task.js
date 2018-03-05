
(function($) {
    'use strict';

    $(document).ready(function() {
        ready();

        function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }

        function csrfSafeMethod(method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        $.ajaxSetup({
            url: "/admin/resource/",
            type: 'POST', //GET
            async: false,
            // timeout:5000,
            dataType: 'json',
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        });

        $('body').on('click', function(e) {
            if (ready()) {
                getData();
            }
        });

        function getStartTime() {
            var date = $('#id_start_time_0').val()
            var time = $('#id_start_time_1').val()

            if (typeof(date) == "undefined" || typeof(time) == "undefined" || date == "" || time == "") {
                return null
            }
            return date + ' ' + time;
        }

        function getEndTime() {
            var date = $('#id_end_time_0').val()
            var time = $('#id_end_time_1').val()

            if (typeof(date) == "undefined" || typeof(time) == "undefined" || date == "" || time == "") {
                return null
            }
            return date + ' ' + time;
        }

        function ready() {
            if (getStartTime() == null || getEndTime() == null || (ready.start == getStartTime() && ready.end == getEndTime())) {
                return false
            }

            console.log(getStartTime() + " " + getEndTime());
            ready.start = getStartTime();
            ready.end = getEndTime();
            return true;
        }

        function reset(id) {
            $(id).html('---------')
            $(id).attr('title', '---------')
        }

        function getData() {
            // getData.loading = layer.load()
            $.ajax({
                data: {
                    'start_time': getStartTime(),
                    'end_time': getEndTime(),
                },
                success: function(data) {
                    var driver = $.parseJSON(data.driver);
                    var driver_content = '<option value selected>---------</option>';
                    var tourguide = $.parseJSON(data.tourguide);
                    var tourguide_content = '<option value selected>---------</option>';
                    var vehicle = $.parseJSON(data.vehicle);
                    var vehicle_content = '<option value selected>---------</option>';

                    $.each(driver, function(i, item) {
                        driver_content += '<option value=' + item.pk + '>' + item.fields.phone + '</option>'
                    });

                    $.each(tourguide, function(i, item) {
                        tourguide_content += '<option value=' + item.pk + '>' + item.fields.phone + '</option>'
                    });

                    $.each(vehicle, function(i, item) {
                        vehicle_content += '<option value=' + item.pk + '>' + item.fields.traffic_plate_no + '</option>'
                    });

                    reset('#select2-id_driver-container')
                    reset('#select2-id_tourguide-container')
                    reset('#select2-id_vehicle-container')

                    $('#id_driver').html(driver_content);
                    $('#id_tourguide').html(driver_content);
                    $('#id_vehicle').html(vehicle_content);

                    // layer.close(getData.loading);
                },

                error: function() {
                    // layer.close(getData.loading);
                    alert('error');
                },
            });
        }
    });

}(django.jQuery));