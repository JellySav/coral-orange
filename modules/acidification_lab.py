import pygame
import random
import math
import sys
import os

# Ajuste de path para importaciones desde core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hydro_log import HydroLog


class CarbonateMolecule:
    """Representa partículas de Carbonato (CO3 2-) y Bicarbonato (HCO3 -) flotando."""
    def __init__(self, x, y, is_carbonate=True):
        self.x = x
        self.y = y
        self.is_carbonate = is_carbonate  # True = CO3 (útil), False = HCO3 (no usable directo)
        self.radius = 6
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-0.8, 0.8)

    def update(self, bounds_x, bounds_y):
        self.x += self.vx
        self.y += self.vy

        if self.x < bounds_x[0] or self.x > bounds_x[1]:
            self.vx *= -1
        if self.y < bounds_y[0] or self.y > bounds_y[1]:
            self.vy *= -1

    def draw(self, screen):
        # CO3 es Cian/Azul brillante (disponible para calcificación); HCO3 es Gris/Opaco
        color = (0, 220, 255) if self.is_carbonate else (140, 150, 160)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.radius)
        if self.is_carbonate:
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 2)


class AcidificationLabModule:
    """
    Módulo 4: Acidification Lab
    Simula la química del carbono en el océano, el pH y la saturación de aragónita (Ω).
    El jugador debe neutralizar la sobreabundancia de CO2 disuelto mediante la adición de
    solución amortiguadora (Alcalinidad/Bicarbonato) para proteger la calcificación.
    """

    def __init__(self, screen_width=900, screen_height=600):
        self.width = screen_width
        self.height = screen_height

        # Parámetros Químicos
        self.ph = 8.1              # pH estándar del océano
        self.co2_ppm = 415.0       # Concentración de CO2 en ppm
        self.aragonite_sat = 3.8   # Saturación de Aragónita Ω (debe ser > 3.0 para calcificar)
        self.calcification_rate = 100.0  # Porcentaje de integridad estructural de conchas/corales

        # Controles e Inyección
        self.buffer_charges = 4
        self.buffer_cooldown = 0
        self.buffer_effect_timer = 0

        # Simulación de Emisiones Continuas
        self.co2_emission_rate = 0.08

        # Partículas Químicas y Estructura
        self.bounds_x = (320, screen_width - 40)
        self.bounds_y = (180, screen_height - 40)
        self.molecules = []
        self._seed_chemistry()

        # Tiempo y Progreso
        self.survival_time = 0.0
        self.target_time = 60.0
        self.game_over = False
        self.win_condition = False

        self.hydro_log = HydroLog(x=20, y=20, width=280, height=140)

    def _seed_chemistry(self):
        """Inicializa las moléculas de carbonato disponibles en el agua."""
        self.molecules.clear()
        for _ in range(30):
            x = random.randint(self.bounds_x[0], self.bounds_x[1])
            y = random.randint(self.bounds_y[0], self.bounds_y[1])
            self.molecules.append(CarbonateMolecule(x, y, is_carbonate=True))

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__(self.width, self.height)
            return

        # Pulso de Solución Amortiguadora (Buffer de Alcalinidad) con ESPACIO
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self._apply_buffer()

    def _apply_buffer(self):
        if self.buffer_charges > 0 and self.buffer_cooldown <= 0:
            self.buffer_charges -= 1
            self.buffer_effect_timer = 90  # Dura 1.5 segundos (~90 FPS)
            self.buffer_cooldown = 150     # Cooldown de 2.5 segundos

    def update(self, delta_time):
        if self.game_over:
            return

        self.survival_time += delta_time
        if self.survival_time >= self.target_time:
            self.win_condition = True
            self.game_over = True

        # 1. Cooldowns
        if self.buffer_cooldown > 0:
            self.buffer_cooldown -= 1

        buffer_power = 0.0
        if self.buffer_effect_timer > 0:
            self.buffer_effect_timer -= 1
            buffer_power = 0.015  # Eleva el pH gradualmente

        # 2. Dinámica Química (CO2 disuelto reduce el pH)
        self.co2_ppm += self.co2_emission_rate
        # Relación logarítmica simplificada de pH respecto a CO2
        target_ph = 8.1 - (math.log10(self.co2_ppm / 400.0) * 0.8) + buffer_power
        self.ph += (target_ph - self.ph) * 0.05

        # 3. Cálculo del Estado de Saturación de Aragónita (Omega Ω)
        # pH 8.1 -> Ω ≈ 3.8 | pH < 7.7 -> Ω < 1.0 (Disolución activa)
        self.aragonite_sat = max(0.2, (self.ph - 7.0) * 3.45)

        # Impacto en la calcificación
        if self.aragonite_sat < 1.5:
            # Erosión / Disolución estructural
            self.calcification_rate = max(0.0, self.calcification_rate - 0.18)
        else:
            # Calcificación saludable
            self.calcification_rate = min(100.0, self.calcification_rate + 0.05)

        # 4. Actualizar Estado de Moléculas según pH
        carbonate_ratio = max(0.1, min(1.0, (self.ph - 7.4) / 0.8))
        for m in self.molecules:
            m.update(self.bounds_x, self.bounds_y)
            m.is_carbonate = random.random() < carbonate_ratio

        # Condición de Derrota
        if self.calcification_rate <= 0.0:
            self.game_over = True
            self.win_condition = False

        # Logs Químicos
        status = "AMORTIGUADOR ACTIVO" if self.buffer_effect_timer > 0 else "ACIDIFICACIÓN EN PROCESO"
        self.hydro_log.push_log(26.5, self.ph, f"Ω Aragónita: {self.aragonite_sat:.2f} | {status}")

    def draw(self, screen, font_large, font_small):
        # Color de agua según el pH (Azul marino sano -> Amarillo/Verde ácido)
        ph_stress = max(0.0, min(1.0, (8.1 - self.ph) / 0.7))
        bg_r = int(10 + (90 * ph_stress))
        bg_g = int(25 + (60 * ph_stress))
        bg_b = int(55 - (30 * ph_stress))
        screen.fill((bg_r, bg_g, bg_b))

        # 1. Visualización de Estructura Calcárea (Concha / Esqueleto de Coral)
        shell_x, shell_y = 160, 360
        shell_radius = int(60 * (self.calcification_rate / 100.0))
        
        # Sombra / Estructura base disuelta
        pygame.draw.circle(screen, (50, 60, 70), (shell_x, shell_y), 62, 2)
        
        if shell_radius > 5:
            # Capa de aragónita
            shell_color = (240, 230, 210) if self.aragonite_sat >= 1.5 else (200, 120, 100)
            pygame.draw.circle(screen, shell_color, (shell_x, shell_y), shell_radius)
            pygame.draw.circle(screen, (255, 255, 255), (shell_x, shell_y), shell_radius, 3)

        shell_lbl = font_small.render(f"Estructura Calcárea: {int(self.calcification_rate)}%", True, (240, 240, 240))
        screen.blit(shell_lbl, (shell_x - shell_lbl.get_width() // 2, shell_y + 75))

        # 2. Renderizar Moléculas de Carbonato
        for m in self.molecules:
            m.draw(screen)

        # 3. HUD Superior y Panel Químico
        self.hydro_log.draw(screen, font_small)

        time_text = font_large.render(f"Tiempo: {int(self.survival_time)}s / {int(self.target_time)}s", True, (255, 255, 255))
        screen.blit(time_text, (self.width - time_text.get_width() - 20, 20))

        charges_color = (0, 230, 255) if self.buffer_charges > 0 else (255, 100, 100)
        charges_text = font_small.render(f"Pulsos Alcalinos (ESPACIO): {self.buffer_charges} disponibles", True, charges_color)
        screen.blit(charges_text, (self.width - charges_text.get_width() - 20, 60))

        # Escala de pH
        pygame.draw.rect(screen, (30, 30, 40), (self.width - 240, 95, 220, 18))
        ph_bar_width = int(220 * max(0.0, min(1.0, (self.ph - 7.0) / 1.5)))
        
        ph_bar_color = (0, 220, 255) if self.ph >= 7.9 else (255, 180, 50) if self.ph >= 7.6 else (255, 70, 70)
        pygame.draw.rect(screen, ph_bar_color, (self.width - 240, 95, ph_bar_width, 18))
        ph_val_lbl = font_small.render(f"pH Océano: {self.ph:.2f}", True, (255, 255, 255))
        screen.blit(ph_val_lbl, (self.width - 240, 118))

        # Leyenda de Moléculas
        screen.blit(font_small.render(" Leyenda:", True, (200, 200, 200)), (self.width - 240, 145))
        pygame.draw.circle(screen, (0, 220, 255), (self.width - 230, 170), 5)
        screen.blit(font_small.render("CO3 (Carbonato libre)", True, (180, 220, 240)), (self.width - 215, 163))

        pygame.draw.circle(screen, (140, 150, 160), (self.width - 230, 190), 5)
        screen.blit(font_small.render("HCO3 (Bicarbonato/Ácido)", True, (160, 170, 180)), (self.width - 215, 183))

        # 4. Pantalla de Fin de Juego
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            if self.win_condition:
                title = font_large.render("¡CALCIFICACIÓN REGULADA!", True, (100, 255, 150))
                sub = font_small.render("Lograste amortiguar la acidificación y preservar la aragónita marina.", True, (220, 220, 220))
            else:
                title = font_large.render("DISOLUCIÓN ESTRUCTURAL", True, (255, 80, 80))
                sub = font_small.render("El pH cayó drásticamente y las conchas/corales se corroyeron.", True, (220, 220, 220))

            restart = font_small.render("Presiona 'R' para reiniciar o 'ESC' para volver al menú", True, (180, 180, 180))

            screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 60))
            screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.height // 2))
            screen.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 50))


# --- BUCLE DE PRUEBA INDEPENDIENTE ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Coral Orange - Acidification Lab Simulation")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("monospace", 24, bold=True)
    font_small = pygame.font.SysFont("monospace", 14)

    module = AcidificationLabModule(900, 600)

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
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