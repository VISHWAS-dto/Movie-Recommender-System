import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests
import os

# =======================
# TMDB API KEY
# =======================
API_KEY = os.getenv("TMDB_API_KEY")  # set in Streamlit Cloud secrets


# =======================
# FETCH MOVIE POSTER
# =======================
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {
            "api_key": API_KEY,
            "language": "en-US"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
        else:
            return "https://via.placeholder.com/500x750?text=No+Poster"

    except Exception:
        return "https://via.placeholder.com/500x750?text=Error"


# =======================
# LOAD MOVIES DATA
# =======================
if not os.path.exists("Movies_dict.pkl"):
    st.error("Movies_dict.pkl file is missing")
    st.stop()

Movies_dict = pickle.load(open("Movies_dict.pkl", "rb"))
Movies = pd.DataFrame(Movies_dict)


# =======================
# LOAD / GENERATE SIMILARITY MATRIX
# =======================
if not os.path.exists("cs.pkl"):
    import generate_cs  # auto-create cs.pkl

cs = pickle.load(open("cs.pkl", "rb"))


# =======================
# RECOMMEND FUNCTION
# =======================
def recommend(movie):
    movie_index = Movies[Movies['title'] == movie].index[0]
    distances = cs[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        reverse=True,
        key=lambda x: x[1]
    )[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_list:
        movie_id = Movies.iloc[i[0]].movie_id
        recommended_movies.append(Movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters


# =======================
# STREAMLIT UI
# =======================
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommender System")

selected_movie_name = st.selectbox(
    "Select a movie",
    Movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)
