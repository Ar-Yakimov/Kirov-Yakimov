import pygame


if __name__ == '__main__':
    pygame.init()
    size = width, height = 800, 400
    screen = pygame.display.set_mode(size)

    running = True
    while running:
        for event in pygame.event.get():
            # при закрытии окна
            if event.type == pygame.QUIT:
                running = False

        # отрисовка и изменение свойств объектов

        pygame.display.flip()
    pygame.quit()
