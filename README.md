# Extracción de links en sitios web

Ejercicio de prueba. Dado una URL, extrae todos los links contenidos en ese sitio. Accesible tanto como endpoint de API (/scraping/) o como comando ejecutado en el container Docker.

### Development

#### Build and run
Ejecutar el siguiente comando desde la raíz del proyecto para hacer el build del Docker y poner a correr los containers.
```
docker-compose up -d --build
```
 
#### Test
Correr tests
```
docker-compose exec web pytest .
```

#### Inspecccionar base de datos
Para acceder a inspeccionar la base de desarrollo:
```
docker-compose exec db psql --username=sraping_websites --dbname=sraping_websites_dev 
```

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
```
docker-compose exec web python get_links.py "https://google.com
```
Ejecutar para obtener ademas un pequeño análisis respecto a scrapings pasados
```
docker-compose exec web python get_links.py -V "https://google.com
```
Comando de ayuda para la aplicacion de consola
```
docker-compose exec web python get_links.py -h
```

## Cómo desplegar en AWS
Para el despliegue de esta aplicación desplegaría el contenedor Docker en Amazon Elastic Container Service (Amazon ECS). Esta aplicación administraría los dos servicios que se crean para esta aplicación: "web" que contiene la lógica de la aplicación, incluyendo la API y el archivo para ejecutar el comando por consola y "db" que contiene la base PostgreSQL para almacenar los logs de los scrapings. ECS administra estos dos servicios de manera transparente y no requiere en principio cambios en la configuración del docker-compose. Este sistema de gestión permitiría administrar el contenedor de manera sencilla y escalar la aplicación de ser necesario.

### Porqué el uso de ASYNC
Debido a que el web scraping es una tarea que lleva tiempo ya que involucra conectarse a la red y parsear un sitio web completo, utilizar un servicio de api asíncrona permite a la aplicación tomar mas pedidos y ejecutarlos de manera rápida pudiendo utilizar el tiempo de espera que se genera al conectarse a un sitio web para atender y procesar otros pedidos. Dependiendo de la demanda que tenga la aplicación, esto podría mejorar la performance en general.


### Warning
El modulo de testing vacia la base y la vuelve a crear para mantener consistencia con los resultados.
En un desarrollo hecho para producción esto debería resolverse con una base aparte para realizar los tests, de manera
que nunca se toque la base que efectivamente se utiliza. Para el proposito de este ejercicio alcanza este warning, pero 
de ninguna manera deberia utilizarse asi en produccion.
