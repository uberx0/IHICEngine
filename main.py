import tkinter as tk
import os
from pygame import mixer

# Константы
DEFAULT_TILE_SIZE = 40
TILE_SIZE = DEFAULT_TILE_SIZE
LVL_DIR = "lvls"
MUSIC_DIR = "music"

# Цвета
RED = "red"
YELLOW = "yellow"
BLUE = "blue"
WHITE = "white"
BLACK = "black"
GRAY = "gray"

# Загрузка карты уровня из файла
def load_map_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()

        title = "Игра"
        music_file = None
        map_data = []
        walls = []
        enemies = []
        player_pos = None
        finish_pos = None

        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                title = line[1:].strip()
            elif line.startswith("!"):
                music_file = line[1:].strip()
            else:
                map_data.append(line)

        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                if cell == "1":
                    walls.append((x, y))
                elif cell == "2":
                    player_pos = (x, y)
                elif cell == "3":
                    enemies.append((x, y))
                elif cell == "4":
                    finish_pos = (x, y)

        return title, music_file, map_data, walls, enemies, player_pos, finish_pos
    except Exception as e:
        print(f"Ошибка при загрузке уровня: {file_path}. Ошибка: {e}")
        return None

# Список файлов уровней
def get_level_files():
    files = [f for f in os.listdir(LVL_DIR) if f.endswith('.lvl')]
    return sorted(files, key=lambda x: int(os.path.splitext(x)[0]))

# Главный класс игры
class Game:
    def __init__(self, root):
        self.root = root
        self.level_files = get_level_files()

        if not self.level_files:
            print("Нет доступных уровней! Игра закрывается.")
            self.root.quit()
            return

        self.level_index = 0
        self.load_level()

    def load_level(self):
        if self.level_index >= len(self.level_files):
            print("Вы завершили все уровни. Игра окончена.")
            self.root.quit()
            return

        level_path = os.path.join(LVL_DIR, self.level_files[self.level_index])
        level_data = load_map_from_file(level_path)

        if not level_data:
            self.root.quit()
            return

        title, music_file, map_data, walls, enemies, player_pos, finish_pos = level_data
        self.root.title(title)

        map_width = len(map_data[0])
        map_height = len(map_data)

        global TILE_SIZE
        if map_width > 14:
            TILE_SIZE = DEFAULT_TILE_SIZE // 2
        else:
            TILE_SIZE = DEFAULT_TILE_SIZE

        window_width = map_width * TILE_SIZE
        window_height = map_height * TILE_SIZE
        self.root.geometry(f"{window_width}x{window_height}")

        if music_file:
            self.play_music(music_file)

        self.walls = walls
        self.enemies = enemies
        self.player_pos = player_pos
        self.finish_pos = finish_pos

        if hasattr(self, 'canvas'):
            self.canvas.destroy()

        self.canvas = tk.Canvas(self.root, width=window_width, height=window_height, bg=BLACK)
        self.canvas.pack()
        self.draw_level()

    def play_music(self, music_file):
        music_path = os.path.join(MUSIC_DIR, music_file)
        if os.path.exists(music_path):
            mixer.init()
            mixer.music.load(music_path)
            mixer.music.play(-1)
            print(f"Музыка {music_file} начала играть.")
        else:
            print(f"Музыка {music_file} не найдена в папке {MUSIC_DIR}. Музыка не будет проигрываться.")

    def draw_level(self):
        self.canvas.delete("all")

        for wall in self.walls:
            x = wall[0] * TILE_SIZE
            y = wall[1] * TILE_SIZE
            self.canvas.create_rectangle(x, y, x + TILE_SIZE, y + TILE_SIZE, fill=GRAY)

        for enemy in self.enemies:
            x = enemy[0] * TILE_SIZE
            y = enemy[1] * TILE_SIZE
            self.canvas.create_rectangle(x, y, x + TILE_SIZE, y + TILE_SIZE, fill=RED)

        player_x = self.player_pos[0] * TILE_SIZE
        player_y = self.player_pos[1] * TILE_SIZE
        self.player = self.canvas.create_rectangle(player_x, player_y,
                                                   player_x + TILE_SIZE, player_y + TILE_SIZE,
                                                   fill=YELLOW)

        if self.finish_pos:
            finish_x = self.finish_pos[0] * TILE_SIZE
            finish_y = self.finish_pos[1] * TILE_SIZE
            self.canvas.create_rectangle(finish_x, finish_y,
                                         finish_x + TILE_SIZE, finish_y + TILE_SIZE, fill=BLUE)

        self.root.bind("<KeyPress>", self.on_key_press)

    def on_key_press(self, event):
        velocity = [0, 0]
        if event.keysym == "Left":
            velocity[0] = -TILE_SIZE
        elif event.keysym == "Right":
            velocity[0] = TILE_SIZE
        elif event.keysym == "Up":
            velocity[1] = -TILE_SIZE
        elif event.keysym == "Down":
            velocity[1] = TILE_SIZE

        next_position = [self.player_pos[0] + velocity[0] // TILE_SIZE, self.player_pos[1] + velocity[1] // TILE_SIZE]

        if not any((next_position[0], next_position[1]) == (wall[0], wall[1]) for wall in self.walls):
            self.player_pos = next_position
            self.canvas.coords(self.player, self.player_pos[0] * TILE_SIZE, self.player_pos[1] * TILE_SIZE,
                               self.player_pos[0] * TILE_SIZE + TILE_SIZE, self.player_pos[1] * TILE_SIZE + TILE_SIZE)

        for enemy in self.enemies:
            if self.player_pos == list(enemy):
                print("Игра окончена! Вы столкнулись с врагом.")
                self.root.quit()
                return

        if self.finish_pos and self.player_pos == list(self.finish_pos):
            self.level_index += 1
            self.load_level()

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
