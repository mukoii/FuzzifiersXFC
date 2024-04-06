from kesslergame import KesslerGraphics
from kesslergame.graphics.graphics_tk import GraphicsTK


class GraphicsBoth(KesslerGraphics):
    def __init__(self):
        self.tk = GraphicsTK({})

    def start(self, scenario):
        self.tk.start(scenario)

    def update(self, score, ships, asteroids, bullets):
        self.tk.update(score, ships, asteroids, bullets)

    def close(self):
        self.tk.close()
