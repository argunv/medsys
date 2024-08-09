document.addEventListener('DOMContentLoaded', function() {
    var input = document.getElementById("id_phone");
    if (input) {
        console.log("Initializing intl-tel-input for", input);
        input.onkeyup = function() {
            this.value = this.value.replace(/[^\d]/g, '');
            changePadding();
        };
        window.intlTelInput(input, {
            utilsScript: "/static/js/utils.js",
            initialCountry: "ru",
            geoIpLookup: function(success, failure) {
                fetch('https://ipinfo.io', {
                    cache: 'reload'
                }).then(function(response) {
                    if (response.ok) {
                        return response.json();
                    }
                    throw new Error('Failed: ' + response.status);
                }).then(function(ipinfo) {
                    success(ipinfo.country);
                }).catch(function() {
                    success('us');
                });
            },
            separateDialCode: true,
        });

        observeAriaExpanded();
    } else {
        console.error("Phone input not found");
    }
});

// When the country dropdown is clicked, the padding of the phone field is changed
function observeAriaExpanded() {
    const targetNode = document.querySelector('.iti__selected-country');
    if (!targetNode) {
        console.error("Element with class '.iti__selected-country' not found");
        return;
    }
    const config = { attributes: true, attributeFilter: ['aria-expanded'] };

    const callback = function(mutationsList) {
        for (let mutation of mutationsList) {
            if (mutation.type === 'attributes' && mutation.attributeName === 'aria-expanded') {
                const elem = mutation.target;
                if (elem.getAttribute('aria-expanded') == 'false') {
                    document.querySelector('.field-phone').style.padding = '10px';
                } else {
                    document.querySelector('.field-phone').style.paddingBottom = '300px';
                }
            }
        }
    };

    const observer = new MutationObserver(callback);
    observer.observe(targetNode, config);
}

// When the form is submitted, the innerText of .iti__selected-dial-code is added to the beginning of the phone field value and then converted to a number
document.addEventListener('submit', function(event) {
    var input = document.getElementById("id_phone");
    var dialCode = document.querySelector('.iti__selected-dial-code').innerText;
    var phone = parseInt(input.value);
    if (isNaN(phone)) {
        input.value = '';
        return;
    }
    input.value = dialCode + parseInt(phone);
});

function changePadding() {
    const targetNode = document.querySelector('.iti__selected-country');
    if (targetNode && targetNode.getAttribute('aria-expanded') == 'false') {
        document.querySelector('.field-phone').style.padding = '10px';
    } else {
        document.querySelector('.field-phone').style.paddingBottom = '300px';
    }
}