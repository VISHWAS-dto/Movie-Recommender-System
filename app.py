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
# LOAD FILES SAFELY
# =======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

MOVIES_PATH = os.path.join(BASE_DIR, "Movies_dict.pkl")
CS_PATH = os.path.join(BASE_DIR, "cs.pkl")

# ---- Load Movies Dictionary ----
try:
    with open(MOVIES_PATH, "rb") as f:
        Movies_dict = pickle.load(f)
except Exception as e:
    st.error("❌ Failed to load Movies_dict.pkl")
    st.exception(e)
    st.stop()

# ---- Load Similarity Matrix ----
try:
    with open(CS_PATH, "rb") as f:
        cs = pickle.load(f)
except Exception as e:
    st.error("❌ Failed to load cs.pkl")
    st.exception(e)
    st.stop()

# =======================
# BUILD DATAFRAME
# =======================
Movies = pd.DataFrame(Movies_dict)

# =======================
# FETCH MOVIE POSTER
# =======================
def fetch_poster(movie_id):
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        response = requests.get(
            url,
            params={"api_key": API_KEY},
            timeout=10
        )
        data = response.json()

        if data.get("poster_path"):
            return "https://image.tmdb.org/t/p/w500" + data["poster_path"]
    except:
        pass

    return "https://via.placeholder.com/500x750?text=No+Poster"

# =======================
# RECOMMEND FUNCTION
# =======================
def recommend(movie):
    movie_index = Movies[Movies["title"] == movie].index[0]
    distances = cs[movie_index]

    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:6]

    names = []
    posters = []

    for i in movie_list:
        movie_id = Movies.iloc[i[0]].movie_id
        names.append(Movies.iloc[i[0]].title)
        posters.append(fetch_poster(movie_id))

    return names, posters

# =======================
# STREAMLIT UI
# =======================
selected_movie = st.selectbox(
    "Select a movie",
    Movies["title"].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie)

    cols = st.columns(5)
    for col, name, poster in zip(cols, names, posters):
        with col:
            st.text(name)
            st.image(poster)

