library(tidyverse)
library(jsonlite)
library(httr2)

# List of top pop albums from 2014-2024
albums_list <- tibble::tribble(
  ~artist, ~album, ~year,
  "Taylor Swift", "1989", 2014,
  "Adele", "25", 2015,
  "Justin Bieber", "Purpose", 2015,
  "Rihanna", "Anti", 2016,
  "Ed Sheeran", "Divide", 2017,
  "Lorde", "Melodrama", 2017,
  "Taylor Swift", "Reputation", 2017,
  "Ariana Grande", "Sweetener", 2018,
  "Ariana Grande", "Thank U, Next", 2019,
  "Taylor Swift", "Lover", 2019,
  "Billie Eilish", "When We All Fall Asleep, Where Do We Go?", 2019,
  "Harry Styles", "Fine Line", 2019,
  "Dua Lipa", "Future Nostalgia", 2020,
  "Taylor Swift", "Folklore", 2020,
  "The Weeknd", "After Hours", 2020,
  "Olivia Rodrigo", "Sour", 2021,
  "Adele", "30", 2021,
  "Harry Styles", "Harry's House", 2022,
  "Taylor Swift", "Midnights", 2022,
  "Olivia Rodrigo", "Guts", 2023
)

# Function to search iTunes API for album cover art
fetch_album_data <- \(artist, album, year) {
  query <- URLencode(paste(artist, album))
  api_url <- paste0("https://itunes.apple.com/search?term=", query, "&entity=album&limit=5")
  
  res <- tryCatch(jsonlite::fromJSON(api_url)$results, error = \(e) NULL)
  if (is.null(res) || nrow(res) == 0) return(NULL)
  
  match <- res[1, ]
  # Get high-resolution 600x600 artwork URL
  img_url <- gsub("100x100bb.jpg", "600x600bb.jpg", match$artworkUrl100)
  
  # Clean filename for saving the image
  clean_name <- paste(artist, album) |>
    str_to_lower() |>
    str_replace_all("[^a-z0-9]+", "_") |>
    str_replace_all("^_|_$", "")
  filename <- paste0("data/covers/", clean_name, ".jpg")
  
  # Download image
  download.file(img_url, destfile = filename, mode = "wb", quiet = TRUE)
  
  tibble(
    artist = artist,
    album = album,
    release_year = year,
    album_title_itunes = match$collectionName,
    cover_image = filename,
    image_url = img_url
  )
}

# Ensure directory exists
dir.create("data/covers", recursive = TRUE, showWarnings = FALSE)

# Download all albums and compile into dataframe
cat("Downloading album covers...\n")
albums_df <- purrr::pmap(
  list(albums_list$artist, albums_list$album, albums_list$year),
  fetch_album_data
) |> 
  bind_rows()

# Save metadata to CSV
write_csv(albums_df, "data/albums.csv")
cat("Saved metadata for", nrow(albums_df), "albums to data/albums.csv\n")
