import streamlit as st
import pickle
import pandas as pd
import requests
import os

# =======================
# STREAMLIT CONFIG
# =======================
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title("🎬 Movie Recommender System")

# =======================
# TMDB API KEY
# =======================
API_KEY = os.getenv("TMDB_API_KEY") or "c9e3b5a3e5b45dfdf1c4ddbe25d9eeb7"

# =======================
# LOAD DATA (SAFE PATH)
# =======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MOVIES_PATH = os.path.join(BASE_DIR, "Movies_dict.pkl")

with open(MOVIES_PATH, "rb") as f:
    Movies_dict = pickle.load(f)

Movies = pd.DataFrame(Movies_dict)

# ⚠️ CHANGE THIS KEY IF NEEDED
cs = Movies_dict["similarity"] if "similarity" in Movies_dict else Movies_dict["cs"]

# =======================
# FETCH MOVIE POSTER
# =======================
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {"api_key": API_KEY}
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
# RECOMMEND FUNCTION
# =======================
def recommend(movie):
    movie_index = Movies[Movies["title"] == movie].index[0]
    distances = cs[movie_index]

    movies_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    names = []
    posters = []

    for i in movies_list:
        movie_id = Movies.iloc[i[0]].movie_id
        names.append(Movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters

# =======================
# UI
# =======================
selected_movie = st.selectbox("Select a movie", Movies["title"].values)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)
    cols = st.columns(5)

    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)

