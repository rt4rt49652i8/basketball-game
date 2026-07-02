import pygame
import sys
import math

# ==================== CONSTANTS ====================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
PLAYER_RADIUS = 15
PLAYER_SPEED = 5
PLAYER_JUMP_POWER = 20
PLAYER_FRICTION = 0.95
BALL_RADIUS = 8
BALL_FRICTION = 0.98
BALL_GRAVITY = 0.5
BALL_BOUNCE = 0.8
COURT_COLOR = (210, 96, 28)
LINE_COLOR = (255, 255, 255)
THREE_POINT_COLOR = (255, 50, 50)
TEAM1_COLOR = (30, 90, 200)
TEAM2_COLOR = (255, 120, 0)
GAME_STATE_MENU = 0
GAME_STATE_PLAYING = 1
GAME_STATE_PAUSED = 2

# ==================== BUTTON CLASS ====================
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
    def update(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect)
        pygame.draw.rect(surface, (255, 107, 107), self.rect, 3)
        font = pygame.font.Font(None, 40)
        text = font.render(self.text, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
    def is_clicked(self, pos, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pos)

# ==================== PLAYER CLASS ====================
class Player:
    def __init__(self, x, y, color, team):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = 0, 0
        self.color = color
        self.team = team
        self.number = 0
        self.is_jumping = False
    def jump(self):
        if not self.is_jumping:
            self.vel_y = -PLAYER_JUMP_POWER
            self.is_jumping = True
    def update(self):
        if self.y >= SCREEN_HEIGHT - 100:
            self.is_jumping = False
            self.y = SCREEN_HEIGHT - 100
            self.vel_y = 0
        else:
            self.vel_y += BALL_GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= PLAYER_FRICTION
        self.x = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, self.x))
        self.y = max(PLAYER_RADIUS, min(SCREEN_HEIGHT - 100, self.y))
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), PLAYER_RADIUS)
        font = pygame.font.Font(None, 24)
        number_text = font.render(str(self.number), True, (255, 255, 255))
        number_rect = number_text.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(number_text, number_rect)
        pygame.draw.circle(surface, (200, 200, 200), (int(self.x), int(self.y)), PLAYER_RADIUS, 2)

# ==================== BALL CLASS ====================
class Ball:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vel_x, self.vel_y = 0, 0
    def update(self):
        self.vel_y += BALL_GRAVITY
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= BALL_FRICTION
        if self.y + BALL_RADIUS >= SCREEN_HEIGHT - 100:
            self.y = SCREEN_HEIGHT - 100 - BALL_RADIUS
            self.vel_y *= -BALL_BOUNCE
            if abs(self.vel_y) < 1:
                self.vel_y = 0
        if self.x - BALL_RADIUS <= 0:
            self.x = BALL_RADIUS
            self.vel_x *= -BALL_BOUNCE
        elif self.x + BALL_RADIUS >= SCREEN_WIDTH:
            self.x = SCREEN_WIDTH - BALL_RADIUS
            self.vel_x *= -BALL_BOUNCE
    def check_collision_with_player(self, player):
        distance = math.sqrt((self.x - player.x) ** 2 + (self.y - player.y) ** 2)
        return distance < BALL_RADIUS + PLAYER_RADIUS
    def bounce_off_player(self, player):
        angle = math.atan2(self.y - player.y, self.x - player.x)
        speed = math.sqrt(self.vel_x ** 2 + self.vel_y ** 2)
        self.vel_x = math.cos(angle) * speed * 1.2
        self.vel_y = math.sin(angle) * speed * 1.2
        distance = BALL_RADIUS + PLAYER_RADIUS + 1
        self.x = player.x + math.cos(angle) * distance
        self.y = player.y + math.sin(angle) * distance
    def reset(self, x, y):
        self.x, self.y, self.vel_x, self.vel_y = x, y, 0, 0
    def draw(self, surface):
        pygame.draw.circle(surface, (255, 153, 0), (int(self.x), int(self.y)), BALL_RADIUS)
        pygame.draw.circle(surface, (200, 100, 0), (int(self.x), int(self.y)), BALL_RADIUS, 2)

# ==================== COURT CLASS ====================
class Court:
    def __init__(self):
        self.basket1_x, self.basket1_y = 80, 150
        self.basket2_x, self.basket2_y = SCREEN_WIDTH - 80, 150
    def draw(self, surface):
        court_rect = pygame.Rect(40, 100, SCREEN_WIDTH - 80, SCREEN_HEIGHT - 200)
        pygame.draw.rect(surface, COURT_COLOR, court_rect)
        pygame.draw.rect(surface, LINE_COLOR, court_rect, 3)
        center_x = SCREEN_WIDTH // 2
        pygame.draw.line(surface, LINE_COLOR, (center_x, 100), (center_x, SCREEN_HEIGHT - 100), 2)
        pygame.draw.circle(surface, LINE_COLOR, (center_x, SCREEN_HEIGHT // 2), 30, 2)
        self.draw_basket(surface, self.basket1_x, self.basket1_y)
        self.draw_basket(surface, self.basket2_x, self.basket2_y)
        pygame.draw.line(surface, THREE_POINT_COLOR, (self.basket1_x + 50, 100), (self.basket1_x + 50, SCREEN_HEIGHT - 100), 2)
        pygame.draw.line(surface, THREE_POINT_COLOR, (self.basket2_x - 50, 100), (self.basket2_x - 50, SCREEN_HEIGHT - 100), 2)
        pygame.draw.line(surface, (100, 100, 100), (0, SCREEN_HEIGHT - 100), (SCREEN_WIDTH, SCREEN_HEIGHT - 100), 1)
    def draw_basket(self, surface, x, y):
        pygame.draw.rect(surface, (200, 200, 200), (x - 25, y - 40, 50, 80), 2)
        pygame.draw.circle(surface, (200, 50, 50), (x, y + 30), 15, 3)
        for i in range(5):
            offset = i * 6 - 12
            pygame.draw.line(surface, (255, 255, 255), (x + offset, y + 30), (x + offset + 8, y + 60), 1)

# ==================== MAIN GAME CLASS ====================
class Game:
    def __init__(self, screen):
        self.screen = screen
        self.state = GAME_STATE_MENU
        self.buttons = {"quick": Button(540, 250, 200, 60, "QUICK PLAY", (50, 50, 200), (100, 100, 255)),
                        "player": Button(540, 350, 200, 60, "MY PLAYER", (50, 50, 200), (100, 100, 255)),
                        "season": Button(540, 450, 200, 60, "SEASON", (50, 50, 200), (100, 100, 255)),
                        "team": Button(540, 550, 200, 60, "MY TEAM", (50, 50, 200), (100, 100, 255))}
    def setup_gameplay(self):
        self.court = Court()
        self.team1 = [Player((200 + i*30, 250 + i*50), TEAM1_COLOR, 1) for i in range(5)]
        self.team2 = [Player((SCREEN_WIDTH - 200 - i*30, 250 + i*50), TEAM2_COLOR, 2) for i in range(5)]
        for i, p in enumerate(self.team1 + self.team2):
            p.number = (i % 5) + 1
        self.ball = Ball(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
        self.score1 = self.score2 = 0
        self.game_time = 600
        self.selected_player = self.team1[0]
    def handle_event(self, event):
        if self.state == GAME_STATE_MENU:
            mouse_pos = pygame.mouse.get_pos()
            for button in self.buttons.values():
                button.update(mouse_pos)
                if button.is_clicked(mouse_pos, event):
                    self.setup_gameplay()
                    self.state = GAME_STATE_PLAYING
        elif self.state == GAME_STATE_PLAYING:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GAME_STATE_PAUSED
                elif event.key == pygame.K_m:
                    self.state = GAME_STATE_MENU
                elif event.key == pygame.K_w:
                    self.selected_player.vel_y = -PLAYER_SPEED
                elif event.key == pygame.K_s:
                    self.selected_player.vel_y = PLAYER_SPEED
                elif event.key == pygame.K_a:
                    self.selected_player.vel_x = -PLAYER_SPEED
                elif event.key == pygame.K_d:
                    self.selected_player.vel_x = PLAYER_SPEED
                elif event.key == pygame.K_SPACE:
                    self.selected_player.jump()
            elif event.type == pygame.KEYUP:
                if event.key in [pygame.K_w, pygame.K_s]:
                    self.selected_player.vel_y = 0
                elif event.key in [pygame.K_a, pygame.K_d]:
                    self.selected_player.vel_x = 0
        elif self.state == GAME_STATE_PAUSED:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.state = GAME_STATE_PLAYING
                elif event.key == pygame.K_m:
                    self.state = GAME_STATE_MENU
    def update(self):
        if self.state == GAME_STATE_PLAYING:
            self.game_time = max(0, self.game_time - 1 / FPS)
            for player in self.team1 + self.team2:
                player.update()
            self.ball.update()
            for player in self.team1 + self.team2:
                if self.ball.check_collision_with_player(player):
                    self.ball.bounce_off_player(player)
            if abs(self.ball.x - self.court.basket1_x) < 20 and abs(self.ball.y - self.court.basket1_y) < 20 and self.ball.vel_y > 0:
                self.score2 += 2
                self.ball.reset(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
            if abs(self.ball.x - self.court.basket2_x) < 20 and abs(self.ball.y - self.court.basket2_y) < 20 and self.ball.vel_y > 0:
                self.score1 += 2
                self.ball.reset(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)
    def draw(self):
        self.screen.fill((0, 0, 0))
        if self.state == GAME_STATE_MENU:
            font = pygame.font.Font(None, 120)
            title = font.render("BASKETBALL 2K26", True, (255, 107, 107))
            self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 100)))
            for button in self.buttons.values():
                button.draw(self.screen)
        elif self.state == GAME_STATE_PLAYING:
            self.court.draw(self.screen)
            for player in self.team1 + self.team2:
                player.draw(self.screen)
            self.ball.draw(self.screen)
            pygame.draw.circle(self.screen, (255, 255, 0), (int(self.selected_player.x), int(self.selected_player.y)), PLAYER_RADIUS + 5, 2)
            pygame.draw.rect(self.screen, (0, 0, 0), (0, 0, SCREEN_WIDTH, 80))
            pygame.draw.line(self.screen, (255, 107, 107), (0, 80), (SCREEN_WIDTH, 80), 2)
            font_large = pygame.font.Font(None, 60)
            home = font_large.render(str(self.score1), True, (100, 150, 255))
            away = font_large.render(str(self.score2), True, (255, 180, 100))
            time_text = font_large.render(f"{int(self.game_time // 60)}:{int(self.game_time % 60):02d}", True, (255, 107, 107))
            self.screen.blit(home, (50, 40))
            self.screen.blit(time_text, (SCREEN_WIDTH // 2 - 80, 40))
            self.screen.blit(away, (SCREEN_WIDTH - 100, 40))
            controls = pygame.font.Font(None, 20).render("WASD: Move | SPACE: Jump | ESC: Pause | M: Menu", True, (150, 150, 150))
            self.screen.blit(controls, (20, SCREEN_HEIGHT - 25))
        elif self.state == GAME_STATE_PAUSED:
            self.court.draw(self.screen)
            for player in self.team1 + self.team2:
                player.draw(self.screen)
            self.ball.draw(self.screen)
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            font = pygame.font.Font(None, 80)
            text = font.render("PAUSED", True, (255, 107, 107))
            self.screen.blit(text, text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
            font_small = pygame.font.Font(None, 40)
            text_small = font_small.render("ESC to Resume | M to Menu", True, (200, 200, 200))
            self.screen.blit(text_small, text_small.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100)))

# ==================== MAIN ====================
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Basketball Game 2K26")
    clock = pygame.time.Clock()
    game = Game(screen)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            game.handle_event(event)
        game.update()
        game.draw()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
