# Project Bicimad README file


### :raising_hand: **Bicimad By Embajadas&Consulados** 

Este proyecto consiste en la elaboración de una APP que una Consulados & Embajadas con estaciones de Bicimad.


### :baby: **Status**
1.1, Ironhack Data Analytic:first project

### :running:**Fuentes de información**

Dos fuentes principales de información: 

API Consulados & Embajadas: 
endpoint: https://datos.madrid.es/egob
embajadas&consulados: /catalogo/201000-0-embajadas-consulados.json

API Bicimad: 
url = 'https://openapi.emtmadrid.es/v1/mobilitylabs/user/login/'

headers = {
    'email': 'your email,
    'password': 'your password'
    }

url='https://openapi.emtmadrid.es/v1/transport/bicimad/stations/'

headers = {
    'accessToken': accessToken,
    }

response = req.request("GET", url, headers=headers)
estaciones=response.json()



### :computer: **Imports**

Para este proyecto hemos importado lo siguiente: 
`import pandas as pd`
`import  requests as req`
`import  json`
`from shapely.geometry import Point`
`import  geopandas as gpd`
`import  fuzzywuzzy import fuzz`
`import  fuzzywuzzy import process`
`import  folium`
`import  polyline`
`import  webbrowser`


Your readers will most likely view your README in a browser so please keep that in mind when formatting its content: 
- Use proper format when necesary (e.g.: `import pandas as pd`). 
- Categorize content using two or three levels of header beneath. 
- Make use of **emphasis** to call out important words. 
- Link to project pages for related libraries you mention. Link to Wikipedia, Wiktionary, even Urban Dictionary definitions for words of which a reader may not be familiar. Make amusing cultural references. 
- Add links to related projects or services. 

> Here you have a markdown cheatsheet [Link](https://commonmark.org/help/) and tutorial [Link](https://commonmark.org/help/tutorial/).


### :boom: **Elaborar CSVs:**
-Desde las fuentes de información, se han creado DataFrames y se han limpiado y ordenado. 
-Con la información de esas tablas hemos creado 2 CSVs:
   **Embajadas**: con la información relevante de cada embajada/consulado y con las 3 estaciones más cercanas a cada una de ellas. 
   **Estaciones**: con la información relevante de casa una de las estaciones y con la más cercana a cada una de ellas. 



### :wrench: **Merge tablas:**

-Cada uno de los CSVs se actualizan con la información actualizada de cada estación desde la API de Bicimad. 


### :see_no_evil: **Funciones de lamada**
-Función de  origen: 
      1.Condición: bicis disponibles. 
Dependiendo de si es consulado, embajada o estación va a buscar en una tabla distinta filtrada. Esto ayudará al **FuzzyWuzzy** a encontrar mejor el input.
 
     2. Condición: bicis disponibles.
En el caso de embajadas/consulados tiene 3 opciones para encontrar estaciones con bicis disponibles cercanas. En el caso de estación solo una alternativa.

Print mensaje deseado

-Función de destino:
   1.Condición: tipo de destino. 
Dependiendo de si es consulado, embajada o estación va a buscar en una tabla distinta filtrada. Esto ayudará al **FuzzyWuzzy** a encontrar mejor el input.

   2.Condición: bicis disponibles.
En el caso de embajadas/consulados      tiene 3 opciones para encontrar estaciones con aparcamientos disponibles cercanos. En el caso de estación solo una alternativa.

Print mensaje deseado

### :shit: **Map**
Con las coordenadasde origen y destino, crea una url de maps con la ruta en bici en google maps y lo abre en el navegador. 


### :file_folder: **Folder structure**
```
└── project
    ├── .gitignore
    ├── README.md
    ├── main_script.py
    ├── notebooks
    │   ├── dev_notebook_.ipynb
    │   ├── filter.ipynb
    │   ├── bicimad_csv.ipynb
    │   └── Trash.ipynb
    │   
    └── data
        ├── raw
        ├── processed
        
```




