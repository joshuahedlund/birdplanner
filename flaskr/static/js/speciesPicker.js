let currentFocus = -1, debounceTimer;

function debounce(func, delay) {
    return function() {
      const context = this;
      const args = arguments;
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => func.apply(context, args), delay);
    };
  }

  const fetchSuggestions = debounce(function(inputField, suggestionsContainer, speciesSearchParams, hotspotSearchParams) {
        // Fetch data for suggestions
        fetch('/api/species-search?' + new URLSearchParams(speciesSearchParams))
          .then(response => response.json())
          .then(data => {
            suggestionsContainer.innerHTML = '';
            data.forEach(item => {
              const query = speciesSearchParams.query;
              const regex = new RegExp(query, 'gi');
              const div = document.createElement('div');
              div.innerHTML = item.name.replace(regex, `<strong>${query}</strong>`);
              div.className = 'suggestion-item';
              div.onclick = function() {
                inputField.value = item.name;
                loadDetails(item.id, hotspotSearchParams);
                suggestionsContainer.innerHTML = '';
                currentFocus = -1;
              };
              suggestionsContainer.appendChild(div);
            });
          });
    }, 500);

  // Function to add active class to suggestion items
  function addActive(suggestions) {
    if (!suggestions) return false;
    removeActive(suggestions);
    if (currentFocus >= suggestions.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = (suggestions.length - 1);
    suggestions[currentFocus].classList.add("autocomplete-active");
  }

  // Function to remove active class from suggestion items
  function removeActive(suggestions) {
    for (var i = 0; i < suggestions.length; i++) {
      suggestions[i].classList.remove("autocomplete-active");
    }
  }

  function loadDetails(speciesId, urlSearchParams) {
    fetch('/api/hotspot-search/' + speciesId + '?' + new URLSearchParams(urlSearchParams))
      .then(response => response.json())
      .then(data => {
        const responseDiv = document.getElementById('responseDiv');
        let text = '';
        for (hotspot of data) {
          if (hotspot.isInTrip) {
            text += `<p class="highlight">`;
           } else {
            text += `<p>`;
            }
          text += `<strong>${hotspot.freq}</strong> <a target="_blank" href="https://ebird.org/hotspot/${hotspot.locId}">${hotspot.name}</a></p>`;
        }
        responseDiv.innerHTML = text;
      });
  }