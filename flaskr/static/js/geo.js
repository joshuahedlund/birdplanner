function getCoordinates(address) {
   var url = `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=${encodeURIComponent(address)}`;

   fetch(url)
       .then(response => response.json())
       .then(data => {
           if (data && data.length > 0) {
               var lat = data[0].lat;
               var lon = data[0].lon;

               if (lat && lon) {
                   document.getElementById('latitude').value = lat;
                   document.getElementById('longitude').value = lon;
               }
           }
       })
       .catch(error => console.error('Error:', error));
}