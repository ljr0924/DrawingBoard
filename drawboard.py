# -*- coding: utf-8 -*-
import math
import time
import pygame
from pygame.locals import *


class Brush:
    def __init__(self, screen):
        """
        初始化函数
        """
        # pygame.Surface 对象
        self.screen = screen
        self.color = (0, 0, 0)
        # 初始时候默认设置画笔大小为 1
        self.size = 4
        self.drawing = False
        self.last_pos = None
        # 如果 style 是 True，则采用png笔刷
        # 若是 style 为 False，则采用一般的铅笔画笔
        self.style = False
        # 加载刷子的样式
        self.brush = pygame.image.load("images/brush.png").convert_alpha()
        self.brush_now = self.brush.subsurface((0, 0), (self.size * 2, self.size * 2))
        # 使用橡皮擦之前的样式
        self.history = {}
        # 是否为画直线
        self.is_drawing_line = False
        self.line_start = None
        self.line_end = None
        # 是否为画矩形
        self.is_drawing_rect = False
        self.rect_start_point = None
        self.rect_end_point = None

    def start_draw(self, pos):
        """
        开始绘制，并记录当前坐标
        """
        self.drawing = True
        self.last_pos = pos

    def end_draw(self):
        """
        结束绘制
        """
        self.drawing = False

    def set_brush_style(self, style):
        """
        设置笔刷的样式
        """
        print("* set brush style to", style)
        self.style = style

    def get_brush_style(self):
        """
        获取笔刷的类型
        """
        return self.style

    def get_current_brush(self):
        """
        获取当前笔刷
        """
        return self.brush_now

    def set_size(self, size):
        """
        设置笔刷大小
        """
        if size < 1:
            size = 1
        elif size > 32:
            size = 32
        print("* set brush size to", size)
        self.size = size
        self.brush_now = self.brush.subsurface((0, 0), (size * 2, size * 2))

    def get_size(self):
        """
        获取笔刷大小
        """
        return self.size

    def set_color(self, color):
        """
        设定笔刷颜色
        """
        self.color = color
        for i in range(self.brush.get_width()):
            for j in range(self.brush.get_height()):
                self.brush.set_at(
                    (i, j),
                    color + (self.brush.get_at((i, j)).a,))

    def get_color(self):
        """
        获取笔刷颜色
        """
        return self.color

    def draw(self, pos):
        """
        绘制
        """
        if self.drawing:
            for p in self._get_points(pos):
                if self.style:
                    # 笔刷
                    self.screen.blit(self.brush_now, p)
                else:
                    # 铅笔
                    pygame.draw.circle(self.screen, self.color, p, self.size)
            self.last_pos = pos

    def draw_line(self, pos):
        """
        画直线
        """
        if not self.line_start:
            self.line_start = (pos[0], pos[1])
        elif not self.line_end:
            self.line_end = (pos[0], pos[1])
        if self.line_start and self.line_end:
            pygame.draw.line(self.screen, self.color, self.line_start, self.line_end, self.size)
            self.line_start, self.line_end = None, None

    def draw_rect(self, pos):
        """
        画直线
        """
        if not self.rect_start_point:
            self.rect_start_point = (pos[0], pos[1])
        elif not self.rect_end_point:
            self.rect_end_point = (pos[0], pos[1])
        if self.rect_start_point and self.rect_end_point:
            start = self.rect_start_point
            end = self.rect_end_point
            if self.rect_start_point[0] > self.rect_end_point[0]:
                start, end = end, start
            width = end[0] - start[0]
            height = end[1] - start[1]
            pygame.draw.rect(self.screen, self.color, ((start[0], start[1]), (width, abs(height))), self.size)
            self.rect_start_point, self.rect_end_point = None, None

    def _get_points(self, pos):
        """
        为了绘制的线条更加平滑，我们需要获取前一个点与当前点之间的所有需要绘制的点
        """
        points = [(self.last_pos[0], self.last_pos[1])]
        len_x = pos[0] - self.last_pos[0]
        len_y = pos[1] - self.last_pos[1]
        length = math.sqrt(len_x ** 2 + len_y ** 2)
        step_x = len_x / length
        step_y = len_y / length
        for i in range(int(length)):
            points.append((points[-1][0] + step_x, points[-1][1] + step_y))
        points = map(lambda x: (int(0.5 + x[0]), int(0.5 + x[1])), points)
        return list(set(points))

    def set_from_history(self, exclude):
        if 'color' in self.history and 'color' not in exclude:
            self.set_color(self.history['color'])
        if 'size' in self.history and 'size' not in exclude:
            self.set_size(self.history['size'])
        if 'style' in self.history and 'style' not in exclude:
            self.set_brush_style(self.history['style'])
        self.history = {}


class Menu:
    def __init__(self, screen):
        """
        初始化函数
        """
        self.is_color_dropper = False
        self.screen = screen
        self.brush = None
        # 画板预定义的颜色值
        self.colors = [
            (0xff, 0x00, 0xff), (0x80, 0x00, 0x80),
            (0x00, 0x00, 0xff), (0x00, 0x00, 0x80),
            (0x00, 0xff, 0xff), (0x00, 0x80, 0x80),
            (0x00, 0xff, 0x00), (0x00, 0x80, 0x00),
            (0xff, 0xff, 0x00), (0x80, 0x80, 0x00),
            (0xff, 0x00, 0x00), (0x80, 0x00, 0x00),
            (0xc0, 0xc0, 0xc0), (0xff, 0xff, 0xff),
            (0x00, 0x00, 0x00), (0x80, 0x80, 0x80),
        ]
        # 计算每个色块在画板中的坐标值，便于绘制
        self.colors_rect = []
        x = 254
        for (i, rgb) in enumerate(self.colors):
            rect = pygame.Rect(x, 10 + i % 2 * 32, 32, 32)
            if (i + 1) % 2 == 0:
                x += 32
            self.colors_rect.append(rect)
        # 两种笔刷的按钮图标
        self.pens = [
            pygame.image.load("images/pen1.png").convert_alpha(),
            pygame.image.load("images/pen2.png").convert_alpha(),
        ]
        # 计算坐标，便于绘制
        self.pens_rect = []
        for (i, img) in enumerate(self.pens):
            rect = pygame.Rect(10 + i * 64, 10, 64, 64)
            self.pens_rect.append(rect)

        # 调整笔刷大小的按钮图标
        self.sizes = [
            pygame.image.load("images/big.png").convert_alpha(),
            pygame.image.load("images/small.png").convert_alpha()
        ]
        # 计算坐标，便于绘制
        self.sizes_rect = []
        for (i, img) in enumerate(self.sizes):
            rect = pygame.Rect(138, 10 + i * 32, 32, 32)
            self.sizes_rect.append(rect)

        # 橡皮擦
        self.eraser = pygame.image.load("images/eraser.png").convert_alpha()
        self.eraser_rect = pygame.Rect(530, 10, 64, 64)
        # 取色管
        self.color_dropper = pygame.image.load("images/color-dropper.png").convert_alpha()
        self.color_dropper_rect = pygame.Rect(604, 10, 32, 32)
        # 橡皮擦
        self.is_eraser = False
        # 保存按钮
        self.save_button_rect = pygame.Rect(1200-32, 10, 32, 32)
        # 画直线
        self.draw_line_rect = pygame.Rect(638, 10, 32, 32)
        # 画矩形
        self.draw_rect_rect = pygame.Rect(638, 42, 32, 32)
        # 清屏按钮
        self.clear = pygame.Rect(1200-32, 42, 32, 32)

    def set_brush(self, brush):
        """
        设置画笔
        """
        self.brush = brush

    def set_brush_color(self, pos):
        """
        设置画笔颜色
        """
        color = self.screen.get_at((pos[0], pos[1]))
        if 'color' in self.brush.history:
            self.brush.history['color'] = color[:3]
        else:
            self.brush.set_color(color[:3])

    def draw(self):
        """
        绘制菜单栏
        """
        # 绘制画笔样式按钮
        for (i, img) in enumerate(self.pens):
            self.screen.blit(img, self.pens_rect[i].topleft)
        # 绘制 + - 按钮
        for (i, img) in enumerate(self.sizes):
            self.screen.blit(img, self.sizes_rect[i].topleft)
        # 绘制用于实时展示笔刷的小窗口
        self.screen.fill((255, 255, 255), (180, 10, 64, 64))
        pygame.draw.rect(self.screen, (0, 0, 0), (180, 10, 64, 64), 1)
        size = self.brush.get_size()
        x = 180 + 32
        y = 10 + 32
        # 如果当前画笔为 png 笔刷，则在窗口中展示笔刷
        # 如果为铅笔，则在窗口中绘制原点
        if self.brush.get_brush_style():
            x = x - size
            y = y - size
            self.screen.blit(self.brush.get_current_brush(), (x, y))
        else:
            # BUG
            pygame.draw.circle(self.screen,
                               self.brush.get_color(), (x, y), size)
        # 绘制色块
        for (i, rgb) in enumerate(self.colors):
            pygame.draw.rect(self.screen, rgb, self.colors_rect[i])

        # 绘制橡皮擦
        self.screen.blit(self.eraser, self.eraser_rect)
        # 绘制取色器
        self.screen.blit(self.color_dropper, self.color_dropper_rect)
        # 绘制保存按钮
        fontObj = pygame.font.SysFont("arial", 16)  # 通过字体文件获得字体对象
        textSurfaceObj = fontObj.render('save', True, (0,0,0), (255, 255, 255))  # 配置要显示的文字
        self.screen.blit(textSurfaceObj, self.save_button_rect)  # 绘制字体

        # 绘制画直线
        fontObj = pygame.font.SysFont("arial", 32)  # 通过字体文件获得字体对象
        textSurfaceObj = fontObj.render('line', True, (0, 0, 0), (255, 255, 255))  # 配置要显示的文字
        self.screen.blit(textSurfaceObj, self.draw_line_rect)  # 绘制字体

        # 绘制画矩形
        fontObj = pygame.font.SysFont("arial", 32)  # 通过字体文件获得字体对象
        textSurfaceObj = fontObj.render('rect', True, (0, 0, 0), (255, 255, 255))  # 配置要显示的文字
        self.screen.blit(textSurfaceObj, self.draw_rect_rect)  # 绘制字体

        # 绘制清屏
        fontObj = pygame.font.SysFont("arial", 16)  # 通过字体文件获得字体对象
        textSurfaceObj = fontObj.render('clear', True, (0, 0, 0), (255, 255, 255))  # 配置要显示的文字
        self.screen.blit(textSurfaceObj, self.clear)  # 绘制字体


    def click_button(self, pos):
        """
        定义菜单按钮的点击响应事件
        """
        x, y = pos
        # 模式初始化
        self.brush.is_drawing_line = False
        self.brush.is_drawing_rect = False
        self.is_color_dropper = False
        self.is_eraser = False

        # 清屏
        if self.clear.collidepoint(x, y):
            self.screen.fill((255,255,255))
            return True

        # 画矩形模式
        if self.draw_rect_rect.collidepoint(x, y):
            if self.is_eraser:
                pass
            pygame.display.set_caption('Painter - rect')
            self.brush.is_drawing_rect = True
            return True

        # 画直线模式
        if self.draw_line_rect.collidepoint(x, y):
            pygame.display.set_caption('Painter - line')
            self.brush.is_drawing_line = True
            return True

        # 保存画布
        if self.save_button_rect.collidepoint(x, y):
            sub = self.screen.subsurface(pygame.rect.Rect(0, 84, 1200, 800-84))
            now = int(time.time())
            pygame.image.save(sub, f'{ now }.jpg')

        # 取色器
        if self.color_dropper_rect.collidepoint(x, y):
            pygame.display.set_caption('Painter - color dropper')
            self.is_color_dropper = True
            return True

        # 橡皮擦
        if self.eraser_rect.collidepoint(x, y):
            pygame.display.set_caption('Painter - eraser')
            self.is_eraser = True
            self.brush.history['color'] = self.brush.get_color()
            self.brush.history['size'] = self.brush.get_size()
            self.brush.history['style'] = self.brush.get_brush_style()
            self.brush.set_brush_style(False)
            self.brush.set_color((0xff, 0xff, 0xff))
            self.brush.set_size(10)
            return True
        # 笔刷
        for (i, rect) in enumerate(self.pens_rect):
            # 判断点是否在Rect对象里面
            if rect.collidepoint(pos):
                self.brush.set_brush_style(bool(i))
                self.brush.set_from_history(['style'])
                size = self.brush.get_size()
                if i:
                    pygame.display.set_caption(f'Painter - brush - {size}')
                else:
                    pygame.display.set_caption(f'Painter - pencil - {size}')
                return True
        # 笔刷大小
        for (i, rect) in enumerate(self.sizes_rect):
            if rect.collidepoint(pos):
                # 画笔大小的每次改变量为 1
                if i:
                    self.brush.set_size(self.brush.get_size() - 1)
                else:
                    self.brush.set_size(self.brush.get_size() + 1)
                return True
        # 颜色
        for (i, rect) in enumerate(self.colors_rect):
            if rect.collidepoint(pos):
                self.brush.set_color(self.colors[i])
                self.brush.set_from_history(['color'])
                return True

        return False


class Painter:
    def __init__(self):
        # 设置了画板窗口的大小与标题
        self.screen = pygame.display.set_mode((1200, 800))
        pygame.display.set_caption("Painter - pencil - 4")
        # 创建 Clock 对象
        self.clock = pygame.time.Clock()
        # 创建 Brush 对象
        self.brush = Brush(self.screen)
        # 创建 Menu 对象，并设置了默认笔刷
        self.menu = Menu(self.screen)
        self.menu.set_brush(self.brush)

    def run(self):
        pygame.init()
        self.screen.fill((255, 255, 255))
        # 程序的主体是一个循环，不断对界面进行重绘，直到监听到结束事件才结束循环
        while True:
            # 设置帧率
            self.clock.tick(30)
            # 监听事件
            for event in pygame.event.get():
                # 结束事件
                if event.type == QUIT:
                    return

                # 键盘按键事件
                elif event.type == KEYDOWN:
                    # 按下 ESC 键，清屏
                    if event.key == K_ESCAPE:
                        self.screen.fill((255, 255, 255))

                # 鼠标按下事件
                elif event.type == MOUSEBUTTONDOWN:
                    mode = [self.brush.is_drawing_rect, self.brush.is_drawing_line, self.menu.is_color_dropper]
                    # 若是当前鼠标位于菜单中，则忽略掉该事件
                    # 否则调用 start_draw 设置画笔的 drawing 标志为 True
                    if event.pos[1] <= 74 and self.menu.click_button(event.pos):
                        pass
                    elif event.pos[1] >= 84 and not any(mode):
                        self.brush.start_draw(event.pos)
                    # 取色器
                    elif event.pos[1] >= 84 and self.menu.is_color_dropper:
                        self.menu.set_brush_color(event.pos)
                    elif event.pos[1] >= 84 and self.brush.is_drawing_line:
                        self.brush.draw_line(event.pos)
                    elif event.pos[1] >= 84 and self.brush.is_drawing_rect:
                        self.brush.draw_rect(event.pos)

                # 鼠标移动事件
                elif event.type == MOUSEMOTION and event.pos[1] >= 84 :
                    self.brush.draw(event.pos)

                # 松开鼠标按键事件
                elif event.type == MOUSEBUTTONUP:
                    # 调用 end_draw 设置画笔的 drawing 标志为 False
                    self.brush.end_draw()
            # 绘制菜单按钮
            self.menu.draw()
            # 刷新窗口
            pygame.display.update()


def main():
    painter = Painter()
    painter.run()


if __name__ == '__main__':
    main()
