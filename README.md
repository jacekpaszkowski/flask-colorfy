# flask-colorfy

Serwer HTTP wyliczajacy kolor tla na podstawie okladki albumu (k-means + wskaznik "colorfulness", zblizony do koloru tla Spotify na Chromecascie).

Uzywany przez Home Assistant:

1. `sensor.spotify_media_cover_entity_picture` zmienia wartosc (nowy utwor),
2. automatyzacja `[media] Extract Spotify media cover color with WS` wywoluje `pyscript.get_dominant_color_and_set_var`
   (`pyscript/dominant_color.py`), ktory robi `POST` na ten serwer (timeout 10 s; przy bledzie uzywany jest szary `174, 174, 174`),
3. wynik trafia do `var.spotify_media_cover_color` w formacie `r, g, b, luma`,
4. kolor czyta strona `www/spotify-cast/spotify.html` (tlo okladki, przez websocket HA)
   oraz automatyzacja `[media] Spotify cover color changed` (swiatla salonu).

Endpoint: `POST http://animus-nas.lan:8766/background_color`

```json
{ "image_url": "https://...", "k_means": 8, "color_tolerance": 2,
  "image_processing_width": 200, "image_processing_height": 200 }
```

Odpowiedz: `{"r": 200, "g": 30, "b": 40}` (wymagane tylko `image_url`).

Lokalnie (kontener nasluchuje na porcie 80):

    docker build -t jackthemenace/flask-colorfy:latest .
    docker run -p 8766:80 jackthemenace/flask-colorfy
    curl -X POST http://localhost:8766/background_color -H "Content-Type: application/json" -d '{"image_url": "https://..."}'

Wdrozenie na NAS: `./redeploy.sh`
