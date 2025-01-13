# Prueba semana 11 - Jenkins y procesos de CI/CD

Esta prueba tiene como finalidad evaluar las capacidades del desarrollador para automatizar tareas mediante pipelines de Jenkins y comprender los conceptos básicos de procesos de CI/CD.

La prueba consta de 3 partes:
- Desarrollo
- Despliegue
- Automatización de tareas

## Desarrollo

Para esto vamos a crear un el directorio [`services/app`](./services/app) un microservicio de python con Postgres y mongo, ambos creando un CRUD de usuarios y los endpoints de guardado sean /mongo/* para los de mongo y /postgrest/* para los de postgres. Las conexiones deben hacerse por variables de entorno las cuales pueden ser con un archivo que venga de un secreto o un texto literal y se debe usar gunicorn como servidor y tini como proceso principal.

## Despliegue

Para este punto necesitamos desplegar los siguientes servicios:

- Un servicio de mongoDB expuesto en el puerto local 27018 y conectado a una red que le permita comunicarse con las demás bases de datos y el backend, pero no con el proxy.

- Un servicio de Postgres expuesto en el puerto local 25432 y conectado a una red que le permita comunicarse con las demás bases de datos y el backend, pero no con el proxy.

- Un servicio de backend con la imagen del servicio creada (descargada de docker hub) el cual se conecta a los servicios de mongo y postgres sin exponer ningún puerto local, este servicio puede comuncarse con las bases de datos y el ingress.

- Un servicio de nginx el cual haga un proxy reverse al backend y esté expuesto por el puerto 80 y 443 con certificados autofirmados por la empresa gopenux de la ciudad de cúcuta, al ingresar por el puerto 80, este debe redireccionar al puerto 443. En caso de acceder a la ruta /livez debe responder con un 403 desde el nginx.

### Notas:
- Se deben usar secretos para las configuraciones de mongo y postgres, pero en el backend solo se usa secretos para las variables de usuario y contraseña.

- La configuración de nginx debe ir en el directorio [services/images/nginx/vhost](./services/images/nginx/vhost/) y los certificados en [services/images/nginx/ssl](./services/images/nginx/ssl/)

- Los datos de mongo y postgres de seben guardar en los directorios [services/persistent-data/mongodb](./services/persistent-data/mongodb) y [services/persistent-data/postgres](./services/persistent-data/postgres)

- Las bases de datos se deben desplegar en un nodo con la etiqueta "databases" y los demás servicios en el nodo manager

- Todos los servicios deben tener un alias en cada red conectada de la manera: "${nombre_del_servicio}.docker"

- El único servicio accesible en todas sus interfaces de red es el del ingress, los demás solo con la ip 127.0.0.1

Desplegar el stack con el nombre gopenux y verificar el funcionamiento (mediante imagenes)

## Automatización de tareas

Para esto crearemos un [docker-compose](./jenkins/docker-compose.yaml) el cual despliegue un jenkins con el que vamos a trabajar (que permita el uso de docker y autorizado al swarm manager).

Una vez desplegado el servicio, tendremos que cumplir con los siguientes puntos:

- Crear un [Jenkinsfile](./services/app/Jenkinsfile) que se encargue de clonar este repositorio, hacer la construcción de la imagen, subida a docker hub y actualización del servicio de backend con un nuevo tag, este lo vamos a enviar como un parametro de la pipeline.

- Crear una tarea de Jenkins el cual tome el Jenkinsfile del repositorio remoto y lo ejecute (recuerda agregar los parametros del tag)

- Revisar el funcionamiento de la pipeline actualizando el servicio de backend con un nuevo endpoint /healthz que responda con:

```json
{"status": "ok"}
```

- Ejecución de la pipeline con muestras de imagenes de la actualización y el funcionamiento de la Aplicación con su nuevo endpoint (tambien del cambio del tag)

- Agregar el halthcheck de la aplicación de backend con una curl al servicio en la ruta /healthz (esto en el docker stack) con intervalos de 30s

# IMPORTANTE

Queda prohibido el uso de IA sin importar las circunstancias, sin embargo, se puede usar la navegación web para busqueda de información.