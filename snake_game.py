import pygame
import random
import sys

# 初始化Pygame
pygame.init()

# 定义颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# 设置游戏窗口
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
BLOCK_SIZE = 20

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('贪吃蛇游戏')


class Snake:
    def __init__(self):
        self.length = 1
        self.positions = [(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)]
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.color = GREEN
        self.score = 0

    def get_head_position(self):
        return self.positions[0]

    def update(self):
        cur = self.get_head_position()
        x, y = cur

        if self.direction == "UP":
            y -= BLOCK_SIZE
        elif self.direction == "DOWN":
            y += BLOCK_SIZE
        elif self.direction == "LEFT":
            x -= BLOCK_SIZE
        elif self.direction == "RIGHT":
            x += BLOCK_SIZE

        # 检查是否碰到边界
        if x >= WINDOW_WIDTH or x < 0 or y >= WINDOW_HEIGHT or y < 0:
            self.reset()
            return

        self.positions.insert(0, (x, y))
        if len(self.positions) > self.length:
            self.positions.pop()

    def reset(self):
        self.length = 1
        self.positions = [(WINDOW_WIDTH//2, WINDOW_HEIGHT//2)]
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.score = 0

    def draw(self, surface):
        for p in self.positions:
            pygame.draw.rect(surface, self.color,
                             (p[0], p[1], BLOCK_SIZE, BLOCK_SIZE))


class Food:
    def __init__(self):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position()

    def randomize_position(self):
        self.position = (random.randint(0, (WINDOW_WIDTH-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE,
                         random.randint(0, (WINDOW_HEIGHT-BLOCK_SIZE)//BLOCK_SIZE) * BLOCK_SIZE)

    def draw(self, surface):
        pygame.draw.rect(
            surface, self.color, (self.position[0], self.position[1], BLOCK_SIZE, BLOCK_SIZE))


def main():
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food()
    font = pygame.font.Font(None, 36)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != "DOWN":
                    snake.direction = "UP"
                elif event.key == pygame.K_DOWN and snake.direction != "UP":
                    snake.direction = "DOWN"
                elif event.key == pygame.K_LEFT and snake.direction != "RIGHT":
                    snake.direction = "LEFT"
                elif event.key == pygame.K_RIGHT and snake.direction != "LEFT":
                    snake.direction = "RIGHT"

        # 更新蛇的位置
        snake.update()

        # 检查是否吃到食物
        if snake.get_head_position() == food.position:
            snake.length += 1
            snake.score += 10
            food.randomize_position()

        # 检查是否撞到自己
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        # 绘制游戏界面
        screen.fill(BLACK)
        snake.draw(screen)
        food.draw(screen)

        # 显示分数
        score_text = font.render(f'分数: {snake.score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        pygame.display.update()
        clock.tick(10)


if __name__ == "__main__":
    main()
