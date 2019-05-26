import pygame


def display_text(screen, text, x, y):
    font = pygame.font.SysFont("Ariel", 25)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)
