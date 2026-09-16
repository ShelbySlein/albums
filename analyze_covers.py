import pandas as pd
import numpy as np
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity

# Load album catalog
df = pd.read_csv("data/albums.csv")

features = []
vectors = []

for idx, row in df.iterrows():
    img_path = row["cover_image"]
    with Image.open(img_path) as img:
        img_rgb = img.convert("RGB")
        arr = np.array(img_rgb)
        
        # Color channels
        r_mean = arr[:, :, 0].mean()
        g_mean = arr[:, :, 1].mean()
        b_mean = arr[:, :, 2].mean()
        
        # HSV metrics (brightness & saturation)
        arr_hsv = np.array(img.convert("HSV"))
        s_mean = arr_hsv[:, :, 1].mean() / 255.0
        v_mean = arr_hsv[:, :, 2].mean() / 255.0
        
        # Colorfulness metric
        rg = np.abs(arr[:, :, 0].astype(float) - arr[:, :, 1].astype(float))
        yb = np.abs(0.5 * (arr[:, :, 0].astype(float) + arr[:, :, 1].astype(float)) - arr[:, :, 2].astype(float))
        colorfulness = np.sqrt(rg.var() + yb.var()) + 0.3 * np.sqrt(rg.mean()**2 + yb.mean()**2)
        
        # Hex code for dominant average color
        hex_color = "#{:02x}{:02x}{:02x}".format(int(r_mean), int(g_mean), int(b_mean))
        
        features.append({
            "artist": row["artist"],
            "album": row["album"],
            "release_year": row["release_year"],
            "cover_image": img_path,
            "brightness": round(v_mean, 3),
            "saturation": round(s_mean, 3),
            "colorfulness": round(colorfulness, 1),
            "avg_color_hex": hex_color,
            "mean_red": round(r_mean, 1),
            "mean_green": round(g_mean, 1),
            "mean_blue": round(b_mean, 1)
        })
        
        # Feature vector for visual similarity (spatial thumbnail + color histogram)
        thumb = img_rgb.resize((32, 32))
        thumb_arr = np.array(thumb, dtype=float).flatten() / 255.0
        hist, _ = np.histogramdd(arr.reshape(-1, 3), bins=(4, 4, 4), range=[(0, 256), (0, 256), (0, 256)])
        hist_feat = hist.flatten() / hist.sum()
        vectors.append(np.concatenate([thumb_arr * 0.5, hist_feat * 0.5]))

# 1. Save album features
feat_df = pd.DataFrame(features)
feat_df.to_csv("data/album_features.csv", index=False)

# 2. Pairwise similarity matrix
sim_matrix = cosine_similarity(vectors)
album_names = df["artist"] + " - " + df["album"]
matrix_df = pd.DataFrame(sim_matrix, index=album_names, columns=album_names)
matrix_df.to_csv("data/similarity_matrix.csv")

# 3. Ranked pairwise comparisons
pairs = []
for i in range(len(album_names)):
    for j in range(i + 1, len(album_names)):
        pairs.append({
            "album_1": album_names[i],
            "album_2": album_names[j],
            "similarity": round(float(sim_matrix[i, j]), 3)
        })

pairs_df = pd.DataFrame(pairs).sort_values("similarity", ascending=False)
pairs_df.to_csv("data/album_similarity.csv", index=False)

print("Analysis complete: saved features, matrix, and ranked pairs.")
