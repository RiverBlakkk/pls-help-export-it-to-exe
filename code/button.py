from typing import Literal, Type
import pygame


COLOR1 = (200, 168, 90)

pygame.font.init()
font = pygame.font.Font('MainMenu/font.ttf', 15)


class Button():
	def __init__(
			self, pos: tuple[int,int], text:str,
			font: pygame.font.Font, invert: bool = False,
			padding: int = 8
		):
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.font = font
		self.text_input = text
		self.text = self.font.render(
			self.text_input, True, (0,0,0) if invert else COLOR1
		)
		self.rect = self.text.get_rect()
		self.rect.size = (
			self.rect.width + padding,
			self.rect.height + padding
		)
		self.rect.center=(self.x_pos, self.y_pos)
		self.text_rect = self.text.get_rect(center=self.rect.center)
		self.invert = invert

	def update(self, screen):
		if self.invert:
			pygame.draw.rect(screen, COLOR1, self.rect)
		screen.blit(self.text, self.text_rect)

	def checkForInput(self, position):
		return self.rect.collidepoint(position)


class OButton:
	"""
		Allows for creating buttons with the class syntax.

		For example::

			class MyButton(OButton):
				x = 10
				y = 10
				text = "Hello"

				def on_click(self):
					print("Clicked!")

				def on_release(self):
					print("Released!")

				def on_mouse_over(self):
					print("Hovered!")

				def on_mouse_out(self):
					print("Un-hovered!")
	"""

	x: int
	y: int
	text: str
	__text: str
	font: pygame.font.Font = font
	invert: bool = False
	padding: int = 8
	anchor: Literal["tl","tc","tr","ml","mc","mr","bl","bc","br"] = "mc"
	width: int | None = None
	__was_mb1_down = False
	__was_hover = False

	@classmethod
	def __init_subclass__(cls, final=True) -> None:
		if final:
			for i in ["text", "x", "y"]:
				if not hasattr(cls, i):
					raise TypeError(f"{cls.__name__} must define {i}")
			cls.__text = cls.text
			cls.text = property(lambda self: self.__text)  # type:ignore

			@cls.text.setter  # type:ignore
			def _(_,__):
				raise AttributeError("Cannot set text, use update_text instead")

	def __init__(self):
		self.update_text(self.text)

	def update_text(self, text: str):
		self.__text = text
		self.text_img = self.font.render(
			text, True, (0,0,0) if self.invert else COLOR1
		)
		self.rect = self.text_img.get_rect()
		if self.width is not None:
			self.rect.width = max(
				self.width,
				self.rect.width + self.padding
			)
		else:
			self.rect.width += self.padding
		self.rect.height = self.rect.height + self.padding
		if self.anchor[0] == "t":
			self.rect.top = self.y
		elif self.anchor[0] == "b":
			self.rect.bottom = self.y
		elif self.anchor[0] == "m":
			self.rect.centery = self.y
		if self.anchor[1] == "l":
			self.rect.left = self.x
		elif self.anchor[1] == "r":
			self.rect.right = self.x
		elif self.anchor[1] == "c":
			self.rect.centerx = self.x
		self.text_rect = self.text_img.get_rect(center=self.rect.center)


	def on_click(self):
		pass

	def on_release(self):
		pass

	def on_mouse_over(self):
		pass

	def on_mouse_out(self):
		pass

	def update(self, screen, pos: tuple[int,int] | None = None):
		if self.invert:
			pygame.draw.rect(screen, COLOR1, self.rect)
		screen.blit(self.text_img, self.text_rect)
		if pos is None:
			pos = pygame.mouse.get_pos()
		if self.rect.collidepoint(pos):
			if not self.__was_hover:
				self.on_mouse_over()
				self.__was_hover = True
			if pygame.mouse.get_pressed()[0] and not self.__was_mb1_down:
				self.on_click()
			elif self.__was_mb1_down:
				self.on_release()
		elif self.__was_hover:
			self.on_mouse_out()
			self.__was_hover = False
		self.__was_mb1_down = pygame.mouse.get_pressed()[0]

	def check_throughput(self, pos: tuple[int,int]):
		return self.rect.collidepoint(pos)


class OMenu(OButton, final=False):
	"""
		Drop down menu, created using a class like interface
		Looks something like this when expanded::

			+------+
			| text |
			+------+
			| item |
			| item |
			| item |
			+------+

		Example usage::

			class MyMenu(OMenu):
				class OneItem(OButton):
					text = "item"
					x = 0
					y = 0
					index = 0

					def on_click(self):
						print("Clicked item 1!")

				class SecondItem(OButton):
					text = "item"
					x = 0
					y = 0
					index = 1

					def on_click(self):
						print("Clicked item 2!")

				class ThirdItem(OButton):
					text = "item"
					x = 0
					y = 0
					index = 2

					def on_click(self):
						print("Clicked item 3!")

				x = 10
				y = 10
				text = "Hello"
				font = pygame.font.SysFont("Arial", 20)
	"""

	__items: list[Type[OButton]]
	items: list[OButton]
	open: bool

	@classmethod
	def __init_subclass__(cls) -> None:
		super().__init_subclass__()

		cls.__items = []
		for _,v in cls.__dict__.items():
			if not isinstance(v,type):
				continue
			if issubclass(v, OButton):
				if not hasattr(v,"index"):
					raise TypeError(f"{v.__name__} must define index")
				cls.__items.append(v)
				if cls.width is not None and v.width is not None:
					cls.width = max(cls.width, v.width)
		cls.__items.sort(key=lambda x: x.index)  # type:ignore

	def __init__(self):
		super().__init__()

		self.items = [
			i() for i in self.__items
		]
		for i in self.items:
			i.parent = self  # type:ignore
		# allow for using the class name to address the item
		self.__dict__.update({
			i.__class__.__name__: i for i in self.items
		})
		self.open = False

		self.open = False

	def on_click(self):
		self.open = not self.open

	def update(self, screen, pos: tuple[int,int] | None = None):
		super().update(screen, pos)

		if self.open:
			y = self.rect.bottom
			for i in self.items:
				i.rect.top = y
				i.rect.w = self.rect.w
				i.rect.centerx = self.rect.centerx
				i.text_rect.center = i.rect.center
				i.update(screen, pos)
				y = i.rect.bottom

	def check_throughput(self, pos: tuple[int,int]):
		if self.open:
			for i in self.items:
				if i.check_throughput(pos):
					return True
		return super().check_throughput(pos)
