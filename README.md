# Coral Orange — Interactive Ocean Science Simulator

> **Coral Orange** es un proyecto personal creado a partir de un reto temático sobre un objeto o espacio y un color.

Una serie de minijuegos de simulación interactiva desarrollada en **Python + Pygame** enfocada en la conservación marina, la química del océano y el modelado ecológico de los arrecifes de coral.

El proyecto combina mecánicas de simulación en tiempo real, dinámica de sistemas biológicos y visualización de datos oceanográficos para educar y experimentar con los efectos del cambio climático en los ecosistemas marinos.

Además, se utilizó para explicar conceptos durante la clase "Escuelita Verde: Integración de programación a conceptos ambientales marinos".


## Módulos de Simulación

El simulador se compone de 4 módulos interactivos independientes integrados en un lanzador central:

| Módulo | Nombre | Descripción & Conceptos Clave |
| :---: | :--- | :--- |
| **01** | **Bleaching Alert** | Simula el estrés térmico en corales durante olas de calor marinas, la expulsión de *Zooxanthellae* y el fenómeno de blanqueamiento. |
| **02** | **Clown Symbiosis** | Modelado de mutualismo entre *Amphiprioninae* (pez payaso) y anémonas. Control de protección de hábitat y flujo de nutrientes. |
| **03** | **Trophic Balance** | Dinámica de poblaciones y redes tróficas marinas. Gestión de Áreas Marinas Protegidas (AMP) para prevenir cascadas tróficas. |
| **04** | **Acidification Lab** | Química del carbono en el agua de mar. Monitoreo de pH, amortiguadores de alcalinidad ($HCO_3^- / CO_3^{2-}$) y estados de saturación de aragonita ($\Omega$) para la calcificación. |


## Estructura del Proyecto

```text
coral-orange/
├── main.py                   # Lanzador principal y menú de selección de módulos
├── requirements.txt          # Dependencias del proyecto
├── README.md                 # Documentación principal
├── core/                     # Clases base y utilidades
│   ├── hydro_log.py          # Registro de parámetros hídricos
│   └── reef_organism.py      # Modelo común de organismos del arrecife
├── modules/                  # Módulos del simulador
    ├── bleaching_alert.py    # Módulo 1: Olas de calor y blanqueamiento
    ├── clown_symbiosis.py   # Módulo 2: Simbiosis y mutualismo
    ├── trophic_balance.py    # Módulo 3: Cadena trófica y AMPs
    └── acidification_lab.py  # Módulo 4: Química marina y pH
└── tests/                    # Pruebas automatizadas
```


## Requisitos e instalación

Python 3.9 o superior.
Se recomienda usar un entorno virtual.

### Pasos de Instalación
Desde la carpeta del proyecto, crea y activa un entorno virtual:
```bash
# En Linux/macOS
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

Instala las dependencias:
```bash
pip install -r requirements.txt
```

Inicia el lanzador:
```bash
python main.py
```

### Vista en navegador

En un Codespace sin escritorio gráfico, instala PyGBag y genera la build:

```bash
python -m pip install pygbag
python -m pygbag --build --width 900 --height 600 --ume_block 0 main.py
python serve_game.py --bind 0.0.0.0 --port 8000
```

Abre el puerto **8000** en la pestaña **Ports** de VS Code para jugar desde el navegador. `serve_game.py` proxifica el runtime oficial bajo el mismo origen para que el aislamiento de WebAssembly no bloquee sus descargas.

### Ejecución Independiente de Módulos
Cada módulo dentro de `modules/` incluye un bucle de prueba autónomo. Puedes ejecutar cualquiera directamente:

```bash
python modules/bleaching_alert.py
python modules/clown_symbiosis.py
python modules/trophic_balance.py
python modules/acidification_lab.py
```

### Controles Generales
* Flechas ARRIBA / ABAJO o W / S: Navegar por el menú principal.

* ENTER: Seleccionar el módulo activo desde el menú.

* ENTER o ESPACIO: Comenzar después de leer el objetivo y los controles del módulo.

* ESPACIO: Acción principal de cada módulo (en Clown Symbiosis, usa las flechas o WASD para mover el pez).

* R: Reiniciar la simulación actual tras un estado de fin de juego (Game Over o Victoria).

* ESC: Volver al menú principal desde cualquier módulo / Salir del juego.


### Fundamentos Científicos
* Relación de pH y $CO_2$: El laboratorio usa una aproximación logarítmica simplificada de la relación entre CO2 disuelto y pH.

* Saturación de aragonita ($\Omega$): Define la viabilidad metabólica de la calcificación biogénica en invertebrados marinos ($\Omega > 3.0$ estado óptimo; $\Omega < 1.0$ disolución activa de estructuras calcáreas).

* Telemetría HydroLog: Registro periódico de temperatura, pH y estado ambiental durante cada simulación.

Los modelos son educativos y cualitativos; no sustituyen cálculos oceanográficos ni predicciones científicas cuantitativas.

### Pruebas automáticas

```bash
python -m unittest discover -s tests
```
