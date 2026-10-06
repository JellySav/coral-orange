import pygame

class HydroLog:
    """Consola visual de datos de temperatura y pH en tiempo real."""
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.logs = []
        self.elapsed = 1.0

    def push_log(self, temp, ph, status, delta_time):
        self.elapsed += delta_time
        if self.logs and self.elapsed < 1.0:
            return

        self.elapsed = 0.0
        log_entry = f"Temp: {temp:.2f}°C | pH: {ph:.1f} | {status}"
        self.logs.append(log_entry)
        if len(self.logs) > 6:
            self.logs.pop(0)

    def draw(self, screen, font):
        pygame.draw.rect(screen, (15, 25, 35, 200), self.rect)
        pygame.draw.rect(screen, (0, 200, 220), self.rect, 2)
        heading = font.render("REGISTRO AMBIENTAL", True, (132, 185, 183))
        screen.blit(heading, (self.rect.x + 10, self.rect.y + 7))
        pygame.draw.line(
            screen,
            (0, 115, 130),
            (self.rect.x + 10, self.rect.y + 27),
            (self.rect.right - 10, self.rect.y + 27),
        )

        previous_clip = screen.get_clip()
        screen.set_clip(self.rect)
        for i, log in enumerate(self.logs):
            while font.size(log)[0] > self.rect.width - 20:
                log = log[:-4] + "..."
            text_surface = font.render(log, True, (0, 230, 180))
            screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 33 + (i * 17)))
        screen.set_clip(previous_clip)