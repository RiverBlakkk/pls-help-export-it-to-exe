from typing import TYPE_CHECKING
import pygame
from particles import ParticleEffect
from support import import_folder
if TYPE_CHECKING:
	from level import Level


class Player(pygame.sprite.Sprite):
	rect: pygame.Rect

	def __init__(self, pos, surface, create_jump_particles):
		super().__init__()
		self.import_character_assets()
		self.frame_index = 0
		self.animation_speed = 0.15
		self.image = self.animations['idle'][self.frame_index]
		self.rect = self.image.get_rect(topleft=pos)

		# dust particles
		self.dust_run_particles = import_folder(
			'../graphics/character/dust_particles/run'
		)
		self.dust_frame_index = 0
		self.dust_animation_speed = 0.15
		self.display_surface = surface
		self.create_jump_particles = create_jump_particles

		# player movement
		self.direction = pygame.math.Vector2(0, 0)
		self.speed = 1
		self.gravity = 0.8
		self.jump_speed = -16

		# player status
		self.status = 'idle'
		self.facing_right = True
		self.on_ground = False
		self.on_ceiling = False
		self.on_left = False
		self.on_right = False

	def import_character_assets(self):
		character_path = '../graphics/character/'
		self.animations = {'idle': [], 'run': [], 'jump': [], 'fall': []}

		for animation in self.animations:
			full_path = character_path + animation
			self.animations[animation] = import_folder(full_path)

	def animate(self):
		animation = self.animations[self.status]

		# loop over frame index
		self.frame_index += self.animation_speed
		if self.frame_index >= len(animation):
			self.frame_index = 0

		image = animation[int(self.frame_index)]
		if self.facing_right:
			self.image = image
		else:
			flipped_image = pygame.transform.flip(image, True, False)
			self.image = flipped_image

		# set the rect
		# if self.on_ground and self.on_right:
		# 	self.rect = self.image.get_rect(
		# 		bottomright=self.rect.bottomright
		# 	)
		# elif self.on_ground and self.on_left:
		# 	self.rect = self.image.get_rect(
		# 		bottomleft=self.rect.bottomleft
		# 	)
		# elif self.on_ground:
		# 	self.rect = self.image.get_rect(
		# 		midbottom=self.rect.midbottom
		# 	)
		# elif self.on_ceiling and self.on_right:
		# 	self.rect = self.image.get_rect(
		# 		topright=self.rect.topright
		# 	)
		# elif self.on_ceiling and self.on_left:
		# 	self.rect = self.image.get_rect(
		# 		topleft=self.rect.topleft
		# 	)
		# elif self.on_ceiling:
		# 	self.rect = self.image.get_rect(
		# 		midtop=self.rect.midtop
		# 	)

		# self.rect = self.image.get_rect(
		# 	center=self.rect.center
		# )

	def run_dust_animation(self):
		if self.status == 'run' and self.on_ground:
			self.dust_frame_index += self.dust_animation_speed
			if self.dust_frame_index >= len(self.dust_run_particles):
				self.dust_frame_index = 0

			dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

			if self.facing_right:
				pos = self.rect.bottomleft - pygame.math.Vector2(6, 10)
				self.display_surface.blit(dust_particle, pos)
			else:
				pos = self.rect.bottomright - pygame.math.Vector2(6, 10)
				flipped_dust_particle = pygame.transform.flip(
					dust_particle, True, False)
				self.display_surface.blit(flipped_dust_particle, pos)

	def get_input(self, level: 'Level'):

		self.direction.y += self.gravity

		# validate movement (collision detection)
		old_on_ground = self.on_ground

		new_rect = self.rect.copy()

		new_rect.y += int(self.direction.y)
		pdy = self.direction.y
		if new_rect.collidelist(
			[i.rect for i in level.tiles if i.rect is not None]
		) != -1:
			# attempt to move to by one pixel to avoid
			# irritating one or two pixel gaps between tiles and the player
			self.direction.y = 2 if self.direction.y > 0 else -2
			new_rect.y = self.rect.y + self.direction.y
		if new_rect.collidelist(
			[i.rect for i in level.tiles if i.rect is not None]
		) != -1:
			self.direction.y = 1 if self.direction.y > 0 else -1
			new_rect.y = self.rect.y + self.direction.y
		if new_rect.collidelist(
			[i.rect for i in level.tiles if i.rect is not None]
		) != -1:
			# self.direction.y = max(pdy+1, -6) if self.direction.y < 0 else 0
			self.direction.y = 0  # no sticking
			"""
				to make hitting some jumps easier
				make the player stick to the ceiling a bit
				see this jump up the ledge in the test map:

				|  XX
				|   <─╮
				|  X  │
				| XX
				|XX

				without sticking this jump is pixel perfect

				Edit: tested it, and it doesn't do shit
				reverted to no strickting
			"""
			new_rect.y = self.rect.y

		new_rect.x += int(self.direction.x * self.speed)
		if new_rect.collidelist(
			[i.rect for i in level.tiles if i.rect is not None]
		) != -1:
			# attempt to move by one pixel to avoid
			# irritating one or two pixel gaps between tiles and the player
			self.direction.x = 1 if self.direction.x > 0 else -1
			new_rect.x = self.rect.x + self.direction.x
		if new_rect.collidelist(
			[i.rect for i in level.tiles if i.rect is not None]
		) != -1:
			self.direction.x = 0
			new_rect.x = self.rect.x

		self.rect = new_rect.copy()  # type:ignore
		new_rect.y += 1
		self.on_ground = new_rect.collidelist(
			[i.rect for i in level.tiles if i.rect is not None]
		) != -1

		keys = pygame.key.get_pressed()

		if keys[pygame.K_RIGHT]:
			self.direction.x += 2 if self.on_ground else 1.2
			self.facing_right = True
		elif keys[pygame.K_LEFT]:
			self.direction.x -= 2 if self.on_ground else 1.2
			self.facing_right = False

		self.direction.x *= 0.8 + 0.05 * (not self.on_ground)
		if abs(self.direction.x) < 0.5:
			self.direction.x = 0

		"""
			lets solve the equations to get the top speeds:

			on the ground:
				(x + 2) * 0.8 = x
				x * 0.8 + 1.6 = x
				1.6 = x * 0.2
				8 = x

			in the air:
				(x + 1.2) * 0.85 = x
				x * 0.85 + 1.02 = x
				0.85 = x * 0.15
				6.8 = x
		"""

		if keys[pygame.K_UP] and self.on_ground:
			self.direction.y = self.jump_speed
			self.create_jump_particles(self.rect.midbottom)

		if self.on_ground and not old_on_ground:
			if self.direction.x < 0:
				offset = pygame.math.Vector2(10, 15)
			elif self.direction.x > 0:
				offset = pygame.math.Vector2(-10, 15)
			else:
				offset = pygame.math.Vector2(0, 15)

			fall_dust_particle = ParticleEffect(
				self.rect.midbottom - offset, 'land')
			level.dust_sprite.add(fall_dust_particle)

	def get_status(self):
		if self.direction.y < 0:
			self.status = 'jump'
		elif self.direction.y > 1:
			self.status = 'fall'
		else:
			self.status = 'run' if self.direction.x != 0 else 'idle'

	def update(self,level: 'Level'):  # type:ignore
		self.get_input(level)
		self.get_status()
		self.animate()
		self.run_dust_animation()
