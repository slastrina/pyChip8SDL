class Display:
    frame = None

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.reset()

    def set_pixel(self, x, y, val):
        self.frame[y][x] = val

    def get_pixel(self, x, y):
        return self.frame[y][x]

    def reset(self):
        self.frame = [bytearray(self.width) for _ in range(self.height)]
        print('Buffer Cleared')

    def render(self):
        for y in self.frame:
            for x in y:
                if x:
                    print('*', end='')
            print()