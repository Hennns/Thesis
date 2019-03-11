

import matplotlib as plt
plt.use("Agg")

import matplotlib.backends.backend_agg as agg
import pylab

import pygame

#http://www.pygame.org/wiki/MatplotlibPygame

class Graph():

    def __init__(self,plot_type):
        self.fig = pylab.figure(figsize=[4, 5], # Inches
                           dpi=100,        # number of dots per inch
                           )


        self.update_delta = 250
        self.last_update_time = 0

        self.title = "title"
        self.ylim_min = None
        self.x_label = "x_label"
        self.y_label = "y_label"

        self.update_graph()
        self.surf = self.get_graph_as_image()

        self.plot_type = plot_type



    def get_graph_as_image(self):

        return self.surf


    def plot(self,x_list,y_list):
        #self.fig.clf()
        ax = self.fig.gca()

        if self.plot_type == "line":
            ax.plot(x_list,y_list)
            
            ax.set_ylim(ymin = self.ylim_min)
        elif self.plot_type == "scatter":
            ax.scatter(x_list,y_list)


        ax.set_title(self.title)
        ax.set_xlabel(self.x_label)
        ax.set_ylabel(self.y_label)




    def update_graph(self):
        #prevents axsis labels from being cut off
        self.fig.tight_layout()


        canvas = agg.FigureCanvasAgg(self.fig)
        canvas.draw()
        renderer = canvas.get_renderer()
        raw_data = renderer.tostring_rgb()
        size = canvas.get_width_height()

        self.surf = pygame.image.fromstring(raw_data, size, "RGB")
        self.fig.clf()
