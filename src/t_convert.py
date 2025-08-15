import pygame
import re


def markdown_to_surface(md_str, font_size=24, max_width=800, font_name=None):
    # 初始化Pygame字体
    pygame.init()
    font = pygame.font.SysFont(font_name, font_size)
    bold_font = pygame.font.SysFont(font_name, font_size, bold=True)
    small_font = pygame.font.SysFont(font_name, font_size - 4)

    # 解析Markdown元素
    elements = []
    lines = md_str.split('\n')
    in_table = False
    table_data = []

    for line in lines:
        # 处理标题
        if line.startswith('#'):
            level = min(line.find(' '), 6)
            elements.append(('heading', level, line[level + 1:].strip()))

        # 处理列表
        elif line.startswith('- '):
            elements.append(('list_item', line[2:]))

        # 处理表格
        elif '|' in line and '---' in line:
            in_table = not in_table
            if not in_table:
                elements.append(('table', table_data))
                table_data = []
        elif '|' in line and in_table:
            table_data.append([cell.strip() for cell in line.split('|')[1:-1]])

        # 处理普通段落
        elif line.strip():
            elements.append(('paragraph', line))

    # 计算所需高度和渲染元素
    y = 20
    renders = []

    for elem in elements:
        if elem[0] == 'heading':
            level = elem[1]
            text = elem[2]
            render_font = pygame.font.SysFont(font_name, font_size + 10 - level * 2, bold=True)
            surf = render_font.render(text, True, (0, 0, 0))
            renders.append((surf, (20, y)))
            y += surf.get_height() + 15

        elif elem[0] == 'list_item':
            text = elem[1]
            surf = font.render('• ' + text, True, (0, 0, 0))
            renders.append((surf, (30, y)))
            y += surf.get_height() + 5

        elif elem[0] == 'paragraph':
            text = elem[1]
            words = text.split()
            current_line = []
            current_width = 0

            for word in words:
                word_surf = font.render(word + ' ', True, (0, 0, 0))
                if current_width + word_surf.get_width() > max_width - 40:
                    line_surf = font.render(' '.join(current_line), True, (0, 0, 0))
                    renders.append((line_surf, (20, y)))
                    y += line_surf.get_height() + 5
                    current_line = [word]
                    current_width = word_surf.get_width()
                else:
                    current_line.append(word)
                    current_width += word_surf.get_width()

            if current_line:
                line_surf = font.render(' '.join(current_line), True, (0, 0, 0))
                renders.append((line_surf, (20, y)))
                y += line_surf.get_height() + 15

        # 修改表格处理部分（约88-96行）
        elif elem[0] == 'table':
            data = elem[1]
            if not data or len(data[0]) == 0:
                continue

            # 计算最大列数
            max_columns = max(len(row) for row in data) if data else 0
            col_widths = [0] * max_columns

            # 统一所有行的列数
            for row in data:
                while len(row) < max_columns:
                    row.append('')  # 补全空单元格
                for i, cell in enumerate(row):
                    if i >= max_columns:
                        break
                    width = small_font.size(cell)[0]
                    col_widths[i] = max(col_widths[i], width)

            # 创建最终Surface
    total_height = y + 20
    surface = pygame.Surface((max_width, total_height))
    surface.fill((255, 255, 255))

    for surf, pos in renders:
        surface.blit(surf, pos)

    return surface

md = open('assets/desc/true eye.md', encoding='utf-8').read()
surface = markdown_to_surface(md)
pygame.image.save(surface, 'output.png')

pygame.quit()