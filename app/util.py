def to_geo_json(plot):
    if "hex" in plot:
        plot["icao"] = plot["hex"]
    geo_obj = {
            "type": "Feature",
            "properties": plot,
            "geometry": {
                "type": "Point",
                "coordinates": [plot["lon"], plot["lat"]]
            }
    }

    return geo_obj