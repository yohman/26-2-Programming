# Real data snapshots

Main classroom example: **Toei train locations**, using the key-free public endpoint. `toei.json` is an Oedo Line response retrieved 2026-10-14, not an automatically updating feed. Source: https://api-public.odpt.org/api/v4/odpt:Train?odpt:operator=odpt.Operator:Toei&odpt:railway=odpt.Railway:Toei.Oedo . Provider: 東京都交通局・公共交通オープンデータ協議会, CC BY 4.0. Official catalog: https://ckan.odpt.org/dataset/r_train_location-toei . Positions use station IDs, not latitude/longitude. Original `dc:date` and `dct:valid` are retained.

Retrieved on 2026-10-14 for classroom use. These are saved examples, not live feeds. The explorer fetches providers directly when requested; the saved-example button restores the default parameters and labels the response as saved. No automatic polling.

- `weather.json`: Open-Meteo, Tokyo, one day, current/hourly temperature. https://api.open-meteo.com/v1/forecast?latitude=35.68&longitude=139.69&current=temperature_2m&hourly=temperature_2m&forecast_days=1&timezone=Asia%2FTokyo
- `earthquakes.geojson`: USGS past-day M2.5+ feed. https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson
- `pokemon.json`: PokéAPI's own API-data repository, Pikachu form 25. Repository data may contain relative resource URLs; live responses may use absolute URLs. https://raw.githubusercontent.com/PokeAPI/api-data/master/data/api/v2/pokemon-form/25/index.json
- `transit.json`: MBTA route 1 vehicle positions, at most 20 records. Positions belong to their `updated_at` timestamps. https://api-v3.mbta.com/vehicles?filter%5Broute%5D=1&page%5Blimit%5D=20
- `holidays.csv`: Cabinet Office holiday file, original bytes in Shift-JIS. The browser decodes it; downloads from the explorer are UTF-8 copies. https://www8.cao.go.jp/chosei/shukujitsu/syukujitsu.csv

Attribution and API documentation remain visible in the explorer. MapLibre renders coordinates with OpenFreeMap/OpenStreetMap attribution. Pokémon example data comes from the community PokéAPI, not a game-company API.

- `tokyo-metro-doc-example.json`: ODPT's official Train response example, dated **2017-11-28**, copied from the API specification served at https://developer.odpt.org/documents (verified 2026-10-14). It is a documentation example, NOT a fetched live response. Live Tokyo Metro Train requests require registration and `acl:consumerKey`; no key is stored or accepted by this site. Station IDs are not train latitude/longitude.
- `lapd.json`: current LAPD NIBRS Offenses dataset `k7nn-b2ep`, retrieved 2026-10-14, newest 50 coordinate-bearing offenses by `date_occ`. Only `date_occ,area_name,nibr_description,hndrdth_lat,hndrdth_lon` are selected. https://data.lacity.org/Public-Safety/LAPD-NIBRS-Offenses-Dataset/k7nn-b2ep . Coordinates are approximate hundred-block locations; rows are offenses, not unique incidents. This is not a real-time feed. Historical `2nrs-mtv8` is no longer updated and is not used here.
