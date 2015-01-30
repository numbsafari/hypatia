# engine/game.py
# Lillian Lemmer <lillian.lynn.lemmer@gmail.com>
#
# This module is part of Hypatia Engine and is released under the
# MIT License: http://opensource.org/licenses/MIT

"""Why stuff is drawn; logic flow for the game.

Glues various modules/game omponents together with behaviors defined
in methods belonging to Game().

Note:
  I have not decided firmly on the approach to take. Expect heavy
  changes in the future.

  Sorry for the poor documentation, I have not devised an actual
  architecture for this particular module. I have not decided
  firmly on the approach to take. Here, I'm sort of imitating
  Flask's app.

"""

import sys

import pygame
from pygame.locals import *

import constants
import render

__author__ = "Lillian Lemmer"
__copyright__ = "Copyright 2015, Lillian Lemmer"
__credits__ = ["Lillian Lemmer"]
__license__ = "MIT"
__maintainer__ = "Lillian Lemmer"
__email__ = "lillian.lynn.lemmer@gmail.com"
__status__ = "Development"


class Game(object):
    """One simple object for referencing all of the game's features.

    Attributes:
      human_player:
      tilemap:
      viewport:
      items:
      screen:

    """

    def __init__(self, tilemap, viewport, human_player, items=None):
        self.human_player = human_player
        self.tilemap = tilemap
        self.viewport = viewport
        self.items = items or []
        self.screen = render.Screen()

    def init(self):
        self.tilemap.convert_layer_images()
        self.human_player.init()

    def item_check(self):
        ungot_items = []

        for item in self.items:

            if item.rect.colliderect(self.human_player.rect):
                # should this be player.pickup item? or both?
                item.pickup(self.human_player)
            else:
                ungot_items.append(item)

        self.items = ungot_items

    def handle_input(self):

        for event in pygame.event.get():

            if event.type == KEYUP:
                self.human_player.action = constants.Stand

        keys = pygame.key.get_pressed()

        if keys[K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if keys[K_UP]:
            self.move_player(constants.Up)

        if keys[K_RIGHT]:
            self.move_player(constants.Right)

        if keys[K_DOWN]:
            self.move_player(constants.Down)

        if keys[K_LEFT]:
            self.move_player(constants.Left)

    def move_player(self, direction):
        """Modify human player's positional data legally (check
        for collisions).

        Note:
          Will round down to nearest probable step
          if full step is impassable.

        Args:
          direction (constants.Direction): may be one of: up, right, down, left
          tilemap (tiles.TileMap): tilemap for reference, so we can
            avoid walking into water and such.

        """

        player = self.human_player
        player.direction = direction
        planned_movement_in_pixels = player.speed_in_pixels_per_second
        adj_speed = self.screen.time_elapsed_milliseconds / 1000.0
        iter_pixels = max([1, int(planned_movement_in_pixels)])

        # test a series of positions
        for pixels in range(iter_pixels, 0, -1):
            # create a rectangle at the new position
            new_topleft_x, new_topleft_y = player.topleft_float

            if pixels == 2:
                adj_speed = 1

            if direction == constants.Up:
                new_topleft_y -= pixels * adj_speed
            elif direction == constants.Right:
                new_topleft_x += pixels * adj_speed
            elif direction == constants.Down:
                new_topleft_y += pixels * adj_speed
            elif direction == constants.Left:
                new_topleft_x -= pixels * adj_speed

            destination_rect = pygame.Rect((new_topleft_x, new_topleft_y),
                                           self.human_player.size)
            collision_rect = player.rect.union(destination_rect)

            if collision_rect.collidelist(self.tilemap.impassability) == -1:
                # we're done, we can move!
                new_topleft = (new_topleft_x, new_topleft_y)
                player.action = constants.Walk
                animation = player.current_animation()
                player.size = animation.get_max_size()
                player.rect = destination_rect
                player.topleft_float = new_topleft

                return True

        # never found an applicable destination
        player.action = constants.Stand

        return False

    def blit_all(self):
        """Drawing behavior for game objects.

        """

        self.viewport.pan_for_entity(self.human_player)
        self.viewport.blit(self.tilemap.layer_images[0])

        for item in self.items:
            item.blit(self.viewport.surface, self.viewport.rect.topleft)

        self.human_player.blit(
                               self.viewport.surface,
                               self.viewport.rect.topleft
                              )

        for layer in self.tilemap.layer_images[1:]:
            self.viewport.blit(layer)

