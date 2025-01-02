import pygame


class ImageError(Exception):
    pass


class BackGround(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("background.gif").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = (0, 0)


if __name__ == "__main__":
    pygame.init()
    size = width, height = 800, 600
    pygame.display.set_caption("Reach the door")
    pygame.display.set_icon(pygame.image.load("icon.gif"))
    screen = pygame.display.set_mode(size)
    bg = BackGround()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(bg.image, bg.rect)

        pygame.display.flip()
    pygame.quit()
