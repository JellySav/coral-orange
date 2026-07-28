import pygame
import sys
import os

# Asegurar importaciones locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.bleaching_alert import BleachingAlertModule


class CoralOrangeLauncher:
    """
    Launcher principal del Arcade Coral Orange.
    Permite seleccionar y desplegar los minijuegos de conservación marina.
     
    """

    def __init__(self, width=900, height=600):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Coral Orange - Marine Ecosystem Suite")
        self.clock = pygame.time.Clock()

        # Fuentes
        self.font_title = pygame.font.SysFont("monospace", 36, bold=True)
        self.font_option = pygame.font.SysFont("monospace", 18, bold=True)
        self.font_sub = pygame.font.SysFont("monospace", 13)

        # Módulos del Arcade
        self.modules_info = [
            {
                "id": 1,
                "title": "1. BLEACHING ALERT",
                "desc": "Simulación de Olas de Calor y Estrés Térmico en Corales",
                "active": True
            },
            {
                "id": 2,
                "title": "2. CLOWN SYMBIOSIS",
                "desc": "Mantenimiento de Mutualismo entre Pez Payaso y Anémonas",
                "active": False
            },
            {
                "id": 3,
                "title": "3. TROPHIC BALANCE",
                "desc": "Gestión de Cadenas Tróficas y Áreas Marinas Protegidas",
                "active": False
            },
            {
                "id": 4,
                "title": "4. ACIDIFICATION LAB",
                "desc": "Química Marina, Monitoreo de pH y Calcificación Calcárea",
                "active": False
            }
        ]

        self.selected_index = 0
        self.active_module = None

    def run(self):
        """Bucle principal del selector y gestor de módulos."""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            if self.active_module is None:
                # --- MODO MENÚ ---
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.selected_index = (self.selected_index - 1) % len(self.modules_info)
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.selected_index = (self.selected_index + 1) % len(self.modules_info)
                        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                            self._launch_selected_module()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

                self._draw_menu()
            else:
                # --- MODO JUEGO ACTIVO ---
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        # Volver al menú principal
                        self.active_module = None
                    else:
                        self.active_module.handle_event(event)

                if self.active_module:
                    self.active_module.update(dt)
                    self.active_module.draw(self.screen, self.font_title, self.font_sub)

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def _launch_selected_module(self):
        """Inicializa el módulo seleccionado."""
        if self.selected_index == 0:
            self.active_module = BleachingAlertModule(self.width, self.height)
        else:
            # Los módulos 2, 3 y 4 se irán integrando secuencialmente
            pass

    def _draw_menu(self):
        """Renderizado estético del menú principal estilo consola oceánica."""
        self.screen.fill((10, 25, 40))

        # Título
        title_surface = self.font_title.render("🪸 CORAL ORANGE 🪸", True, (255, 127, 80))
        sub_surface = self.font_sub.render("Ecosystem Simulation & Ocean Conservation Suite", True, (0, 200, 220))
        
        self.screen.blit(title_surface, (self.width // 2 - title_surface.get_width() // 2, 50))
        self.screen.blit(sub_surface, (self.width // 2 - sub_surface.get_width() // 2, 95))

        # Marco del menú
        menu_box = pygame.Rect(100, 140, self.width - 200, 360)
        pygame.draw.rect(self.screen, (15, 35, 55), menu_box)
        pygame.draw.rect(self.screen, (0, 180, 200), menu_box, 2)

        # Opciones
        for i, mod in enumerate(self.modules_info):
            item_y = 170 + (i * 80)
            is_selected = (i == self.selected_index)

            # Color del texto según selección
            if is_selected:
                pygame.draw.rect(self.screen, (25, 55, 80), (120, item_y - 5, self.width - 240, 65))
                pygame.draw.rect(self.screen, (255, 127, 80), (120, item_y - 5, self.width - 240, 65), 2)
                color_title = (255, 160, 120)
                color_desc = (240, 240, 240)
            else:
                color_title = (120, 160, 180) if mod["active"] else (80, 100, 120)
                color_desc = (90, 110, 130)

            # Renderizado de texto
            tag = "[LISTO]" if mod["active"] else "[EN DESARROLLO]"
            title_txt = self.font_option.render(f"{mod['title']} {tag}", True, color_title)
            desc_txt = self.font_sub.render(f"  {mod['desc']}", True, color_desc)

            self.screen.blit(title_txt, (140, item_y))
            self.screen.blit(desc_txt, (140, item_y + 28))

        # Footer / Instrucciones
        info_txt = self.font_sub.render("Usa las flechas [↑/↓] para navegar | [ENTER] para iniciar | [ESC] para salir", True, (150, 180, 200))
        self.screen.blit(info_txt, (self.width // 2 - info_txt.get_width() // 2, 525))


if __name__ == "__main__":
    launcher = CoralOrangeLauncher()
    launcher.run()