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

#python main_script.py -o italia -d IFEMA -to embajada -td estacion
#python main_script.py -o italia -d zurbano -to embajada -td estacion
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
with open('contraseñas.txt', 'r') as file:
    # Leer la contraseña
    contraseña = file.read().strip().split('\n')


url = 'https://openapi.emtmadrid.es/v1/mobilitylabs/user/login/'

headers = {
    'email': contraseña[0],
    'password': contraseña[1]
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

embajadas = pd.read_csv('data/processed/embajadas.csv')
result = pd.merge(embajadas, estaciones_api, on='number', how='left')

estaciones_csv = pd.read_csv('data/processed/estaciones.csv')
estaciones = pd.merge(estaciones_csv,estaciones_api, on='number', how='left')



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

#functions to find the source and destination in the table they are in and return the data you want
coordenadas=[]
def buscar_origen(type_of_place_origen, origen):
    lat_start, long_start= 0, 0
    
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

        if len(ruta_data_origen) == 0:
            print(f"No se encontraron datos para el origen '{origen}' que cumplan con las condiciones")
        
        coordenadas.append((lat_start, long_start)) 
        mensaje = f'HOLA, estás en la/el {ruta_data_origen["title"].iloc[0].upper()} ({ruta_data_origen["street-address"].iloc[0].title()}). '
        mensaje += f' La estación de Bicimad más cercana es {ruta_data_origen["name"].iloc[0].upper()}({ruta_data_origen["address"].iloc[0].split(" ,")[0]}) '
        mensaje += f'a {round(ruta_data_origen["distance"].iloc[0])} metros de distancia y con {ruta_data_origen["dock_bikes"].iloc[0]} bicis libres.'
        return mensaje
    
    elif type_of_place_origen.lower() == 'estacion':
        posibles_coincidencias = process.extract(origen, estaciones['name_x'], scorer=fuzz.WRatio, limit=1)

        ruta_data_origen = estaciones[estaciones['name_x'].isin([x[0] for x in posibles_coincidencias])]
        ruta_data_origen = ruta_data_origen[(ruta_data_origen['no_available_y'] == 0) & (ruta_data_origen['dock_bikes_y'] > 0)]

        if len(ruta_data_origen) == 0:
            print(f"No se encontraron datos para el origen '{origen}' que cumplan con las condiciones")
        else:
            lat_start = ruta_data_origen['latitude_y'].iloc[0]
            long_start = ruta_data_origen['longitude_y'].iloc[0]
            
            coordenadas.append((lat_start, long_start))
            
            numeros_origen = ruta_data_origen['number'].tolist()
            cercanas = result[result['number'].isin(numeros_origen)]
            
            if not cercanas.empty:
                embajadas_cercanas = cercanas[['title', 'distance']].values.tolist()
                mensaje_cercanas = "Embajadas/Consulados cercanos:\n"
                for i, (embajada, distancia) in enumerate(embajadas_cercanas, 1):
                    mensaje_cercanas += f"{i}. {embajada} - {round(distancia)} metros\n"
            else:
                pass
           
            
    mensaje = f'HOLA, estás en la estación de Bicimad {ruta_data_origen["name_x"].iloc[0].upper()} ({ruta_data_origen["address_x"].iloc[0].split(" ,")[0].title()}), con {ruta_data_origen["dock_bikes_y"].iloc[0]} bicis libres.'   
    print (mensaje)
    
    return (mensaje_cercanas)

def buscar_destino(type_of_place_destino, destino):
    lat_finish, long_finish = 0, 0
    mensaje_cercanas = ""
    
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
        else:
            lat_finish = ruta_data_destino['latitude_y'].iloc[0]
            long_finish = ruta_data_destino['longitude_y'].iloc[0]
            
            coordenadas.append((lat_finish, long_finish))
            
        mensaje = f'Tu destino es la/el {ruta_data_destino["title"].iloc[0].upper()} ({ruta_data_destino["street-address"].iloc[0].title()}). '
        mensaje += f' La estación de Bicimad más cercana es {ruta_data_destino["name"].iloc[0].upper()}({ruta_data_destino["address"].iloc[0].split(" ,")[0]}) '
        mensaje += f'a {round(ruta_data_destino["distance"].iloc[0])} metros de distancia y con {ruta_data_destino["free_bases"].iloc[0]} aparcamientos libres.'
        return (mensaje)    
    
    elif type_of_place_destino.lower() == 'estacion':
        posibles_coincidencias = process.extract(destino, estaciones['name_x'], scorer=fuzz.WRatio, limit=1)

        ruta_data_destino = estaciones[estaciones['name_x'].isin([x[0] for x in posibles_coincidencias])]
        ruta_data_destino = ruta_data_destino[(ruta_data_destino['no_available_y'] == 0) & (ruta_data_destino['free_bases_y'] > 0)]
        
        if len(ruta_data_destino) == 0:
            print(f"No se encontraron datos para el destino '{destino}' que cumplan con las condiciones")
        else:
            lat_finish = ruta_data_destino['latitude_y'].iloc[0]
            long_finish = ruta_data_destino['longitude_y'].iloc[0]
            
            coordenadas.append((lat_finish, long_finish))
            
            numeros_destino = ruta_data_destino['number'].tolist()
            cercanas = result[result['number'].isin(numeros_destino)]
            
            if not cercanas.empty:
                embajadas_cercanas = cercanas[['title', 'distance']].values.tolist()
                mensaje_cercanas = "Embajadas/Consulados cercanos:\n"
                for i, (embajada, distancia) in enumerate(embajadas_cercanas, 1):
                    mensaje_cercanas += f"{i}. {embajada} - {round(distancia)} metros\n"
            else:
                pass
        
    mensaje = f'Tu destino es la estación de Bicimad {ruta_data_destino["name_x"].iloc[0].upper()} ({ruta_data_destino["address_x"].iloc[0].split(" ,")[0].title()}), con {ruta_data_destino["free_bases_y"].iloc[0]} aparcamientos libres.'
    print (mensaje)
    return (mensaje_cercanas)
  
print ( )    
print(buscar_origen(type_of_place_origen, origen))
print ( )
print(buscar_destino(type_of_place_destino, destino))
print ( )
print(f'La distancia total en bici serán {round(distance_meters(coordenadas[0][0],coordenadas[0][1],coordenadas[1][0],coordenadas[1][1])[0])} metros.')
print ( )


def abrir_ruta_bicicleta(origen_lat, origen_long, destino_lat, destino_long):
 
    url = f"https://www.google.com/maps/dir/{origen_lat},{origen_long}/{destino_lat},{destino_long}/data=!4m2!4m1!3e1"
     
    webbrowser.open(url)

origen_lat, origen_long = coordenadas[0][0], coordenadas[0][1]  
destino_lat, destino_long = coordenadas[1][0], coordenadas[1][1] 

abrir_ruta_bicicleta(origen_lat, origen_long, destino_lat, destino_long)
