// Tampilkan/sembunyikan halaman
function showPage(pageId) {
    $('.page').hide()
    $(`#${pageId}`).show();
}

// Registrasi anggota baru
$('#registerForm').submit(function(e) {
    e.preventDefault()

    $.post('/api/register', {
        name: $('#memberName').val(),
        transport: $('#transportType').val()
    })
    .done(function(response) {
        alert(`Member registered! Code: ${response.memberCode}`);
        $('#registerForm')[0].reset()
        $('#transportType').val('BUS')
    })
    .fail(function() {
        alert('Failed to register member. Please try again later.')
    });
});

// Catat Kehadiran
$('#attendanceForm').submit(function(e) {
    e.preventDefault();
    $.post('/api/attendance', {
        code: $('#memberCode').val()
    }, function(response) {
        alert(response.message);
        if (response.needPayment) {
            alert('Payment needed! Amount: ' + response.paymentAmount);
        }
        $('#attendanceForm')[0].reset();
    }).fail(function(xhr) {
        alert(xhr.responseJSON.message);
        $('#attendanceForm')[0].reset()
    });
});

// Memuat daftar kehadiran
function loadAttendanceList() {
    $.get('/api/attendance-list')
    .done(function(response) {
        $('#reportData').html(response);
    })
    .fail(function() {
        $('#reportData').html('<p>Error loading attendance list. Please try again later.</p>');
    });
}

// Memuat daftar pembayaran 
function loadPaymentList() {
    $.get('/api/payment-list')
    .done(function(response) {
        $('#reportData').html(response);
    })
    .fail(function() {
        $('#reportData').html('<p>Error loading payment list. Please try again later.</p>');
    });
}


// Fungsi untuk membayar tagihan anggota
function payNow(memberCode) {
    $.post('/api/pay', { code: memberCode })
    .done(function(response) {
        alert(response.message);  
        loadPaymentList(); 
    })
    .fail(function(xhr) {
        alert(xhr.responseJSON.message);
    });
}