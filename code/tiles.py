import pygame
from pathlib import Path
import yaml
from settings import TILE_SIZE

COLOR = (200, 168, 90)

tiles = yaml.safe_load(open('../tiles.yml'))


tile_sprite_folder = Path(__file__).parent.parent / 'graphics/tiles'

sprite_cache: dict[str,pygame.surface.Surface] = {}


def load_sprite(spec: str,size: tuple[int,int]) -> pygame.surface.Surface:
	if spec in sprite_cache:
		return sprite_cache[spec]
	if ":" in spec:
		spec, index = spec.split(':')
		index = int(index)
		if spec in sprite_cache:
			sprite = sprite_cache[spec]
		else:
			sprite = pygame.image.load(
				(tile_sprite_folder / f'{spec}.png').open("rb")
			).convert_alpha()
			sprite_cache[spec] = sprite
		o = pygame.surface.Surface(size)
		o.blit(sprite, (0, 0), (index * size[0], 0, size[0], size[1]))
		spec = f"{spec}:{index}"
	else:
		o = pygame.image.load(
			(tile_sprite_folder / f'{spec}.png').open("rb")
		).convert_alpha()
	sprite_cache[spec] = o
	return o


class Tile(pygame.sprite.Sprite):
	rect: pygame.Rect

	def __init__(self, pos, type_id):
		super().__init__()
		size = (TILE_SIZE * tiles[type_id]["width"], TILE_SIZE * tiles[type_id]["height"])
		self.image = load_sprite(tiles[type_id]['sprite'], size)
		self.type_id = type_id
		self.rect = self.image.get_rect(topleft=pos)  # type:ignore

	def update(self, x_shift):
		self.rect.x += x_shift
