

import matplotlib
matplotlib.use("Agg")

import matplotlib.backends.backend_agg as agg
import pylab

import pygame

#http://www.pygame.org/wiki/MatplotlibPygame

class Graph():

    def __init__(self):
        self.fig = pylab.figure(figsize=[4, 5], # Inches
                           dpi=100,        # number of dots per inch
                           )


        self.update_delta = 250
        self.last_update_time = 0



        self.surf = "somevalue"
        self.update_graph()


    def get_graph_as_image(self):
        return self.surf

    #data is list of points
    def plot(self,data):
        self.fig.clf()

        ax = self.fig.gca()
        print(ax)
        ax.plot(data)


    def update_graph(self):
        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()

        size = canvas.get_width_height()

        self.surf = pygame.image.fromstring(raw_data, size, "RGB")
