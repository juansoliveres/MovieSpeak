function displayMovieImagesWithLinks(imageUrls, movieIds) {
    if (!imageUrls || !movieIds || imageUrls.length !== movieIds.length) {
        console.error('Invalid image URLs or movie IDs provided');
        return;
    }

    const imageContainer = document.getElementById('movie-images-container');
    imageContainer.innerHTML = '';

    for (let i = 0; i < imageUrls.length; i++) {
        const imageUrl = imageUrls[i];
        const movieId = movieIds[i];

        const imgElement = document.createElement('img');
        imgElement.src = imageUrl;
        imgElement.alt = 'Movie Image';
        imgElement.style.width = '200px';
        imgElement.style.margin = '30px';

        const linkElement = document.createElement('a');
        linkElement.href = `https://www.themoviedb.org/movie/${movieId}`;
        linkElement.target = '_blank'; // Open link in a new tab
        linkElement.appendChild(imgElement);

        imageContainer.appendChild(linkElement);
    }
}


async function fetchMovieImages(movieIds) {
    const apiKey = 'd3aaf25b70b88ed723ce5dd53695654e';
    const imageBaseUrl = 'https://image.tmdb.org/t/p/w500';
    const movieImages = [];

    for (const movieId of movieIds) {
        const url = `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}`;
        const response = await fetch(url);
        const movieData = await response.json();

        if (movieData && movieData.poster_path) {
            movieImages.push(imageBaseUrl + movieData.poster_path);
        } else {
            console.error('No poster path available for movieId:', movieId);
        }
    }

    return movieImages;
}

function setupScrollButtons() {
    const container = document.getElementById('movie-images-container');
    const scrollRightButton = document.getElementById('scroll-right');
    const scrollLeftButton = document.getElementById('scroll-left');
    
    scrollRightButton.addEventListener('click', () => {
        container.scrollLeft += 780; // Adjust this value based on your actual image and margin widths
        scrollLeftButton.style.display = 'block'; // Show left arrow when scrolling right
    });

    scrollLeftButton.addEventListener('click', () => {
        container.scrollLeft -= 780; // Adjust this value as needed
        if (container.scrollLeft === 0) {
            scrollLeftButton.style.display = 'none'; // Hide left arrow if at start
        }
    });
}

tmdb_ids = eval(tmdb_ids)
fetchMovieImages(tmdb_ids)
    .then((imageUrls) => {
        // Display movie images on the webpage
        displayMovieImagesWithLinks(imageUrls, tmdb_ids);
    })
    .catch((error) => {
        console.error('Error fetching movie images:', error);
    });

setupScrollButtons();
    