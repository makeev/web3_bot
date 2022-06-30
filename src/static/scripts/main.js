const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");

function validate_json(str) {
    try {
        return JSON.parse(str);
    } catch (e) {
        return false;
    }
}

function show_alert(type, message) {
    // types: success, danger, warning, info, primary, secondary
    $('#alert').attr('class', 'alert alert-' + type);
    $('#alert .message').html(message);

    $("#alert").fadeTo(3000, 500).slideUp(500, function () {
        $("#alert").slideUp(500);
    });
}

var small_spinner_html = '<div class="spinner-border spinner-border-sm text-secondary" role="status"><span class="sr-only">Загрузка...</span></div>';
var big_spinner_html = '<div class="spinner-border text-primary" role="status"><span class="sr-only">Загрузка...</span></div>';

function clear_form_validation(form) {
    form.find('select,textarea,input').each(function (key, el) {
        var $input = $(el);
        $input.removeClass('is-invalid');
    });

    form.find('.feedback').each(function (key, el) {
        $(el).removeClass('invalid-feedback').text('');
    });
}

function parse_errors(errors, form) {
    var elements_with_errors = [];
    $.each(errors, function (input_name, errors_list) {
        // if list of strings - display it, else parse nested list
        if (Array.isArray(errors_list)) {
            var $input = form.find('[name=' + input_name + ']');
            $input.addClass('is-invalid');
            $input.parent().find('.feedback').addClass('invalid-feedback').text(errors_list.join(' '));
            elements_with_errors.push($input);
        } else {
            console.log(errors_list)
            elements_with_errors.concat(parse_errors(errors_list, form));
        }
    });

    return elements_with_errors;
}


/**
 * Send form using POST request and parse validation response
 * @param $form
 * @param data (optional) - default $form.serialize()
 * @param contentType (optional)
 */
function post_form($form, data, contentType) {

    if (data === undefined) {
        data = $form.serialize();
    }

    var params = {
        url: $form.attr('action'),
        method: $form.attr('method'),
        data: data,
        dataType: 'json',
        statusCode: {
            200: function (json) {
                clear_form_validation($form);
                show_alert('success', 'Форма сохранена');
            },
            400: function (jqxhr) {
                // clear form validation
                clear_form_validation($form);
                // open accordion to prevent element not in focus error
                $('.collapse').collapse('show');

                // display errors
                var response = jqxhr.responseJSON.errors;
                var $first_element = false;

                var errors = response.form;
                if (errors === undefined) {
                    errors = response.json;
                }

                var elements_with_errors = parse_errors(errors, $form);

                if ($first_element) {
                    var scroll_to = $first_element.offset().top - 50;
                    $([document.documentElement, document.body]).animate({
                        scrollTop: scroll_to
                    }, 300);
                }
            },
            500: function (jqxhr) {
                clear_form_validation($form);
                show_alert("danger", "Ошибка на сервере")
            }
        }
    };

    if (contentType !== undefined) {
        params['contentType'] = contentType;
    }

    $.ajax(params);
}


/**
 * Copyright (c) 2021 Gist Applications Inc.
 *
 * Form serializer capable of handling nested data and arrays. Based largely from
 * the Ben Alman's De-param function from the JQuery BBQ plugin, but altered to
 * have no jQuery dependencies, and convert FormData into javascript objects,
 * instead of query parameters
 *
 * http://benalman.com/projects/jquery-bbq-plugin/
 *
 *
 * @summary Convert form data to javascript object
 * @author Zac Fair <zac@gist-apps.com>
 * @website https://gist-apps.com
 *
 * Created at     : 2021-10-26 3:04:00
 * Last modified  : 2021-10-26 3:04:00
 */

function deepSerializeForm(form) {

    var obj = {};

    var formData = new FormData(form);

    var coerce_types = {'true': !0, 'false': !1, 'null': null, "": null};

    for (var pair of formData.entries()) {

        var key = pair[0];
        var val = pair[1];
        ;
        var cur = obj;
        var i = 0;
        var keys = key.split('][');
        var keys_last = keys.length - 1;

        if (/\[/.test(keys[0]) && /\]$/.test(keys[keys_last])) {

            keys[keys_last] = keys[keys_last].replace(/\]$/, '');

            keys = keys.shift().split('[').concat(keys);

            keys_last = keys.length - 1;

        } else {

            keys_last = 0;
        }

        val = val && !isNaN(val) ? +val              // number
            : val === 'undefined' ? undefined         // undefined
                : coerce_types[val] !== undefined ? coerce_types[val] // true, false, null
                    : val;

        if (keys_last) {

            for (; i <= keys_last; i++) {
                key = keys[i] === '' ? cur.length : keys[i];
                cur = cur[key] = i < keys_last
                    ? cur[key] || (keys[i + 1] && isNaN(keys[i + 1]) ? {} : [])
                    : val;
            }

        } else {

            if (Array.isArray(obj[key])) {

                obj[key].push(val);

            } else if (obj[key] !== undefined) {

                obj[key] = [obj[key], val];

            } else {

                obj[key] = val;

            }

        }

    }

    return obj;
}

$(document).ready(function () {
    $.ajaxSetup({
        error: function(jqXHR) {
            console.log('error 400')
            if (jqXHR.responseJSON && jqXHR.responseJSON.json.error) {
                // ошибка валидации, не хватило полей
                var error = jqXHR.responseJSON.json.error;
                if (error.message) {
                    alert(error.message);
                }
                if (error.error_user_title) {
                    alert(error.error_user_title + error.error_user_msg);
                }
            }
        }
    })

    function getFromSource() {
        var tooltipText = "";
        $.ajax({
            url: $(this).data('source'),
            type: 'GET',
            async: false,
            success: function (response) {
                tooltipText = response;
            }
        });
        return tooltipText;

    }

    $('.my-tooltip').tooltip({
        placement: "right",
        html: true,
        title: getFromSource,
    })
});
