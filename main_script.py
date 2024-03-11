import argparse
import pandas as pd 
import requests as req
import json
import re

from shapely.geometry import Point
import geopandas as gpd
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import folium
import webbrowser

#python main_script.py -o italia -d ifema -to embajada -td estacion
parser = argparse.ArgumentParser(description='BiciMad')



# definicion de argumentos
parser.add_argument('-o', '--origen', type=str, help='Origen de usuarios')
parser.add_argument('-d', '--destino', type=str, help='Destino de usuarios')
parser.add_argument('-to', '--type_of_place_origen', type=str, help='Origen de usuarios')
parser.add_argument('-td', '--type_of_place_destino', type=str, help='Destino de usuarios')


parser_args = parser.parse_args()

origen = parser_args.origen
destino= parser_args.destino
type_of_place_origen= parser_args.type_of_place_origen
type_of_place_destino= parser_args.type_of_place_destino


# variables que le paso por terminal, nombre viene del --nombre


url = 'https://openapi.emtmadrid.es/v1/mobilitylabs/user/login/'

headers = {
    'email': 'veronicagrim@hotmail.com',
    'password': 'Proyectodata14'
    }

response = req.request('GET', url, headers=headers)
response.json()
accessToken=response.json()['data'][0]['accessToken']
url='https://openapi.emtmadrid.es/v1/transport/bicimad/stations/'

headers = {
    'accessToken': accessToken,
    }

response = req.request("GET", url, headers=headers)
estaciones=response.json()

estaciones=estaciones['data']
estaciones_api=pd.DataFrame(estaciones)

names=[f['name'].split('-')[1].strip() for f in estaciones]
coordenadas=[[f['geometry']['coordinates'] for f in estaciones]]

estaciones_api['name']=names
estaciones_api['geometry']=coordenadas[0]  


def dividir_lista(row):
    return pd.Series(row['geometry'])
estaciones_api[['longitude', 'latitude']] = estaciones_api.apply(dividir_lista, axis=1)
estaciones_api=estaciones_api.drop(columns=['geometry'])

embajadas = pd.read_csv('data/processed/embajadas.csv')
result = pd.merge(embajadas, estaciones_api, on='number', how='left')



def buscar_origen(type_of_place_origen, origen):
    if type_of_place_origen.lower() == 'embajada' or type_of_place_origen.lower() == 'consulado':
        if type_of_place_origen.lower() == 'embajada':
            filtered_results = result[result['type_of_place'] == 'embajada']
        elif type_of_place_origen.lower() == 'consulado':
            filtered_results = result[result['type_of_place'] == 'consulado']
       
        posibles_coincidencias = process.extract(origen, filtered_results['title'], scorer=fuzz.WRatio, limit=3)
    
        ruta_data_origen = filtered_results[filtered_results['title'].isin([x[0] for x in posibles_coincidencias])]
        ruta_data_origen = ruta_data_origen[(ruta_data_origen['no_available'] == 0) & (ruta_data_origen['dock_bikes'] > 0)]

        if len(ruta_data_origen) == 0:
            print(f"No se encontraron datos para el origen '{origen}' que cumplan con las condiciones")
            
        mensaje = f'HOLA, estás en la/el {ruta_data_origen["title"].iloc[0]} ({ruta_data_origen["street-address"].iloc[0]}). '
        mensaje += f'La estación de Bicimad más cercana es {ruta_data_origen["name"].iloc[0]}({ruta_data_origen["address"].iloc[0].split(" ,")[0]}) '
        mensaje += f'a {round(ruta_data_origen["distance"].iloc[0])} metros de distancia y con {ruta_data_origen["dock_bikes"].iloc[0]} bicis libres.'
        return mensaje
    
    elif type_of_place_origen.lower() == 'estacion':
        posibles_coincidencias = process.extract(origen, estaciones_api['name'], scorer=fuzz.WRatio, limit=1)

        ruta_data_origen = estaciones_api[estaciones_api['name'].isin([x[0] for x in posibles_coincidencias])]

        if len(ruta_data_origen) == 0:
            print(f"No se encontraron datos para el origen '{origen}' que cumplan con las condiciones")
            
        mensaje = f'HOLA, estás en la estación de Bicimad {ruta_data_origen["name"].iloc[0]} ({ruta_data_origen["address"].iloc[0].split(",")[0]}), con {ruta_data_origen["dock_bikes"].iloc[0]} bicis libres.'
        return mensaje
    

def buscar_destino(type_of_place_destino, destino):
    if type_of_place_destino.lower() == 'embajada' or type_of_place_destino.lower() == 'consulado':
        if type_of_place_destino.lower() == 'embajada':
            filtered_results = result[result['type_of_place'] == 'embajada']
        elif type_of_place_destino.lower() == 'consulado':
            filtered_results = result[result['type_of_place'] == 'consulado']
       
        posibles_coincidencias = process.extract(destino, filtered_results['title'], scorer=fuzz.WRatio, limit=3)
    
        ruta_data_destino = filtered_results[filtered_results['title'].isin([x[0] for x in posibles_coincidencias])]
        ruta_data_destino = ruta_data_destino[(ruta_data_destino['no_available'] == 0) & (ruta_data_destino['free_bases'] > 0)]

        if len(ruta_data_destino) == 0:
            print(f"No se encontraron datos para el destino '{destino}' que cumplan con las condiciones")
            
        mensaje = f'Tu destino es la/el {ruta_data_destino["title"].iloc[0]} ({ruta_data_destino["street-address"].iloc[0]}). '
        mensaje += f'Con la estación de Bicimad más cercana es {ruta_data_destino["name"].iloc[0]}({ruta_data_destino["address"].iloc[0].split(" ,")[0]}) '
        mensaje += f'a {round(ruta_data_destino["distance"].iloc[0])} metros de distancia y con {ruta_data_destino["free_bases"].iloc[0]} aparcamientos libres.'
        return mensaje
    
    elif type_of_place_destino.lower() == 'estacion':
        posibles_coincidencias = process.extract(destino, estaciones_api['name'], scorer=fuzz.WRatio, limit=1)

        ruta_data_destino = estaciones_api[estaciones_api['name'].isin([x[0] for x in posibles_coincidencias])]

        if len(ruta_data_destino) == 0:
            print(f"No se encontraron datos para el destino '{destino}' que cumplan con las condiciones")
            
        mensaje = f'Tu destino es la estación de Bicimad {ruta_data_destino["name"].iloc[0]} ({ruta_data_destino["address"].iloc[0].split(",")[0]}), con {ruta_data_destino["free_bases"].iloc[0]} aparcamientos libres.'
        return mensaje
    
    
def to_mercator(lat, long):
    # transform latitude/longitude data in degrees to pseudo-mercator coordinates in metres
    c = gpd.GeoSeries([Point(lat, long)], crs=4326)
    c = c.to_crs(3857)
    return c

def distance_meters(lat_start, long_start, lat_finish, long_finish):
    # return the distance in metres between to latitude/longitude pair points in degrees 
    # (e.g.: Start Point -> 40.4400607 / -3.6425358 End Point -> 40.4234825 / -3.6292625)
    start = to_mercator(lat_start, long_start)
    finish = to_mercator(lat_finish, long_finish)
    return start.distance(finish)


coordenadas=[]
def distancia(type_of_place_origen, origen, type_of_place_destino, destino):
    
    lat_start, long_start, lat_finish, long_finish = 0, 0, 0, 0
    
    if type_of_place_origen.lower() == 'embajada' or type_of_place_origen.lower() == 'consulado':
        
        if type_of_place_origen.lower() == 'embajada':
            filtered_results = result[result['type_of_place'] == 'embajada']
        elif type_of_place_origen.lower() == 'consulado':
            filtered_results = result[result['type_of_place'] == 'consulado']
        
        posibles_coincidencias = process.extract(origen, filtered_results['title'], scorer=fuzz.WRatio, limit=3)
    
        ruta_data_origen = filtered_results[filtered_results['title'].isin([x[0] for x in posibles_coincidencias])]
        ruta_data_origen = ruta_data_origen[(ruta_data_origen['no_available'] == 0) & (ruta_data_origen['dock_bikes'] > 0)]
        lat_start = ruta_data_origen['latitude_y'].iloc[0]
        long_start = ruta_data_origen['longitude_y'].iloc[0]
        
    elif type_of_place_origen.lower() == 'estacion':
        posibles_coincidencias = process.extract(origen, estaciones_api['name'], scorer=fuzz.WRatio, limit=1)

        ruta_data_origen = estaciones_api[estaciones_api['name'].isin([x[0] for x in posibles_coincidencias])]
        ruta_data_origen = ruta_data_origen[(ruta_data_origen['no_available'] == 0) & (ruta_data_origen['dock_bikes'] > 0)]

        lat_start = ruta_data_origen['latitude'].iloc[0]
        long_start = ruta_data_origen['longitude'].iloc[0]
        
    if type_of_place_destino.lower() == 'embajada' or type_of_place_destino.lower() == 'consulado':
            
        if type_of_place_destino.lower() == 'embajada':
            filtered_results = result[result['type_of_place'] == 'embajada']
        elif type_of_place_destino.lower() == 'consulado':
            filtered_results = result[result['type_of_place'] == 'consulado']
        
        posibles_coincidencias = process.extract(destino, filtered_results['title'], scorer=fuzz.WRatio, limit=3)
    
        ruta_data_destino = filtered_results[filtered_results['title'].isin([x[0] for x in posibles_coincidencias])]
        ruta_data_destino = ruta_data_destino[(ruta_data_destino['no_available'] == 0) & (ruta_data_destino['free_bases'] > 0)]
        
        lat_finish = ruta_data_destino['latitude_y'].iloc[0]
        long_finish = ruta_data_destino['longitude_y'].iloc[0]
        
        
    elif type_of_place_destino.lower() == 'estacion':
        posibles_coincidencias = process.extract(destino, estaciones_api['name'], scorer=fuzz.WRatio, limit=1)

        ruta_data_destino = estaciones_api[estaciones_api['name'].isin([x[0] for x in posibles_coincidencias])]
        ruta_data_destino = ruta_data_destino[(ruta_data_destino['no_available'] == 0) & (ruta_data_destino['free_bases'] > 0)]

        lat_finish = ruta_data_destino['latitude'].iloc[0]
        long_finish = ruta_data_destino['longitude'].iloc[0]
        
    coordenadas.append((lat_start, long_start, lat_finish, long_finish))
    return f'La distancia total en bici serán {round(distance_meters(lat_start, long_start, lat_finish, long_finish)[0])} metros.'
  
    
print ( )
print(buscar_origen(type_of_place_origen, origen))
print ( )
print(buscar_destino(type_of_place_destino, destino))
print ( )
print(distancia(type_of_place_origen, origen, type_of_place_destino, destino))

lat_center = (coordenadas[0][0] + coordenadas[0][2]) / 2
long_center = (coordenadas[0][1] + coordenadas[0][3]) / 2

start=(coordenadas[0][0], coordenadas[0][1])
finish=(coordenadas[0][2],coordenadas[0][3])

# Crear el mapa centrado en el punto medio de las coordenadas
mapa = folium.Map(location=[lat_center, long_center], zoom_start=14)

# Añadir la línea que conecta los puntos
folium.PolyLine(locations=[start, finish], color='blue').add_to(mapa)

# Mostrar el mapa
mapa

mapa.save("map.html")
webbrowser.open("map.html")
