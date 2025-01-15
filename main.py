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
    win = None
    images = [pygame.image.load(rf"character/sprite_{i}.gif") for i in range(1, 4)]
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
        self.gravity = 0.6
        self.jump_speed = -28
        self.on_ground = True
        self.show = True

    def update_time_dependent(self, dt):
        sleep(0.06)
        if self.velocity.x > 0:
            self.images = self.img_r
        elif self.velocity.x < 0:
            self.images = self.img_l

        if not self.on_ground:
            self.velocity.y += self.gravity

        self.current_time += dt
        if self.current_time >= self.anim_time:
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def update(self, dt):
        if self.show:
            self.update_time_dependent(dt)
            if not self.on_ground:
                self.velocity.y += self.gravity

            old_rect = self.rect.copy()
            self.rect.move_ip(*self.velocity)

            if self.rect.left < 0:
                self.rect.left = 0
            elif self.rect.right > 800:
                self.rect.right = 800

            if self.rect.top < 0:
                self.rect.top = 0
            elif self.rect.bottom >= 600:
                self.rect.bottom = 600
                self.on_ground = True
                self.velocity.y = 0

            for obj in all_objs:
                if isinstance(obj, Platform):
                    if old_rect.colliderect(obj.rect) and not self.rect.colliderect(obj.rect):
                        if self.velocity.y > 0 and old_rect.bottom <= obj.rect.top + abs(self.velocity.y):
                            self.rect.bottom = obj.rect.top
                            self.on_ground = True
                            self.velocity.y = 0
                        elif self.velocity.y < 0 and obj.rect.top <= old_rect.top <= obj.rect.bottom:
                            self.rect.top = obj.rect.bottom
                            self.velocity.y = 0

                        if old_rect.right > obj.rect.left > old_rect.left:
                            self.rect.right = obj.rect.left
                            self.velocity.x = 0
                        elif old_rect.left < obj.rect.right < old_rect.right:
                            self.rect.left = obj.rect.right
                            self.velocity.x = 0

            if not self.on_ground and self.rect.bottom < 600:
                self.velocity.y += self.gravity
        else:
            self.image = pygame.image.load("player_faded.gif")

    def jump(self):
        if self.on_ground:
            self.velocity.y = self.jump_speed
            self.on_ground = False


class Platform(pygame.sprite.Sprite):
    images = {
        "big": pygame.image.load(r"platform/platform_big.gif"),
        "medium": pygame.image.load(r"platform/platform_medium.gif"),
        "small": pygame.image.load(r"platform/platform_small.gif")
    }

    sizes = {
        "big": (158, 40),
        "medium": (113, 40),
        "small": (75, 40)
    }

    def __init__(self, kind: str, pos: tuple[int, int]):
        super().__init__()
        self.image = self.images[kind]
        self.size = self.sizes[kind]
        self.rect = pygame.Rect(pos, self.size)

class Door(pygame.sprite.Sprite):
    images = {
        "close": pygame.image.load(r"door/door_close.gif"),
        "open": pygame.image.load(r"door/door_open.gif")
    }
    size = (65, 115)

    def __init__(self, *pos):
        super().__init__()
        self.rect = pygame.Rect(pos, self.size)
        self.image = self.images["close"]
        self.is_open = False
        self.open_time = 0
        self.door_open_duration = 400

    def update(self, dt):
        if self.rect.colliderect(player.rect) and player.show and not self.is_open:
            player.show = False
            player.win = True
            self.is_open = True
            self.image = self.images["open"]
            self.open_time = pygame.time.get_ticks()

        if self.is_open and (pygame.time.get_ticks() - self.open_time > self.door_open_duration):
            self.is_open = False
            self.image = self.images["close"]

class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos, size):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill((241, 8, 150))
        self.rect = self.image.get_rect(topleft=pos)
        self.font = pygame.font.Font(None, 25)
        self.text = text

    def draw(self):
        pygame.draw.rect(screen, (241, 8, 150), self.rect)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


if __name__ == "__main__":
    pygame.init()
    size = width, height = 800, 600
    FPS = 60
    pygame.display.set_caption("Reach the door")
    pygame.display.set_icon(pygame.image.load("icon.gif"))
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()
    bg = BackGround()
    player = Character([20, 440])

    platform_1 = Platform("big", (10, 540))
    platform_2 = Platform("medium", (300, 485))
    platform_3 = Platform("small", (500, 380))
    platform_4 = Platform("medium", (650, 280))
    door = Door(680, 165)

    all_objs = pygame.sprite.Group(player,
                                   platform_1,
                                   platform_2,
                                   platform_3,
                                   platform_4,
                                   door)

    font = pygame.font.Font(None, 50)

    NEW_GAME = True

    running = True
    while running:
        dt = clock.tick(FPS) / 1000
        screen.blit(bg.image, bg.rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.velocity.x = 15
                elif event.key == pygame.K_LEFT:
                    player.velocity.x = -15
                elif event.key == pygame.K_UP:
                    player.jump()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    player.velocity.x = 0

            if NEW_GAME and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                btn_in_pos = (300, 250)
                btn_in_size = (150, 100)
                btn_in = Button("Начать", btn_in_pos, btn_in_size)
                if btn_in.is_clicked(event.pos):
                    NEW_GAME = False

        if NEW_GAME:
            text = font.render("Нажмите, чтобы начать игру", True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 - 85))
            btn_in = Button("Начать", (275, 250), (250, 100))
            btn_in.draw()
        else:
            all_objs.update(dt)
            all_objs.draw(screen)

            player.on_ground = False
            for obj in all_objs:
                if isinstance(obj, Platform):
                    if player.rect.colliderect(obj.rect):
                        if player.velocity.y > 0 and player.rect.bottom <= obj.rect.top + abs(player.velocity.y):
                            player.rect.bottom = obj.rect.top
                            player.on_ground = True
                            player.velocity.y = 0
                        elif player.velocity.y < 0 and obj.rect.top <= player.rect.top <= obj.rect.bottom:
                            player.rect.top = obj.rect.bottom
                            player.velocity.y = 0

                        if player.rect.right > obj.rect.left > player.rect.left:
                            player.rect.right = obj.rect.left
                            player.velocity.x = 0
                        elif player.rect.left < obj.rect.right < player.rect.right:
                            player.rect.left = obj.rect.right
                            player.velocity.x = 0

            if not player.on_ground and player.rect.bottom < height:
                player.velocity.y += player.gravity

        pygame.display.update()

    pygame.quit()

