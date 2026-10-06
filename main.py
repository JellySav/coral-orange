import asyncio
import math
import pygame
import sys
import os

# Asegurar importaciones locales
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.bleaching_alert import BleachingAlertModule
from modules.clown_symbiosis import ClownSymbiosisModule
from modules.trophic_balance import TrophicBalanceModule
from modules.acidification_lab import AcidificationLabModule


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
        self.font_title = pygame.font.SysFont("sans", 42, bold=True)
        self.font_option = pygame.font.SysFont("sans", 19, bold=True)
        self.font_sub = pygame.font.SysFont("sans", 14)
        self.font_micro = pygame.font.SysFont("sans", 11, bold=True)
        self.font_intro_title = pygame.font.SysFont("sans", 27, bold=True)
        self.elapsed = 0.0
        self.module_colors = [
            (255, 126, 92),
            (244, 123, 171),
            (117, 216, 165),
            (102, 205, 222),
        ]
        self.particles = [
            (38 + (index * 137) % (width - 76), 125 + (index * 71) % (height - 150), index % 3 + 1)
            for index in range(24)
        ]

        # Módulos del Arcade
        self.modules_info = [
            {
                "id": 1,
                "title": "1. BLEACHING ALERT",
                "desc": "Simulación de Olas de Calor y Estrés Térmico en Corales",
                "objective": "Mantén viva la colonia durante la ola de calor.",
                "concept": "El estrés térmico prolongado puede provocar blanqueamiento y pérdida de zooxantelas.",
                "controls": "ESPACIO: aplicar un pulso frío. Reserva tus cargas para los picos de temperatura.",
                "active": True,
                "module": BleachingAlertModule
            },
            {
                "id": 2,
                "title": "2. CLOWN SYMBIOSIS",
                "desc": "Mantenimiento de Mutualismo entre Pez Payaso y Anémonas",
                "objective": "Protege la anémona y conserva la relación de mutualismo.",
                "concept": "El pez obtiene refugio; la anémona recibe protección y limpieza.",
                "controls": "Flechas o WASD: mover. Limpia parásitos morados, ahuyenta depredadores y vuelve a la anémona.",
                "active": True,
                "module": ClownSymbiosisModule
            },
            {
                "id": 3,
                "title": "3. TROPHIC BALANCE",
                "desc": "Gestión de Cadenas Tróficas y Áreas Marinas Protegidas",
                "objective": "Evita el colapso de la red trófica durante la simulación.",
                "concept": "La protección de depredadores ayuda a mantener el equilibrio entre niveles tróficos.",
                "controls": "ESPACIO: activar o retirar el Área Marina Protegida (AMP).",
                "active": True,
                "module": TrophicBalanceModule
            },
            {
                "id": 4,
                "title": "4. ACIDIFICATION LAB",
                "desc": "Química Marina, Monitoreo de pH y Calcificación Calcárea",
                "objective": "Preserva la estructura calcárea frente a la acidificación.",
                "concept": "Más CO2 disuelto reduce el pH y la disponibilidad de carbonato para calcificar.",
                "controls": "ESPACIO: aplicar una dosis de amortiguador alcalino.",
                "active": True,
                "module": AcidificationLabModule
            }
        ]

        self.selected_index = 0
        self.active_module = None
        self.show_intro = False

    async def run(self):
        """Bucle principal del selector y gestor de módulos."""
        running = True
        while running:
            dt = min(self.clock.tick(60) / 1000.0, 0.1)
            self.elapsed += dt

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
                        self.show_intro = False
                    elif self.show_intro:
                        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                            self.show_intro = False
                    else:
                        self.active_module.handle_event(event)

                if self.active_module:
                    if not self.show_intro:
                        self.active_module.update(dt)
                    self.active_module.draw(self.screen, self.font_title, self.font_sub)
                    if self.show_intro:
                        self._draw_intro()

            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()

    def _launch_selected_module(self):
        """Inicializa el módulo seleccionado."""
        module_class = self.modules_info[self.selected_index]["module"]
        self.active_module = module_class(self.width, self.height)
        self.show_intro = True

    def _draw_intro(self):
        module = self.modules_info[self.selected_index]
        accent = self.module_colors[self.selected_index]
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((3, 12, 19, 185))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect((self.width - 680) // 2, (self.height - 380) // 2, 680, 380)
        pygame.draw.rect(self.screen, (10, 35, 43), panel, border_radius=8)
        pygame.draw.rect(self.screen, accent, panel, 1, border_radius=8)

        kicker = self.font_micro.render(f"PREPARACIÓN   /   0{self.selected_index + 1}", True, accent)
        self.screen.blit(kicker, (panel.x + 28, panel.y + 24))
        title = self.font_intro_title.render(module["title"].split(". ", 1)[-1], True, (247, 242, 225))
        self.screen.blit(title, (panel.x + 28, panel.y + 48))

        sections = (
            ("OBJETIVO", module["objective"]),
            ("CONCEPTO", module["concept"]),
            ("CONTROLES", module["controls"]),
        )
        for index, (heading, text) in enumerate(sections):
            heading_y = panel.y + 105 + index * 76
            heading_surface = self.font_micro.render(heading, True, accent)
            self.screen.blit(heading_surface, (panel.x + 28, heading_y))
            self._draw_wrapped_text(
                text,
                self.font_sub,
                (203, 220, 211),
                pygame.Rect(panel.x + 28, heading_y + 19, panel.width - 56, 48),
            )

        start = self.font_option.render("ENTER / ESPACIO  ·  COMENZAR", True, (247, 242, 225))
        back = self.font_sub.render("ESC  ·  VOLVER", True, (137, 177, 171))
        self.screen.blit(start, (panel.x + 28, panel.bottom - 39))
        self.screen.blit(back, (panel.right - back.get_width() - 28, panel.bottom - 37))

    def _draw_menu(self):
        """Renderiza el selector como una estación de monitoreo submarina."""
        self.screen.fill((7, 24, 34))

        for band in range(12):
            y = 112 + band * 37 + int(math.sin(self.elapsed * 0.4 + band) * 5)
            pygame.draw.line(self.screen, (10, 34 + band, 43 + band), (0, y), (self.width, y), 1)

        for index, (x, y, radius) in enumerate(self.particles):
            drift_y = int((y + self.elapsed * (4 + index % 4)) % (self.height - 90))
            pulse = 0.5 + 0.5 * math.sin(self.elapsed + index)
            color = (int(32 + pulse * 24), int(103 + pulse * 42), int(113 + pulse * 38))
            pygame.draw.circle(self.screen, color, (x, drift_y), radius)

        reef_line = [
            (0, self.height - 28),
            (90, self.height - 37),
            (175, self.height - 24),
            (260, self.height - 42),
            (365, self.height - 26),
            (480, self.height - 39),
            (600, self.height - 25),
            (720, self.height - 43),
            (self.width, self.height - 27),
            (self.width, self.height),
            (0, self.height),
        ]
        pygame.draw.polygon(self.screen, (11, 44, 47), reef_line)

        eyebrow = self.font_micro.render("OCEAN FIELD STATION   /   INTERACTIVE SCIENCE", True, (112, 202, 195))
        self.screen.blit(eyebrow, (54, 25))
        title = self.font_title.render("CORAL ORANGE", True, (247, 242, 225))
        self.screen.blit(title, (50, 43))
        pygame.draw.rect(self.screen, (255, 126, 92), (53, 98, 62, 4), border_radius=2)
        subtitle = self.font_sub.render("Conservación marina a escala de arrecife", True, (157, 187, 183))
        self.screen.blit(subtitle, (128, 91))

        status = self.font_micro.render("SIMULACIONES DISPONIBLES", True, (124, 161, 160))
        self.screen.blit(status, (self.width - status.get_width() - 55, 45))
        count = self.font_option.render(f"0{len(self.modules_info)}", True, (247, 242, 225))
        self.screen.blit(count, (self.width - count.get_width() - 55, 64))

        list_box = pygame.Rect(48, 137, 500, 374)
        pygame.draw.rect(self.screen, (9, 31, 40), list_box, border_radius=8)
        pygame.draw.rect(self.screen, (29, 70, 75), list_box, 1, border_radius=8)

        for index, module in enumerate(self.modules_info):
            item_y = 151 + index * 87
            selected = index == self.selected_index
            accent = self.module_colors[index]
            item_rect = pygame.Rect(59, item_y, 478, 78)

            if selected:
                pygame.draw.rect(self.screen, (18, 53, 59), item_rect, border_radius=6)
                pygame.draw.rect(self.screen, accent, item_rect, 1, border_radius=6)
                pygame.draw.rect(self.screen, accent, (item_rect.x, item_rect.y + 13, 3, 52), border_radius=2)

            index_text = self.font_micro.render(f"0{index + 1}", True, accent if selected else (91, 125, 126))
            title_text = self.font_option.render(module["title"].split(". ", 1)[-1], True, (245, 240, 222) if selected else (157, 179, 174))
            state_text = self.font_micro.render("READY", True, (114, 215, 169))
            self.screen.blit(index_text, (76, item_y + 15))
            self.screen.blit(title_text, (112, item_y + 13))
            self.screen.blit(state_text, (item_rect.right - state_text.get_width() - 15, item_y + 17))

            if selected:
                detail = self.font_sub.render(module["desc"], True, (169, 200, 193))
                self.screen.blit(detail, (112, item_y + 44))
            else:
                marker = pygame.Rect(112, item_y + 49, 82, 2)
                pygame.draw.rect(self.screen, (45, 83, 83), marker, border_radius=1)

        selected_module = self.modules_info[self.selected_index]
        accent = self.module_colors[self.selected_index]
        preview = pygame.Rect(568, 137, self.width - 616, 374)
        pygame.draw.rect(self.screen, (9, 31, 40), preview, border_radius=8)
        pygame.draw.rect(self.screen, (29, 70, 75), preview, 1, border_radius=8)

        preview_label = self.font_micro.render("FIELD NOTE   /   0" + str(self.selected_index + 1), True, accent)
        self.screen.blit(preview_label, (preview.x + 20, preview.y + 19))
        art_center = (preview.centerx, preview.y + 130)
        self._draw_module_art(self.selected_index, art_center, accent)

        preview_title = self.font_option.render(selected_module["title"].split(". ", 1)[-1], True, (247, 242, 225))
        self.screen.blit(preview_title, (preview.x + 20, preview.y + 220))
        self._draw_wrapped_text(
            selected_module["desc"],
            self.font_sub,
            (169, 200, 193),
            pygame.Rect(preview.x + 20, preview.y + 253, preview.width - 40, 75),
        )

        footer_y = self.height - 66
        self._draw_key_hint("UP / DOWN", "EXPLORAR", (53, footer_y))
        self._draw_key_hint("ENTER", "INICIAR", (250, footer_y), (255, 126, 92))
        self._draw_key_hint("ESC", "SALIR", (self.width - 171, footer_y))

    def _draw_module_art(self, module_index, center, accent):
        x, y = center
        phase = self.elapsed * 1.6

        if module_index == 0:
            pygame.draw.circle(self.screen, accent, (x, y), 27, 2)
            pygame.draw.circle(self.screen, (255, 184, 127), (x, y), 12)
            for ray in range(8):
                angle = ray * math.tau / 8
                start = (x + int(math.cos(angle) * 35), y + int(math.sin(angle) * 35))
                end = (x + int(math.cos(angle) * 47), y + int(math.sin(angle) * 47))
                pygame.draw.line(self.screen, accent, start, end, 2)
        elif module_index == 1:
            for tentacle in range(12):
                angle = tentacle * math.tau / 12
                sway = math.sin(phase + tentacle) * 5
                end = (x + int(math.cos(angle) * (43 + sway)), y + int(math.sin(angle) * (43 + sway)))
                pygame.draw.line(self.screen, accent, (x, y), end, 3)
            pygame.draw.circle(self.screen, (255, 177, 103), (x + 37, y - 4), 11)
            pygame.draw.line(self.screen, (247, 242, 225), (x + 36, y - 14), (x + 36, y + 6), 3)
        elif module_index == 2:
            nodes = [(x - 42, y + 15), (x - 17, y - 25), (x + 22, y - 17), (x + 44, y + 20), (x + 4, y + 34)]
            for start, end in ((0, 1), (1, 2), (2, 3), (0, 4), (4, 3), (1, 4)):
                pygame.draw.line(self.screen, (76, 139, 126), nodes[start], nodes[end], 2)
            for index, node in enumerate(nodes):
                pygame.draw.circle(self.screen, accent if index == 2 else (233, 194, 111), node, 7)
        else:
            molecule_nodes = [(x - 38, y - 8), (x, y - 30), (x + 37, y - 3), (x + 7, y + 32)]
            for start, end in ((0, 1), (1, 2), (2, 3), (3, 0)):
                pygame.draw.line(self.screen, (104, 153, 155), molecule_nodes[start], molecule_nodes[end], 2)
            for index, node in enumerate(molecule_nodes):
                pygame.draw.circle(self.screen, accent if index % 2 == 0 else (225, 227, 206), node, 9)

    def _draw_wrapped_text(self, text, font, color, bounds):
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            candidate = f"{current_line} {word}".strip()
            if current_line and font.size(candidate)[0] > bounds.width:
                lines.append(current_line)
                current_line = word
            else:
                current_line = candidate
        if current_line:
            lines.append(current_line)

        for index, line in enumerate(lines):
            if (index + 1) * font.get_linesize() > bounds.height:
                break
            self.screen.blit(font.render(line, True, color), (bounds.x, bounds.y + index * font.get_linesize()))

    def _draw_key_hint(self, key_label, action, position, key_color=(111, 166, 161)):
        key = self.font_micro.render(key_label, True, (247, 242, 225))
        label = self.font_micro.render(action, True, (139, 174, 169))
        self.screen.blit(key, position)
        self.screen.blit(label, (position[0] + key.get_width() + 8, position[1]))


if __name__ == "__main__":
    async def main():
        launcher = CoralOrangeLauncher()
        await launcher.run()

    asyncio.run(main())