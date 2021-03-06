(function($) {
    'use strict';

    $(document).ready(function() {
        $('strong').hide()

        $('body').on('click', function(e) {
            setupVehicle(getStartTime(), getEndTime())
            setupDriver(getStartTime(), getEndTime())
            setupTourguide(getStartTime(), getEndTime())
        });

        function setupUrl(id, url, key, start, end) {
            if (start == null || end == null) {
                $(id).attr('href', url)
            } else {
                $(id).attr('href', url + '&' + key + 'start_time=' + start + '&' + key + 'end_time=' + end)
            }
        }

        function setupVehicle(start, end) {
            if (setupVehicle.url == null) {
                setupVehicle.url = $('#lookup_id_vehicle').attr('href');
            }
            setupUrl('#lookup_id_vehicle', setupVehicle.url, 'vehicle_task__', start, end)
        }

        function setupDriver(start, end) {
            if (setupDriver.url == null) {
                setupDriver.url = $('#lookup_id_driver').attr('href');
            }
            setupUrl('#lookup_id_driver', setupDriver.url, 'driver_task__', start, end)
        }

        function setupTourguide(start, end) {
            if (setupTourguide.url == null) {
                setupTourguide.url = $('#lookup_id_tourguide').attr('href');
            }
            setupUrl('#lookup_id_tourguide', setupTourguide.url, 'tourguide_task__', start, end)
        }

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
    });
}(django.jQuery));