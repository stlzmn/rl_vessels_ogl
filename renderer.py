from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from meshes import EncMesh, Mesh

import pyrr
import numpy as np

class RenderPass:
    def __init__(self, g_engine, mesh, vert_filepath, frag_filepath):
        self.g_engine = g_engine
        self.mesh = mesh
        self.shader = self.g_engine.create_shader(vert_filepath, frag_filepath)
        glUseProgram(self.shader)
        self._acquire_unifrorm_locs()
        self._setup_onetime_uniforms()

    def _setup_onetime_uniforms(self):
        glUniform1f(glGetUniformLocation(self.shader,  'screenWidth'), SCREEN_WIDTH)
        glUniform1f(glGetUniformLocation(self.shader, 'screenHeight'), SCREEN_HEIGHT)

    def _acquire_unifrorm_locs(self):
        self.model_mat_loc = glGetUniformLocation(self.shader, 'model')
        self.view_mat_loc = glGetUniformLocation(self.shader, 'view')
        self.proj_mat_loc = glGetUniformLocation(self.shader, 'projection')
        self.disp_range_loc = glGetUniformLocation(self.shader, 'displayRange') 

    def render(self, scene, entity):
        glUseProgram(self.shader)

        glUniform1f(self.disp_range_loc, 100000)

        glUniformMatrix4fv(self.model_mat_loc, 1, GL_FALSE, entity.model_transform)
        glUniformMatrix4fv(self.view_mat_loc, 1, GL_FALSE, scene.camera.view_transform)
        glUniformMatrix4fv(self.proj_mat_loc, 1, GL_FALSE, scene.projection_transform)

        # glBindVertexArray(self.mesh.vao)
        # glDrawArrays(render_mode, 0, self.mesh.n_verts)
        self.mesh.render()
        
class RenderPassVessel:
    def __init__(self, g_engine, mesh, vert_filepath, frag_filepath):
        self.g_engine = g_engine
        self.mesh = mesh
        self.shader = self.g_engine.create_shader(vert_filepath, frag_filepath)
        glUseProgram(self.shader)
        self._acquire_unifrorm_locs()
        self._setup_onetime_uniforms()

    def _setup_onetime_uniforms(self):
        glUniform1f(glGetUniformLocation(self.shader,  'screenWidth'), SCREEN_WIDTH)
        glUniform1f(glGetUniformLocation(self.shader, 'screenHeight'), SCREEN_HEIGHT)

    def _acquire_unifrorm_locs(self):
        self.model_mat_loc = glGetUniformLocation(self.shader, 'model')
        self.view_mat_loc = glGetUniformLocation(self.shader, 'view')
        self.proj_mat_loc = glGetUniformLocation(self.shader, 'projection')
        self.disp_range_loc = glGetUniformLocation(self.shader, 'displayRange') 

    def render(self, scene, entity, render_mode):
        glUseProgram(self.shader)

        glUniform1f(self.disp_range_loc, scene.chart.display_range)

        glUniformMatrix4fv(self.model_mat_loc, 1, GL_FALSE, entity.model_transform)
        glUniformMatrix4fv(self.view_mat_loc, 1, GL_FALSE, scene.camera.view_transform)
        glUniformMatrix4fv(self.proj_mat_loc, 1, GL_FALSE, scene.projection_transform)

        glBindVertexArray(self.mesh.vao)
        glDrawArrays(render_mode, 0, self.mesh.n_verts)

class RenderPassTargets(RenderPass):
    def __init__(self, g_engine, mesh, vert_filepath, frag_filepath):
        super().__init__(g_engine, mesh, vert_filepath, frag_filepath)
        self.n_targets = 1000
        model_verts = []
        for _ in range(self.n_targets):
            transform = pyrr.matrix44.create_identity(dtype=np.float32)
            transform = pyrr.matrix44.multiply(m1=transform, m2=pyrr.matrix44.create_from_eulers(np.radians([0, 0, 0]), dtype=np.float32))
            transform = pyrr.matrix44.multiply(m1=transform, m2=pyrr.matrix44.create_from_translation(np.random.rand(1, 3), dtype=np.float32))
            model_verts.extend(transform)
        self.targets_transforms = np.array(model_verts, dtype=np.float32)

        self.targets_transforms_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.targets_transforms_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.targets_transforms.nbytes, self.targets_transforms, GL_STATIC_DRAW)
        glBindVertexArray(self.mesh.vao)
        glEnableVertexAttribArray(3)
        glVertexAttribPointer(3, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(0))
        glEnableVertexAttribArray(4)
        glVertexAttribPointer(4, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(16))
        glEnableVertexAttribArray(5)
        glVertexAttribPointer(5, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(32))
        glEnableVertexAttribArray(6)
        glVertexAttribPointer(6, 4, GL_FLOAT, GL_FALSE, 64, ctypes.c_void_p(48))
        # glVertexAttribDivisor(3, 0)
        # glVertexAttribDivisor(4, 0)
        # glVertexAttribDivisor(5, 0)
        # glVertexAttribDivisor(6, 0)
        

    def render(self, scene, entity, n_targets, render_mode):
        glUseProgram(self.shader)

        glUniform1f(self.disp_range_loc, scene.chart.display_range)
        glUniformMatrix4fv(self.view_mat_loc, 1, GL_FALSE, scene.camera.view_transform)
        glUniformMatrix4fv(self.proj_mat_loc, 1, GL_FALSE, scene.projection_transform)
        glBindVertexArray(self.mesh.vao)

        glBindBuffer(GL_ARRAY_BUFFER, self.targets_transforms_vbo)
        glBufferData(GL_ARRAY_BUFFER, self.targets_transforms.nbytes, self.targets_transforms, GL_STATIC_DRAW)
        glDrawArraysInstanced(render_mode, 0, self.mesh.n_verts, self.n_targets)


class GraphicEngine:
    def __init__(self):
        self._make_assets()

    def _make_assets(self):
        self.textures = {}
        self.meshes = {
            'ENC': EncMesh(['maps/PL2MP500.000', 'maps/PL5GDYNA.000']),#  'maps/PL4MAP36.000' 'maps/PL4MAP37.000', 'maps/PL4MAP38.000', 'maps/PL5SWINO.000', 'maps/PL5SZCZE.000',
            'Vessel': Mesh('models/vessel.obj')
        }
        self._render_pass_enc = RenderPass(self, self.meshes['ENC'], 'shaders/enc/vertex.txt', 'shaders/enc/fragment.txt')
        self._render_pass_vessel = RenderPassVessel(self, self.meshes['Vessel'], 'shaders/vessel/vertex.txt', 'shaders/vessel/fragment.txt')
        self._render_pass_targets = RenderPassTargets(self, self.meshes['Vessel'], 'shaders/target/vertex.txt', 'shaders/target/fragment.txt')

    def create_shader(self, vertex_filepath, fragment_filepath):
        shader_srcs = {}
        for filepath in (vertex_filepath, fragment_filepath):
            with open(filepath, 'r') as f:
                shader_srcs[filepath] = f.readlines()

        shader = compileProgram(
            compileShader(shader_srcs[vertex_filepath], GL_VERTEX_SHADER),
            compileShader(shader_srcs[fragment_filepath], GL_FRAGMENT_SHADER)
        )
        return shader
    
    def reload_meshes(self):
        self._make_assets()
    
    def render(self, scene):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        self._render_pass_enc.render(scene, scene.chart)
        # self._render_pass_vessel.render(scene, scene.own_ship, GL_LINES)
        # self._render_pass_targets.render(scene, scene.own_ship, 1, GL_TRIANGLES)

        glFlush()

    def terminate(self):
        for _, texture in self.textures.items():
            texture.destroy()

        for _, mesh in self.meshes.items():
            mesh.destroy()