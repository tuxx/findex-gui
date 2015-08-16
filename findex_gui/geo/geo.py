import geoip2.database

def ip_city(ip):

    reader = geoip2.database.Reader('GeoLite2-City.mmdb')
    response = reader.city(ip)
    d = {
        'country_iso': response.country.iso_code,
        'country_name': response.country.name,
        'city': response.city.name,
        'region_name': response.subdivisions.most_specific.name,
        'postal_code': response.postal.code,
        'location_lat': response.location.latitude,
        'location_long': response.location.longitude
    }

    reader.close()

    return d