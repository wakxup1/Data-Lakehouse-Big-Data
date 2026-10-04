# Guía de Configuración de Apache Spark (PySpark) en Windows

Esta guía detalla los pasos exactos para configurar un entorno local funcional de Big Data utilizando PySpark en Windows, resolviendo los problemas de compatibilidad con Java y los permisos de escritura del sistema de archivos Hadoop.

## 1. Instalación de Java (JDK)
Apache Spark requiere el motor de Java para funcionar. Se recomienda la versión 11 o 17.

1. Abre **PowerShell como Administrador**.
2. Ejecuta el siguiente comando para instalar Java 17:
   `winget install EclipseAdoptium.Temurin.17.JDK`
   *(Si prefieres hacerlo manual, descarga el instalador desde la página oficial de Adoptium Temurin).*

## 2. Descarga de Binarios de Hadoop para Windows
Spark necesita librerías nativas (`winutils.exe` y `hadoop.dll`) para poder escribir particiones de datos en el disco (como archivos Parquet) sin arrojar errores de permisos.

1. Abre **PowerShell como Administrador** (es vital para evitar el error de "Acceso denegado").
2. Crea la carpeta base ejecutando:
   `New-Item -ItemType Directory -Force -Path "C:\hadoop\bin"`
3. Descarga los archivos ejecutando:
   `Invoke-WebRequest -Uri "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.5/bin/winutils.exe" -OutFile "C:\hadoop\bin\winutils.exe"`
   `Invoke-WebRequest -Uri "https://raw.githubusercontent.com/cdarlint/winutils/master/hadoop-3.3.5/bin/hadoop.dll" -OutFile "C:\hadoop\bin\hadoop.dll"`
4. Copia el archivo DLL a la carpeta del sistema para garantizar los permisos de lectura/escritura:
   `Copy-Item -Path "C:\hadoop\bin\hadoop.dll" -Destination "C:\Windows\System32\"`

## 3. Configuración de Variables de Entorno
Windows necesita saber exactamente dónde están instalados Java y Hadoop.

1. Presiona la tecla Windows, escribe **"Editar las variables de entorno del sistema"** y presiona Enter.
2. Haz clic en el botón **"Variables de entorno..."**.
3. En la sección inferior (**Variables del sistema**), haz clic en **"Nueva..."** para crear dos variables:
   * **Nombre:** `JAVA_HOME` | **Valor:** `C:\Program Files\Eclipse Adoptium\jdk-17.0.x.x-hotspot\` *(Verifica tu ruta exacta)*
   * **Nombre:** `HADOOP_HOME` | **Valor:** `C:\hadoop`
4. En la misma lista de variables del sistema, busca la variable llamada **`Path`**, selecciónala y presiona **"Editar..."**.
5. Haz clic en **"Nuevo"** y agrega estas dos líneas (una por una):
   * `%JAVA_HOME%\bin`
   * `%HADOOP_HOME%\bin`
6. Haz clic en **Aceptar** en todas las ventanas.

## 4. Instalación de PySpark
Con la infraestructura base lista, instala la librería en tu entorno de Python.

1. Abre una terminal normal (puede ser en Visual Studio Code).
2. Ejecuta:
   `pip install pyspark`

## 5. Reinicio del Entorno
**Paso crítico:** Para que Visual Studio Code y tu terminal reconozcan las nuevas variables de entorno y el archivo DLL, debes **cerrar por completo el editor** y volver a abrirlo. Si omites este paso, los scripts seguirán arrojando errores de que Java o Hadoop no existen.