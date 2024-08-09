function setCookie(name, value) {
    var expires = "";
    var date = new Date();
    date.setTime(date.getTime() + (365*24*60*60*1000)); // 1 year
    expires = "; expires=" + date.toUTCString();
    document.cookie = name + "=" + (value || "")  + expires + "; path=/";
    console.log("Cookie set: " + name + "=" + value);
}

function resetSearchCookie() {
    setCookie('search', 'true');
    window.location = '/search';
}
