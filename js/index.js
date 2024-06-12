$(document).ready(function() {
    $('#upload-form').on('submit', function(e) {
        e.preventDefault(); // Mencegah form dikirim secara normal

        var formData = new FormData(this);

        $.ajax({
            type: 'POST',
            url: '/index.html', // Rute Flask untuk menerima gambar
            data: formData,
            contentType: false,
            cache: false,
            processData: false,
            success: function(response) {
                // Menangani respons dari server Flask
                $('#prediction-result').html(response.prediction);
                $('#image-preview').attr('src', response.image_path);
            },
            error: function(xhr, status, error) {
                console.log(error);
            }
        });
    });
});