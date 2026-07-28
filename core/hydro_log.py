import pygame

class HydroLog:
    """Consola visual de datos de temperatura y pH en tiempo real."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.logs = []

    def push_log(self, temp, ph, status):
        log_entry = f"Temp: {temp:.2f}°C | pH: {ph:.1f} | {status}"
        self.logs.append(log_entry)
        if len(self.logs) > 6:
            self.logs.pop(0)

    def draw(self, screen, font):
        # Fondo estilo consola
        pygame.draw.rect(screen, (15, 25, 35, 200), self.rect)
        pygame.draw.rect(screen, (0, 200, 220), self.rect, 2)

        for i, log in enumerate(self.logs):
            text_surface = font.render(log, True, (0, 230, 180))
            screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 10 + (i * 18)))