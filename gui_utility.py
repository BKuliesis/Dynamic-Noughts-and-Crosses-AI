import pygame


class Button:
    def __init__(self, surface, graphic, graphic_hovering, pos):
        self.surface = surface
        self.graphic = self.graphic_not_hovering = graphic
        self.graphic_hovering = graphic_hovering
        self.rect = self.graphic.get_rect(topleft=pos)

    def check_if_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.left <= mouse_pos[0] <= self.rect.right and self.rect.top <= mouse_pos[1] <= self.rect.bottom:
            return True
        else:
            return False

    def display_button(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.left <= mouse_pos[0] <= self.rect.right and self.rect.top <= mouse_pos[1] <= self.rect.bottom:
            self.graphic = self.graphic_hovering
        else:
            self.graphic = self.graphic_not_hovering
        self.surface.blit(self.graphic, self.rect)

    def get_pos(self):
        return self.rect.topleft


class ScaledImageButton(Button):
    def __init__(self, surface, image, image_hovering, width, height, pos):
        image = pygame.transform.scale(image, (width, height))
        image_hovering = pygame.transform.scale(image_hovering, (width, height))
        Button.__init__(self, surface, image, image_hovering, pos)


class TextButton(Button):
    def __init__(self, surface, text, font, colour, colour_hovering, pos):
        text_not_hovering = font.render(text, True, colour)
        text_hovering = font.render(text, True, colour_hovering)
        Button.__init__(self, surface, text_not_hovering, text_hovering, pos)
