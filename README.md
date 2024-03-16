# Project Bicimad README file


### :raising_hand: **Bicimad By Embajadas&Consulados** 

This project consists of the development of an APP that links Consulates & Embassies with Bicimad stations.

The inputs will be origin and destination. Both origin and destination can be embassies, consulates or stations.  In the case of embassy or destination, the output is the nearest bicimad station with bikes or free parking. And in the case of station it tells you how many bikes or free parking has, in the case of not having, it looks for the nearest one.

Finally it tells you how many meters is the route in bice from station to station, and returns the map with the route.  

![Image](https://www.bicimad.com/sites/default/files/styles/news_full/public/2023-03/243A0004.jpg.webp?itok=AqUARnFb)


###  **Status**
1.1, Ironhack Data Analytic:first project

### **Sources of information**

Two main sources of information: 


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



### :computer: **Used libraries**

For this project we have imported the following:
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
`import  argparse`



###  **Create CSVs:**
-From the information sources, DataFrames have been created, cleaned and sorted. 
-With the information from these tables we have created 2 CSVs:
  - **Embassies**: with the relevant information of each embassy/consulate and with the 3 nearest stations to each of them. 
  - **Stations**: with the relevant information of each of the stations and with the closest station to each of them. 



###  **Merge DataFrames:**

-Each of the CSVs are updated with the updated information of each station from the Bicimad API. 


###  **Lick functions**
-**Function of origin**: 

-Condition: available bikes. 
Depending on whether it is consulate, embassy or station it will search in a different filtered table. This will help the **FuzzyWuzzy** to find the input better.
 
-Condition: bikes available.
In the case of embassy/consulate you have 3 options to find stations with available bikes nearby. In case of station only one alternative.

Print desired message

-**Destination function**:

-Condition: destination type. 
Depending on whether it is consulate, embassy or station it will search in a different filtered table. This will help the **FuzzyWuzzy** to find the input better.

-Condition: bikes available.
In the case of embassies/consulates you have 3 options to find stations with available parking nearby. In case of station only one alternative.

Print desired message


###  **argparse**
We use argarse in .py to give the inputs to our functions and get our output back in the terminal.

### **Map**
With the coordinates of origin and destination, create a maps url with the bike route in google maps and open it in the browser.


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




