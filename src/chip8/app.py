#import sdl2.ext
#from chip8 import resource_path
from chip8.lib.system import System


def main():
    """
    Application entrypoint
    """
    #sdl2.ext.init()

    #window = sdl2.ext.Window("Hello World!", size=(640, 480))
    #window.show()

    #factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
    #sprite = factory.from_image(resource_path.get_path("hello.bmp"))

    #sprite_renderer = factory.create_sprite_render_system(window)

    #sprite.position = 10, 20

    #sprite_renderer.render(sprite)

    #processor = sdl2.ext.TestEventProcessor()
    #processor.run(window)

    #sdl2.ext.quit()


if __name__ == '__main__':
    """
    Start application
    """
    chip8 = System()
    chip8.load_font()
    chip8.load_rom()
    chip8.start()

    #main()
