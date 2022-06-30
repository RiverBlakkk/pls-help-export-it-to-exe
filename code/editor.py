from player import Player
from tiles import Tile
from settings import SCREEN_HEIGHT, SCREEN_WIDTH
from settings import TILE_SIZE
from level import Level
from typing import Any, Callable, cast, overload
import pygame
from pathlib import Path
import string
from button import OButton, OMenu
import main

win = pygame.display.set_mode((800, 600), pygame.NOFRAME)

COLOR1 = (200, 168, 90)

font = pygame.font.Font('MainMenu/font.ttf', 16)

maps_folder = Path(__file__).parent.parent / 'maps'


def format_path(path: Path) -> str:
	return str(path.as_posix()[len(maps_folder.as_posix())+1:])


def select() -> Path:
	available = list(maps_folder.glob("*.tiemap*"))
	scroll = 0
	f_name = ""
	arrow_len = font.size("->")[0]
	was_non_click_frame = False
	while True:
		win.fill((0,0,0))

		filtered = list(filter(
				lambda v: str(format_path(v)).startswith(f_name),
				available
		))

		did_click = False

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					did_click = True
				if event.button == 4 and (scroll < 0):
					scroll += 10
				elif event.button == 5 and (scroll > (len(filtered) + 1)*20):
					scroll -= 10
			if event.type == pygame.KEYDOWN:
				if event.unicode in string.printable[:95]:
					f_name += event.unicode
				elif event.key == pygame.K_BACKSPACE:
					f_name = f_name[:-1]

		if was_non_click_frame:
			process_click = did_click
		else:
			process_click = False
			was_non_click_frame = not did_click

		path: Path
		i = -1
		for i,path in enumerate(
				filtered
			):
			win.blit(
				font.render(format_path(path), True, COLOR1),
				(arrow_len, i*20+scroll+22)
			)
		i += 1
		if "tiemap" in f_name.split("."):
			f_path = maps_folder / f_name
		else:
			f_path = maps_folder / f'{f_name}.tiemap'
		win.blit(
			font.render(f"New map ({format_path(f_path)})", True, COLOR1),
			(arrow_len, i*20+scroll+22)
		)

		# draw arrow to hovered map
		m_x, m_y = pygame.mouse.get_pos()
		if m_y > 20 and m_y < 580:
			index = (m_y - 20 - scroll) // 20
			if index < len(filtered) + 1:
				a_y = index * 20 + 22 + scroll
				win.blit(font.render("->", False, COLOR1), (0,a_y))
				if process_click:
					return f_path if index == len(filtered) else filtered[index]
		else:
			index = -1

		pygame.draw.rect(win, COLOR1, (0,0,800,20), 0)
		win.blit(font.render("select map:", False, (0,0,0)), (0,2))
		pygame.draw.rect(win, COLOR1, (0,580,800,20), 0)
		win.blit(font.render(f_name, False, (0,0,0)), (0,582))

		if f_name != "":
			text = font.render("clear", False, (0,0,0))
			rect = text.get_rect(right=795, top=582)
			win.blit(text, rect)
			if m_y > 580 and m_x > rect.left and process_click:
				f_name = ""

		# x button in top right
		text = font.render("x", False, (0,0,0))
		rect = text.get_rect(right=795, top=2)
		win.blit(text, rect)
		if m_y < 20 and m_x > rect.left and process_click:
			exit()

		pygame.display.update()


class EditorFileMenu(OMenu):
	class OpenButton(OButton):
		parent: 'EditorFileMenu'
		x = 0
		y = 0
		text = "open"
		index = 0
		invert = True

		def on_click(self):
			raise NotImplementedError(
				"This function must be created for an instance "
				"(hint: use the open_map decorator on EditorFileMenu)"
			)

	class SaveButton(OButton):
		parent: 'EditorFileMenu'
		x = 0
		y = 0
		text = "save"
		index = 1
		invert = True

		def on_click(self):
			raise NotImplementedError(
				"This function must be created for an instance "
				"(hint: use the save_map decorator on EditorFileMenu)"
			)

	class SaveAsButton(OButton):
		parent: 'EditorFileMenu'
		x = 0
		y = 0
		text = "save as"
		index = 2
		invert = True

		def on_click(self):
			raise NotImplementedError(
				"This function must be created for an instance "
				"(hint: use the save_as_map decorator on EditorFileMenu)"
			)

	class TestButton(OButton):
		parent: 'EditorFileMenu'
		x = 0
		y = 0
		text = "test"
		index = 3
		invert = True

		def on_click(self):
			raise NotImplementedError(
				"This function must be created for an instance "
				"(hint: use the test_map decorator on EditorFileMenu)"
			)

	def open_map(self, func):
		self.OpenButton.on_click = staticmethod(func)
		return func

	def save_map(self, func):
		self.SaveButton.on_click = staticmethod(func)
		return func

	def save_as_map(self, func):
		self.SaveAsButton.on_click = staticmethod(func)
		return func

	def test_map(self, func):
		self.TestButton.on_click = staticmethod(func)
		return func

	padding = 4
	text = "  file  "
	anchor = 'tl'  # type:ignore
	invert = True
	x = 0
	y = 0


class TestMenu(OMenu):

	class FlyToggleButton(OButton):
		parent: 'TestMenu'
		x = 0
		y = 0
		text = " [f]ly "
		index = 0
		invert = True
		active = False

		def on_click(self):
			self.active = not self.active
			self.update_text("X[f]ly " if self.active else " [f]ly ")

	x = 0
	y = 0
	text = "  test  "
	anchor = 'tl'  # type:ignore
	invert = True


class FakePygame:
	class ModuleProxy:
		path: tuple[str,...]

		def __init__(self, path: tuple[str], fake_pygame: 'FakePygame'):
			self.path = path
			self.fake_pygame = fake_pygame

		def __getattr__(self, __name: str) -> Any:
			if self.path + (__name,) in self.fake_pygame.overrides:
				return self.fake_pygame.overrides[self.path + (__name,)]

			m = pygame

			for path in self.path:
				m = getattr(m, path)

			o = getattr(m, __name)

			if isinstance(o, type(pygame)):
				return self.ModuleProxy((__name,), self)

			return o

	overrides: dict[tuple[str,...], Any]

	def __init__(self, overrides: dict[tuple[str,...], Any] | None = None):
		self.overrides = {} if overrides is None else overrides

	@overload
	def override(self,*path: str) -> Callable[[Callable], Callable]:
		...

	@overload
	def override(self,*path: str, v:Any) -> Any:
		...

	def override(self,*path: str, v:Any = None) -> Any:
		if v is not None:
			self.overrides[path] = v
			return v

		def decorator(func: Callable):
			self.overrides[path] = func
			return func
		return decorator

	def __getattr__(self, __name: str) -> Any:
		if (__name,) in self.overrides:
			return self.overrides[(__name,)]

		o = getattr(pygame, __name)
		if isinstance(o, type(pygame)):
			return self.ModuleProxy((__name,), self)

		return o


if __name__ == "__main__":
	file_menu = EditorFileMenu()
	test_menu = TestMenu()

	inner_game_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
	inner_game_screen.fill((255,0,0))
	fake_pygame = FakePygame()

	path: Path = None  # type:ignore
	level: Level = Level(None, inner_game_screen)

	@file_menu.open_map
	def open_map():
		global path, selected
		selected = None
		path = select()
		file_menu.open = False
		if path.exists():
			level.setup_level(path)
		else:
			level.setup_empty()
			level.player.add(Player(
				(0,SCREEN_HEIGHT-TILE_SIZE),
				win, level.create_jump_particles
			))

	@file_menu.save_map
	def save_map():
		global path
		if path is None:
			save_as(False)

		tiles = []
		cord_max = 0

		def convert_pos(pos: tuple[int,int]) -> tuple[int,int]:
			# reverse dx=x*TILE_SIZE, dy=SCREEN_HEIGHT-(y+1)*TILE_SIZE
			# x = dx/TILE_SIZE, y = (SCREEN_HEIGHT-dy)/TILE_SIZE
			return (pos[0] // TILE_SIZE, (SCREEN_HEIGHT - pos[1]) // TILE_SIZE - 1)

		for tile in level.tiles:
			rect = tile.rect
			if rect is None:
				continue
			rect = rect.copy()
			if (tid:=getattr(tile, "type_id", None)) == "":
				continue

			# update cord_max
			if rect.left > cord_max:
				cord_max = rect.left
			if rect.top > cord_max:
				cord_max = rect.top

			rect.x += level.current_x

			tiles.append((*convert_pos(rect.topleft), tid))

		# figure out size of position coordinates
		scale = 1
		while 256**scale < cord_max:
			scale += 1
		scale = int(scale)

		# write map
		with open(path, "wb") as f:
			# check what format to use
			if path.name.endswith(".tiemap.txt") or path.name.endswith(".txt"):
				format = "hex"
				written_bytes = 0

				def write(data:bytes):
					nonlocal written_bytes
					for b in data:
						f.write(f"{b:02x}".encode())
						# add spaces every 4 bytes and newline every 32 bytes
						if written_bytes % 32 == 31:
							f.write(b"\n")
						elif written_bytes % 4 == 3:
							f.write(b" ")
						written_bytes += 1
			else:
				format = "bin"

				# assume binary
				def write(data:bytes):
					f.write(data)

			def write_int(i:int, size:int = 1):
				write(i.to_bytes(size, "big"))

			# write header
			write(b'\x00')
			write_int(scale)

			# write player position
			p_rect = level.player.sprite.rect
			if p_rect is not None:
				write(b'\x02')
				c_pos = convert_pos(p_rect.topleft)
				write_int(c_pos[0], scale)
				write_int(c_pos[1], scale)

			# write tiles
			for x, y, tid in tiles:
				write(b'\x01')
				write_int(tid, 1)
				write_int(x, scale)
				write_int(y, scale)

			# write level transitions
			for data, name in level.level_transitions.items():
				write(b'\x03')
				write_int(data[0]//TILE_SIZE, scale)
				write_int(-(data[1] - SCREEN_HEIGHT) // TILE_SIZE , scale)
				write_int(data[2]//TILE_SIZE, scale)
				write_int(data[3]//TILE_SIZE, scale)
				write_int(len(name), 1)
				write(name.encode())

			# write death zones
			for zone in level.death_zones:
				write(b'\x04')
				write_int((zone[0])//TILE_SIZE, scale)
				write_int(-(zone[1] - SCREEN_HEIGHT) // TILE_SIZE , scale)
				write_int(zone[2]//TILE_SIZE, scale)
				write_int(zone[3]//TILE_SIZE, scale)

			# write a smiley face
			if format == "hex":
				# we can just print a smiley face,
				# since neither a colon or a bracket is used in hex
				f.write(b"\n:)")
			else:
				# make a comment
				f.write(b"\x00\x02:)")

	@file_menu.save_as_map
	def save_as(do_save:bool = True):
		global path
		path = select()
		file_menu.open = False
		if path.exists():
			# TODO: ask if overwrite
			pass
		if do_save:
			save_map()

	@file_menu.test_map
	def test_map():
		save_map()
		main.SCREEN = inner_game_screen
		main.level = Level(path, inner_game_screen)
		main.pygame = fake_pygame  # we do a little trolling
		main.play()
		file_menu.open = False

	@fake_pygame.override("display", "update")
	def update_inner_game_screen():
		win.blit(main.SCREEN, (0,test_menu.text_rect.bottom))
		pygame.draw.rect(win, COLOR1, (0,0,SCREEN_WIDTH,test_menu.text_rect.bottom), 0)
		test_menu.update(win)
		if test_menu.FlyToggleButton.active:
			p: Player = main.level.player.sprite  # type:ignore
			p.direction.x = 0
			p.direction.y = 0
			keys = pygame.key.get_pressed()
			if keys[pygame.K_UP]:
				p.rect.y -= 8
			if keys[pygame.K_DOWN]:
				p.rect.y += 8
			if keys[pygame.K_LEFT]:
				p.rect.x -= 8
			if keys[pygame.K_RIGHT]:
				p.rect.x += 8
		pygame.display.update()

	@fake_pygame.override("event", "get")
	def get_inner_game_screen_event():
		events = pygame.event.get()
		for event in events:
			if event.type == pygame.KEYDOWN and event.key == pygame.K_f:
				test_menu.FlyToggleButton.on_click()  # type:ignore
		return events

	open_map()

	selected: Tile | Player | None = None

	while True:
		level.world_shift = 0

		do_click = True
		click = False

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				exit()
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					exit()
				if event.key == pygame.K_DELETE and isinstance(selected, Tile):
					level.tiles.remove(selected)
					selected = None
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 1:
					click = True
				# scroll map
				elif event.button == 4:
					level.world_shift = TILE_SIZE
					level.current_x -= TILE_SIZE
				elif event.button == 5:
					level.world_shift = -TILE_SIZE
					level.current_x += TILE_SIZE

			elif event.type == pygame.MOUSEMOTION:
				# if event.rel[0] < 1 and event.rel[1] < 5:
				# 	continue
				# if event.rel[0] > -1 and event.rel[1] > -1:
				# 	continue
				do_click = False
				if selected is not None and event.buttons[0]:
					rel = list(event.pos)
					rel[0] += TILE_SIZE // 2
					rel[0] = rel[0] - (rel[0] - TILE_SIZE // 2) % TILE_SIZE + TILE_SIZE // 2
					rel[0] -= TILE_SIZE // 2

					rel[1] += TILE_SIZE // 2
					rel[1] = rel[1] - (rel[1] - TILE_SIZE // 2) % TILE_SIZE + TILE_SIZE // 2
					rel[1] -= TILE_SIZE // 2

					selected.rect.center = tuple(rel)  # type:ignore

		click = click and do_click
		keys = pygame.key.get_pressed()

		win.fill((0,0,0))

		level.tiles.update(level.world_shift)
		level.tiles.draw(win)

		for zone in level.death_zones:
			s = font.render("x", True, COLOR1)
			for x in range(zone.left, zone.right, TILE_SIZE):
				for y in range(zone.top, zone.bottom, TILE_SIZE):
					win.blit(s, (x,y))

		if level.player.sprite.image is not None \
				and level.player.sprite.rect is not None:
			rect = level.player.sprite.rect.copy()
			rect.x -= level.current_x
			win.blit(level.player.sprite.image,rect)

		if selected is not None:
			# draw a rectangle to show the selected tile
			rect = selected.rect.copy()
			if isinstance(selected,Player):
				rect.x -= level.current_x
			pygame.draw.rect(win, (0,0,0), rect, 1)
			rect.inflate_ip(-2,-2)
			pygame.draw.rect(win, COLOR1, rect, 1)
			rect.inflate_ip(-2,-2)
			pygame.draw.rect(win, (0,0,0), rect, 1)

		m_pos = pygame.mouse.get_pos()

		if not file_menu.check_throughput(m_pos):
			if click:
				for tile in level.tiles:
					rect = tile.rect  # type:ignore
					if rect is not None and rect.collidepoint(m_pos):
						selected = cast(Tile,tile)
						break
				else:
					rect = level.player.sprite.rect  # type:ignore
					if rect is not None and rect.collidepoint(m_pos):
						selected = cast(Player,level.player.sprite)
					else:
						selected = None
			if do_click and selected is None and pygame.mouse.get_pressed()[2]:
				for tile in level.tiles:
					rect = tile.rect  # type:ignore
					if rect is not None and rect.collidepoint(m_pos):
						break
				else:
					rect = level.player.sprite.rect  # type:ignore
					if not(rect is not None and rect.collidepoint(m_pos)):
						pos = list(m_pos)
						pos[0] = pos[0] - (pos[0]) % TILE_SIZE
						pos[1] = pos[1] - (pos[1]) % TILE_SIZE

						level.tiles.add(Tile(pos,0))
			if do_click and pygame.mouse.get_pressed()[2] and keys[pygame.K_DELETE]:
				for tile in level.tiles:
					rect = tile.rect  # type:ignore
					if rect is not None and rect.collidepoint(m_pos):
						level.tiles.remove(tile)
						break

		win.fill(COLOR1, (0,0,800,20))
		file_menu.update(win)

		pygame.display.update()
