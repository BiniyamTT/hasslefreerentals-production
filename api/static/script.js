function sendotp() {
    var value = document.getElementById('phonenumber').value;
    $.ajax({
        url: '/sendotp',
        type: 'POST',
        data: { 'data': value }
    });
}