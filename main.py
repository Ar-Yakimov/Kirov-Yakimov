import pygame
from time import sleep


class ImageError(Exception):
    pass


class BackGround(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("background.gif").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = (0, 0)


class Character(pygame.sprite.Sprite):
    images = [pygame.image.load(rf"character\sprite_{i}.gif") for i in range(1, 4)]
    size = (50, 100)

    def __init__(self, pos):
        super().__init__()
        self.rect = pygame.Rect(pos, self.size)
        self.img_r = self.images
        self.img_l = [pygame.transform.flip(image, True, False) for image in self.images]
        self.index = 0
        self.image = self.images[self.index]
        self.velocity = pygame.math.Vector2(0, 0)
        self.anim_time = 0.1
        self.current_time = 0

    def update_time_dependent(self, dt):
        sleep(0.08)

        if self.velocity.x > 0:
            self.images = self.img_r
        elif self.velocity.x < 0:
            self.images = self.img_l

        self.current_time += dt
        if self.current_time >= self.anim_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        self.rect.move_ip(*self.velocity)

    def update(self, dt):
        self.update_time_dependent(dt)


if __name__ == "__main__":
    pygame.init()
    size = width, height = 800, 600
    FPS = 60
    pygame.display.set_caption("Reach the door")
    pygame.display.set_icon(pygame.image.load("icon.gif"))
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    bg = BackGround()
    player = Character([20, 500])

    all_objs = pygame.sprite.Group(player)

    running = True
    while running:

        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.velocity.x = 15
                elif event.key == pygame.K_LEFT:
                    player.velocity.x = -15
                elif event.key == pygame.K_DOWN:
                    player.velocity.y = 15
                elif event.key == pygame.K_UP:
                    player.velocity.y = -15
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    player.velocity.x = 0
                elif event.key == pygame.K_DOWN or event.key == pygame.K_UP:
                    player.velocity.y = 0

        all_objs.update(dt)
        screen.blit(bg.image, bg.rect)
        all_objs.draw(screen)

        pygame.display.update()
    pygame.quit()
