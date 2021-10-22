# Extracción de links en sitios web

Ejercicio de prueba. Dado una URL, extrae todos los links contenidos en ese sitio. Accesible tanto como endpoint de API (/scraping/) o como comando ejecutado en el container Docker.

### Development

#### Build and run
Ejecutar el siguiente comando desde la raíz del proyecto para hacer el build del Docker y poner a correr los containers.
```docker-compose up -d --build```
 
#### Test
Correr tests
```docker-compose exec web pytest .```

#### Inspecccionar base de datos
Para acceder a inspeccionar la base de desarrollo:
```docker-compose exec db psql --username=sraping_websites --dbname=sraping_websites_dev ```

### Uso

#### FastAPI entrypoint
Se puede ejecutar el comando POST directamente
```
curl -X 'POST' \
  'http://localhost:8002/scraping/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "https://google.com"
}'
```
o probarlo de forma manual desde [http://localhost:8002/docs](http://localhost:8002/docs) una vez 

#### Comando para el container Docker
Ejecutar para extraer lista de links (se puede concatenar con un '> links.csv' para guardar en archivp)
```docker-compose exec web python get_links.py "https://google.com```
Ejecutar para obtener ademas un pequeño análisis respecto a scrapings pasados
```docker-compose exec web python get_links.py -V "https://google.com```
Comando de ayuda para la aplicacion de consola
```docker-compose exec web python get_links.py -h```

### Warning
El modulo de testing vacia la base y la vuelve a crear para mantener consistencia con los resultados.
En un desarrollo hecho para producción esto debería resolverse con una base aparte para realizar los tests, de manera
que nunca se toque la base que efectivamente se utiliza. Para el proposito de este ejercicio alcanza este warning, pero 
de ninguna manera deberia utilizarse asi en produccion.