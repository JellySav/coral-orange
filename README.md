# Coral Orange — Interactive Ocean Science Simulator

> **Coral Orange** es un repostiorio bajo un mini reto personal a traves de la tematica de un objeto/espacio y un color. 

Una serie de minijuegos de simulación interactiva desarrollada en **Python + Pygame** enfocada en la conservación marina, la química del océano y el modelado ecológico de los arrecifes de coral.

El proyecto combina mecánicas de simulación en tiempo real, dinámica de sistemas biológicos y visualización de datos oceanográficos para educar y experimentar con los efectos del cambio climático en los ecosistemas marinos.

Ademas; fue utilizado para explicar conceptos durante la clase "Escuelita Verde: Integracion de programacion a conceptos ambientales marinos".


## Módulos de Simulación

El simulador se compone de 4 módulos interactivos independientes integrados en un lanzador central:

| Módulo | Nombre | Descripción & Conceptos Clave |
| :---: | :--- | :--- |
| **01** | **Bleaching Alert** | Simula el estrés térmico en corales durante olas de calor marinas, la expulsión de *Zooxanthellae* y el fenómeno de blanqueamiento. |
| **02** | **Clown Symbiosis** | Modelado de mutualismo entre *Amphiprioninae* (pez payaso) y anémonas. Control de protección de hábitat y flujo de nutrientes. |
| **03** | **Trophic Balance** | Dinámica de poblaciones y redes tróficas marinas. Gestión de Áreas Marinas Protegidas (AMP) para prevenir cascadas tróficas. |
| **04** | **Acidification Lab** | Química del carbono en el agua de mar. Monitoreo de pH, amortiguadores de alcalinidad ($HCO_3^- / CO_3^{2-}$) y estados de saturación de aragónita ($\Omega$) para la calcificación. |


## Estructura del Proyecto

```text
coral-orange/
├── main.py                   # Lanzador principal y menú de selección de módulos
├── requirements.txt          # Dependencias del proyecto
├── README.md                 # Documentación principal
├── core/                     # Clases base y utilidades
│   ├── hydro_log.py          # Sistema de registro y telemetría de parámetros hídricos
│   └── display_utils.py      # Helpers de renderizado, colores e interfaces
└── modules/                  # Módulos del simulador
    ├── bleaching_alert.py    # Módulo 1: Olas de calor y blanqueamiento
    ├── clown_symbiosis.py   # Módulo 2: Simbiosis y mutualismo
    ├── trophic_balance.py    # Módulo 3: Cadena trófica y AMPs
    └── acidification_lab.py  # Módulo 4: Química marina y pH
```


## Requisitos e InstalaciónPrerrequisitos
Python 3.9 o superior.
Entorno virtual de Python (recomendado).

### Pasos de Instalación
Clona el repositorio:
```Bash
git clone [https://github.com/tu-usuario/coral-orange.git](https://github.com/tu-usuario/coral-orange.git)
cd coral-orange
```

Crea y activa un entorno virtual:
```Bash
# En Linux/macOS
python3 -m venv venv
source venv/bin/activate

# En Windows
python -m venv venv
venv\Scripts\activate
```

Instala las dependencias:
```Bash
pip install -r requirements.txt
```

Ejecuta la suite principal:
```Bash
python main.py
```

### Ejecución Independiente de Módulos
Cada módulo dentro de modules/ incluye su propio bucle de prueba autónomo. Puedes ejecutar cualquier módulo de forma directa sin pasar por el menú principal:

```Bash
# Probar la simulación de química marina y pH
python modules/acidification_lab.py

# Probar la simulación de estrés térmico
python modules/bleaching_alert.py
```

### Controles Generales
* Flechas ARRIBA / ABAJO: Navegar por el menú principal (main.py).

* ENTER: Seleccionar/Iniciar módulo.

* ESPACIO: Acción e interacción principal dentro de cada módulo (ej. inyección de solución amortiguadora en Acidification Lab).

* R: Reiniciar la simulación actual tras un estado de fin de juego (Game Over o Victoria).

* ESC: Volver al menú principal desde cualquier módulo / Salir del juego.


### Fundamentos Científicos
* Relación de pH y $CO_2$: Basada en la escala logarítmica de la concentración de dióxido de carbono disuelto en agua superficial.

* Saturación de Aragónita ($\Omega$): Define la viabilidad metabólica de la calcificación biogénica en invertebrados marinos ($\Omega > 3.0$ estado óptimo; $\Omega < 1.0$ disolución activa de estructuras calcáreas).

* Telemetría HydroLog: Registro dinámico de salinidad, temperatura y pH para monitoreo de condiciones ambientales en tiempo real.
