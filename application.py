import glfw
import glfw.GLFW as GC
from OpenGL.GL import *
import numpy as np

from renderer import GraphicEngine
from scene import Scene
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
from report_flow import AisReportFlow

class App:
    def __init__(self):
        self._init_glfw()
        self._setup_render()
        self._setup_timer()
        self._setup_ais_dataflow()
        self._mainloop()

    def _init_glfw(self):
        glfw.init()
        glfw.window_hint(GC.GLFW_CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(GC.GLFW_CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(GC.GLFW_OPENGL_PROFILE, GC.GLFW_OPENGL_CORE_PROFILE)
        glfw.window_hint(GC.GLFW_OPENGL_FORWARD_COMPAT, GC.GLFW_TRUE)
        glfw.window_hint(GC.GLFW_DOUBLEBUFFER, GL_FALSE)
        self.window = glfw.create_window(SCREEN_WIDTH, SCREEN_HEIGHT, 'AIS_s57', None, None)
        self._setup_input_mode()
        glfw.make_context_current(self.window)

        glEnable(GL_PROGRAM_POINT_SIZE)
        glPointSize(5)
        glClearColor(0.1, 0.1, 0.2, 1.0)
        glEnable(GL_LINE_SMOOTH);
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST);

    def _setup_render(self):
        self.graphic_eng = GraphicEngine()
        self.scene = Scene()

    def _setup_ais_dataflow(self):
        self.ais_flow = AisReportFlow(source='server', destination=self.scene.target_ships)
        # self.ais_flow.run()

    def _setup_timer(self):
        self.last_time = glfw.get_time()
        self.current_time = 0.0
        self.n_frames = 0.0
        self.frame_time = 0.0

    def _setup_input_mode(self):
        glfw.set_cursor(self.window, GC.glfwCreateStandardCursor(GC.GLFW_CROSSHAIR_CURSOR))
        glfw.set_scroll_callback(self.window, self._mouse_scroll_callback)

    def _mouse_scroll_callback(self, window, x_offset, y_offset):
        if hasattr(self, 'display_range'):
            delta_range = self.display_range + y_offset
            self.display_range = max(0.3, min(12.0, delta_range))
        else:
            self.display_range = 1
        self.scene.chart.display_range = self.display_range

    def _mainloop(self):
        running = True
        while running:
            if glfw.window_should_close(self.window) or glfw.get_key(self.window, GC.GLFW_KEY_ESCAPE) == GC.GLFW_PRESS:
                running = False

            self._handle_user_input()
            glfw.poll_events()
            self.scene.update(self.frame_time / 16.667)
            self.graphic_eng.render(self.scene)
            self._calc_fps()
        self._on_quit()
    
    def _handle_user_input(self):
        self._mouse_input()
        self._keyboard_input()

    def _mouse_input(self):
        x, y = glfw.get_cursor_pos(self.window)
        rate = self.frame_time / 16.667
        theta_inc = rate * (SCREEN_WIDTH / 2 - x)
        phi_inc = rate * (SCREEN_HEIGHT / 2 - y)
        eulers = np.array([0, phi_inc, theta_inc], dtype=np.float32)
        self.scene.spin_camera(eulers)
        glfw.set_cursor_pos(self.window, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def _keyboard_input(self):
        keys_comb = 0
        dire_mod = 0
        keys_2_zoom = {GC.GLFW_KEY_1: 15, GC.GLFW_KEY_2: 30, GC.GLFW_KEY_3: 45}
        keys_2_elev = {GC.GLFW_KEY_R: 1, GC.GLFW_KEY_F: -1}
        keys_2_move = {GC.GLFW_KEY_W: 1, GC.GLFW_KEY_A: 2, GC.GLFW_KEY_S: 4, GC.GLFW_KEY_D: 8}
        comb_2_dire = {(3,): 45, (2, 7): 90, (6,): 135, (4, 14): 180, (12,): 225, (8, 13): 270, (9,): 315}

        dfact = 0.05
        rate = self.frame_time / 16.667
        camera_elev = 0.0

        for key, val in keys_2_zoom.items():
            if glfw.get_key(self.window, key) == GC.GLFW_PRESS:
                self.scene.fovy = val

        for key, val in keys_2_move.items():
            if glfw.get_key(self.window, key) == GC.GLFW_PRESS:
                keys_comb += val

        for key, val in keys_2_elev.items():
            if glfw.get_key(self.window, key) == GC.GLFW_PRESS:
                camera_elev += val

        dpos = dfact * rate * np.array([0, 0, camera_elev], dtype=np.float32)
        
        if keys_comb:
            for comb, dire in comb_2_dire.items():
                if keys_comb in comb:
                    dire_mod = dire

            dpos = dfact * rate * np.array([
                np.cos(np.deg2rad(self.scene.camera.eulers[2] + dire_mod)),
                np.sin(np.deg2rad(self.scene.camera.eulers[2] + dire_mod)), 
                camera_elev
            ], dtype=np.float32)

        self.scene.move_camera(dpos)

    def _calc_fps(self):
        self.current_time = glfw.get_time()
        dtime = self.current_time - self.last_time
        if dtime >= 1:
            fps = max(1, int(self.n_frames / dtime))
            glfw.set_window_title(self.window, f'{fps} fps.')
            self.last_time = self.current_time
            self.n_frames = -1
            self.frame_time = float(1000.0 / max(1, fps))
        self.n_frames += 1

    def _on_quit(self):
        self.graphic_eng.terminate()
        self.ais_flow.terminate()

if __name__ == '__main__':
    app = App()