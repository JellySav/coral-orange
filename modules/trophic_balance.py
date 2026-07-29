import pygame
import random
import math
import sys
import os

# Ajuste de path para importaciones desde core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hydro_log import HydroLog


class Creature:
    """Representa a un individuo dentro de la red trófica."""
    def __init__(self, species, x, y):
        self.species = species  # "ALGAE", "HERBIVORE", "CARNIVORE", "SHARK"
        self.x = x
        self.y = y
        self.vx = random.uniform(-1.5, 1.5) if species != "ALGAE" else 0
        self.vy = random.uniform(-1.5, 1.5) if species != "ALGAE" else 0
        self.energy = 100.0

        # Propiedades por especie
        if species == "ALGAE":
            self.radius = 4
            self.color = (50, 205, 50)
        elif species == "HERBIVORE":  # Pez Loro
            self.radius = 8
            self.color = (0, 206, 209)
        elif species == "CARNIVORE":  # Mero / Pargo
            self.radius = 12
            self.color = (255, 140, 0)
        elif species == "SHARK":      # Tiburón Arrecifal
            self.radius = 18
            self.color = (112, 128, 144)

    def move(self, bounds_x, bounds_y):
        if self.species == "ALGAE":
            return

        self.x += self.vx
        self.y += self.vy

        # Rebote en bordes del mapa
        if self.x < bounds_x[0] or self.x > bounds_x[1]:
            self.vx *= -1
        if self.y < bounds_y[0] or self.y > bounds_y[1]:
            self.vy *= -1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        if self.species == "SHARK":
            # Aleta distintiva para los superdepredadores
            pygame.draw.polygon(screen, (70, 80, 95), [
                (int(self.x), int(self.y - self.radius)),
                (int(self.x - 6), int(self.y - self.radius - 8)),
                (int(self.x + 6), int(self.y - self.radius))
            ])


class TrophicBalanceModule:
    """
    Módulo 3: Trophic Balance
    Simulador de dinámicas de poblaciones en redes tróficas marinas.
    El jugador puede declarar un Área Marina Protegida (AMP) para frenar la sobrepesca
    y reequilibrar la biomasa de los 4 niveles tróficos.
    """

    def __init__(self, screen_width=900, screen_height=600):
        self.width = screen_width
        self.height = screen_height

        # Área Marina Protegida (AMP)
        self.mpa_active = False
        self.mpa_rect = pygame.Rect(320, 180, 260, 260)
        self.mpa_cooldown = 0

        # Límites de nado
        self.bounds_x = (40, screen_width - 40)
        self.bounds_y = (180, screen_height - 40)

        # Poblaciones iniciales
        self.creatures = []
        self._seed_ecosystem()

        # Sistema de Puntuación
        self.survival_time = 0.0
        self.target_time = 60.0
        self.game_over = False
        self.win_condition = False

        self.hydro_log = HydroLog(x=20, y=20, width=280, height=140)

    def _seed_ecosystem(self):
        """Genera el estado inicial balanceado de la biomasa."""
        self.creatures.clear()
        counts = {"ALGAE": 40, "HERBIVORE": 20, "CARNIVORE": 8, "SHARK": 3}

        for species, count in counts.items():
            for _ in range(count):
                x = random.randint(self.bounds_x[0], self.bounds_x[1])
                y = random.randint(self.bounds_y[0], self.bounds_y[1])
                self.creatures.append(Creature(species, x, y))

    def handle_event(self, event):
        if self.game_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.__init__(self.width, self.height)
            return

        # Conmutar Área Marina Protegida con la barra Espaciadora
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.mpa_cooldown <= 0:
                self.mpa_active = not self.mpa_active
                self.mpa_cooldown = 60  # Cooldown suave de 1 segundo

    def update(self, delta_time):
        if self.game_over:
            return

        self.survival_time += delta_time
        if self.survival_time >= self.target_time:
            self.win_condition = True
            self.game_over = True

        if self.mpa_cooldown > 0:
            self.mpa_cooldown -= 1

        # 1. Mover criaturas
        for c in self.creatures:
            c.move(self.bounds_x, self.bounds_y)

        # 2. Interacciones Depredación / Consumo
        algae = [c for c in self.creatures if c.species == "ALGAE"]
        herbs = [c for c in self.creatures if c.species == "HERBIVORE"]
        carns = [c for c in self.creatures if c.species == "CARNIVORE"]
        sharks = [c for c in self.creatures if c.species == "SHARK"]

        # Herbívoros comen Algas
        for h in herbs:
            for a in algae:
                if math.hypot(h.x - a.x, h.y - a.y) < h.radius + a.radius:
                    if a in self.creatures:
                        self.creatures.remove(a)
                        break

        # Carnívoros comen Herbívoros
        for car in carns:
            for h in herbs:
                if math.hypot(car.x - h.x, car.y - h.y) < car.radius + h.radius:
                    if h in self.creatures:
                        self.creatures.remove(h)
                        break

        # Tiburones comen Carnívoros
        for s in sharks:
            for car in carns:
                if math.hypot(s.x - car.x, s.y - car.y) < s.radius + car.radius:
                    if car in self.creatures:
                        self.creatures.remove(car)
                        break

        # 3. Presión de Pesca Furtiva fuera de la AMP
        if random.random() < 0.04:  # Evento de pesca
            target_species = "SHARK" if len(sharks) > 1 else "CARNIVORE"
            candidates = [c for c in self.creatures if c.species == target_species]
            
            for cand in candidates:
                # Si la criatura NO está protegida dentro del AMP, puede ser pescada
                if not (self.mpa_active and self.mpa_rect.collidepoint(cand.x, cand.y)):
                    self.creatures.remove(cand)
                    break

        # 4. Crecimiento orgánico de algas y reproducción básica
        if len(algae) < 50 and random.random() < 0.2:
            ax = random.randint(self.bounds_x[0], self.bounds_x[1])
            ay = random.randint(self.bounds_y[0], self.bounds_y[1])
            self.creatures.append(Creature("ALGAE", ax, ay))

        if len(herbs) > 0 and len(herbs) < 15 and random.random() < 0.03:
            self.creatures.append(Creature("HERBIVORE", random.randint(100, 800), random.randint(200, 500)))

        # 5. Evaluación de colapso de red trófica
        curr_sharks = len([c for c in self.creatures if c.species == "SHARK"])
        curr_algae = len([c for c in self.creatures if c.species == "ALGAE"])
        curr_herbs = len([c for c in self.creatures if c.species == "HERBIVORE"])

        # Colapso por extinción de superdepredadores o asfixia por algas
        if curr_sharks == 0 or curr_herbs == 0 or curr_algae > 65:
            self.game_over = True
            self.win_condition = False

        # Logs
        status = "AMP ACTIVA [ZONA PROTEGIDA]" if self.mpa_active else "PESCA ABIERTA [RIESGO]"
        self.hydro_log.push_log(26.5, 8.1, f"Tiburones: {curr_sharks} | {status}")

    def draw(self, screen, font_large, font_small):
        # Fondo Océano Profundo
        screen.fill((8, 20, 38))

        # 1. Dibujar Área Marina Protegida (AMP)
        if self.mpa_active:
            mpa_surface = pygame.Surface((self.mpa_rect.width, self.mpa_rect.height), pygame.SRCALPHA)
            mpa_surface.fill((0, 230, 150, 45))
            screen.blit(mpa_surface, (self.mpa_rect.x, self.mpa_rect.y))
            pygame.draw.rect(screen, (0, 255, 180), self.mpa_rect, 2)

            mpa_label = font_small.render("ÁREA MARINA PROTEGIDA (AMP)", True, (100, 255, 200))
            screen.blit(mpa_label, (self.mpa_rect.x + 10, self.mpa_rect.y + 10))

        # 2. Renderizar criaturas de la red trófica
        for c in self.creatures:
            c.draw(screen)

        # 3. HUD Superior e Indicadores
        self.hydro_log.draw(screen, font_small)

        time_text = font_large.render(f"Tiempo: {int(self.survival_time)}s / {int(self.target_time)}s", True, (255, 255, 255))
        screen.blit(time_text, (self.width - time_text.get_width() - 20, 20))

        btn_color = (0, 255, 180) if self.mpa_active else (255, 160, 80)
        btn_text = font_small.render(f"AMP (ESPACIO): {'ACTIVADA' if self.mpa_active else 'DESACTIVADA'}", True, btn_color)
        screen.blit(btn_text, (self.width - btn_text.get_width() - 20, 60))

        # Leyenda de Niveles Tróficos
        legend_x = 320
        legend_y = 20
        pygame.draw.circle(screen, (112, 128, 144), (legend_x, legend_y + 10), 6)
        screen.blit(font_small.render("Tiburón", True, (200, 200, 200)), (legend_x + 12, legend_y + 2))

        pygame.draw.circle(screen, (255, 140, 0), (legend_x + 90, legend_y + 10), 6)
        screen.blit(font_small.render("Carnívoro", True, (200, 200, 200)), (legend_x + 102, legend_y + 2))

        pygame.draw.circle(screen, (0, 206, 209), (legend_x + 200, legend_y + 10), 6)
        screen.blit(font_small.render("Herbívoro", True, (200, 200, 200)), (legend_x + 212, legend_y + 2))

        pygame.draw.circle(screen, (50, 205, 50), (legend_x + 310, legend_y + 10), 6)
        screen.blit(font_small.render("Alga", True, (200, 200, 200)), (legend_x + 322, legend_y + 2))

        # 4. Pantalla de Fin de Juego / Victoria
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            if self.win_condition:
                title = font_large.render("¡RED TRÓFICA EN EQUILIBRIO!", True, (100, 255, 150))
                sub = font_small.render("La declaración estratégica del AMP protegió a los superdepredadores.", True, (220, 220, 220))
            else:
                title = font_large.render("COLAPSO DEL ECOSISTEMA", True, (255, 80, 80))
                sub = font_small.render("Ocurrió una cascada trófica por sobrepesca o desbalance de biomasa.", True, (220, 220, 220))

            restart = font_small.render("Presiona 'R' para reiniciar o 'ESC' para volver al menú", True, (180, 180, 180))

            screen.blit(title, (self.width // 2 - title.get_width() // 2, self.height // 2 - 60))
            screen.blit(sub, (self.width // 2 - sub.get_width() // 2, self.height // 2))
            screen.blit(restart, (self.width // 2 - restart.get_width() // 2, self.height // 2 + 50))


# --- BUCLE DE PRUEBA INDEPENDIENTE ---
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((900, 600))
    pygame.display.set_caption("Coral Orange - Trophic Balance Simulation")
    clock = pygame.time.Clock()

    font_large = pygame.font.SysFont("monospace", 24, bold=True)
    font_small = pygame.font.SysFont("monospace", 14)

    module = TrophicBalanceModule(900, 600)

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