import pygame
import random
import math
import sys

# Si se ejecuta de forma independiente, ajustamos el path para importar desde core
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reef_organism import ReefOrganism
from core.hydro_log import HydroLog


class BleachingAlertModule:
    """
    Módulo 1: Bleaching Alert
    Simula la respuesta térmica de una colonia de corales ante olas de calor marinas.
    El jugador debe aplicar pulsos de enfriamiento ambiental para reducir la
    temperatura del agua antes de que los corales pierdan sus zooxantelas.
    """

    def __init__(self, screen_width=900, screen_height=600):
        self.width = screen_width
        self.height = screen_height
        
        # Parámetros Ambientales Base
        self.base_temp = 26.5        # Temperatura normal del agua (°C)
        self.current_temp = 26.5     # Temperatura actual con fluctuaciones
        self.ocean_ph = 8.1          # pH constante para este nivel
        
        # Mecánica de Olas de Calor
        self.heat_wave_timer = 0
        self.heat_wave_active = False
        self.heat_intensity = 0.0    # Incremento adicional de temperatura por ola de calor
        
        # Habilidades del Jugador
        self.cooling_charges = 3     # Pulsos de enfriamiento disponibles
        self.cooling_cooldown = 0    # Enfriamiento de la habilidad (frames)
        self.cooling_active_timer = 0
        
        # Sistema de Puntuación y Tiempo
        self.survival_time = 0.0     # Segundos sobrevivientes
        self.game_over = False
        self.win_condition = False
        self.target_time = 60.0      # Sobrevivir 60 segundos
        
        # Componentes del Motor
        self.hydro_log = HydroLog(x=20, y=20, width=280, height=140)
        self.corals = []
        self._init_reef()

    def _init_reef(self):
        """Genera una colonia de corales con variaciones de resistencia térmica."""
        colors = [
            (255, 127, 80),   # Coral Orange
            (255, 99, 71),    # Coral Red
            (233, 150, 122),  # Dark Salmon
            (255, 160, 122)   # Light Salmon
        ]
        
        id_counter = 1
        # Crear cuadrícula/organización orgánica de corales en el centro del arrecife -> La cuadrill debe ser lo suf para no chocar con los bordes 
        for i in range(5):
            for j in range(4):
                offset_x = random.randint(-15, 15)
                offset_y = random.randint(-15, 15)
                x = 380 + (i * 90) + offset_x
                y = 220 + (j * 80) + offset_y
                
                coral = ReefOrganism(
                    organism_id=f"CORAL-{id_counter:02d}",
                    name=f"Acropora #{id_counter}",
                    x=x,
                    y=y,
                    species_type="CORAL",
                    color=random.choice(colors)
                )
                self.corals.append(coral)
                id_counter += 1

    def handle_event(self, event):
        """Manejo de entradas de teclado y mouse."""
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__(self.width, self.height)  # Reiniciar módulo
            return

        # Tecla ESPACIO para desplegar ola de enfriamiento
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._trigger_cooling_pulse()

    def _trigger_cooling_pulse(self):
        """Activa una corriente fría de emergencia si hay cargas disponibles."""
        if self.cooling_charges > 0 and self.cooling_cooldown <= 0:
            self.cooling_charges -= 1
            self.cooling_active_timer = 120  # La corriente dura 2 segundos (~120 FPS)
            self.cooling_cooldown = 180      # Reutilización en 3 segundos

    def update(self, delta_time):
        """Lógica principal de simulación física y biológica."""
        if self.game_over:
            return

        self.survival_time += delta_time
        if self.survival_time >= self.target_time:
            self.win_condition = True
            self.game_over = True

        # 1. Gestión de Cooldowns y Habilidades
        if self.cooling_cooldown > 0:
            self.cooling_cooldown -= 1
            
        cooling_effect = 0.0
        if self.cooling_active_timer > 0:
            self.cooling_active_timer -= 1
            cooling_effect = -2.5  # Enfría 2.5 °C drásticamente

        # 2. Dinámica de Olas de Calor (Ciclos Térmicos)
        self.heat_wave_timer += delta_time
        if self.heat_wave_timer > 8.0:  # Cada 8 segundos varía el clima
            self.heat_wave_active = random.random() > 0.35
            self.heat_wave_timer = 0
            
        if self.heat_wave_active:
            # Incremento progresivo de temperatura de hasta +4.0 °C
            self.heat_intensity = min(4.0, self.heat_intensity + 0.01)
        else:
            self.heat_intensity = max(0.0, self.heat_intensity - 0.015)

        # Ruido térmico suave + efecto de ola de calor + efecto de enfriamiento
        thermal_noise = math.sin(pygame.time.get_ticks() * 0.002) * 0.3
        self.current_temp = self.base_temp + self.heat_intensity + thermal_noise + cooling_effect

        # 3. Actualizar estado de salud de la colonia de corales
        bleached_count = 0
        for coral in self.corals:
            coral.update_health(temp_celsius=self.current_temp, ocean_ph=self.ocean_ph)
            if coral.bleached:
                bleached_count += 1

        # Si más del 70% de los corales han muerto/blanqueado -> Game Over
        if bleached_count >= len(self.corals) * 0.7:
            self.game_over = True
            self.win_condition = False

        # 4. Registrar datos hidrológicos
        status_msg = "OLA DE CALOR DETECTADA" if self.heat_wave_active else "SISTEMA TÉRMICO ESTABLE"
        if self.cooling_active_timer > 0:
            status_msg = "INYECCIÓN FRÍA ACTIVA"
            
        self.hydro_log.push_log(self.current_temp, self.ocean_ph, status_msg)

    def draw(self, screen, font_large, font_small):
        """Renderizado completo del canvas."""
        # Color del océano según la temperatura (Azul fresco -> Rojo térmico) -> cambiarlo mas adelante a naranja oscuro
        temp_stress = min(1.0, max(0.0, (self.current_temp - 26.0) / 4.5))
        bg_r = int(10 + (80 * temp_stress))
        bg_g = int(30 - (10 * temp_stress))
        bg_b = int(70 - (40 * temp_stress))
        screen.fill((bg_r, bg_g, bg_b))

        # Efecto visual de Pulso Frío 
        if self.cooling_active_timer > 0:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 180, 255, 35))
            screen.blit(overlay, (0, 0))

        # 1. Renderizar Corales
        for coral in self.corals:
            coral.draw(screen, font_small)

        # 2. Renderizar Consola de Logs Ambientales
        self.hydro_log.draw(screen, font_small)

        # 3. HUD Superior (Tiempo, Controles y Cargas)
        time_text = font_large.render(f"Tiempo: {int(self.survival_time)}s / {int(self.target_time)}s", True, (255, 255, 255))
        screen.blit(time_text, (self.width - time_text.get_width() - 20, 20))

        charges_color = (0, 255, 200) if self.cooling_charges > 0 else (255, 80, 80)
        charges_text = font_small.render(f"Pulsos Fríos (ESPACIO): {self.cooling_charges} disponibles", True, charges_color)
        screen.blit(charges_text, (self.width - charges_text.get_width() - 20, 60))

        # 4. Indicador de Ola de Calor Alerta
        if self.heat_wave_active and not self.game_over:
            alert_text = font_small.render("⚠️ ALERTA: Anomalía Térmica Marina en Proceso", True, (255, 90, 90))
            screen.blit(alert_text, (self.width // 2 - alert_text.get_width() // 2, 20))

        # 5. Pantalla Fin de Juego / Victoria
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            if self.win_condition:
                title = font_large.render("¡ARRECIFE SALVADO!", True, (100, 255, 150))
                sub = font_small.render("Lograste mantener la temperatura estable hasta disipar la ola de calor.", True, (220, 220, 220))
            else:
                title = font_large.render("DESASTRE ECOLÓGICO", True, (255, 80, 80))
                sub = font_small.render("La colonia sufrió un blanqueamiento masivo por estrés térmico.", True, (220, 220, 220))

            restart = font_small.render("Presiona 'R' para reiniciar la simulación o 'ESC' para volver", True, (180, 180, 180))
            
            screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 60))
            screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.height // 2))
            screen.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 50))


# --- BUCLE DE PRUEBA INDEPENDIENTE ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Coral Orange - Bleaching Alert Simulation")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("monospace", 24, bold=True)
    font_small = pygame.font.SysFont("monospace", 14)

    module = BleachingAlertModule(900, 600)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0  # Delta time en segundos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            
            module.handle_event(event)

        module.update(dt)
        module.draw(screen, font_large, font_small)
        pygame.display.flip()

    pygame.quit()