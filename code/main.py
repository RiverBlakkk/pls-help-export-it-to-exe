import contextlib
import pygame
import sys
from settings import *
from level import Level
from pygame import mixer
from button import Button

# Pygame setup
pygame.init()
pygame.mixer.init()
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
level = Level(r"../maps/test.tiemap.txt", SCREEN)

pygame.display.set_caption("MENU")

with contextlib.suppress(Exception):
	mixer.init()
	mixer.music.load(r'..\sound&music\music\music1.wav')
	mixer.music.play(-1)
	mixer.music.set_volume(0.7)

COLOR1 = (200, 168, 90)

BG = pygame.image.load('MainMenu/MainMenuBackgrond.png')



def get_font(size):  # Returns Press-Start-2P in the desired size
	return pygame.font.Font("MainMenu/font.ttf", size)


bg_images = [pygame.image.load(f'../graphics/bg/paralax{i}.png').convert_alpha() for i in range(1, 3)]
bg_width = bg_images[0].get_width()
bg_overlay = pygame.image.load('../graphics/bg/paralax3.png')

font = get_font(16)

ALLOW_FRAME_ADVANCE = False
# allow the usage of frame advance
# hint: ' and / are used for frame advance


def draw_bg(scroll: float):
	for j,i in enumerate(bg_images):
		SCREEN.blit(i, (-scroll * (1.5-0.5*j), 0))
		if -scroll * (1.5-0.5*j) + bg_width > SCREEN_WIDTH:
			SCREEN.blit(i, (-scroll * (1.5-0.5*j) - bg_width, 0))
		elif -scroll * (1.5-0.5*j) < 0:
			SCREEN.blit(i, (-scroll * (1.5-0.5*j) + bg_width, 0))
	SCREEN.blit(bg_overlay, (0, 0))


play_override = False  # allows for forcing the play loop end by injected code (like the editor)


def play():
	paused = False
	pause_buttons = [
		Button((SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 48), "--PAUSED--", get_font(32)),
		Button(
			(SCREEN_WIDTH//2, SCREEN_HEIGHT//2),"RESUME",get_font(32),
			True
		),
		Button((SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 48), "QUIT",  get_font(32), True)
	]
	while not play_override:
		pygame.display.set_caption("GAME")

		SCREEN.fill((0, 0, 0))
		draw_bg(-level.current_x)
		SCREEN.blit(bg_overlay, (0, 0))

		clicked = False
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
				paused = not paused
			if event.type == pygame.MOUSEBUTTONDOWN:
				clicked = True

		if not paused:
			level.run()
		else:
			level.draw()
			sum_rect = pygame.Rect(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, 0, 0)
			for button in pause_buttons:
				sum_rect = sum_rect.union(button.rect)
			sum_rect.inflate_ip(32, 32)
			pygame.draw.rect(SCREEN, (0, 0, 0), sum_rect)
			pygame.draw.rect(SCREEN, COLOR1, sum_rect, 16)
			for button in pause_buttons:
				button.update(SCREEN)

			m_pos = pygame.mouse.get_pos()

			if clicked:
				if pause_buttons[1].checkForInput(m_pos):
					paused = False
				elif pause_buttons[2].checkForInput(m_pos):
					return

		if ALLOW_FRAME_ADVANCE and pygame.key.get_pressed()[pygame.K_QUOTE]:
			# display some debug info
			player: Player = level.player.sprite  # type:ignore
			SCREEN.blit(font.render(
					f"{player.rect.center[0]-level.current_x} {player.rect.center[1]} {player.direction}",
					True, COLOR1
				), (0, 0)
			)
			print(f"{int(player.rect.center[0]-level.current_x)//TILE_SIZE:X} {int(SCREEN_HEIGHT-player.rect.center[1])//TILE_SIZE:X}")
			pygame.draw.rect(SCREEN, COLOR1, player.rect, 1)
			pygame.display.update()
			while pygame.key.get_pressed()[pygame.K_QUOTE]:
				pygame.event.pump()
			while not(pygame.key.get_pressed()[pygame.K_QUOTE]) \
					and not(pygame.key.get_pressed()[pygame.K_SLASH]):
				pygame.event.pump()

		pygame.display.update()
		clock.tick(60)


def credits():
	credit_text = {
		"@RiverBlak#7781": (375, 65),
		"@Lady Yami#3939": (375, 115),
		"@mikey0929#2441": (375, 165),
		"@MinekPo1#9801": (375, 215),
		"by BigExplosionTeam": (375, 15)
	}
	OPTIONS_BACK = Button(
		(375, 300), "BACK", get_font(75)
	)
	while True:
		pygame.display.set_caption("OPTIONS")

		OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

		SCREEN.fill("black")

		for text,pos in credit_text.items():
			text_surf = get_font(16).render(text, False, COLOR1)
			text_rect = text_surf.get_rect(center=pos)
			SCREEN.blit(text_surf, text_rect)

		# if OPTIONS_BACK:
		# 	SCREEN.fill("black")

		OPTIONS_BACK.update(SCREEN)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN and OPTIONS_BACK.checkForInput(
				OPTIONS_MOUSE_POS
			):
				return

		pygame.display.update()


def main_menu():
	PLAY_BUTTON = Button(
		(610, 50),
		"PLAY", get_font(32), True
	)

	OPTIONS_BUTTON = Button(
		(610, 132),
		"CREDITS", get_font(32), True
	)

	QUIT_BUTTON = Button(
		(610, 252),
		"QUIT", get_font(32), True
	)

	while True:

		SCREEN.blit(BG, (0, 0))

		MENU_MOUSE_POS = pygame.mouse.get_pos()

		# MENU_TEXT = get_font(100).render("_", True, (255, 255, 255))
		# MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

		# SCREEN.blit(MENU_TEXT, MENU_RECT)

		for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
			button.update(SCREEN)

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
					play()
				if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
					credits()
				if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
					pygame.quit()
					sys.exit()

		pygame.display.update()
		clock.tick(60)


if __name__ == "__main__":
	main_menu()
