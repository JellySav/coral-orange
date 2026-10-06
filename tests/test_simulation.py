import os
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from threading import Thread
from urllib.request import urlopen

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

from core.hydro_log import HydroLog
from core.reef_organism import ReefOrganism
from main import CoralOrangeLauncher
from modules.acidification_lab import AcidificationLabModule
from modules.bleaching_alert import BleachingAlertModule
from modules.clown_symbiosis import ClownSymbiosisModule
from modules.trophic_balance import Creature, TrophicBalanceModule
from serve_game import CDN_ROUTE, GameRequestHandler, WEB_ROOT, rewrite_html


class SimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((900, 600))

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def test_launcher_dispatches_each_minigame(self):
        launcher = CoralOrangeLauncher()
        expected_modules = (
            BleachingAlertModule,
            ClownSymbiosisModule,
            TrophicBalanceModule,
            AcidificationLabModule,
        )

        for index, module_type in enumerate(expected_modules):
            launcher.selected_index = index
            launcher._launch_selected_module()
            self.assertIsInstance(launcher.active_module, module_type)
            self.assertTrue(launcher.show_intro)

    def test_web_page_uses_same_origin_for_runtime_assets(self):
        page = (
            b'<script src="https://pygame-web.github.io/cdn/0.9.3/pythons.js"></script>'
            b'<script src="https://pygame-web.github.io/cdn/0.9.3//browserfs.min.js"></script>'
        )

        rewritten = rewrite_html(page)

        self.assertIn(CDN_ROUTE.encode() + b"0.9.3/pythons.js", rewritten)
        self.assertNotIn(b"pygame-web.github.io", rewritten)
        self.assertNotIn(b"browserfs.min.js", rewritten)

    def test_web_server_rewrites_the_root_page(self):
        handler = partial(GameRequestHandler, directory=str(WEB_ROOT))
        server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with urlopen(f"http://127.0.0.1:{server.server_port}/") as response:
                page = response.read()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.headers.get("Cross-Origin-Embedder-Policy"), "require-corp")
                self.assertIn(b"/__runtime_cdn__/0.9.3/pythons.js", page)
                self.assertNotIn(b"https://pygame-web.github.io/cdn/", page)
                self.assertNotIn(b"browserfs.min.js", page)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_simulation_rates_are_stable_at_30_and_60_fps(self):
        coral_60 = ReefOrganism("a", "coral", 0, 0, "CORAL", (255, 127, 80))
        coral_30 = ReefOrganism("b", "coral", 0, 0, "CORAL", (255, 127, 80))
        chemistry_60 = AcidificationLabModule()
        chemistry_30 = AcidificationLabModule()

        for _ in range(60):
            coral_60.update_health(30, 8.1, 1 / 60)
            chemistry_60.update(1 / 60)
        for _ in range(30):
            coral_30.update_health(30, 8.1, 1 / 30)
            chemistry_30.update(1 / 30)

        self.assertAlmostEqual(coral_60.health, coral_30.health)
        self.assertAlmostEqual(chemistry_60.co2_ppm, chemistry_30.co2_ppm, places=9)
        self.assertAlmostEqual(chemistry_60.ph, chemistry_30.ph, places=4)

    def test_hydro_log_keeps_samples_one_second_apart(self):
        hydro_log = HydroLog(0, 0, 280, 140)

        for _ in range(120):
            hydro_log.push_log(26.5, 8.1, "estable", 1 / 60)

        self.assertEqual(len(hydro_log.logs), 2)

    def test_clownfish_movement_is_frame_rate_independent(self):
        class RightKeyState:
            def __getitem__(self, key):
                return key in (pygame.K_RIGHT, pygame.K_d)

        original_get_pressed = pygame.key.get_pressed
        pygame.key.get_pressed = lambda: RightKeyState()
        try:
            game_60 = ClownSymbiosisModule()
            game_30 = ClownSymbiosisModule()
            for _ in range(60):
                game_60.update(1 / 60)
            for _ in range(30):
                game_30.update(1 / 30)
        finally:
            pygame.key.get_pressed = original_get_pressed

        self.assertAlmostEqual(game_60.fish_x, game_30.fish_x)

    def test_creature_movement_is_frame_rate_independent(self):
        creature_60 = Creature("HERBIVORE", 400, 300)
        creature_30 = Creature("HERBIVORE", 400, 300)
        creature_60.vx = creature_30.vx = 1.0
        creature_60.vy = creature_30.vy = 0.0

        for _ in range(60):
            creature_60.move((0, 900), (0, 600), 1 / 60)
        for _ in range(30):
            creature_30.move((0, 900), (0, 600), 1 / 30)

        self.assertAlmostEqual(creature_60.x, creature_30.x)


if __name__ == "__main__":
    unittest.main()