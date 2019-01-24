import colors
import pygame
import pygame.gfxdraw
import numpy as np
import colorsys
import matplotlib as mpl
import matplotlib.path
#import shapely.geometry


def smooth(x):
    return np.log(1 + x * 6.3) / 2


class ChangingColorsAnimation:

    def __init__(self, polygon, start_hue=None, color_velocity=None, flash_with_volume=False, change_size_with_volume=False, which_volume=None):
        if color_velocity is None:
            color_velocity = 0.2 * np.random.rand()
        if start_hue is None:
            start_hue = np.random.rand()
        if which_volume is None:
            # TODO: Maybe change this dynamically from time to time.
            which_volume = np.random.choice(['all', 'low', 'high'])
        self.polygon = polygon
        self.hue = start_hue
        self.flash_with_volume = flash_with_volume
        self.change_size_with_volume = change_size_with_volume
        self.which_volume = which_volume
        self.color_velocity = color_velocity

        self.saturation = 1
        self.value = 1
        self.border_width = 0

    def update(self, elapsed_ms, volumes):
        self.hue += self.color_velocity * elapsed_ms / 1000
        if self.hue > 1:
            self.hue = 0
        if self.flash_with_volume:
            #self.value = volume
            #self.value = volumes[self.which_volume]
            self.value = smooth(volumes[self.which_volume])
            #self.value = max(self.value, 0.1)
        if self.change_size_with_volume:
            # TODO: Smooth this a bit.
            self.border_width = int((1-volume)*50)#int((1-volume)*10)#int(np.log(1 + (1 - volume) * 6.3) * 5)

    def draw(self, screen):
        color = 255 * np.array(colorsys.hsv_to_rgb(self.hue, self.saturation, self.value))
        #pygame.draw.polygon(screen, color, self.polygon)
        #pygame.draw.aalines(screen, color, True, self.polygon, False)
        pygame.gfxdraw.filled_polygon(screen, self.polygon, color)
        pygame.gfxdraw.aapolygon(screen, self.polygon, color)

        # TODO: Make this antialiased.
        if self.change_size_with_volume and self.border_width > 0:
            pygame.draw.polygon(screen, colors.black, self.polygon, self.border_width)


class MovingBarAnimation:

    def __init__(self, polygon, start_hue=None, color_velocity=None, which_volume=None, fill_below=False, bar_height=10):
        if color_velocity is None:
            color_velocity = 0.2 * np.random.rand()
        if start_hue is None:
            start_hue = np.random.rand()
        if which_volume is None:
            # TODO: Maybe change this dynamically from time to time.
            #which_volume = np.random.choice(['all', 'low', 'high'])
            which_volume = 'all'
        self.polygon = polygon
        #self.shapely_polygon = shapely.geometry.Polygon(polygon)
        self.hue = start_hue
        self.which_volume = which_volume
        self.color_velocity = color_velocity
        self.fill_below = fill_below

        self.saturation = 1
        self.value = 1
        #self.bar_y = 0
        #self.bar_left = 0
        #self.bar_right = 100
        self.bar_height = bar_height

        xs = np.array(polygon)[:, 0]
        ys = np.array(polygon)[:, 1]
        self.bbox_left = np.min(xs)
        self.bbox_right = np.max(xs)
        self.bbox_top = np.min(ys)
        self.bbox_bottom = np.max(ys)
        self.bbox_width = self.bbox_right - self.bbox_left
        self.bbox_height = self.bbox_bottom - self.bbox_top

    def update(self, elapsed_ms, volumes):
        # Change color.
        self.hue += self.color_velocity * elapsed_ms / 1000
        if self.hue > 1:
            self.hue = 0

        # Calculate bar position.
        self.relative_height = np.clip(volumes[self.which_volume], 0.001, 0.999)

        # Old code to draw line directly.
        #self.bar_y = self.bbox_top + np.clip(volumes[self.which_volume], 0.001, 0.999) * self.bbox_height
        #shapely_line = shapely.geometry.LineString([[self.min_x, self.bar_y], [self.max_x, self.bar_y]])
        #intersection_points = list(self.shapely_polygon.intersection(shapely_line).coords)
        #self.bar_left = intersection_points[0][0]
        #self.bar_right = intersection_points[1][0]

    def draw(self, screen):
        color = 255 * np.array(colorsys.hsv_to_rgb(self.hue, self.saturation, self.value))

        pygame.gfxdraw.filled_polygon(screen, self.polygon, color)
        pygame.gfxdraw.box(screen, [self.bbox_left, self.bbox_top, self.bbox_width, self.relative_height * self.bbox_height - self.bar_height], colors.black)
        if not self.fill_below:
            pygame.gfxdraw.box(screen, [self.bbox_left, self.bbox_top + self.relative_height * self.bbox_height, self.bbox_width, self.bbox_height - self.relative_height * self.bbox_height], colors.black)

        #pygame.gfxdraw.hline(screen, int(self.bar_left), int(self.bar_right), int(self.bar_y), color)
        pygame.gfxdraw.aapolygon(screen, self.polygon, color)



class FadeAnimation:

    def __init__(self, polygon, fade_time=1000, min_wait=500, max_wait=3000):
        self.polygon = polygon
        self.hue = np.random.rand()
        self.value = 0
        self.saturation = 1

        self.state = 'off'  # off, on, turning_on, turning_off
        self.fade_time = fade_time
        self.min_wait = min_wait
        self.max_wait = max_wait
        self.reset_wait()

    def reset_wait(self):
        self.wait = np.random.randint(self.min_wait, self.max_wait)

    def update(self, elapsed_ms, volumes):
        if self.state == 'on':
            self.wait -= elapsed_ms
            if self.wait < 0:
                self.state = 'turning_off'
        elif self.state == 'off':
            self.wait -= elapsed_ms
            if self.wait < 0:
                self.state = 'turning_on'
                self.hue = np.random.rand()  # choose new color
        elif self.state == 'turning_on':
            self.value += elapsed_ms / self.fade_time
            if self.value > 1:
                self.value = 1
                self.state = 'on'
                self.reset_wait()
        elif self.state == 'turning_off':
            self.value -= elapsed_ms / self.fade_time
            if self.value < 0:
                self.value = 0
                self.state = 'off'
                self.reset_wait()

    def draw(self, screen):
        pygame.draw.polygon(screen, 255 * np.array(colorsys.hsv_to_rgb(self.hue, self.saturation, self.value)), self.polygon)


class EdgeAnimation:

    def __init__(self, polygon, velocity=1, reverse=False):
        self.polygon = np.asarray(polygon)
        if reverse:
            self.polygon = np.roll(self.polygon[::-1], 1, axis=0)
        self.velocity = velocity
        self.reset()

    def reset(self):
        self.edge_polygon = self.polygon[0][None].astype(float)
        self.next_point_index = 1
        self.state = 'adding'  # adding, removing

    def get_direction_and_distance(self):
        vector_to_next_point = self.polygon[self.next_point_index] - self.edge_polygon[-1]
        distance = np.linalg.norm(vector_to_next_point)
        direction = vector_to_next_point / distance
        return direction, distance

    def add_point_to_edge(self, point):
        self.edge_polygon = np.append(self.edge_polygon, point[None], axis=0)

    def update(self, elapsed_ms, volumes):
        if self.state == 'adding':
            direction, distance = self.get_direction_and_distance()
            if self.velocity < distance:
                self.add_point_to_edge(self.edge_polygon[-1] + self.velocity * direction)
            else:  # passed a point in the polygon
                self.add_point_to_edge(self.polygon[self.next_point_index])
                if self.next_point_index == 0:  # polygon is complete, start to remove points from the edge
                    self.state = 'removing'
                else:
                    self.next_point_index += 1
                    if self.next_point_index == len(self.polygon):  # go to first point again in the end
                        self.next_point_index = 0
        elif self.state == 'removing':
            self.edge_polygon = self.edge_polygon[1:]
            if len(self.edge_polygon) == 0:
                self.reset()

    def draw(self, screen):
        if len(self.edge_polygon) > 2:
            pygame.gfxdraw.aapolygon(screen, self.edge_polygon.astype(int), colors.white)


class ShootingBallsAnimation:

    def __init__(self, polygon, control_velocity_with_volume=False, which_volume=None):
        if which_volume is None:
            # TODO: Maybe change this dynamically from time to time.
            which_volume = np.random.choice(['all', 'low', 'high'])
        self.polygon = polygon
        self.polygon_path = mpl.path.Path(self.polygon)  # this is a matplotlib object to check if a point is in the polygon
        self.ball_positions = []
        self.ball_velocities = []
        self.ball_hues = []
        self.center = np.mean(polygon, axis=0)
        self.which_volume = which_volume
        self.control_velocity_with_volume = control_velocity_with_volume

    def update(self, elapsed_ms, volumes):
        # Move existing balls (velocity depends on volume).
        if self.control_velocity_with_volume:
            base_velocity = elapsed_ms * max(0.2, volumes[self.which_volume])
        else:
            base_velocity = elapsed_ms * 0.5
        for i in range(len(self.ball_positions)):
            self.ball_positions[i] += self.ball_velocities[i] * base_velocity

        # Remove balls that are outside of the polygon.
        ball_in_polgyon = [self.polygon_path.contains_point(pos) for pos in self.ball_positions]
        self.ball_positions = [x for i, x in enumerate(self.ball_positions) if ball_in_polgyon[i]]
        self.ball_velocities = [x for i, x in enumerate(self.ball_velocities) if ball_in_polgyon[i]]
        self.ball_hues = [x for i, x in enumerate(self.ball_hues) if ball_in_polgyon[i]]

        # Create new balls (amount depends on volume).
        for i in range(np.random.poisson(8 * volumes[self.which_volume]**4)):
            self.ball_positions.append(self.center.copy())
            velocity = np.random.rand(2) - 0.5
            velocity = velocity / np.linalg.norm(velocity) * 0.2
            self.ball_velocities.append(velocity)
            self.ball_hues.append(np.random.rand())

        #if self.change_size_with_volume:
        #    print(np.log(1 + volume * 10) * 5)
        #    self.dot_radii[:] = np.log(1 + volume * 10) * 5
        #    self.dot_radii = self.dot_radii.clip(3, 10)

    def draw(self, screen):
        for pos, hue in zip(self.ball_positions, self.ball_hues):
            #pygame.gfxdraw.filled_circle(screen, int(pos[0]), int(pos[1]), 3, colors.white)
            pygame.gfxdraw.filled_circle(screen, int(pos[0]), int(pos[1]), 3, 255 * np.array(colorsys.hsv_to_rgb(hue, 1, 1)))
        pygame.gfxdraw.aapolygon(screen, self.polygon, colors.white)
