import pygame
from collections import deque
import time
import heapq
from copy import deepcopy
from queue import PriorityQueue, LifoQueue
import random
import math
import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
from pygame.font import SysFont, Font, get_fonts

# Constants
WIDTH = 1800  # Window width
HEIGHT = 1030  # Window height
TILE_SIZE = min(100, max(70, min(WIDTH, HEIGHT) // 10))  # Tile size
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (220, 220, 220)
RED = (220, 60, 60)
BLUE = (70, 130, 230)
GREEN = (60, 180, 75)
LIGHT_GREEN = (120, 230, 120)
LIGHT_BLUE = (180, 210, 240)
PANEL_BLUE = (230, 240, 255)
TILE_COLOR = (180, 180, 180)
TITLE_COLOR = (50, 50, 120)
YELLOW = (240, 190, 40)
PURPLE = (180, 110, 200)
GROUP_UNINFORMED = (70, 130, 200)
GROUP_INFORMED = (60, 180, 100)
GROUP_LOCAL = (200, 100, 100)
GROUP_EVOLUTIONARY = (180, 110, 200)
GROUP_TITLE_BG = (240, 240, 240)
moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Blank tile moves

def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j

def is_valid(x, y):
    return 0 <= x < 3 and 0 <= y < 3

def state_to_tuple(state):
    return tuple(tuple(row) for row in state)

def get_next_states(state):
    blank_x, blank_y = find_blank(state)
    next_states = []
    for move_x, move_y in moves:
        new_x, new_y = blank_x + move_x, blank_y + move_y
        if is_valid(new_x, new_y):
            new_state = deepcopy(state)
            new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
            next_states.append(new_state)
    return next_states

def states_to_moves(states):
    if not states or len(states) < 2:
        return []
    moves_list = []
    for i in range(len(states) - 1):
        current_state = states[i]
        next_state = states[i + 1]
        blank_x, blank_y = find_blank(current_state)
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                temp_state = deepcopy(current_state)
                temp_state[blank_x][blank_y], temp_state[new_x][new_y] = temp_state[new_x][new_y], temp_state[blank_x][blank_y]
                if state_to_tuple(temp_state) == state_to_tuple(next_state):
                    moves_list.append((new_x, new_y))
                    break
    return moves_list

def linear_conflict(state, goal):
    conflict = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                continue
            value = state[i][j]
            for gi in range(3):
                for gj in range(3):
                    if goal[gi][gj] == value:
                        goal_row, goal_col = gi, gj
                        break
            if i == goal_row:
                for k in range(j + 1, 3):
                    if state[i][k] == 0:
                        continue
                    other_value = state[i][k]
                    for gi in range(3):
                        for gj in range(3):
                            if goal[gi][gj] == other_value:
                                other_goal_col = gj
                                break
                    if other_value in [goal[i][c] for c in range(3)] and j < k and other_goal_col < goal_col:
                        conflict += 2
            if j == goal_col:
                for k in range(i + 1, 3):
                    if state[k][j] == 0:
                        continue
                    other_value = state[k][j]
                    for gi in range(3):
                        for gj in range(3):
                            if goal[gi][gj] == other_value:
                                other_goal_row = gi
                                break
                    if other_value in [goal[r][j] for r in range(3)] and i < k and other_goal_row < goal_row:
                        conflict += 2
    return conflict

def show_message(title, message):
    pygame_surf = pygame.display.get_surface()
    pygame_surf_copy = pygame_surf.copy() if pygame_surf else None
    screen_width, screen_height = pygame_surf.get_size()
    
    font_size = max(24, min(36, int(screen_width * 0.028)))
    small_font_size = max(18, min(28, int(screen_width * 0.020)))
    font = pygame.font.Font(None, font_size)
    small_font = pygame.font.Font(None, small_font_size)
    
    padding = max(10, min(20, int(screen_width * 0.015)))
    title_text = font.render(title, True, BLACK)
    message_lines = message.strip().split('\n')
    message_renders = [small_font.render(line, True, BLACK) for line in message_lines]
    
    width = max([title_text.get_width()] + [text.get_width() for text in message_renders]) + padding * 2
    message_height = sum(text.get_height() for text in message_renders) + (len(message_lines) - 1) * 5
    button_margin = max(10, min(20, int(screen_height * 0.025)))
    
    ok_button_width = min(100, max(80, int(width * 0.25)))
    ok_button_height = max(30, min(40, int(screen_height * 0.06)))
    
    height = padding * 2 + title_text.get_height() + 15 + message_height + button_margin + ok_button_height
    
    if width > screen_width - 40:
        width = screen_width - 40
    if height > screen_height - 40:
        height = screen_height - 40
    
    box = pygame.Surface((width, height))
    box.fill(PANEL_BLUE)
    pygame.draw.rect(box, BLACK, (0, 0, width, height), 2, border_radius=15)
    
    box.blit(title_text, (padding, padding))
    
    y_offset = padding + title_text.get_height() + 15
    for text in message_renders:
        text_x = (width - text.get_width()) // 2
        box.blit(text, (text_x, y_offset))
        y_offset += text.get_height() + 5
    
    ok_button_x = (width - ok_button_width) // 2
    ok_button_y = padding + title_text.get_height() + 15 + message_height + button_margin
    
    pygame.draw.rect(box, GREEN, (ok_button_x, ok_button_y, ok_button_width, ok_button_height), border_radius=10)
    pygame.draw.rect(box, BLACK, (ok_button_x, ok_button_y, ok_button_width, ok_button_height), 2, border_radius=0)
    
    ok_text = small_font.render("OK", True, BLACK)
    ok_text_rect = ok_text.get_rect(center=(ok_button_x + ok_button_width // 2, ok_button_y + ok_button_height // 2))
    box.blit(ok_text, ok_text_rect)
    
    box_x = (screen_width - width) // 2
    box_y = (screen_height - height) // 2
    
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    pygame_surf.blit(overlay, (0, 0))
    pygame_surf.blit(box, (box_x, box_y))
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if (box_x + ok_button_x <= mouse_x <= box_x + ok_button_x + ok_button_width and
                    box_y + ok_button_y <= mouse_y <= box_y + ok_button_y + ok_button_height):
                    waiting = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    waiting = False
        
        pygame_surf.blit(box, (box_x, box_y))
        pygame.display.flip()
    
    if pygame_surf_copy:
        pygame_surf.blit(pygame_surf_copy, (0, 0))
        pygame.display.flip()

def show_state_history(states):
    if not states:
        show_message("Thong bao", "Chua co lich su trang thai de hien thi!")
        return
    
    pygame_surf = pygame.display.get_surface()
    pygame_surf_copy = pygame_surf.copy()
    screen_width, screen_height = pygame_surf.get_size()
    
    padding = max(10, min(20, int(screen_width * 0.02)))
    history_width = min(int(screen_width * 0.8), 800)
    history_height = min(int(screen_height * 0.8), 600)
    
    if history_width > screen_width - 40:
        history_width = screen_width - 40
    if history_height > screen_height - 40:
        history_height = screen_height - 40
    
    history_x = (screen_width - history_width) // 2
    history_y = (screen_height - history_height) // 2
    
    font_size = max(24, min(36, int(screen_width * 0.028)))
    small_font_size = max(18, min(24, int(screen_width * 0.018)))
    mono_font_size = max(14, min(18, int(screen_width * 0.012)))
    
    font = pygame.font.Font(None, font_size)
    small_font = pygame.font.Font(None, small_font_size)
    mono_font = pygame.font.SysFont("courier", mono_font_size)
    
    history_box = pygame.Surface((history_width, history_height))
    history_box.fill(PANEL_BLUE)
    pygame.draw.rect(history_box, BLACK, (0, 0, history_width, history_height), 2, border_radius=15)
    
    title_text = font.render("Lich su trang thai", True, BLACK)
    history_box.blit(title_text, (padding, padding))
    
    total_steps = len(states) - 1
    steps_text = small_font.render(f"Tong so buoc: {total_steps}", True, BLACK)
    history_box.blit(steps_text, (padding, padding + title_text.get_height() + 10))
    
    content_y = padding + title_text.get_height() + steps_text.get_height() + 20
    content_height = history_height - content_y - padding * 2 - 50
    content_width = history_width - padding * 2
    
    line_height = mono_font.get_height()
    step_height = line_height * 4 + 10
    total_content_height = step_height * len(states)
    
    scroll_content = pygame.Surface((content_width, max(total_content_height, content_height)))
    scroll_content.fill(WHITE)
    
    current_y = 5
    for i, state in enumerate(states):
        step_text = mono_font.render(f"Buoc {i}:", True, BLACK)
        scroll_content.blit(step_text, (5, current_y))
        current_y += line_height
        
        for row in state:
            row_text = mono_font.render(" ".join(str(x) if x != 0 else " " for x in row), True, BLACK)
            scroll_content.blit(row_text, (20, current_y))
            current_y += line_height
        
        current_y += 5
    
    scroll_pos = 0
    max_scroll = max(0, total_content_height - content_height)
    scroll_bar_height = min(content_height, content_height * content_height / total_content_height) if total_content_height > 0 else content_height
    
    ok_button_width = min(100, int(history_width * 0.25))
    ok_button_height = min(40, int(history_height * 0.08))
    ok_button_x = (history_width - ok_button_width) // 2
    ok_button_y = history_height - padding - ok_button_height
    
    waiting = True
    dragging = False
    
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    pygame_surf.blit(overlay, (0, 0))
    
    while waiting:
        history_box.fill(PANEL_BLUE)
        pygame.draw.rect(history_box, BLACK, (0, 0, history_width, history_height), 2, border_radius=15)
        history_box.blit(title_text, (padding, padding))
        history_box.blit(steps_text, (padding, padding + title_text.get_height() + 10))
        
        viewport = pygame.Surface((content_width, content_height))
        viewport.fill(WHITE)
        viewport.blit(scroll_content, (0, -scroll_pos))
        history_box.blit(viewport, (padding, content_y))
        
        if total_content_height > content_height:
            pygame.draw.rect(history_box, GRAY, 
                          (history_width - padding - 10, content_y, 10, content_height))
            scroll_bar_pos = content_y + (scroll_pos / max_scroll) * (content_height - scroll_bar_height) if max_scroll > 0 else content_y
            pygame.draw.rect(history_box, BLACK, 
                          (history_width - padding - 10, scroll_bar_pos, 10, scroll_bar_height))
        
        pygame.draw.rect(history_box, GREEN, 
                       (ok_button_x, ok_button_y, ok_button_width, ok_button_height), 
                       border_radius=10)
        pygame.draw.rect(history_box, BLACK, 
                       (ok_button_x, ok_button_y, ok_button_width, ok_button_height), 
                       2, border_radius=10)
        
        ok_text = small_font.render("OK", True, BLACK)
        history_box.blit(ok_text, (ok_button_x + (ok_button_width - ok_text.get_width()) // 2, 
                                 ok_button_y + (ok_button_height - ok_text.get_height()) // 2))
        
        pygame_surf.blit(history_box, (history_x, history_y))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                elif event.key == pygame.K_UP:
                    scroll_pos = max(0, scroll_pos - line_height * 2)
                elif event.key == pygame.K_DOWN:
                    scroll_pos = min(max_scroll, scroll_pos + line_height * 2)
                elif event.key == pygame.K_PAGEUP:
                    scroll_pos = max(0, scroll_pos - content_height + line_height)
                elif event.key == pygame.K_PAGEDOWN:
                    scroll_pos = min(max_scroll, scroll_pos + content_height - line_height)
                elif event.key == pygame.K_HOME:
                    scroll_pos = 0
                elif event.key == pygame.K_END:
                    scroll_pos = max_scroll
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    waiting = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                rel_x = mouse_x - history_x
                rel_y = mouse_y - history_y
                if (ok_button_x <= rel_x <= ok_button_x + ok_button_width and
                    ok_button_y <= rel_y <= ok_button_y + ok_button_height):
                    waiting = False
                elif (history_width - padding - 10 <= rel_x <= history_width - padding and
                      content_y <= rel_y <= content_y + content_height):
                    dragging = True
                    if max_scroll > 0:
                        click_ratio = (rel_y - content_y) / content_height
                        scroll_pos = max(0, min(max_scroll, click_ratio * total_content_height))
                elif (padding <= rel_x <= padding + content_width and
                      content_y <= rel_y <= content_y + content_height):
                    if event.button == 4:
                        scroll_pos = max(0, scroll_pos - line_height * 3)
                    elif event.button == 5:
                        scroll_pos = min(max_scroll, scroll_pos + line_height * 3)
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            elif event.type == pygame.MOUSEMOTION and dragging and max_scroll > 0:
                rel_y = event.pos[1] - history_y - content_y
                scroll_ratio = max(0, min(1, rel_y / content_height))
                scroll_pos = scroll_ratio * max_scroll
    
    pygame_surf.blit(pygame_surf_copy, (0, 0))
    pygame.display.flip()

def bfs(initial, goal):
    queue = deque([(initial, [])])
    visited = set()
    visited.add(state_to_tuple(initial))
    while queue:
        state, path = queue.popleft()
        if state == goal:
            return path, 0  
        blank_x, blank_y = find_blank(state)
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    visited.add(new_tuple)
                    queue.append((new_state, path + [(new_x, new_y)]))
    return None, 0

def ucs(initial, goal):
    priority_queue = PriorityQueue()
    priority_queue.put((0, initial, []))
    visited = set()
    visited.add(state_to_tuple(initial))
    while not priority_queue.empty():
        cost, state, path = priority_queue.get()
        if state == goal:
            return path, 0
        blank_x, blank_y = find_blank(state)
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    visited.add(new_tuple)
                    priority_queue.put((cost + 1, new_state, path + [(new_x, new_y)]))
    return None, 0

def dfs(initial, goal):
    stack = LifoQueue()
    stack.put((initial, []))
    visited = set()
    visited.add(state_to_tuple(initial))
    while not stack.empty():
        state, path = stack.get()
        if state == goal:   
            return path, 0
        blank_x, blank_y = find_blank(state)
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    visited.add(new_tuple)
                    stack.put((new_state, path + [(new_x, new_y)]))
    return None, 0

def depth_limited_search(state, goal, depth_limit, path, visited):
    if state == goal:
        return path
    if depth_limit == 0:
        return None
    visited.add(state_to_tuple(state))
    blank_x, blank_y = find_blank(state)
    for move_x, move_y in moves:
        new_x, new_y = blank_x + move_x, blank_y + move_y
        if is_valid(new_x, new_y):
            new_state = deepcopy(state)
            new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
            new_tuple = state_to_tuple(new_state)
            if new_tuple not in visited:
                result = depth_limited_search(new_state, goal, depth_limit - 1, path + [(new_x, new_y)], visited)
                if result:
                    return result
    return None

def iddfs(initial, goal, max_depth=100):
    for depth in range(1, max_depth):
        visited = set()
        result = depth_limited_search(initial, goal, depth, [], visited)
        if result is not None:
            return result, 0
    return None, 0

def manhattan_distance(state, goal):
    distance = 0
    for i in range(3):
        for j in range(3):
            value = state[i][j]
            if value != 0:
                for x in range(3):
                    for y in range(3):
                        if goal[x][y] == value:
                            distance += abs(i - x) + abs(j - y)
    return distance

def greedy_search(initial, goal):
    priority_queue = PriorityQueue()
    priority_queue.put((manhattan_distance(initial, goal), initial, []))
    visited = set()
    visited.add(state_to_tuple(initial))
    while not priority_queue.empty():
        _, state, path = priority_queue.get()
        if state == goal:
            return path, 0
        blank_x, blank_y = find_blank(state)
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    visited.add(new_tuple)
                    priority_queue.put((manhattan_distance(new_state, goal), new_state, path + [(new_x, new_y)]))
    return None, 0

def a_star(initial, goal):
    priority_queue = PriorityQueue()
    priority_queue.put((manhattan_distance(initial, goal) + 0, 0, initial, []))
    visited = set()
    visited.add(state_to_tuple(initial))
    while not priority_queue.empty():
        f, g, state, path = priority_queue.get()
        if state == goal:
            return path, 0
        blank_x, blank_y = find_blank(state)
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    visited.add(new_tuple)
                    new_g = g + 1
                    new_h = manhattan_distance(new_state, goal)
                    new_f = new_h + new_g
                    priority_queue.put((new_f, new_g, new_state, path + [(new_x, new_y)]))
    return None, 0

def a_star_limited(state, goal, threshold, g, path, visited):
    h = manhattan_distance(state, goal)
    f = g + h
    if f > threshold:
        return f, None
    if state == goal:
        return -1, path
    min_threshold = float('inf')
    blank_x, blank_y = find_blank(state)
    for move_x, move_y in moves:
        new_x, new_y = blank_x + move_x, blank_y + move_y
        if is_valid(new_x, new_y):
            new_state = deepcopy(state)
            new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
            new_tuple = state_to_tuple(new_state)
            if new_tuple not in visited:
                visited_copy = visited.copy()
                visited_copy.add(new_tuple)
                t, result = a_star_limited(new_state, goal, threshold, g + 1, path + [(new_x, new_y)], visited_copy)
                if t == -1:
                    return -1, result
                if t < min_threshold:
                    min_threshold = t
    return min_threshold, None

def ida_star(initial, goal):
    threshold = manhattan_distance(initial, goal)
    path = []
    while True:
        visited = set([state_to_tuple(initial)])
        t, result = a_star_limited(initial, goal, threshold, 0, path, visited)
        if t == -1:
            return result, 0
        if t == float('inf'):
            return None, 0
        threshold = t

def simple_hill_climbing(initial, goal):
    current_state = initial
    current_path = []
    visited = set([state_to_tuple(initial)])
    while True:
        current_value = manhattan_distance(current_state, goal)
        blank_x, blank_y = find_blank(current_state)
        best_neighbor = None
        best_value = float('inf')
        best_move = None
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(current_state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    new_value = manhattan_distance(new_state, goal)
                    if new_value < best_value:
                        best_value = new_value
                        best_neighbor = new_state
                        best_move = (new_x, new_y)
        if best_neighbor is None or current_state == goal:
            return current_path if current_state == goal else None, 0
        if best_value < current_value:
            current_state = best_neighbor
            current_path.append(best_move)
            visited.add(state_to_tuple(current_state))
        else:
            return current_path if current_state == goal else None, 0

def steepest_ascent_hill_climbing(initial, goal):
    current_state = initial
    current_path = []
    visited = set([state_to_tuple(initial)])
    while True:
        current_value = manhattan_distance(current_state, goal)
        blank_x, blank_y = find_blank(current_state)
        best_neighbor = None
        best_value = float('inf')
        best_move = None
        all_neighbors_checked = True
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(current_state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    all_neighbors_checked = False
                    new_value = manhattan_distance(new_state, goal)
                    if new_value < best_value:
                        best_value = new_value
                        best_neighbor = new_state
                        best_move = (new_x, new_y)
        if all_neighbors_checked or current_state == goal:
            return current_path if current_state == goal else None, 0
        if best_value >= current_value:
            return current_path if current_state == goal else None, 0
        current_state = best_neighbor
        current_path.append(best_move)
        visited.add(state_to_tuple(current_state))
        if len(current_path) > 1000:
            return None, 0

def stochastic_hill_climbing(initial, goal):
    current_state = initial
    current_path = []
    visited = set([state_to_tuple(initial)])
    while True:
        current_value = manhattan_distance(current_state, goal)
        blank_x, blank_y = find_blank(current_state)
        better_states = []
        moves_dict = {}
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(current_state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    new_value = manhattan_distance(new_state, goal)
                    if new_value < current_value:
                        better_states.append(new_state)
                        moves_dict[new_tuple] = (new_x, new_y)
        if not better_states or current_state == goal:
            return current_path if current_state == goal else None, 0
        next_state = random.choice(better_states)
        next_tuple = state_to_tuple(next_state)
        current_state = next_state
        current_path.append(moves_dict[next_tuple])
        visited.add(next_tuple)
        if len(current_path) > 1000:
            return None, 0

def simulated_annealing(initial, goal, initial_temp=1000, cooling_rate=0.95, min_temp=1):
    current_state = deepcopy(initial)
    current_path = []
    visited = set([state_to_tuple(initial)])
    temp = initial_temp

    while temp > min_temp:
        current_value = manhattan_distance(current_state, goal)
        blank_x, blank_y = find_blank(current_state)

        neighbors = []
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(current_state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_tuple = state_to_tuple(new_state)
                if new_tuple not in visited:
                    neighbors.append((new_state, (move_x, move_y)))

        if not neighbors or current_state == goal:
            if current_state == goal:
                return current_path, len(current_path)
            else:
                return None, 0

        next_state, move = random.choice(neighbors)
        next_value = manhattan_distance(next_state, goal)
        delta = next_value - current_value

        if delta < 0 or random.random() < math.exp(-delta / temp):
            current_state = next_state
            current_path.append(move)
            visited.add(state_to_tuple(next_state))

        temp *= cooling_rate
        if len(current_path) > 1000:
            return None, 0

    return (current_path, len(current_path)) if current_state == goal else (None, 0)

def beam_search(initial, goal, beam_width=3):
    priority_queue = PriorityQueue()
    priority_queue.put((manhattan_distance(initial, goal), initial, []))
    visited = set([state_to_tuple(initial)])
    while not priority_queue.empty():
        beam = []
        for _ in range(beam_width):
            if priority_queue.empty():
                break
            h, state, path = priority_queue.get()
            beam.append((h, state, path))
            if state == goal:
                return path, 0
        next_states = []
        for h, state, path in beam:
            blank_x, blank_y = find_blank(state)
            for move_x, move_y in moves:
                new_x, new_y = blank_x + move_x, blank_y + move_y
                if is_valid(new_x, new_y):
                    new_state = deepcopy(state)
                    new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                    new_tuple = state_to_tuple(new_state)
                    if new_tuple not in visited:
                        visited.add(new_tuple)
                        h_value = manhattan_distance(new_state, goal)
                        next_states.append((h_value, new_state, path + [(new_x, new_y)]))
        next_states.sort(key=lambda x: x[0])
        for state_info in next_states[:beam_width]:
            priority_queue.put(state_info)
        if priority_queue.empty():
            return None, 0
    return None, 0

def and_or_search(initial, goal, max_depth=15):
    memo = {}
    
    def or_search(state, path, depth):
        # Nếu trạng thái hiện tại là mục tiêu, trả về kế hoạch rỗng
        if state == goal:
            return []
        
        state_tuple = state_to_tuple(state)
        # Kiểm tra độ sâu và chu kỳ
        if depth <= 0 or state_tuple in path:
            return None
        # Kiểm tra memoization
        if state_tuple in memo:
            return memo[state_tuple]
        
        blank_x, blank_y = find_blank(state)
        # Thử từng hành động (di chuyển ô trống)
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                # Tạo trạng thái mới bằng cách hoán đổi ô trống với ô mới
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_path = path | {state_tuple}  # Cập nhật đường đi
                # Gọi and_search cho trạng thái mới
                plan = and_search(new_state, new_path, depth - 1)
                if plan is not None:
                    # Nếu tìm được kế hoạch, lưu vào memo và trả về
                    memo[state_tuple] = [(new_x, new_y)] + plan  # Trả về vị trí mới của ô trống
                    return memo[state_tuple]
        # Nếu không hành động nào thành công, lưu thất bại vào memo
        memo[state_tuple] = None
        return None

    def and_search(state, path, depth):
        # Nếu trạng thái hiện tại là mục tiêu, trả về kế hoạch rỗng
        if state == goal:
            return []
        
        state_tuple = state_to_tuple(state)
        # Kiểm tra độ sâu và chu kỳ
        if depth <= 0 or state_tuple in path:
            return None
        # Kiểm tra memoization
        if state_tuple in memo:
            return memo[state_tuple]
        
        blank_x, blank_y = find_blank(state)
        # Trong 8-puzzle, mỗi hành động chỉ dẫn đến một trạng thái, nên chỉ cần một nhánh thành công
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_path = path | {state_tuple}
                plan = or_search(new_state, new_path, depth - 1)
                if plan is not None:
                    memo[state_tuple] = [(new_x, new_y)] + plan  # Trả về vị trí mới của ô trống
                    return memo[state_tuple]
        memo[state_tuple] = None
        return None

    # Gọi or_search để bắt đầu tìm kiếm
    result = or_search(initial, set(), max_depth)
    return result, 0  # Trả về (danh sách vị trí, số trạng thái mở rộng)

def genetic_algorithm(initial, goal, population_size=100, generations=100, mutation_rate=0.2):
    def is_solvable(state):
        flat_state = [x for row in state for x in row if x != 0]
        inversions = 0
        for i in range(len(flat_state)):
            for j in range(i + 1, len(flat_state)):
                if flat_state[i] > flat_state[j]:
                    inversions += 1
        return inversions % 2 == 0  # Dành cho puzzle 3x3 với ô trống ở dưới cùng bên phải trong mục tiêu

    def fitness(state):
        return manhattan_distance(state, goal)

    def create_individual():
        state = deepcopy(initial)
        path = []
        blank_x, blank_y = find_blank(state)
        visited = set([state_to_tuple(state)])
        for _ in range(random.randint(10, 30)):  # Giảm phạm vi để có đường dẫn ngắn hơn
            valid_moves = [(blank_x + dx, blank_y + dy) for dx, dy in moves 
                          if is_valid(blank_x + dx, blank_y + dy)]
            if not valid_moves:
                break
            move = random.choice(valid_moves)
            new_x, new_y = move
            state[blank_x][blank_y], state[new_x][new_y] = state[new_x][new_y], state[blank_x][blank_y]
            new_tuple = state_to_tuple(state)
            if new_tuple in visited:
                state[blank_x][blank_y], state[new_x][new_y] = state[new_x][new_y], state[blank_x][blank_y]
                continue
            visited.add(new_tuple)
            path.append(move)
            blank_x, blank_y = new_x, new_y
        if not is_solvable(state):
            return create_individual()  # Tái tạo nếu không giải được
        return state, path

    def apply_path(state, path):
        current = deepcopy(state)
        blank_x, blank_y = find_blank(current)
        valid_path = []
        visited = set([state_to_tuple(current)])
        for move in path:
            new_x, new_y = move
            if (is_valid(new_x, new_y) and 
                abs(new_x - blank_x) + abs(new_y - blank_y) == 1):
                current[blank_x][blank_y], current[new_x][new_y] = current[new_x][new_y], current[blank_x][blank_y]
                new_tuple = state_to_tuple(current)
                if new_tuple in visited:
                    current[blank_x][blank_y], current[new_x][new_y] = current[new_x][new_y], current[blank_x][blank_y]
                    continue
                visited.add(new_tuple)
                valid_path.append(move)
                blank_x, blank_y = new_x, new_y
            else:
                break
        return current, valid_path

    def reproduce(parent1, parent2):
        path1, path2 = parent1[1], parent2[1]
        n = min(len(path1), len(path2))
        if n == 0:
            return deepcopy(parent1)
        c = random.randint(0, n)
        child_path = path1[:c] + path2[c:]
        child_state, valid_child_path = apply_path(initial, child_path)
        if not is_solvable(child_state):
            return create_individual()
        return child_state, valid_child_path

    def mutate(individual):
        state, path = individual
        blank_x, blank_y = find_blank(state)
        for _ in range(random.randint(1, 3)):
            valid_moves = [(blank_x + dx, blank_y + dy) for dx, dy in moves 
                          if is_valid(blank_x + dx, blank_y + dy)]
            if valid_moves:
                move = random.choice(valid_moves)
                new_x, new_y = move
                state[blank_x][blank_y], state[new_x][new_y] = state[new_x][new_y], state[blank_x][blank_y]
                path.append(move)
                blank_x, blank_y = new_x, new_y
        if not is_solvable(state):
            return create_individual()
        return state, path

    # Khởi tạo quần thể
    population = [create_individual() for _ in range(population_size)]
    best_individual = min(population, key=lambda x: fitness(x[0]))
    best_fitness = fitness(best_individual[0])

    for gen in range(generations):
        fitness_scores = [fitness(state) for state, _ in population]
        if min(fitness_scores) == 0:
            for i, score in enumerate(fitness_scores):
                if score == 0:
                    return population[i][1], 0
            return best_individual[1], 0

        # Cập nhật cá thể tốt nhất
        current_best = min(population, key=lambda x: fitness(x[0]))
        current_best_fitness = fitness(current_best[0])
        if current_best_fitness < best_fitness:
            best_individual = current_best
            best_fitness = current_best_fitness

        # Trọng số lựa chọn
        max_fit = max(fitness_scores)
        weights = [max_fit - f + 1 for f in fitness_scores]

        # Tạo quần thể mới
        new_population = [best_individual]  # Elitism: giữ cá thể tốt nhất
        while len(new_population) < population_size:
            parent1, parent2 = random.choices(population, weights=weights, k=2)
            child = reproduce(parent1, parent2)
            if random.random() < mutation_rate:
                child = mutate(child)
            new_population.append(child)

        population = new_population

    # Nếu không tìm thấy giải pháp, thử A* từ trạng thái tốt nhất đến mục tiêu
    if best_fitness > 0:
        best_state = best_individual[0]
        path_to_best = best_individual[1]
        remaining_path, _ = a_star(best_state, goal)
        if remaining_path:
            return path_to_best + remaining_path, 0
    return best_individual[1], 0

# CSP-Backtracking Framework
def backtracking_search(initial, goal, max_depth=30):
    # Tạo bài toán CSP với các thông số cần thiết
    csp = {
        "state": deepcopy(initial),
        "goal": goal,
        "max_depth": max_depth,
        "visited": set([state_to_tuple(initial)])
    }
    # Gọi hàm BACKTRACK với assignment rỗng ban đầu
    result = backtrack(csp, [])
    return result, 0

def backtrack(csp, assignment):
    # Nếu assignment đã hoàn thành (tìm thấy trạng thái đích)
    if csp["state"] == csp["goal"]:
        return assignment
    
    # Nếu đã đạt đến độ sâu tối đa
    if len(assignment) >= csp["max_depth"]:
        return None
    
    # Chọn biến chưa gán giá trị - ở đây là lựa chọn vị trí để di chuyển
    blank_x, blank_y = find_blank(csp["state"])
    
    # Tạo danh sách các giá trị có thể cho biến
    domain_values = []
    for dx, dy in moves:
        nx, ny = blank_x + dx, blank_y + dy
        if is_valid(nx, ny):
            # Tạo trạng thái mới khi di chuyển ô trống
            new_state = deepcopy(csp["state"])
            new_state[blank_x][blank_y], new_state[nx][ny] = new_state[nx][ny], new_state[blank_x][blank_y]
            new_tuple = state_to_tuple(new_state)
            
            # Kiểm tra tính nhất quán (không đi đến trạng thái đã thăm)
            if new_tuple not in csp["visited"]:
                # Sắp xếp domain values theo heuristic
                h = manhattan_distance(new_state, csp["goal"])
                domain_values.append((h, new_state, (nx, ny)))
    
    # Sắp xếp domain values theo heuristic (ORDER-DOMAIN-VALUES)
    domain_values.sort()   
    # Duyệt qua các giá trị có thể
    for _, new_state, move in domain_values:
        # Gán giá trị cho biến (thêm bước di chuyển vào assignment)
        assignment.append(move)
        
        # Cập nhật trạng thái và các thông tin khác
        old_state = csp["state"]
        csp["state"] = new_state
        csp["visited"].add(state_to_tuple(new_state))
        
        # Gọi đệ quy để tiếp tục tìm kiếm (INFERENCE không được sử dụng)
        result = backtrack(csp, assignment)
        
        # Nếu tìm thấy kết quả, trả về
        if result is not None:
            return result
        
        # Nếu không, quay lui (backtrack)
        assignment.pop()
        csp["state"] = old_state
    
    return None

def constraint_satisfaction(initial, goal, max_steps=50):
    visited = set([state_to_tuple(initial)])
    current_state = deepcopy(initial)
    path = []

    def get_arcs(state):
        """Trả về danh sách các cung (arc) giữa các ô liền kề có thể trao đổi giá trị"""
        arcs = []
        for i in range(len(state)):
            for j in range(len(state[0])):
                for dx, dy in moves:
                    ni, nj = i + dx, j + dy
                    if is_valid(ni, nj):
                        arcs.append(((i, j), (ni, nj)))
        return arcs

    def revise(state, xi, xj):
        """Loại bỏ giá trị không hợp lệ ở xi dựa trên xj"""
        revised = False
        # Nếu xi hoặc xj là ô trống, bỏ qua
        if state[xi[0]][xi[1]] == 0 or state[xj[0]][xj[1]] == 0:
            return False
        if state[xi[0]][xi[1]] == state[xj[0]][xj[1]]:
            state[xi[0]][xi[1]] = 0  # loại bỏ giá trị
            revised = True
        return revised

    def ac3(state):
        """Thuật toán AC-3: loại bỏ giá trị không hợp lệ trong trạng thái"""
        queue = deque(get_arcs(state))
        while queue:
            xi, xj = queue.popleft()
            if revise(state, xi, xj):
                for dx, dy in moves:
                    ni, nj = xi[0] + dx, xi[1] + dy
                    if is_valid(ni, nj) and (ni, nj) != xj:
                        queue.append(((ni, nj), xi))
        return state

    # Áp dụng AC-3 như bước tiền xử lý
    current_state = ac3(current_state)
    def mrv_selection(state):
        """Selects next variables to try using MRV (Minimum Remaining Values) heuristic"""
        blank_x, blank_y = find_blank(state)
        candidates = []
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                if state_to_tuple(new_state) not in visited:
                    # Tính heuristic (giá trị nhỏ → tốt hơn)
                    h_score = manhattan_distance(new_state, goal)
                    candidates.append(((new_x, new_y), h_score))

        # Sắp xếp theo giá trị heuristic tăng dần (MRV)
        candidates.sort(key=lambda x: x[1])
        return [pos for pos, _ in candidates]

    step_count = 0
    while step_count < max_steps and current_state != goal:
        variables = mrv_selection(current_state)
        if not variables:
            if not path:
                return None, 0
            visited.remove(state_to_tuple(current_state))
            last_move = path.pop()
            blank_x, blank_y = find_blank(current_state)
            move_x, move_y = last_move
            current_state[blank_x][blank_y], current_state[move_x][move_y] = current_state[move_x][move_y], current_state[blank_x][blank_y]
            step_count += 1
            continue

        move = variables[0]
        blank_x, blank_y = find_blank(current_state)
        new_state = deepcopy(current_state)
        new_state[blank_x][blank_y], new_state[move[0]][move[1]] = new_state[move[0]][move[1]], new_state[blank_x][blank_y]

        current_state = new_state
        visited.add(state_to_tuple(current_state))
        path.append(move)
        step_count += 1

        if manhattan_distance(current_state, goal) < manhattan_distance(initial, goal) * 0.5:
            visited = set([state_to_tuple(current_state)])

        if step_count > max_steps * 0.7 and manhattan_distance(current_state, goal) >= manhattan_distance(initial, goal):
            remaining_path, _ = a_star(current_state, goal)
            if remaining_path:
                return path + remaining_path, 0

    return (path if current_state == goal else None), 0

def trust_based_search(initial, goal, max_expanded=200000):
    def calculate_trust_score(state, heuristic, visited_states):
        trust_factor = 0
        if visited_states:
            avg_distance = sum(manhattan_distance(state, visited_state) 
                             for visited_state in visited_states[:10]) / min(len(visited_states), 10)
            trust_factor = 1 / (1 + avg_distance)  # Trust factor giảm dần theo khoảng cách
        # Điều chỉnh trust_factor để không vượt quá heuristic
        trust_factor = min(trust_factor, 0.5)  # Giới hạn tối đa 0.5
        return -heuristic * (1 - trust_factor)  # Trust ảnh hưởng theo tỷ lệ

    # Khởi tạo hàng đợi với heuristic và trust score
    initial_heuristic = manhattan_distance(initial, goal) + linear_conflict(initial, goal)
    initial_trust = calculate_trust_score(initial, initial_heuristic, [])
    pq = [(initial_trust, 0, initial, initial_heuristic, [initial])]  # (trust_score, step, state, heuristic, path)
    visited = set([state_to_tuple(initial)])
    expanded = 0
    recent_visited = []

    while pq and expanded < max_expanded:
        trust_score, step, current_state, current_heuristic, path = heapq.heappop(pq)
        expanded += 1
        
        if current_state == goal:
            return states_to_moves(path), expanded
        
        recent_visited.append(current_state)
        if len(recent_visited) > 10:
            recent_visited.pop(0)
        
        for next_state in get_next_states(current_state):
            next_state_tuple = state_to_tuple(next_state)
            if next_state_tuple not in visited:
                visited.add(next_state_tuple)
                step += 1
                # Tính heuristic một lần và lưu trữ
                next_heuristic = manhattan_distance(next_state, goal) + linear_conflict(next_state, goal)
                next_trust = calculate_trust_score(next_state, next_heuristic, recent_visited)
                heapq.heappush(pq, (next_trust, step, next_state, next_heuristic, path + [next_state]))
    
    return None, expanded
def run_trust_partial_search(initial, goal, max_steps=200000):
    known_goal_row = [1, 2, 3]
    full_goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    
    def calculate_row_heuristic(state, known_goal_row):
        state_row_1 = [state[0][j] for j in range(3)]
        mismatches = sum(1 for a, b in zip(state_row_1, known_goal_row) if a != b)
        return mismatches
    
    def calculate_trust_score(state, visited_states):
        row_heuristic = calculate_row_heuristic(state, known_goal_row)
        state_row_1 = [state[0][j] for j in range(3)]
        row_match_score = sum(1 for a, b in zip(state_row_1, known_goal_row) if a == b)
        row_trust = row_match_score * 2
        trust_factor = 0
        if visited_states:
            good_states = [s for s in visited_states if [s[0][j] for j in range(3)] == known_goal_row]
            if good_states:
                avg_distance = sum(manhattan_distance(state, s) for s in good_states) / len(good_states)
                trust_factor = 1 / (1 + avg_distance)
        return -(row_heuristic - row_trust - trust_factor)

    pq = [(calculate_trust_score(initial, []), initial, [initial])]
    visited = set([state_to_tuple(initial)])
    expanded = 0
    recent_visited = []
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    states = [initial]

    for _ in range(max_steps):
        if not pq:
            break
        score, state, path = heapq.heappop(pq)
        expanded += 1
        state_row_1 = [state[0][j] for j in range(3)]
        if state == full_goal:
            return states, expanded
        if state_row_1 == known_goal_row:
            states.append(state)
        recent_visited.append(state)
        if len(recent_visited) > 10:
            recent_visited.pop(0)
        blank_x, blank_y = find_blank(state)
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_state_tuple = state_to_tuple(new_state)
                if new_state_tuple not in visited:
                    visited.add(new_state_tuple)
                    new_path = path + [new_state]
                    new_score = calculate_trust_score(new_state, recent_visited)
                    heapq.heappush(pq, (new_score, new_state, new_path))
                    states.append(new_state)

    return states, expanded

# Hàm kiểm tra tính khả thi
def is_solvable(state):
    flat_state = [x for row in state for x in row if x != 0]
    inversions = 0
    for i in range(len(flat_state)):
        for j in range(i + 1, len(flat_state)):
            if flat_state[i] > flat_state[j]:
                inversions += 1
    return inversions % 2 == 0

# Hàm hiển thị tự động các trạng thái
def display_solution(states, known_goal_row):
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Solution Playback")
    font = pygame.font.Font(None, 36)
    
    tile_size = 120
    spacing = 15
    start_x = (600 - 3 * (tile_size + spacing)) // 2
    start_y = (400 - 3 * (tile_size + spacing)) // 2

    # Lọc các trạng thái: không hiển thị trạng thái có hàng đầu tiên khớp với known_goal_row
    filtered_states = [
        state for state in states
        if [state[0][j] for j in range(3)] != known_goal_row
    ]

    if not filtered_states:
        print("Không có trạng thái nào để hiển thị sau khi lọc!")
        pygame.quit()
        return

    running = True
    current_state_idx = 0

    while running:
        screen.fill((255, 255, 255))

        # Hiển thị trạng thái hiện tại
        state = filtered_states[current_state_idx]
        draw_state(screen, deepcopy(state), start_x, start_y, tile_size)

        # Hiển thị thông báo
        message = font.render(f"State {current_state_idx + 1}/{len(filtered_states)}", True, (0, 0, 0))
        message_rect = message.get_rect(center=(300, start_y - 30))
        screen.blit(message, message_rect)

        pygame.display.flip()

        # Chuyển sang trạng thái tiếp theo sau 1 giây
        time.sleep(1)
        current_state_idx = (current_state_idx + 1) % len(filtered_states)

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()


# Hàm kiểm tra tính khả thi
def is_solvable(state):
    flat_state = [x for row in state for x in row if x != 0]
    inversions = 0
    for i in range(len(flat_state)):
        for j in range(i + 1, len(flat_state)):
            if flat_state[i] > flat_state[j]:
                inversions += 1
    return inversions % 2 == 0

# Hàm hiển thị tự động các trạng thái
def display_solution(states, known_goal_row):
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Solution Playback")
    font = pygame.font.Font(None, 36)
    
    tile_size = 100
    spacing = 10
    start_x = (600 - 3 * (tile_size + spacing) + spacing) // 2
    start_y = (400 - 3 * (tile_size + spacing) + spacing) // 2

    # Lọc các trạng thái: không hiển thị trạng thái có hàng đầu tiên khớp với known_goal_row
    filtered_states = [
        state for state in states
        if [state[0][j] for j in range(3)] != known_goal_row
    ]

    if not filtered_states:
        print("Không có trạng thái nào để hiển thị sau khi lọc!")
        pygame.quit()
        return

    running = True
    current_state_idx = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((255, 255, 255))

        # Hiển thị trạng thái hiện tại
        state = filtered_states[current_state_idx]
        for i in range(3):
            for j in range(3):
                num = state[i][j]
                x = start_x + j * (tile_size + spacing)
                y = start_y + i * (tile_size + spacing)
                pygame.draw.rect(screen, (200, 200, 200), (x, y, tile_size, tile_size))
                if num != 0:
                    text = font.render(str(num), True, (0, 0, 0))
                    text_rect = text.get_rect(center=(x + tile_size // 2, y + tile_size // 2))
                    screen.blit(text, text_rect)

        # Hiển thị thông báo
        message = font.render(f"State {current_state_idx + 1}/{len(filtered_states)}", True, (0, 0, 0))
        message_rect = message.get_rect(center=(300, start_y - 30))
        screen.blit(message, message_rect)

        pygame.display.flip()

        # Chuyển sang trạng thái tiếp theo sau 1 giây
        time.sleep(1)
        current_state_idx = (current_state_idx + 1) % len(filtered_states)

    pygame.quit()

# Hàm kiểm tra tính khả thi
def is_solvable(state):
    flat_state = [x for row in state for x in row if x != 0]
    inversions = 0
    for i in range(len(flat_state)):
        for j in range(i + 1, len(flat_state)):
            if flat_state[i] > flat_state[j]:
                inversions += 1
    return inversions % 2 == 0

# Hàm hiển thị tự động các trạng thái
def display_solution(states, known_goal_row):
    pygame.init()
    screen = pygame.display.set_mode((600, 400))
    pygame.display.set_caption("Solution Playback")
    font = pygame.font.Font(None, 36)
    
    tile_size = 120
    spacing = 15
    start_x = (600 - 3 * (tile_size + spacing)) // 2
    start_y = (400 - 3 * (tile_size + spacing)) // 2

    # Lọc các trạng thái: không hiển thị trạng thái có hàng đầu tiên khớp với known_goal_row
    filtered_states = [
        state for state in states
        if [state[0][j] for j in range(3)] != known_goal_row
    ]

    if not filtered_states:
        print("Không có trạng thái nào để hiển thị sau khi lọc!")
        pygame.quit()
        return

    running = True
    current_state_idx = 0

    while running:
        screen.fill((255, 255, 255))

        # Hiển thị trạng thái hiện tại
        state = filtered_states[current_state_idx]
        draw_state(screen, deepcopy(state), start_x, start_y, tile_size)

        # Hiển thị thông báo
        message = font.render(f"State {current_state_idx + 1}/{len(filtered_states)}", True, (0, 0, 0))
        message_rect = message.get_rect(center=(300, start_y - 30))
        screen.blit(message, message_rect)

        pygame.display.flip()

        # Chuyển sang trạng thái tiếp theo sau 1 giây
        time.sleep(1)
        current_state_idx = (current_state_idx + 1) % len(filtered_states)

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()

def trust_based_search_partial(initial, goal, screen, states_history):
    # Kiểm tra tính khả thi của trạng thái ban đầu
    if not is_solvable(initial):
        print("Trạng thái ban đầu không thể giải được!")
        return None, 0

    font = pygame.font.Font(None, 36)
    label_font = pygame.font.Font(None, 24)
    
    # Đảm bảo states_history là danh sách
    if not isinstance(states_history, list):
        current_states = [(initial, [initial])]  # (state, path)
    else:
        current_states = [(deepcopy(s), [deepcopy(s)]) for s in states_history]
    
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Phải, xuống, trái, lên
    step = 0
    expanded = 0
    found_goal = False
    full_goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    known_goal_row = full_goal[0]  # Hàng đầu tiên: [1, 2, 3]
    visited = set(map(state_to_tuple, [s for s, _ in current_states]))

    next_button = pygame.Rect(900, 10, 200, 60)
    back_button = pygame.Rect(680, 10, 200, 60)
    running = True
    
    # Hàm tính heuristic dựa trên hàng đang tập trung
    def calculate_row_heuristic(state, target_row, row_idx):
        state_row = [state[row_idx][j] for j in range(3)]
        mismatches = sum(1 for a, b in zip(state_row, target_row) if a != b)
        return mismatches
    
    # Hàm xác định hàng nào cần tập trung
    def get_focus_row(state):
        if [state[0][j] for j in range(3)] != full_goal[0]:
            return 0  # Tập trung vào hàng 1
        if [state[1][j] for j in range(3)] != full_goal[1]:
            return 1  # Tập trung vào hàng 2
        if [state[2][j] for j in range(3)] != full_goal[2]:
            return 2  # Tập trung vào hàng 3
        return None  # Đã đạt mục tiêu

    # Hàm tìm bước di chuyển tốt nhất để làm giống hàng mục tiêu
    def get_best_move(state, blank_x, blank_y, focus_row):
        target_row = full_goal[focus_row]
        best_move = None
        best_mismatch = float('inf')
        
        for move_x, move_y in moves:
            new_x, new_y = blank_x + move_x, blank_y + move_y
            if is_valid(new_x, new_y):
                new_state = deepcopy(state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                # Tính số mismatch cho hàng đang tập trung
                mismatch = calculate_row_heuristic(new_state, target_row, focus_row)
                # Ưu tiên trạng thái làm giống hàng hiện tại
                if mismatch < best_mismatch:
                    best_mismatch = mismatch
                    best_move = (move_x, move_y)
                elif mismatch == best_mismatch:
                    # Nếu số mismatch bằng nhau, ưu tiên di chuyển ô trống gần vị trí cần sửa
                    target_pos = None
                    for j in range(3):
                        if new_state[focus_row][j] != target_row[j]:
                            target_pos = (focus_row, j)
                            break
                    if target_pos:
                        dist_current = abs(new_x - target_pos[0]) + abs(new_y - target_pos[1])
                        dist_best = abs(blank_x + best_move[0] - target_pos[0]) + abs(blank_y + best_move[1] - target_pos[1])
                        if dist_current < dist_best:
                            best_move = (move_x, move_y)
        
        return best_move

    while running:
        screen.fill((255, 255, 255))
        
        tile_size = 120
        spacing = 15
        total_width = 8 * (tile_size + spacing) - spacing
        total_height = 5 * (tile_size + spacing + 25) - spacing
        start_x = (1800 - total_width) // 2
        start_y = (1030 - total_height) // 2 + 50

        for i, (state, _) in enumerate(current_states[:40]):
            row = i // 8
            col = i % 8
            x_pos = start_x + col * (tile_size + spacing)
            y_pos = start_y + row * (tile_size + spacing + 25)
            label_text = label_font.render(f"State {i+1}", True, (0, 0, 0))
            label_rect = label_text.get_rect(center=(x_pos + tile_size // 2, y_pos - 15))
            screen.blit(label_text, label_rect)
            draw_state(screen, deepcopy(state), x_pos, y_pos, tile_size)

        pygame.draw.rect(screen, (0, 128, 255), next_button, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), next_button, 2, border_radius=10)
        next_text = font.render("Tiếp theo", True, (255, 255, 255))
        next_text_rect = next_text.get_rect(center=next_button.center)
        screen.blit(next_text, next_text_rect)

        pygame.draw.rect(screen, (255, 99, 71), back_button, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), back_button, 2, border_radius=10)
        back_text = font.render("Trở về", True, (255, 255, 255))
        back_text_rect = back_text.get_rect(center=back_button.center)
        screen.blit(back_text, back_text_rect)

        if found_goal:
            message = font.render("Goal State Reached for Belief Set", True, (255, 0, 0))
            message_rect = message.get_rect(center=(1800 // 2, start_y + total_height + 30))
            screen.blit(message, message_rect)
            message2 = font.render("Press SPACE to continue", True, (255, 0, 0))
            message2_rect = message2.get_rect(center=(1800 // 2, start_y + total_height + 70))
            screen.blit(message2, message2_rect)

        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None, expanded
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    running = False
                    break
                elif not found_goal and next_button.collidepoint(event.pos):
                    step += 1
                    new_states = []
                    for state, path in current_states:
                        # Kiểm tra trạng thái hiện tại
                        state_row_1 = [state[0][j] for j in range(3)]
                        blank_x, blank_y = find_blank(state)
                        new_state = deepcopy(state)
                        moved = False

                        # Xác định hàng cần tập trung
                        focus_row = get_focus_row(state)
                        if focus_row is None:  # Đã đạt mục tiêu
                            found_goal = True
                            new_states = [(state, path)]
                            break

                        # Nếu hàng 1 đã khớp, ưu tiên làm giống các hàng tiếp theo
                        best_move = get_best_move(state, blank_x, blank_y, focus_row)
                        if best_move:
                            move_x, move_y = best_move
                            new_x, new_y = blank_x + move_x, blank_y + move_y
                            new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                            new_state_tuple = state_to_tuple(new_state)
                            if new_state_tuple not in visited:
                                visited.add(new_state_tuple)
                                if new_state == full_goal:
                                    found_goal = True
                                    new_states = [(new_state, path + [new_state])]
                                    break
                                new_states.append((new_state, path + [new_state]))
                                expanded += 1
                                moved = True
                        
                        if not moved:  # Nếu không tìm được bước di chuyển tốt, giữ nguyên trạng thái
                            new_states.append((state, path))
                    
                    current_states = new_states[:40]
                    if found_goal:
                        break
            elif event.type == pygame.KEYDOWN:
                if found_goal and event.key == pygame.K_SPACE:
                    running = False
                    break
                elif event.key == pygame.K_ESCAPE:
                    running = False
                    break

    if found_goal:
        # Lấy path của trạng thái mục tiêu
        final_state, final_path = current_states[0]
        if final_state != full_goal:
            print("Lỗi: Trạng thái cuối không khớp với mục tiêu!")
            pygame.quit()
            return None, expanded
        
        # Hiển thị tự động các trạng thái
        display_solution(final_path, known_goal_row)
        
        solution = states_to_moves(final_path)
        pygame.quit()
        return solution, expanded
    
    pygame.quit()
    return None, expanded
def draw_state(screen, state, offset_x, offset_y, tile_size=120):
    font_size = tile_size // 3
    font = pygame.font.Font(None, font_size)
    
    TILE_COLOR = (200, 200, 200)
    BLACK = (0, 0, 0)
    SHADOW_COLOR = (150, 150, 150)
    BLUR_COLOR = (150, 150, 150, 128)  # Màu xám trong suốt để làm mờ
    HIGHLIGHT_COLOR = (0, 255, 0, 128)  # Màu xanh lá trong suốt để làm nổi bật
    
    # Kiểm tra hàng đầu
    state_row_1 = [state[0][j] for j in range(3)]
    known_goal_row = [1, 2, 3]
    is_blurred = state_row_1 != known_goal_row
    is_highlighted = state_row_1 == known_goal_row

    for i in range(3):
        for j in range(3):
            x, y = offset_x + j * tile_size // 3, offset_y + i * tile_size // 3
            if state[i][j] != 0:
                # Vẽ bóng
                pygame.draw.rect(screen, SHADOW_COLOR,
                                 (x + 5, y + 5, tile_size // 3 - 2, tile_size // 3 - 2),
                                 border_radius=5)
                
                # Vẽ gradient
                for k in range(3):
                    offset = k * 2
                    color_offset = k * 3
                    gradient_color = (
                        max(0, TILE_COLOR[0] - color_offset),
                        max(0, TILE_COLOR[1] - color_offset),
                        max(0, TILE_COLOR[2] - color_offset)
                    )
                    pygame.draw.rect(screen, gradient_color,
                                     (x + offset, y + offset, 
                                      tile_size // 3 - offset * 2, tile_size // 3 - offset * 2),
                                     border_radius=5)
                
                # Vẽ viền
                pygame.draw.rect(screen, BLACK,
                                 (x, y, tile_size // 3, tile_size // 3),
                                 2, border_radius=5)
                
                # Vẽ số
                text = font.render(str(state[i][j]), True, BLACK)
                text_rect = text.get_rect(center=(x + tile_size // 6, y + tile_size // 6))
                screen.blit(text, text_rect)
    
    # Làm mờ nếu hàng đầu không khớp
    if is_blurred:
        blur_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        blur_surface.fill(BLUR_COLOR)
        screen.blit(blur_surface, (offset_x, offset_y))
    # Làm nổi bật nếu hàng đầu khớp
    elif is_highlighted:
        highlight_surface = pygame.Surface((tile_size, tile_size), pygame.SRCALPHA)
        highlight_surface.fill(HIGHLIGHT_COLOR)
        screen.blit(highlight_surface, (offset_x, offset_y))

def q_learning(initial, goal, episodes=500, max_steps=2000, alpha=0.1, gamma=0.9, epsilon_start=0.3, epsilon_min=0.01, epsilon_decay=0.99):
    def state_to_key(state):
        return tuple(tuple(row) for row in state)

    q_table = {}
    moves = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    visited = set()

    for episode in range(episodes):
        current_state = deepcopy(initial)
        total_reward = 0
        steps = 0
        epsilon = max(epsilon_min, epsilon_start * (epsilon_decay ** episode))

        while steps < max_steps:
            state_key = state_to_key(current_state)
            if state_key not in q_table:
                q_table[state_key] = {move: 0 for move in moves}

            if random.random() < epsilon:
                action = random.choice(moves)
            else:
                action = max(q_table[state_key].items(), key=lambda x: x[1])[0]

            blank_x, blank_y = find_blank(current_state)
            move_x, move_y = action
            new_x, new_y = blank_x + move_x, blank_y + move_y

            if is_valid(new_x, new_y):
                new_state = deepcopy(current_state)
                new_state[blank_x][blank_y], new_state[new_x][new_y] = new_state[new_x][new_y], new_state[blank_x][blank_y]
                new_state_key = state_to_key(new_state)

                current_distance = manhattan_distance(current_state, goal)
                new_distance = manhattan_distance(new_state, goal)
                reward = 100 if new_state == goal else (1 if current_distance > new_distance else -0.01)
                if state_to_key(new_state) in visited:
                    reward -= 0.5

                if new_state_key not in q_table:
                    q_table[new_state_key] = {move: 0 for move in moves}
                max_future_q = max(q_table[new_state_key].values()) if q_table[new_state_key] else 0
                old_q = q_table[state_key][action]
                q_table[state_key][action] = old_q + alpha * (reward + gamma * max_future_q - old_q)

                current_state = new_state
                total_reward += reward
                steps += 1

                if current_state == goal:
                    break
            else:
                continue

        visited.add(state_key)

    path = []
    current_state = deepcopy(initial)
    steps = 0
    while steps < max_steps and current_state != goal:
        state_key = state_to_key(current_state)
        if state_key not in q_table or not q_table[state_key]:
            break
        action = max(q_table[state_key].items(), key=lambda x: x[1])[0]
        blank_x, blank_y = find_blank(current_state)
        move_x, move_y = action
        new_x, new_y = blank_x + move_x, blank_y + move_y
        if is_valid(new_x, new_y):
            current_state[blank_x][blank_y], current_state[new_x][new_y] = current_state[new_x][new_y], current_state[blank_x][blank_y]
            path.append((new_x, new_y))
        steps += 1

    if current_state != goal and manhattan_distance(current_state, goal) > 0:
        remaining_path, _ = a_star(current_state, goal)
        if remaining_path:
            path.extend(remaining_path)

    return path, len(visited)

def draw_grid(screen, state, offset_x, offset_y, title):
    font = pygame.font.Font(None, 36)
    title_font = pygame.font.Font(None, 28)
    title_text = title_font.render(title, True, TITLE_COLOR)
    screen.blit(title_text, (offset_x, offset_y - 30))
    for i in range(3):
        for j in range(3):
            x, y = offset_x + j * TILE_SIZE, offset_y + i * TILE_SIZE
            if state[i][j] != 0:
                for k in range(5):
                    offset = k * 2
                    color_offset = k * 3
                    gradient_color = (TILE_COLOR[0] - color_offset, 
                                     TILE_COLOR[1] - color_offset, 
                                     TILE_COLOR[2] - color_offset)
                    pygame.draw.rect(screen, gradient_color, 
                                   (x + offset, y + offset, 
                                    TILE_SIZE - offset*2, TILE_SIZE - offset*2), 
                                   border_radius=10)
                pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 2, border_radius=10)
                text = font.render(str(state[i][j]), True, BLACK)
                text_rect = text.get_rect(center=(x + TILE_SIZE // 2, y + TILE_SIZE // 2))
                screen.blit(text, text_rect)

def draw_buttons(screen, x, y, w, h, text, color, highlight=False):
    if highlight:
        pulse_offset = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 3
        pygame.draw.rect(screen, color, (x - int(pulse_offset), y - int(pulse_offset), 
                    w + int(pulse_offset*2), h + int(pulse_offset*2)),
                       border_radius=10)
        pygame.draw.rect(screen, (200, 255, 200), 
                       (x-3, y-3, w+6, h+6), 
                       border_radius=10)
        x = x - int(pulse_offset * 0.5)
        y = y - int(pulse_offset * 0.5)
        w = w + int(pulse_offset)
        h = h + int(pulse_offset)
        base_color = (min(color[0] + 40, 255), min(color[1] + 40, 255), min(color[2] + 40, 255))
    else:
        base_color = color
    for i in range(3):
        offset = i * 2
        if i == 0:
            gradient_color = (min(base_color[0] + 30, 255), 
                             min(base_color[1] + 30, 255), 
                             min(base_color[2] + 30, 255))
        else:
            gradient_color = (max(base_color[0] - 20*i, 0), 
                             max(base_color[1] - 20*i, 0), 
                             max(base_color[2] - 20*i, 0))
        pygame.draw.rect(screen, gradient_color, 
                       (x, y + offset + 2, w, h - (offset+2)*2), 
                       border_radius=10)
    pygame.draw.rect(screen, BLACK, (x, y, w, h), 2, border_radius=10)
    text_length = len(text)
    if text_length > 10:
        font_size = 20
    else:
        font_size = 24
    font = pygame.font.Font(None, font_size)
    text_surface = font.render(text, True, BLACK)
    text_rect = text_surface.get_rect(center=(x + w // 2, y + h // 2))
    screen.blit(text_surface, text_rect)

def draw_interface(screen, state, goal, selected_algorithm, speed, steps=0, algorithm_time=0, expanded_nodes=0):
    screen.fill(WHITE)
    current_width, current_height = screen.get_size()
    
    margin = max(10, min(15, int(current_width * 0.015)))
    title_height = int(current_height * 0.07)
    
    main_font = pygame.font.Font(None, min(48, max(32, int(current_width * 0.037))))
    main_title = main_font.render("8-PUZZLE SOLVER", True, TITLE_COLOR)
    title_shadow = main_font.render("8-PUZZLE SOLVER", True, (200, 200, 220))
    main_title_rect = main_title.get_rect(center=(current_width // 2, title_height))
    screen.blit(title_shadow, (main_title_rect.x + 2, main_title_rect.y + 2))
    screen.blit(main_title, main_title_rect)
    
    board_y = title_height * 2
    board_size = 3 * TILE_SIZE
    available_width = current_width - 2 * margin
    gap_between_boards = min(80, max(40, int(available_width * 0.1)))
    
    total_boards_width = 2 * board_size + gap_between_boards
    if total_boards_width > available_width:
        scale_factor = available_width / total_boards_width
        adjusted_board_size = int(board_size * scale_factor)
        adjusted_gap = int(gap_between_boards * scale_factor)
        left_board_x = margin
        right_board_x = left_board_x + adjusted_board_size + adjusted_gap
    else:
        left_board_x = (current_width - total_boards_width) // 2
        right_board_x = left_board_x + board_size + gap_between_boards
    
    draw_grid(screen, state, left_board_x, board_y, "Trang thai ban dau")
    draw_grid(screen, goal, right_board_x, board_y, "Trang thai dich")
    
    algo_panel_y = board_y + board_size + margin * 2
    algo_panel_height = current_height - algo_panel_y - margin
    algo_panel_width = current_width - margin * 2
    
    pygame.draw.rect(screen, PANEL_BLUE, 
                    (margin, algo_panel_y, algo_panel_width, algo_panel_height), 
                    border_radius=10)
    pygame.draw.rect(screen, BLACK, 
                    (margin, algo_panel_y, algo_panel_width, algo_panel_height), 
                    2, border_radius=10)
    
    font_size = min(32, max(24, int(current_width * 0.025)))
    font = pygame.font.Font(None, font_size)
    small_font_size = max(18, min(24, int(font_size * 0.75)))
    small_font = pygame.font.Font(None, small_font_size)
    
    title_text = font.render("THUAT TOAN & CHUC NANG", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(current_width // 2, algo_panel_y + 25))
    screen.blit(title_text, title_rect)
    
    btn_margin_x = max(5, min(10, int(algo_panel_width * 0.01)))
    btn_margin_y = max(5, min(10, int(algo_panel_height * 0.02)))
    btn_height = max(30, min(40, int(algo_panel_height * 0.07)))
    
    left_panel_width = min(algo_panel_width * 0.6, algo_panel_width - 250)
    right_panel_width = algo_panel_width - left_panel_width - margin
    
    # Danh sách các thuật toán và màu sắc tương ứng
    algorithms = [
        ("BFS", BLUE), 
        ("DFS", BLUE), 
        ("UCS", BLUE),
        ("IDDFS", BLUE),
        ("Backtracking", BLUE),
        ("CSP", BLUE),
        ("Greedy", GREEN), 
        ("A*", GREEN), 
        ("IDA*", GREEN),
        ("Beam Search", GREEN),
        ("AND-OR", GREEN),
        ("Simple Hill", RED), 
        ("Steepest Hill", RED), 
        ("Stochastic Hill", RED),
        ("Simulated Annealing", RED),
        ("Genetic Algorithm", PURPLE),
        ("Trust-Based", PURPLE),
        ("Trust-Partial", PURPLE),
        ("Q-Learning", PURPLE)
    ]
    
    algo_count = len(algorithms)
    best_columns = 5
    for cols in range(5, 2, -1):
        rows = (algo_count + cols - 1) // cols
        btn_width = (left_panel_width - (cols + 1) * btn_margin_x) / cols
        if btn_width >= 80:
            best_columns = cols
            break
    
    algo_columns = best_columns
    btn_width = (left_panel_width - (algo_columns + 1) * btn_margin_x) / algo_columns
    
    btn_all_algorithms = []
    for idx, (algo_name, algo_color) in enumerate(algorithms):
        row = idx // algo_columns
        col = idx % algo_columns
        btn_x = margin + btn_margin_x + col * (btn_width + btn_margin_x)
        btn_y = algo_panel_y + 60 + row * (btn_height + btn_margin_y)
        btn_all_algorithms.append((algo_name, btn_x, btn_y, btn_width, btn_height))
        # Truyền đúng tham số cho hàm draw_buttons
        draw_buttons(screen, btn_x, btn_y, btn_width, btn_height, algo_name, algo_color, selected_algorithm == algo_name)
    
    control_panel_x = margin + left_panel_width + margin
    
    if selected_algorithm:
        selected_y = algo_panel_y + 60
        selected_bg = pygame.Rect(control_panel_x, selected_y, right_panel_width - margin, 40)
        pygame.draw.rect(screen, LIGHT_BLUE, selected_bg, border_radius=10)
        pygame.draw.rect(screen, BLACK, selected_bg, 2, border_radius=10)
        
        algo_font_size = font_size
        if len(selected_algorithm) > 15:
            algo_font_size = int(font_size * 0.8)
        algo_font = pygame.font.Font(None, algo_font_size)
        
        selected_text = algo_font.render(f"Thuat toan: {selected_algorithm}", True, BLACK)
        selected_rect = selected_text.get_rect(
            center=(control_panel_x + right_panel_width / 2 - margin/2, selected_y + 20)
        )
        screen.blit(selected_text, selected_rect)
    
    btn_speed = []
    speed_y = algo_panel_y + 120
    speed_label = small_font.render("Toc do:", True, BLACK)
    screen.blit(speed_label, (control_panel_x, speed_y))
    
    speed_btn_width = (right_panel_width - margin - btn_margin_x * 2) / 3
    speed_y += 25
    
    slow_btn = (control_panel_x, speed_y, speed_btn_width, btn_height)
    btn_speed.append(("Slow", *slow_btn))
    draw_buttons(screen, *slow_btn, "Cham", YELLOW, speed == 0.5)
    
    normal_btn = (control_panel_x + speed_btn_width + btn_margin_x, speed_y, speed_btn_width, btn_height)
    btn_speed.append(("Normal", *normal_btn))
    draw_buttons(screen, *normal_btn, "Thuong", YELLOW, speed == 0.3)
    
    fast_btn = (control_panel_x + (speed_btn_width + btn_margin_x) * 2, speed_y, speed_btn_width, btn_height)
    btn_speed.append(("Fast", *fast_btn))
    draw_buttons(screen, *fast_btn, "Nhanh", YELLOW, speed == 0.1)
    
    btn_control = []
    control_y = speed_y + btn_height + btn_margin_y + 15
    control_label = small_font.render("Dieu khien:", True, BLACK)
    screen.blit(control_label, (control_panel_x, control_y))
    
    control_y += 25
    control_btn_width = (right_panel_width - margin - btn_margin_x) / 2
    
    available_height = algo_panel_y + algo_panel_height - control_y - margin
    if available_height < (btn_height + btn_margin_y) * 2 + 150:
        btn_height = max(25, int(available_height * 0.15))
        btn_margin_y = max(2, int(btn_margin_y * 0.5))
    
    run_btn = (control_panel_x, control_y, control_btn_width, btn_height)
    btn_control.append(("Run", *run_btn))
    draw_buttons(screen, *run_btn, "Chay", RED, False)
    
    reset_btn = (control_panel_x + control_btn_width + btn_margin_x, control_y, control_btn_width, btn_height)
    btn_control.append(("Reset", *reset_btn))
    draw_buttons(screen, *reset_btn, "Dat lai", GREEN, False)
    
    custom_btn = (control_panel_x, control_y + btn_height + btn_margin_y, control_btn_width, btn_height)
    btn_control.append(("Custom State", *custom_btn))
    draw_buttons(screen, *custom_btn, "Tuy chinh", (240, 150, 150), False)
    
    history_btn = (control_panel_x + control_btn_width + btn_margin_x, control_y + btn_height + btn_margin_y, control_btn_width, btn_height)
    btn_control.append(("View History", *history_btn))
    draw_buttons(screen, *history_btn, "Lich su", LIGHT_BLUE, False)
    
    info_y = control_y + (btn_height + btn_margin_y) * 2 + 20
    remaining_height = algo_panel_y + algo_panel_height - info_y - margin
    info_panel_height = min(120, remaining_height * 0.65)
    
    info_panel_width = right_panel_width - margin
    info_bg = pygame.Rect(control_panel_x, info_y, info_panel_width, info_panel_height)
    pygame.draw.rect(screen, (240, 240, 255), info_bg, border_radius=10)
    pygame.draw.rect(screen, BLACK, info_bg, 2, border_radius=10)
    
    info_title = small_font.render("THONG TIN GIAI:", True, TITLE_COLOR)
    screen.blit(info_title, (control_panel_x + 10, info_y + 10))
    
    steps_text = small_font.render(f"So buoc: {steps}", True, BLACK)
    screen.blit(steps_text, (control_panel_x + 15, info_y + 40))
    
    time_text = small_font.render(f"Thoi gian: {algorithm_time:.4f} giay", True, BLACK)
    screen.blit(time_text, (control_panel_x + 15, info_y + 70))
    nodes_text = small_font.render(f"Trang thai mo rong: {expanded_nodes}", True, BLACK)
    screen.blit(nodes_text, (control_panel_x + 15, info_y + 100))
    
    hint_y = info_y + info_panel_height + 10
    if hint_y + 60 < algo_panel_y + algo_panel_height - margin:
        hint_bg = pygame.Rect(control_panel_x, hint_y, right_panel_width - margin, 60)
        pygame.draw.rect(screen, LIGHT_GREEN, hint_bg, border_radius=10)
        pygame.draw.rect(screen, BLACK, hint_bg, 2, border_radius=10)
        
        hint_title = small_font.render("HUONG DAN:", True, BLACK)
        screen.blit(hint_title, (control_panel_x + 10, hint_y + 10))
        
        tiny_font = pygame.font.Font(None, max(16, small_font_size-2))
        hint_text = tiny_font.render("1. Chon thuat toan", True, BLACK)
        screen.blit(hint_text, (control_panel_x + 15, hint_y + 30))
        
        hint_text2 = tiny_font.render("2. Chon toc do > Chay", True, BLACK)
        screen.blit(hint_text2, (control_panel_x + right_panel_width // 2, hint_y + 30))
    
    return {
        "uninformed": [],
        "informed": [],
        "local": [],
        "speed": btn_speed,
        "control": btn_control,
        "algorithms": btn_all_algorithms
    }

def create_custom_state():
    root = tk.Tk()
    root.title("Chon Trang Thai Ban Dau")
    root.geometry("400x400")
    root.resizable(False, False)
    custom_state = [[0 for _ in range(3)] for _ in range(3)]
    number_used = [False] * 9
    grid_frame = tk.Frame(root)
    grid_frame.pack(pady=20)
    entries = []
    for i in range(3):
        row_entries = []
        for j in range(3):
            entry = tk.Entry(grid_frame, width=5, font=('Arial', 20), justify='center')
            entry.grid(row=i, column=j, padx=5, pady=5)
            row_entries.append(entry)
        entries.append(row_entries)
    message_label = tk.Label(root, text="Nhap cac so tu 0-8, moi so chi duoc dung mot lan.\n0 dai dien cho o trong.", fg="blue")
    message_label.pack(pady=10)
    error_label = tk.Label(root, text="", fg="red")
    error_label.pack(pady=5)
    result = {"state": None}
    def validate_state():
        for i in range(9):
            number_used[i] = False
        for i in range(3):
            for j in range(3):
                try:
                    value = int(entries[i][j].get())
                    if not (0 <= value <= 8):
                        error_label.config(text=f"Gia tri khong hop le tai [{i},{j}]: {value}. Chi chap nhan 0-8.")
                        return False
                    if number_used[value]:
                        error_label.config(text=f"So {value} da duoc su dung nhieu lan.")
                        return False
                    number_used[value] = True
                    custom_state[i][j] = value
                except ValueError:
                    error_label.config(text=f"Vui long nhap mot so tai [{i},{j}].")
                    return False
        for i in range(9):
            if not number_used[i]:
                error_label.config(text=f"So {i} chua duoc su dung.")
                return False
        return True
    def is_solvable(state):
        flat_state = []
        for i in range(3):
            for j in range(3):
                if state[i][j] != 0:
                    flat_state.append(state[i][j])
        inversions = 0
        for i in range(len(flat_state)):
            for j in range(i+1, len(flat_state)):
                if flat_state[i] > flat_state[j]:
                    inversions += 1
        blank_row = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    blank_row = i
        if blank_row % 2 == 0:
            return inversions % 2 == 1
        else:
            return inversions % 2 == 0
    def confirm_state():
        if validate_state():
            if is_solvable(custom_state):
                result["state"] = custom_state
                root.destroy()
            else:
                error_label.config(text="Trang thai nay khong the giai duoc. Vui long nhap lai.")
    def fill_random_state():
        while True:
            numbers = list(range(9))
            random.shuffle(numbers)
            for i in range(3):
                for j in range(3):
                    custom_state[i][j] = numbers[i*3 + j]
            if is_solvable(custom_state):
                break
        for i in range(3):
            for j in range(3):
                entries[i][j].delete(0, tk.END)
                entries[i][j].insert(0, str(custom_state[i][j]))
    button_frame = tk.Frame(root)
    button_frame.pack(pady=20)
    confirm_button = tk.Button(button_frame, text="Xac nhan", command=confirm_state, 
                             bg="green", fg="white", font=('Arial', 12))
    confirm_button.pack(side=tk.LEFT, padx=10)
    random_button = tk.Button(button_frame, text="Ngau nhien", command=fill_random_state, 
                            bg="blue", fg="white", font=('Arial', 12))
    random_button.pack(side=tk.LEFT, padx=10)
    cancel_button = tk.Button(button_frame, text="Huy", command=root.destroy, 
                            bg="red", fg="white", font=('Arial', 12))
    cancel_button.pack(side=tk.LEFT, padx=10)
    examples_frame = tk.Frame(root)
    examples_frame.pack(pady=10)
    example_label = tk.Label(examples_frame, text="Vi du ve trang thai co the giai:", font=('Arial', 10))
    example_label.pack()
    example_text = "2 8 3\n1 6 4\n7 0 5"
    example_state = tk.Label(examples_frame, text=example_text, font=('Courier', 10))
    example_state.pack()
    root.mainloop()
    return result["state"]

# Define a function to get a safe font that will be available on any system
def get_safe_font(size, bold=False):
    # Try to use a system font that's commonly available
    available_fonts = pygame.font.get_fonts()
    preferred_fonts = ['arial', 'freesans', 'dejavusans', 'verdana', 'timesnewroman']
    
    for font_name in preferred_fonts:
        if font_name in available_fonts:
            return SysFont(font_name, size, bold=bold)
    
    # If none of the preferred fonts are available, use the default
    try:
        return Font(None, size)
    except:
        # Last resort - pick the first available system font
        return SysFont(available_fonts[0] if available_fonts else 'freesans', size, bold=bold)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("8-Puzzle")
    initial_state = [[2, 6, 5], [0, 8, 7], [4, 3, 1]]
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    state = deepcopy(initial_state)
    states_history = [deepcopy(initial_state)]
    selected_algorithm = None
    speed = 0.3
    steps = 0
    algorithm_time = 0
    expanded_nodes = 0
    running = True
    btn_positions = {}
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if "algorithms" in btn_positions:
                    for algo_name, btn_x, btn_y, btn_w, btn_h in btn_positions["algorithms"]:
                        if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                            selected_algorithm = algo_name
                            break
                for speed_name, btn_x, btn_y, btn_w, btn_h in btn_positions["speed"]:
                    if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                        if speed_name == "Slow":
                            speed = 0.5
                        elif speed_name == "Normal":
                            speed = 0.3
                        elif speed_name == "Fast":
                            speed = 0.1
                        break
                for btn_name, btn_x, btn_y, btn_w, btn_h in btn_positions["control"]:
                    if btn_x <= x <= btn_x + btn_w and btn_y <= y <= btn_y + btn_h:
                        if btn_name == "Run":
                            if selected_algorithm:
                                start_time = time.time()
                                states_history = [deepcopy(state)]
                                algo_map = {
                                    "BFS": bfs,
                                    "DFS": dfs,
                                    "UCS": ucs,
                                    "IDDFS": iddfs,
                                    "Backtracking": backtracking_search,
                                    "CSP": constraint_satisfaction,
                                    "Greedy": greedy_search, 
                                    "A*": a_star, 
                                    "IDA*": ida_star,
                                    "Beam Search": beam_search,
                                    "AND-OR": and_or_search,
                                    "Simple Hill": simple_hill_climbing,
                                    "Steepest Hill": steepest_ascent_hill_climbing,
                                    "Stochastic Hill": stochastic_hill_climbing,
                                    "Simulated Annealing": simulated_annealing,
                                    "Genetic Algorithm": genetic_algorithm,
                                    "Trust-Based": trust_based_search,
                                    "Trust-Partial": lambda s, g: trust_based_search_partial(s, g, screen, run_trust_partial_search(s, g)[0]),
                                    "Q-Learning": q_learning
                                }
                                try:
                                    result = algo_map[selected_algorithm](state, goal)
                                    if isinstance(result, tuple) and len(result) >= 2:
                                        solution, expanded = result[0], result[1]
                                    else:
                                        solution, expanded = result, 0
                                except Exception as e:
                                    show_message("Loi thuat toan", f"Thuat toan {selected_algorithm} da gap loi: {str(e)}")
                                    solution, expanded = None, 0
                                algorithm_time = time.time() - start_time
                                expanded_nodes = expanded
                                if not pygame.get_init():
                                    running = False
                                    break
                                if solution:
                                    steps = len(solution)
                                    for move in solution:
                                        blank_x, blank_y = find_blank(state)
                                        state[blank_x][blank_y], state[move[0]][move[1]] = state[move[0]][move[1]], state[blank_x][blank_y]
                                        states_history.append(deepcopy(state))
                                        btn_positions = draw_interface(screen, state, goal, selected_algorithm, speed, steps, algorithm_time, expanded_nodes)
                                        pygame.display.flip()
                                        time.sleep(speed)
                                    show_message("Thong bao", f"Da giai xong bang {selected_algorithm}!\nSo buoc: {steps}\nThoi gian chay: {algorithm_time:.4f} giay\nTrang thai mo rong: {expanded_nodes}")
                                else:
                                    btn_positions = draw_interface(screen, state, goal, selected_algorithm, speed, steps, algorithm_time, expanded_nodes)
                                    pygame.display.flip()
                                    show_message("Thong bao", f"Khong tim thay giai phap bang {selected_algorithm}!\nThoi gian chay: {algorithm_time:.4f} giay\nTrang thai mo rong: {expanded_nodes}")
                            else:
                                show_message("Thong bao", "Vui long chon thuat toan truoc khi chay!")
                        elif btn_name == "Reset":
                            state = deepcopy(initial_state)
                            states_history = [deepcopy(initial_state)]
                            steps = 0
                            algorithm_time = 0
                            expanded_nodes = 0
                        elif btn_name == "Custom State":
                            custom_state = create_custom_state()
                            if custom_state:
                                initial_state = custom_state
                                state = deepcopy(initial_state)
                                states_history = [deepcopy(initial_state)]
                                steps = 0
                                algorithm_time = 0
                                expanded_nodes = 0
                        elif btn_name == "View History":
                            if states_history:
                                show_state_history(states_history)
                            else:
                                show_message("Thong bao", "Chua co lich su trang thai de hien thi!")
                        break
        if not running:
            break  # Thoát khỏi vòng lặp chính ngay khi running = False
        btn_positions = draw_interface(screen, state, goal, selected_algorithm, speed, steps, algorithm_time, expanded_nodes)
        pygame.display.flip()
    pygame.quit()

if __name__ == "__main__":
    main()