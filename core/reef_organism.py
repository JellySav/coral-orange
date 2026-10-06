import pygame
import math

class ReefOrganism:
    """
    Clase base para representar especies del arrecife
    (Corales, Peces Payaso, Anémonas, Algas).
    """
    def __init__(self, organism_id, name, x, y, species_type, color):
        self.organism_id = organism_id
        self.name = name
        self.x = x
        self.y = y
        self.species_type = species_type  # "CORAL", "FISH", "ANEMONE", "ALGAE"
        self.color = color
        self.health = 100.0              # 0 a 100%
        self.bleached = False

    def update_health(self, temp_celsius, ocean_ph, delta_time=1 / 60):
        """Actualiza el estado de salud según la temperatura y el pH."""
        frame_scale = delta_time * 60.0
        # Estrés térmico en corales
        if self.species_type == "CORAL":
            if temp_celsius > 29.0:
                self.health = max(0.0, self.health - 0.5 * frame_scale)
                if self.health < 40.0:
                    self.bleached = True
                    self.color = (220, 220, 220)  # Pierde su color Coral Orange
            elif temp_celsius <= 28.0 and self.health < 100:
                self.health = min(100.0, self.health + 0.2 * frame_scale)

    def draw(self, screen, font):
        """Renderizado en pantalla según el tipo de organismo."""
        radius = 20 if self.species_type == "CORAL" else 12
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), radius)
        
        # Indicador visual de salud (Anillo exterior)
        border_color = (0, 255, 120) if self.health > 60 else (255, 180, 0) if self.health > 30 else (255, 50, 50)
        pygame.draw.circle(screen, border_color, (int(self.x), int(self.y)), radius + 3, 2)

        # Nombre del organismo
        identifier = str(self.organism_id)
        label_text = f"#{identifier.rsplit('-', 1)[-1]}" if "-" in identifier else self.name
        label = font.render(label_text, True, (240, 240, 240))
        screen.blit(label, (int(self.x) - label.get_width() // 2, int(self.y) + radius + 5))