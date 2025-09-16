import pygame
import pygame.gfxdraw
import math

class LightingEngine:
    def __init__(self, screen_width, screen_height, resolution_factor=1.0):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.resolution_factor = max(0.05, min(1.0, resolution_factor))

        self.light_width = int(screen_width * self.resolution_factor)
        self.light_height = int(screen_height * self.resolution_factor)

        self.light_surface = pygame.Surface((self.light_width, self.light_height), pygame.SRCALPHA)
        self.hull_mask = pygame.Surface((self.light_width, self.light_height), pygame.SRCALPHA)
        self.hull_mask.fill((255, 255, 255, 255))

        self.final_light_surface = pygame.Surface((screen_width, screen_height), flags=pygame.SRCALPHA | pygame.BLEND_PREMULTIPLIED)

        self.lights = []
        self.set_ambient_light((30, 30, 30, 255))

        self.light_cache = {}
        self.ambient_light = (30, 30, 30, 255)

    def set_resolution_factor(self, factor):
        self.resolution_factor = max(0.1, min(1.0, factor))
        new_width = int(self.screen_width * self.resolution_factor)
        new_height = int(self.screen_height * self.resolution_factor)

        if new_width != self.light_width or new_height != self.light_height:
            self.light_width = new_width
            self.light_height = new_height
            self.light_surface = pygame.Surface((self.light_width, self.light_height), pygame.SRCALPHA)
            self.hull_mask = pygame.Surface((self.light_width, self.light_height), pygame.SRCALPHA)
            self.hull_mask.fill((255, 255, 255, 255))

    def clear(self):
        self.lights = []
        self.hull_mask.fill((255, 255, 255, 255))

    def hull(self, rect):
        if isinstance(rect, pygame.Rect):
            scaled_rect = pygame.Rect(
                rect.x * self.resolution_factor,
                rect.y * self.resolution_factor,
                rect.width * self.resolution_factor,
                rect.height * self.resolution_factor
            )
        else:
            scaled_rect = (
                rect[0] * self.resolution_factor,
                rect[1] * self.resolution_factor,
                rect[2] * self.resolution_factor,
                rect[3] * self.resolution_factor
            )

        pygame.draw.rect(self.hull_mask, (0, 0, 0, 255), scaled_rect)

    def point_light(self, color, pos, radius, power=1.0):
        scaled_pos = (
            pos[0] * self.resolution_factor,
            pos[1] * self.resolution_factor
        )
        scaled_radius = radius * self.resolution_factor

        if len(color) == 3:
            color = color + (255,)

        r, g, b = color[:3]
        lightness = max(0.0001, 0.2126 * (r / 255) + 0.7152 * (g / 255) + 0.0722 * (b / 255))

        self.lights.append({
            'type': 'point',
            'color': color,
            'pos': scaled_pos,
            'radius': scaled_radius * 2,
            'power': max(0.0, min(1.0, power / lightness / 3))
        })

    def update(self, surface):
        # Fill the light surface with ambient light
        self.light_surface.fill(self.ambient_light)

        for light in self.lights:
            if light['type'] == 'point':
                self._render_point_light(light)

        # Apply the hull mask to the light surface
        self._apply_hull_mask()

        # Scale the light surface directly to the screen size
        pygame.transform.scale(
            self.light_surface,
            (self.screen_width, self.screen_height),
            self.final_light_surface
        )

        # Blit the final light surface onto the main surface
        surface.blit(self.final_light_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def _render_point_light(self, light):
        color = light['color']
        pos = light['pos']
        radius = light['radius']
        power = light['power']

        cache_key = (radius, color, power)

        if cache_key not in self.light_cache:
            diameter = int(radius * 2)
            light_surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)

            # Use gfxdraw for optimized circle drawing
            for r in range(int(radius), 0, -1):  # Draw from outer radius inward for gradient
                attenuation = 1.0 - (r / radius) ** 2
                attenuation *= power

                r_color = int(color[0] * attenuation)
                g_color = int(color[1] * attenuation)
                b_color = int(color[2] * attenuation)
                a_color = int(color[3] * attenuation)

                pygame.gfxdraw.aacircle(light_surf, int(radius), int(radius), r, (r_color, g_color, b_color, a_color))
                pygame.gfxdraw.filled_circle(light_surf, int(radius), int(radius), r, (r_color, g_color, b_color, a_color))

            self.light_cache[cache_key] = light_surf

        light_surf = self.light_cache[cache_key]
        light_pos = (pos[0] - radius, pos[1] - radius)
        self.light_surface.blit(light_surf, light_pos, special_flags=pygame.BLEND_ADD)

    def _apply_hull_mask(self):
        # Directly apply hull mask without copying
        self.light_surface.blit(self.hull_mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    def set_ambient_light(self, color):
        if len(color) == 3:
            color = color + (255,)
        if color[:3] == (0, 0, 0):
            color = (30, 30, 30, color[3])
        self.ambient_light = color