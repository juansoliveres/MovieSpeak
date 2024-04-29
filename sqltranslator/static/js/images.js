async function fetchMovieImages(movieIds) {
    const apiKey = 'd3aaf25b70b88ed723ce5dd53695654e';
    const imageBaseUrl = 'https://image.tmdb.org/t/p/w500'; // Base URL for TMDB images
    const movieImages = [];

    for (const movieId of movieIds) {
        const url = `https://api.themoviedb.org/3/movie/${movieId}?api_key=${apiKey}`;
        const response = await fetch(url);
        const movieData = await response.json();

        if (movieData && movieData.poster_path) {
            movieImages.push(imageBaseUrl + movieData.poster_path);
        }
    }

    return movieImages;
}

// Function to display movie images on the page
function displayMovieImages(imageUrls) {
    const imageContainer = document.getElementById('movie-images-container');

    imageUrls.forEach((imageUrl) => {
        const imgElement = document.createElement('img');
        imgElement.src = imageUrl;
        imgElement.alt = 'Movie Image';
        imgElement.style.width = '100px'; // Set the size as required
        imgElement.style.margin = '10px';
        imageContainer.appendChild(imgElement);
    });
}

// Example usage after SQL query result
const movieIds = [693134, 106379, 948549, 578]; // Replace with movie IDs obtained from SQL query
fetchMovieImages(movieIds)
    .then(displayMovieImages)
    .catch(error => console.error('Error fetching movie images:', error));
