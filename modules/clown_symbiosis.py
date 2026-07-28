import pygame
import random
import math
import sys
import os

# Ajuste de path para importaciones desde core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.reef_organism import ReefOrganism
from core.hydro_log import HydroLog


class Parasite:
    """Parásito que se adhiere a la anémona y reduce su salud."""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 6
        self.alive = True

    def draw(self, screen):
        if self.alive:
            pygame.draw.circle(screen, (160, 30, 200), (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, (220, 100, 255), (int(self.x), int(self.y)), self.radius - 2)


class ButterflyFish:
    """Depredador que intenta morder los tentáculos de la anémona."""
    def __init__(self, screen_width, screen_height, target_x, target_y):
        self.x = random.choice([-30, screen_width + 30])
        self.y = random.randint(100, screen_height - 150)
        self.speed = 1.8
        self.target_x = target_x
        self.target_y = target_y
        self.radius = 16
        self.active = True

    def update(self):
        # Moverse hacia la anémona
        angle = math.atan2(self.target_y - self.y, self.target_x - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

    def draw(self, screen):
        if self.active:
            # Cuerpo de Pez Mariposa (Amarillo con franja negra)
            pygame.draw.circle(screen, (255, 215, 0), (int(self.x), int(self.y)), self.radius)
            pygame.draw.line(screen, (20, 20, 20), (int(self.x), int(self.y - self.radius)), (int(self.x), int(self.y + self.radius)), 4)


class ClownSymbiosisModule:
    """
    Módulo 2: Clown Symbiosis
    Simula la relación mutualista entre el Pez Payaso y la Anémona de Mar.
    Mecánicas:
    - Movimiento con flechas / WASD para controlar al Pez Payaso.
    - Visitar la anémona para recargar el recubrimiento de mucosidad (Mucus Layer).
    - Colisionar con parásitos morados para devorarlos/limpiar la anémona.
    - Ahuyentar peces mariposa alejándolos de la anémona.
    """

    def __init__(self, screen_width=900, screen_height=600):
        self.width = screen_width
        self.height = screen_height

        # Anémona (Centro del Hábitat)
        self.anemone_x = screen_width // 2
        self.anemone_y = screen_height // 2 + 30
        self.anemone_health = 100.0
        self.anemone_radius = 50

        # Pez Payaso (Jugador)
        self.fish_x = self.anemone_x - 100
        self.fish_y = self.anemone_y
        self.fish_vx = 0
        self.fish_vy = 0
        self.fish_speed = 4.2
        self.fish_radius = 14
        self.mucus_layer = 100.0  # Capa de protección contra las toxinas de la anémona

        # Entidades dinámicas
        self.parasites = []
        self.predators = []

        # Temporizadores de spawns
        self.parasite_timer = 0
        self.predator_timer = 0

        # Sistema de Juego
        self.survival_time = 0.0
        self.target_time = 60.0
        self.game_over = False
        self.win_condition = False

        self.hydro_log = HydroLog(x=20, y=20, width=280, height=140)

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__(self.width, self.height)

    def update(self, delta_time):
        if self.game_over:
            return

        self.survival_time += delta_time
        if self.survival_time >= self.target_time:
            self.win_condition = True
            self.game_over = True

        # 1. Movimiento del Pez Payaso (Jugador)
        keys = pygame.key.get_pressed()
        self.fish_vx = 0
        self.fish_vy = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.fish_vx = -self.fish_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.fish_vx = self.fish_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.fish_vy = -self.fish_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.fish_vy = self.fish_speed

        self.fish_x = max(20, min(self.width - 20, self.fish_x + self.fish_vx))
        self.fish_y = max(20, min(self.height - 20, self.fish_y + self.fish_vy))

        # 2. Interacción con la Anémona
        dist_to_anemone = math.hypot(self.fish_x - self.anemone_x, self.fish_y - self.anemone_y)
        in_anemone = dist_to_anemone < self.anemone_radius + 10

        if in_anemone:
            # Recargar capa de mucosidad estando dentro de los tentáculos
            self.mucus_layer = min(100.0, self.mucus_layer + 1.2)
        else:
            # Degradar mucosidad progresivamente en mar abierto
            self.mucus_layer = max(0.0, self.mucus_layer - 0.15)

        # 3. Spawns de Parásitos y Depredadores
        self.parasite_timer += delta_time
        if self.parasite_timer > 3.5 and len(self.parasites) < 6:
            self.parasite_timer = 0
            px = self.anemone_x + random.randint(-35, 35)
            py = self.anemone_y + random.randint(-35, 35)
            self.parasites.append(Parasite(px, py))

        self.predator_timer += delta_time
        if self.predator_timer > 6.0 and len(self.predators) < 3:
            self.predator_timer = 0
            self.predators.append(ButterflyFish(self.width, self.height, self.anemone_x, self.anemone_y))

        # 4. Actualizar Parásitos y Limpieza
        for p in self.parasites:
            if p.alive:
                self.anemone_health = max(0.0, self.anemone_health - 0.02)
                # Colisión Pez - Parásito (Limpieza)
                if math.hypot(self.fish_x - p.x, self.fish_y - p.y) < self.fish_radius + p.radius:
                    p.alive = False

        self.parasites = [p for p in self.parasites if p.alive]

        # 5. Actualizar Depredadores (Peces Mariposa)
        for pred in self.predators:
            if pred.active:
                pred.update()
                # Si llega a la anémona, la muerde
                if math.hypot(pred.x - self.anemone_x, pred.y - self.anemone_y) < self.anemone_radius:
                    self.anemone_health = max(0.0, self.anemone_health - 8.0)
                    pred.active = False

                # Si el Pez Payaso los embiste, los ahuyenta
                elif math.hypot(self.fish_x - pred.x, self.fish_y - pred.y) < self.fish_radius + pred.radius:
                    pred.active = False

        self.predators = [p for p in self.predators if p.active]

        # Condición de derrota
        if self.anemone_health <= 0 or self.mucus_layer <= 0:
            self.game_over = True
            self.win_condition = False

        # Logs de Simbiosis
        status = "PROTECCIÓN ACTIVA" if in_anemone else "EN PATRULLA"
        if self.mucus_layer < 25:
            status = "CRÍTICO: MUCUS BAJO"
        self.hydro_log.push_log(26.5, 8.1, f"Anémona: {int(self.anemone_health)}% | {status}")

    def draw(self, screen, font_large, font_small):
        # Fondo Océano
        screen.fill((12, 35, 60))

        # 1. Renderizar Anémona (Tentáculos con animación oscilante)
        time_ms = pygame.time.get_ticks() * 0.003
        num_tentacles = 14
        for i in range(num_tentacles):
            angle = (2 * math.pi / num_tentacles) * i
            wave = math.sin(time_ms + i) * 12
            tx = self.anemone_x + math.cos(angle) * (self.anemone_radius + wave)
            ty = self.anemone_y + math.sin(angle) * (self.anemone_radius + wave)
            
            # Color tentáculo (Verde/Rosa fluor según salud)
            t_color = (230, 80, 160) if self.anemone_health > 40 else (180, 140, 160)
            pygame.draw.line(screen, t_color, (self.anemone_x, self.anemone_y), (tx, ty), 6)

        pygame.draw.circle(screen, (200, 60, 130), (self.anemone_x, self.anemone_y), 22)

        # 2. Renderizar Parásitos
        for p in self.parasites:
            p.draw(screen)

        # 3. Renderizar Depredadores
        for pred in self.predators:
            pred.draw(screen)

        # 4. Renderizar Pez Payaso (Jugador)
        # Anillo de mucosidad protectora
        mucus_alpha = int((self.mucus_layer / 100.0) * 180)
        mucus_surf = pygame.Surface((self.fish_radius * 4, self.fish_radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(mucus_surf, (0, 230, 255, mucus_alpha), (self.fish_radius * 2, self.fish_radius * 2), self.fish_radius + 4, 3)
        screen.blit(mucus_surf, (self.fish_x - self.fish_radius * 2, self.fish_y - self.fish_radius * 2))

        # Cuerpo Naranja con franjas blancas (Pez Payaso)
        pygame.draw.circle(screen, (255, 110, 20), (int(self.fish_x), int(self.fish_y)), self.fish_radius)
        pygame.draw.rect(screen, (255, 255, 255), (int(self.fish_x) - 3, int(self.fish_y) - self.fish_radius, 6, self.fish_radius * 2))

        # 5. UI / HUD
        self.hydro_log.draw(screen, font_small)

        # Barras de estado superiores
        time_text = font_large.render(f"Tiempo: {int(self.survival_time)}s / {int(self.target_time)}s", True, (255, 255, 255))
        screen.blit(time_text, (self.width - time_text.get_width() - 20, 20))

        # Barra de Mucosidad del Pez
        pygame.draw.rect(screen, (40, 40, 40), (self.width - 220, 60, 200, 14))
        pygame.draw.rect(screen, (0, 220, 255), (self.width - 220, 60, int(200 * (self.mucus_layer / 100.0)), 14))
        mucus_lbl = font_small.render("Capa Mucosa (Anémona):", True, (200, 240, 255))
        screen.blit(mucus_lbl, (self.width - 220, 42))

        # Barra de Salud de la Anémona
        pygame.draw.rect(screen, (40, 40, 40), (self.width - 220, 100, 200, 14))
        pygame.draw.rect(screen, (230, 80, 160), (self.width - 220, 100, int(200 * (self.anemone_health / 100.0)), 14))
        anemone_lbl = font_small.render("Salud de la Anémona:", True, (255, 180, 220))
        screen.blit(anemone_lbl, (self.width - 220, 82))

        # 6. Fin de juego / Victoria
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            if self.win_condition:
                title = font_large.render("¡MUTUALISMO EXITOSO!", True, (100, 255, 150))
                sub = font_small.render("Mantuviste la anémona libre de parásitos y protegida de depredadores.", True, (220, 220, 220))
            else:
                title = font_large.render("SIMBIOSIS ROTA", True, (255, 80, 80))
                sub = font_small.render("La anémona pereció o perdiste tu recubrimiento de mucosidad protectora.", True, (220, 220, 220))

            restart = font_small.render("Presiona 'R' para reiniciar o 'ESC' para volver al menú", True, (180, 180, 180))

            screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 60))
            screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.height // 2))
            screen.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 50))


# --- BUCLE DE PRUEBA INDEPENDIENTE ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Coral Orange - Clown Symbiosis Simulation")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("monospace", 24, bold=True)
    font_small = pygame.font.SysFont("monospace", 14)

    module = ClownSymbiosisModule(900, 600)

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