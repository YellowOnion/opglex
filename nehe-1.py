print 'importing numpy...',
import numpy as np
print 'done'
print 'importing pyglet, gletools, etc...',
import pyglet
from gletools.gl import *
from gletools import (
        ShaderProgram, FragmentShader, VertexShader, Matrix, VertexObject
        )

pyglet.options['debug_gl'] = True
print 'done'

print 'importing pyglet reactor...',
import pygletreactor
print 'done'

print 'installing...',
pygletreactor.install()
print 'done'

print 'importing twisted...',
from twisted.internet import reactor
print 'done'

import time, math
from ctypes import sizeof, POINTER
        
def size_of(array):
    return array.dtype.itemsize * len(array)

n_vertices = 36

right  =  0.8
left   = -right
top    =  0.2
middle =  0.0
bottom = -top
front  = -1.25
rear   = -1.75

green = [ 0.75, 0.75, 1.0, 1.0 ]
blue  = [ 0.0,  0.5,  0.0, 1.0 ]
red   = [ 1.0,  0.0,  0.0, 1.0 ]
grey  = [ 0.8,  0.8,  0.8, 1.0 ]
brown = [ 0.5,  0.5,  0.0, 1.0 ]

vertex_data = np.array([
    # Object 1 positions
    left,  top,    rear,
    left,  middle, front,
    right, middle, front,
    right, top,    rear,

    left, bottom, rear,
    left, middle, front,
    right, middle, front,
    right, bottom, rear,

    left, top, rear,
    left, middle, front,
    left, bottom, rear,

    right, top, rear,
    right, middle, front,
    right, bottom, rear,

    left, bottom, rear,
    left, top, rear,
    right, top, rear,
    right, bottom, rear,

    #Object 2

    top, right, rear,
    middle, right, front,
    middle, left, front,
    top, left, rear,

    bottom, right, rear,
    middle, right, front,
    middle, left, front,
    bottom, left, rear,

    top, right, rear,
    middle, right, front,
    bottom, right, rear,

    top, left, rear,
    middle, left, front,
    bottom, left, rear,
    
    bottom, right, rear,
    top, right, rear,
    top, left, rear,
    bottom, left, rear
    ] + \
    #Object 1 colours,
        (green * 4) +\
        (blue * 4) +\
        (red * 3) +\
        (grey * 3) +\
        (brown * 4) +\
    #object 2 colours,
        (red * 4) +\
        (brown * 4) +\
        (blue * 3) +\
        (green * 3) +\
        (grey * 4)
    , dtype=GLfloat)    

index_data = np.array([
    0, 2, 1,
    3, 2, 0,

    4, 5, 6,
    6, 7, 4,

    8, 9, 10,
    11, 13, 12,

    14, 16, 15,
    17, 16, 14,
    ], dtype=GLshort)


class World(pyglet.window.Window):
    
    def __init__(self, *args, **kwargs):
        super(World, self).__init__(*args, **kwargs)

        self.init()
    

    def init_program(self):
        self.near = 0.25
        self.far = 3.0
        self.fov = 120.0
        self.program = ShaderProgram(
                VertexShader.open('simple.vert'),
                FragmentShader.open('simple.frag'),
                offset = [0.0, 0.0, 0.0],
                perspectiveMatrix = Matrix.perspective(self.width, self.height, self.fov, self.near, self.far)
        )

    def init_vertex_buffer(self):
        self.vertex_buffer_object = GLuint()
        self.index_buffer_object = GLuint()

        glGenBuffers(1, self.vertex_buffer_object)

        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_object)
        glBufferData(GL_ARRAY_BUFFER, size_of(vertex_data), vertex_data.ctypes.data, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        glGenBuffers(1, self.index_buffer_object)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer_object)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, size_of(index_data), index_data.ctypes.data, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    def init_vaos(self):
        self.vao1 = GLuint()
        glGenVertexArrays(1, self.vao1)
        glBindVertexArray(self.vao1)

        color_data_offset = sizeof(GLfloat) * 3 * n_vertices
        glBindBuffer(GL_ARRAY_BUFFER, self.vertex_buffer_object)
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, 0)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, color_data_offset)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer_object)
        glBindVertexArray(0)
        
        self.vao2 = GLuint()
        glGenVertexArrays(1, self.vao2)
        glBindVertexArray(self.vao2)

        pos_data_offset    = sizeof(GLfloat) * 3 * (n_vertices / 2)
        color_data_offset += sizeof(GLfloat) * 4 * (n_vertices / 2)
        
        glEnableVertexAttribArray(0)
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, pos_data_offset)
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, color_data_offset)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.index_buffer_object)

        glBindVertexArray(0)

    def init(self):
        
        self.init_program()
        pyglet.clock.schedule(lambda dt: None)
        self.fps = pyglet.clock.ClockDisplay()
        self.init_vertex_buffer()
        self.init_vaos()
                
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)
        glFrontFace(GL_CW)

        glEnable(GL_DEPTH_TEST)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LEQUAL)
        glDepthRange(0.0, 1.0)

    def on_draw(self):
#        print 'draw!'
#        x, y = self.comp_offset()
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        with self.program:
            glBindVertexArray(self.vao1)
            glUniform3f(self.program.uniform_location('offset'), 0.0, 0.0, 0.0)
            glDrawElements(GL_TRIANGLES, size_of(index_data), GL_UNSIGNED_SHORT, 0)

            glBindVertexArray(self.vao2)
            glUniform3f(self.program.uniform_location('offset'), 0.0, 0.0, 0.0 )
            glDrawElements(GL_TRIANGLES, size_of(index_data), GL_UNSIGNED_SHORT, 0)

            glBindVertexArray(0)

        self.fps.draw()

    def on_resize(self, w, h):
#        print 'resizing'
        self.program.vars['perspectiveMatrix'] = Matrix.perspective(w, h, self.fov, self.near, self.far)
        glViewport(0, 0, w, h)
        
    def on_key_press(self, symbol, modifiers):
        print 'key pressed'
        if symbol == pyglet.window.key.ESCAPE:
            print 'escape'
            self.dispatch_event('on_close')
        elif symbol == pyglet.window.key.SPACE:
            try: depth_clamp
            except NameError:
                depth_clamp = False
            if depth_clamp:
                glDisable(GL_DEPTH_CLAMP)
            else:
                glEnable(GL_DEPTH_CLAMP)

            depth_clamp = not depth_clamp

    def comp_offset(self):
        spin_time = 5.0
        scale = math.pi * 2.0 / spin_time
        elapsed_ms = time.clock() / 10
        current_ms = elapsed_ms % spin_time
        x = math.cos(current_ms * scale) * 0.5
        y = math.sin(current_ms * scale) * 0.5
#        print x, y
        return x, y

    def on_close(self):
        print 'reactor stopping'
        reactor.callFromThread(reactor.stop)

        return True
world = World(vsync=True, resizable=True)
reactor.run(call_interval=1/1000.0)

