import pickle
import streamlit as st
import requests
import time

def fetch_poster(movie_id, retries=3, delay=2):
    for attempt in range(retries):
        try:
            url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
            response = requests.get(url, timeout=10)  # Increased timeout
            response.raise_for_status()
            data = response.json()
            poster_path = data.get('poster_path')  # Use .get() to avoid KeyError
            if poster_path:
                full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
                return full_path
            else:
                st.warning(f"No poster available for movie ID {movie_id}")
                return "https://via.placeholder.com/500x750?text=Poster+Not+Available"
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:  # Don't wait on the last attempt
                time.sleep(delay)  # Wait before retrying
            else:
                st.warning(f"Failed to fetch poster for movie ID {movie_id} after {retries} attempts: {e}")
                return "https://via.placeholder.com/500x750?text=Poster+Not+Available"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movie_names = []
    recommended_movie_posters = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        poster_url = fetch_poster(movie_id)
        if poster_url:  # Only add if poster URL is fetched successfully
            recommended_movie_posters.append(poster_url)
            recommended_movie_names.append(movies.iloc[i[0]].title)

    return recommended_movie_names, recommended_movie_posters

st.header('Movie Recommender System')
movies = pickle.load(open('movie_list.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

movie_list = movies['title'].values
selected_movie = st.selectbox(
    "Type or select a movie from the dropdown",
    movie_list
)

if st.button('Show Recommendation'):
    recommended_movie_names, recommended_movie_posters = recommend(selected_movie)
    if recommended_movie_names:  # Check if recommendations are available
        col1, col2, col3, col4, col5 = st.columns(5)
        for i, (name, poster) in enumerate(zip(recommended_movie_names, recommended_movie_posters)):
            with eval(f"col{i+1}"):  # Dynamically assign columns
                st.text(name)
                st.image(poster)
    else:
        st.warning("No recommendations available or failed to fetch data.")