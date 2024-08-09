document.addEventListener("DOMContentLoaded", function() {
    var form = document.querySelector('.search-form');
    var searchFlag = getCookie('search');
    console.log("Search flag on load: " + searchFlag);

    if (searchFlag === 'false') {
        form.classList.add('hidden');
    } else {
        form.classList.remove('hidden');
    }
});

var button = document.querySelector('.btn');
button.onclick = function(event) {
    event.preventDefault(); // Предотвращаем отправку формы по умолчанию
    var form = document.querySelector('.search-form');
    var searchFlag = getCookie('search');
    console.log("Search flag before click: " + searchFlag);

    if (searchFlag) {
        searchFlag = searchFlag === 'true' ? 'false' : 'true';
        setCookie('search', searchFlag);
        console.log("Search flag after click: " + searchFlag);
        if (searchFlag === 'false') {
            // add class to form
            form.classList.add('hidden');
        } else {
            // remove class from form
            form.classList.remove('hidden');
        }
    } else {
        setCookie('search', 'true');
        console.log("Search flag set to true");
    }
    form.submit();
};

function setCookie(name, value) {
    var expires = "";
    var date = new Date();
    date.setTime(date.getTime() + (365*24*60*60*1000)); // 1 year
    expires = "; expires=" + date.toUTCString();
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    console.log("Cookie set: " + name + "=" + value);
}

function getCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}