import ctypes

import sdl2


class Display:
    frame = None

    def __init__(self, width, height, scale=12, title="pyChip8SDL", fg=(255, 255, 255), bg=(0, 0, 0)):
        self.height = height
        self.width = width
        self.scale = scale
        self.title = title
        self.fg = fg
        self.bg = bg
        self.window = None
        self.renderer = None
        self.window_id = None

        self.reset()

    def open(self, x=None, y=None):
        if self.window:
            return

        self.window = sdl2.SDL_CreateWindow(
            self.title.encode("utf-8"),
            sdl2.SDL_WINDOWPOS_CENTERED if x is None else x,
            sdl2.SDL_WINDOWPOS_CENTERED if y is None else y,
            self.width * self.scale,
            self.height * self.scale,
            sdl2.SDL_WINDOW_SHOWN,
        )
        if not self.window:
            raise RuntimeError(f"SDL window creation failed: {sdl2.SDL_GetError().decode()}")
        self.window_id = sdl2.SDL_GetWindowID(self.window)

        self.renderer = sdl2.SDL_CreateRenderer(
            self.window, -1, sdl2.SDL_RENDERER_ACCELERATED
        )
        if not self.renderer:
            raise RuntimeError(f"SDL renderer creation failed: {sdl2.SDL_GetError().decode()}")

    def set_pixel(self, x, y, val):
        self.frame[y][x] = val

    def get_pixel(self, x, y):
        return self.frame[y][x]

    def reset(self):
        self.frame = [bytearray(self.width) for _ in range(self.height)]

    def render(self):
        sdl2.SDL_SetRenderDrawColor(self.renderer, *self.bg, 255)
        sdl2.SDL_RenderClear(self.renderer)
        sdl2.SDL_SetRenderDrawColor(self.renderer, *self.fg, 255)

        rect = sdl2.SDL_Rect()
        rect.w = self.scale
        rect.h = self.scale
        for y in range(self.height):
            row = self.frame[y]
            for x in range(self.width):
                if row[x]:
                    rect.x = x * self.scale
                    rect.y = y * self.scale
                    sdl2.SDL_RenderFillRect(self.renderer, ctypes.byref(rect))

        sdl2.SDL_RenderPresent(self.renderer)

    def shutdown(self):
        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
            self.renderer = None
        if self.window:
            sdl2.SDL_DestroyWindow(self.window)
            self.window = None
