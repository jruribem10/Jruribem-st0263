# Proyecto 1: Tópicos de Telemática ST0263

## Estudiantes
- **Jaime Uribe**: jruribem@eafit.edu.com
- **Juan Pablo Duque**: jpduquep@eafit.edu.co
- **Samuel Rendon**: jpduquep@eafit.edu.co

## Profesor
- **Alvaro Enrique Ospina Sanjuan**: aeospinas@eafit.edu.co

## Descripción
El proyecto implementa un sistema de archivos distribuidos basado en bloques. Permite almacenar, replicar y recuperar archivos distribuidos en múltiples nodos que para este caso son DataNodes de forma eficiente, asegurando la disponibilidad de los datos a través de la replicación de bloques en diferentes nodos.
Este sistema está compuesto por un NameNode, que se encarga de gestionar el almacenamiento distribuido y coordinar la replicación, y varios DataNodes, que almacenan físicamente los bloques de datos.
El cliente se comunica con el sistema a través de una interfaz de comandos (CLI) que ofrece funcionalidades como cargar, descargar, listar archivos, crear y eliminar directorios, y otras operaciones comunes de manejo de archivos.




## Información General

### Arquitectura
Este proyecto está diseñado para ser utilizado en sistemas distribuidos que requieran almacenamiento confiable, escalable y tolerante a fallos. El DFS sigue una estructura centralizada, donde el NameNode actúa como el coordinador de todas las operaciones, mientras que los DataNodes manejan el almacenamiento de los datos.
El cliente puede interactuar con el sistema utilizando comandos similares a los de un sistema de archivos local, pero con la ventaja de que los archivos están distribuidos en múltiples nodos de forma transparente.
El sistema garantiza la replicación de los bloques de datos en al menos dos nodos para asegurar la tolerancia a fallos. Cada nodo líder es responsable de replicar su bloque en un nodo secundario (Follower). Si un DataNode se desconecta, el sistema intenta redirigir las operaciones hacia los nodos disponibles.

## Características Principales

- **Almacenamiento distribuido** de archivos basado en bloques.
- **Replicación de bloques** para asegurar la tolerancia a fallos.
- **Interfaz de línea de comandos (CLI)** con comandos como `put`, `get`, `ls`, `cd`, `mkdir`, `rm`, `rmdir`.
- **Detección de nodos no disponibles** y redirección automática a réplicas.
- **Gestión de archivos y directorios por usuario**.
- **Comunicación entre procesos** utilizando gRPC.

  ## Funcionamiento del Sistema

El sistema garantiza la replicación de los bloques de datos en al menos dos nodos para asegurar la tolerancia a fallos. Cada nodo líder es responsable de replicar sus bloques en un nodo secundario (Follower). Si un **DataNode** se desconecta, el sistema redirige las operaciones hacia los nodos disponibles.

## Componentes Principales

- **Cliente**: Proporciona la interfaz para interactuar con el DFS.
- **NameNode**: Coordina la asignación de bloques y la replicación entre los DataNodes.
- **DataNodes**: Almacenan los bloques de archivos y son responsables de la replicación.
- **Archivos .proto**: El archivo .proto define las estructuras de datos y los servicios que se comunican entre los componentes del sistema, especialmente entre el NameNode y los DataNodes utilizando gRPC




![image](https://github.com/user-attachments/assets/00553c7f-0750-4452-b419-36f94c8ca46e)


### Patrones

Este proyecto implementa varios patrones de diseño típicos en sistemas distribuidos:

- **Patrón de Coordinación Centralizada**: El **NameNode** actúa como un coordinador central que gestiona las operaciones de almacenamiento, replicación y recuperación de bloques. Aunque el sistema es distribuido, el **NameNode** centraliza la lógica de toma de decisiones.

- **Patrón de Replicación**: Cada bloque de archivo se replica en al menos dos nodos (Líder y Follower). Este patrón asegura que los datos estén disponibles incluso si uno de los nodos falla, proporcionando tolerancia a fallos.

- **Patrón Cliente-Servidor**: La interacción entre el cliente y el DFS sigue el patrón clásico de cliente-servidor, donde el cliente solicita operaciones (como subir/descargar archivos o crear/eliminar directorios) y el **NameNode** las coordina y ejecuta.

- **Patrón RESTful**: El **NameNode** utiliza una API REST para que los **DataNodes** se registren, envíen señales de estado y manejen otras operaciones de control, permitiendo una comunicación flexible y escalable entre los componentes del sistema.




### Prácticas Utilizadas
Este proyecto implementa diversas prácticas de desarrollo que aseguran la robustez, escalabilidad y mantenibilidad del sistema:

- **Tolerancia a fallos**: Cada bloque de archivo se replica en múltiples nodos, lo que asegura que la pérdida de un nodo no resulte en la pérdida de datos.

- **Transparencia de replicación**: Los usuarios del sistema no necesitan preocuparse por la replicación, ya que es gestionada automáticamente por el **NameNode** y los **DataNodes**.

- **Escalabilidad**: El sistema puede crecer fácilmente añadiendo más **DataNodes**. El **NameNode** se encarga de la asignación de bloques a los nuevos nodos de manera automática, lo que permite una expansión sencilla.

- **Interfaz de línea de comandos**: El cliente ofrece una interfaz intuitiva y familiar para interactuar con el DFS, similar a las operaciones de un sistema de archivos tradicional.

- **Comunicación eficiente**: Se utiliza **gRPC** para la comunicación entre nodos, lo que permite una transferencia de datos rápida y eficiente entre los diferentes componentes del sistema.

## Entorno de Desarrollo y Configuraciones

### IDE
- Visual Studio Code

### Lenguaje de Programación
- Python

### Librerías y Paquetes
- Flask
- Requests
- JSON

### Instalación de Librerías
ara ejecutar este proyecto, asegúrate de instalar las siguientes dependencias:

- **gRPC y Protobuf**: Utilizados para la comunicación eficiente entre los nodos del sistema.
  ```bash
  pip install grpcio grpcio-tools
  pip install Flask
  pip install requests




