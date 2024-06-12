$(document).ready(function () {
  // -[Prediksi Model]---------------------------

  // Fungsi untuk memanggil API ketika tombol prediksi ditekan
  $('#prediksi_submit').click(function (e) {
    e.preventDefault();

    $('#placeholder-apilkasi').remove();
    // Get File Gambar yg telah diupload pengguna
    var file_data = $('#input_gambar').prop('files')[0];
    var pics_data = new FormData();
    pics_data.append('file', file_data);

    $('#hasil_prediksi').html('<p>Loading...</p>');

    // Panggil API dengan timeout 1 detik (1000 ms)
    setTimeout(function () {
      try {
        $.ajax({
          url: '/api/deteksi',
          type: 'POST',
          data: pics_data,
          processData: false,
          contentType: false,
          success: function (res) {
            // Ambil hasil prediksi dan path gambar yang diprediksi dari API
            res_data_prediksi = res['prediksi'];
            res_gambar_prediksi = res['gambar_prediksi'];
            res_akurasi_prediksi = res['akurasi'];  // Ambil nilai akurasi

            $('#loading_indicator').hide();
            // Tampilkan hasil prediksi ke halaman web
            generate_prediksi(res_data_prediksi, res_gambar_prediksi, res_akurasi_prediksi);

          },
        });
      } catch (e) {
        // Jika gagal memanggil API, tampilkan error di console
        console.log('Gagal !');
        console.log(e);
      }
    }, 1000);
  });

  // Fungsi untuk menampilkan hasil prediksi model
  function generate_prediksi(data_prediksi, image_prediksi, akurasi_prediksi) {  // Tambahkan parameter akurasi
    var str = '';

    if (image_prediksi == '(none)') {
      str += '<br>';
      str += '<h4>Please upload image file (.jpg)</h4>';
    } else {
      str += '<br>';
      str += "<img src='" + image_prediksi + '\' width="400"></img>';
      str += '<p>The result is:</p>';
      str += '<h2>' + data_prediksi + '</h2>';
      str += '<p>Accuracy: ' + (akurasi_prediksi * 100).toFixed(2) + '%</p>';  // Tampilkan akurasi
    }
    $('#hasil_prediksi').html(str);
  }
  fetch('http://localhost:5000/get-news')
  .then(response => response.json())
  .then(data => {
      const boxes = document.querySelectorAll('.news-card');
      data.forEach((news, index) => {
          if (index < boxes.length) {
              boxes[index].querySelector('h2').innerText = news.title;
              boxes[index].querySelector('p').innerText = news.summary;
              boxes[index].querySelector('a').href = news.link;
              boxes[index].querySelector('img').src = news.image;
          }
      });      
  })
  .catch(error => console.error('Error:', error));
});


