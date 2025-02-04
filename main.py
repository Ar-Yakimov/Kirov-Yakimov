import os
import random
import re
import sys
from time import sleep

import pygame


#  Импорт модулей


class LVL_parser:
    root_point = r"environments/"

    def __init__(self):
        self.data = [self.unpack(self.root_point + file) for file in os.listdir(self.root_point)]

    @staticmethod
    def unpack(file):
        with open(file=file, mode="r") as source:
            raw = source.read()
            char = list(map(int, re.search(r"CHAR\s\|\s\{([\d;]+)\}", raw).group(1).split(';')))
            door = list(map(int, re.search(r"DOOR\s\|\s\{([\d;]+)\}", raw).group(1).split(';')))
            blocks = [(m[0].lower(), tuple(map(int, m[1].split(';')))) for m in
                      re.findall(r"(\w+)\s\|\s\{([\d;]+)\}", raw[raw.index("BLOCKS"):])]
            group = pygame.sprite.Group(Character(char), Door(*door), *(Platform(size, pos) for size, pos in blocks))
        return group

    def __iter__(self):
        yield from self.data

    def __len__(self):
        return len(self.data)

    def __getitem__(self, item):
        try:
            return self.data[item]
        except IndexError:
            raise FileNotFoundError(f"File {self.root_point + f"lvl_{item + 1}.lvl"} doesn`t exist!")


class ParticleSystem(pygame.sprite.Sprite):
    """Источник частиц"""
    images = [pygame.image.load(r"sprites/particle.gif")]
    for scale in (2, 4, 6):
        images.append(pygame.transform.scale(images[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        """Инициализация"""
        super().__init__()
        self.image = random.choice(self.images)
        self.rect = self.image.get_rect()

        self.velocity = pygame.math.Vector2(dx, dy)
        self.rect.x, self.rect.y = pos

        self.gravity = player.gravity

    def update(self):
        self.velocity.y += self.gravity
        self.rect.move_ip(*self.velocity)
        if not self.rect.colliderect((0, 0, width, height)):
            self.kill()


class BackGround(pygame.sprite.Sprite):
    def __init__(self):
        """Создание заднего фона"""
        super().__init__()
        self.image = pygame.image.load("sprites/background.gif").convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = (0, 0)


class Character(pygame.sprite.Sprite):
    """Спрайт игрока"""
    images = [pygame.image.load(rf"sprites/character/sprite_{i}.gif") for i in range(1, 4)]
    size = (50, 100)

    def __init__(self, pos):
        """Инициализация"""
        super().__init__()
        self.rect = pygame.Rect(pos, self.size)
        self.start = pos  # сохраняем начальную позицию
        self.img_r = self.images
        self.img_l = [pygame.transform.flip(image, True, False) for image in self.images]  # отражаем картинки
        self.index = 0  # индекс текущего кадра
        self.image = self.images[self.index]
        self.velocity = pygame.math.Vector2(0, 0)  # создаём вектор скорости
        self.anim_time = 0.1  # время анимации
        self.current_time = 0  # текущее время
        self.gravity = 0.6  # гравитация
        self.jump_speed = -28  # высота прыжка
        self.on_ground = True  # нахождение в полёте
        self.show = True  # нужно ли показывать персонажа
        self.win = None  # флаг победы
        self.particles = pygame.sprite.Group()

    def update_time_dependent(self, dt):
        sleep(0.06)  # задержка анимации
        if self.velocity.x > 0:
            self.images = self.img_r  # картинки, если идти вправо
        elif self.velocity.x < 0:
            self.images = self.img_l  # картинки, если идти влево

        if not self.on_ground:  # прыжок, если не на земле
            self.velocity.y += self.gravity

        self.current_time += dt  # обновляем текущее время
        if self.current_time >= self.anim_time:  # обновляем кадр
            self.current_time = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

    def create_particle(self, pos, count):
        for _ in range(count):
            particle = ParticleSystem(pos, *[random.choice(range(-5, 6)) for _ in range(2)])
            self.particles.add(particle)

    def update(self, dt):
        if self.show:  # если спрайт виден
            self.update_time_dependent(dt)
            self.particles.update()
            if not self.on_ground:  # применяем падение
                self.velocity.y += self.gravity

            if abs(self.velocity.x) != 0:
                self.create_particle([self.rect.centerx, self.rect.bottom], 10)

            old_rect = self.rect.copy()  # передвигаем спрайт
            self.rect.move_ip(*self.velocity)

            if self.rect.left < 0:  # проверяем коллизии с границей экрана
                self.rect.left = 0
            elif self.rect.right > 800:
                self.rect.right = 800

            if self.rect.top < 0:
                self.rect.top = 0
            elif self.rect.bottom >= 600:
                self.win = False
                self.show = False

            for obj in all_objs:  # проверяем коллизии с другими обьектами
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

            if not self.on_ground and self.rect.bottom < 600:  # применяем падение
                self.velocity.y += self.gravity
        else:
            self.kill()  # прячем игрока

    def jump(self):
        if self.on_ground:  # применяем отрицательную вертикальную скорость
            self.velocity.y = self.jump_speed
            self.on_ground = False

    def reset(self):
        """восстанавливаем значения"""
        self.win = None
        self.show = True
        self.on_ground = True
        self.rect = pygame.Rect(self.start, self.size)


class Platform(pygame.sprite.Sprite):
    images = {
        "big": pygame.image.load(r"sprites/platform/platform_big.gif"),
        "medium": pygame.image.load(r"sprites/platform/platform_medium.gif"),
        "small": pygame.image.load(r"sprites/platform/platform_small.gif")
    }  # все картинки

    sizes = {
        "big": (158, 40),
        "medium": (113, 40),
        "small": (75, 40)
    }  # размерность

    def __init__(self, kind: str, pos: tuple[int, int]):
        """инициализация платформы"""
        super().__init__()
        self.image = self.images[kind]
        self.size = self.sizes[kind]
        self.rect = pygame.Rect(pos, self.size)


class Door(pygame.sprite.Sprite):
    images = {
        "close": pygame.image.load(r"sprites/door/door_close.gif"),
        "open": pygame.image.load(r"sprites/door/door_open.gif")
    }  # картинки разных состояний
    size = (65, 115)

    def __init__(self, *pos):
        """создание необходимых атрибутов"""
        super().__init__()
        self.rect = pygame.Rect(pos, self.size)
        self.image = self.images["close"]
        self.is_open = False
        self.open_time = 0
        self.door_open_duration = 400

    def update(self, dt):
        if self.rect.colliderect(player.rect) and player.show and not self.is_open:  # если игрок дошёл до двери
            player.show = False
            player.win = True
            self.is_open = True
            self.image = self.images["open"]
            self.open_time = pygame.time.get_ticks()

        if self.is_open and (pygame.time.get_ticks() - self.open_time > self.door_open_duration):  # если пора закрытся
            self.is_open = False
            self.image = self.images["close"]


class Button(pygame.sprite.Sprite):
    def __init__(self, text, pos, size):
        """инициализируем параметры"""
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill((241, 8, 150))
        self.rect = self.image.get_rect(topleft=pos)
        self.font = pygame.font.Font(None, 25)
        self.text = text

    def draw(self):
        """отрисовываем кнопку"""
        pygame.draw.rect(screen, (241, 8, 150), self.rect)
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, mouse_pos):
        """если кнопка нажата"""
        return self.rect.collidepoint(mouse_pos)


if __name__ == "__main__":
    pygame.init()  # настройка окна
    size = width, height = 800, 600
    FPS = 60
    pygame.display.set_caption("Reach the door")
    pygame.display.set_icon(pygame.image.load("sprites/icon.gif"))
    screen = pygame.display.set_mode(size)
    clock = pygame.time.Clock()  # создаём часы для анимации
    bg = BackGround()  # задаём задний фон

    parser = LVL_parser()
    level = 0

    font = pygame.font.Font(None, 50)  # определение шрифта

    NEW_GAME = True  # флаг экрана новой игры

    running = True  # основной цикл
    while running:
        all_objs = parser[level]
        player = all_objs.sprites()[0]
        dt = clock.tick(FPS) / 1000  # изменение времени
        screen.blit(bg.image, bg.rect)  # добавление фона

        for event in pygame.event.get():  # цикл обработки событий
            if event.type == pygame.QUIT:  # нажатие на крестик
                running = False
            elif event.type == pygame.KEYDOWN:  # нажатие кнопки
                if event.key == pygame.K_RIGHT:  # стрелка вправо
                    player.velocity.x = 15
                elif event.key == pygame.K_LEFT:  # стрелка влево
                    player.velocity.x = -15
                elif event.key == pygame.K_UP:  # прыжок
                    player.jump()
            elif event.type == pygame.KEYUP:  # прекратить движение
                if event.key == pygame.K_RIGHT or event.key == pygame.K_LEFT:
                    player.velocity.x = 0

            if (NEW_GAME or player.win is not None) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_in.is_clicked(event.pos) and player.win is None:  # начало новой игры
                    NEW_GAME = False
                elif btn_out.is_clicked(event.pos):  # выход из игры
                    pygame.quit()
                    sys.exit()
                elif player.win is False:  # перезапуск
                    if btn_rsrt.is_clicked(event.pos):
                        player.reset()
                elif player.win is True:
                    if level != 2:
                        if btn_next.is_clicked(event.pos):
                            level += 1
                    else:
                        if btn_rsrt.is_clicked(event.pos):
                            player.reset()

        if NEW_GAME:  # создать экран новой игры
            text = font.render("Нажмите, чтобы начать игру", True, (0, 0, 0))
            screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 - 85))
            btn_in = Button("Начать", (275, 250), (250, 100))
            btn_out = Button("Выход", (275, 400), (250, 100))
            btn_in.draw()
            btn_out.draw()
        elif player.win is not None:  # экран победы|пройгрыша
            if player.win is False:  # экран пройгрыша
                text = font.render("Вы проиграли!", True, (0, 0, 0))
                screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 - 85))
                btn_rsrt = Button("Заново", (275, 250), (250, 100))
                btn_out = Button("Выход", (275, 400), (250, 100))
                btn_out.draw()
                btn_rsrt.draw()
            elif player.win is True:  # экран победы
                text = font.render("Вы победили!", True, (0, 0, 0))
                screen.blit(text, (width // 2 - text.get_width() // 2, height // 2 - text.get_height() // 2 - 85))
                btn_out = Button("Выход", (275, 400), (250, 100))
                btn_out.draw()
                if level != 2:
                    btn_next = Button("Дальше", (275, 250), (250, 100))
                    btn_next.draw()
                else:
                    btn_rsrt = Button("Заново", (275, 250), (250, 100))
                    btn_rsrt.draw()
        else:  # обновление экрана
            all_objs.update(dt)
            all_objs.draw(screen)

            player.on_ground = False
            for obj in all_objs:  # проверка нахождения на поверхности
                if isinstance(obj, Platform):
                    if player.rect.colliderect(obj.rect):  # обновление флага
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

            if not player.on_ground and player.rect.bottom < height:  # применяем гравитацию
                player.velocity.y += player.gravity

        pygame.display.update()  # обновление дисплея

    pygame.quit()  # выход из игры
