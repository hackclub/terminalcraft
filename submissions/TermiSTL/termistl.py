import sys
from pathlib import Path
import os
from typing import Iterable

import numpy as np
from stl import mesh

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, DirectoryTree
from textual.containers import Container, Horizontal
from textual.events import MouseDown, MouseMove, MouseUp

from numba import njit, prange

ASCII_SHADING_CHARACTERS = " ░▒▓█"

@njit(parallel=True)
def rasterize_triangles_to_depth_buffer(
    triangle_vertices_2d: np.ndarray,
    triangle_vertices_z_depth: np.ndarray,
    canvas_width: int,
    canvas_height: int,
    model_min_coord_x: float,
    model_min_coord_y: float,
    model_scale_x: float,
    model_scale_y: float,
    model_offset_x: float,
    model_offset_y: float
) -> np.ndarray:
    depth_buffer = np.full((canvas_height, canvas_width), -1e20, dtype=np.float64)

    for tri_idx in prange(triangle_vertices_2d.shape[0]):
        current_tri_vx_2d = triangle_vertices_2d[tri_idx, :, 0]
        current_tri_vy_2d = triangle_vertices_2d[tri_idx, :, 1]
        current_tri_vz_depth = triangle_vertices_z_depth[tri_idx]

        pixel_coords_x = (current_tri_vx_2d - model_min_coord_x) * model_scale_x + model_offset_x
        pixel_coords_y = (current_tri_vy_2d - model_min_coord_y) * model_scale_y + model_offset_y
        pixel_coords_y = (canvas_height - 1) - pixel_coords_y

        bbox_min_x = max(0, int(np.floor(pixel_coords_x.min())))
        bbox_max_x = min(canvas_width - 1, int(np.ceil(pixel_coords_x.max())))
        bbox_min_y = max(0, int(np.floor(pixel_coords_y.min())))
        bbox_max_y = min(canvas_height - 1, int(np.ceil(pixel_coords_y.max())))

        v0x, v0y = pixel_coords_x[0], pixel_coords_y[0]
        v1x, v1y = pixel_coords_x[1], pixel_coords_y[1]
        v2x, v2y = pixel_coords_x[2], pixel_coords_y[2]
        
        barycentric_denominator = (v1y - v2y) * (v0x - v2x) + (v2x - v1x) * (v0y - v2y)
        if abs(barycentric_denominator) < 1e-6:
            continue

        for y_pixel in range(bbox_min_y, bbox_max_y + 1):
            for x_pixel in range(bbox_min_x, bbox_max_x + 1):
                weight_v0 = ((v1y - v2y) * (x_pixel - v2x) + (v2x - v1x) * (y_pixel - v2y)) / barycentric_denominator
                weight_v1 = ((v2y - v0y) * (x_pixel - v2x) + (v0x - v2x) * (y_pixel - v2y)) / barycentric_denominator
                weight_v2 = 1.0 - weight_v0 - weight_v1
                
                if weight_v0 >= 0 and weight_v1 >= 0 and weight_v2 >= 0:
                    interpolated_z_at_pixel = weight_v0 * current_tri_vz_depth[0] + weight_v1 * current_tri_vz_depth[1] + weight_v2 * current_tri_vz_depth[2]
                    if interpolated_z_at_pixel > depth_buffer[y_pixel, x_pixel]:
                        depth_buffer[y_pixel, x_pixel] = interpolated_z_at_pixel
    return depth_buffer

class FilteredDirectoryTree(DirectoryTree):
    def filter_paths(self, paths: Iterable[Path]) -> Iterable[Path]:
        filtered = []
        for path_object in paths:
            if path_object.is_dir() or path_object.suffix.lower() == ".stl":
                filtered.append(path_object)
        return filtered

class TermiSTL(App):
    CSS_PATH = "termistl.css"
    BINDINGS = [
        ("f", "set_view('front')", "Front"),
        ("t", "set_view('top')", "Top"),
        ("s", "set_view('side')", "Side"),
        ("up", "rotate_x(-0.1)", "Rot X-"),
        ("down", "rotate_x(0.1)", "Rot X+"),
        ("left", "rotate_y(-0.1)", "Rot Y-"),
        ("right", "rotate_y(0.1)", "Rot Y+"),
        ("u", "rotate_z(0.1)", "Roll CCW"),
        ("o", "rotate_z(-0.1)", "Roll CW"),
        ("pageup", "adjust_zoom_level(1.2)", "Zoom In"),
        ("pagedown", "adjust_zoom_level(0.83333)", "Zoom Out"),
        ("a", "previous_stl", "Previous STL"),
        ("d", "next_stl", "Next STL"),
        ("r", "toggle_auto_rotation", "Rotate"),
        ("delete", "delete_current_stl", "Delete STL"),
        ("q", "quit_application", "Quit"),
    ]

    def __init__(self, start_path: Path):
        super().__init__()
        self.start_path = start_path
        self.current_stl_file_path: Path | None = None
        self.stl_mesh_data = None
        self.information_panel_text = "Loading..."
        
        self.current_directory: Path | None = None
        self.stl_files_in_directory: list[Path] = []
        self.current_stl_index_in_dir: int = -1

        self.auto_rotate_mode = 0
        self.auto_rotate_timer = None

        self.camera_rotation_x_radians = 0.0
        self.camera_rotation_y_radians = 0.0
        self.camera_rotation_z_radians = 0.0
        
        self.model_center_of_gravity = np.zeros(3)
        self.current_zoom_level = 1.0
        self._apply_view_preset('front')

        self.dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self._throttle_active = False

        self.file_pending_deletion_confirmation: Path | None = None
        self.delete_confirmation_timer_object = None

    def _stop_auto_rotation(self):
        if self.auto_rotate_timer:
            self.auto_rotate_timer.stop()
            self.auto_rotate_timer = None
            self.auto_rotate_mode = 0

    def _apply_view_preset(self, view: str):
        if view == 'front':
            self.camera_rotation_x_radians = np.deg2rad(-90)
            self.camera_rotation_y_radians = 0.0
            self.camera_rotation_z_radians = 0.0
        elif view == 'top':
            self.camera_rotation_x_radians = 0.0
            self.camera_rotation_y_radians = 0.0
            self.camera_rotation_z_radians = 0.0
        elif view == 'side':
            self.camera_rotation_x_radians = np.deg2rad(-90)
            self.camera_rotation_y_radians = np.deg2rad(-90)
            self.camera_rotation_z_radians = 0.0

    def compose(self) -> ComposeResult:
        yield Header("TermiSTL – ASCII Preview")
        with Horizontal(id="main-container"):
            yield FilteredDirectoryTree("", id="file-explorer")
            with Container(id="app-grid"):
                yield Static(self.information_panel_text, id="stats")
                yield Static(id="preview")
        yield Footer()

    def _update_stl_files_in_current_directory(self, directory_to_scan: Path | None = None):
        scan_dir = directory_to_scan if directory_to_scan else self.current_directory
        if scan_dir and scan_dir.is_dir():
            self.current_directory = scan_dir
            self.stl_files_in_directory = sorted(
                [f for f in scan_dir.glob('*.stl') if f.is_file()]
            )
            if self.current_stl_file_path in self.stl_files_in_directory:
                self.current_stl_index_in_dir = self.stl_files_in_directory.index(self.current_stl_file_path)
            else:
                self.current_stl_index_in_dir = -1
        else:
            self.stl_files_in_directory = []
            self.current_stl_index_in_dir = -1
        
        dt_widget = self.query_one(FilteredDirectoryTree)
        if scan_dir and Path(dt_widget.path) != scan_dir:
             dt_widget.path = str(scan_dir)


    def load_stl_file(self, file_to_load: Path | None):
        if file_to_load is None or not file_to_load.is_file():
            self.current_stl_file_path = None
            self.stl_mesh_data = None
            self.information_panel_text = "No STL file selected or file not found."
            if self.current_directory:
                 self.information_panel_text += f"\nDirectory: {self.current_directory}"
            else:
                 self.information_panel_text += "\nNo directory selected."
            self.query_one("#stats", Static).update(self.information_panel_text)
            self.query_one("#preview", Static).update("")
            self.current_stl_index_in_dir = -1
            return

        self.current_stl_file_path = file_to_load
        if self.current_directory != file_to_load.parent:
            self._update_stl_files_in_current_directory(file_to_load.parent)

        if file_to_load in self.stl_files_in_directory:
            self.current_stl_index_in_dir = self.stl_files_in_directory.index(file_to_load)
        else:
            self._update_stl_files_in_current_directory(file_to_load.parent)
            if file_to_load in self.stl_files_in_directory:
                self.current_stl_index_in_dir = self.stl_files_in_directory.index(file_to_load)
            else:
                self.current_stl_index_in_dir = -1


        self.information_panel_text = f"Loading {file_to_load.name}..."
        self.query_one("#stats", Static).update(self.information_panel_text)
        self.query_one("#preview", Static).update("Rendering...")

        stl_load_modes = [("auto_detect", {}), ("binary", {"mode": 2}), ("ascii", {"mode": 1})]
        mesh_loaded_successfully = False
        
        for mode_name, mode_params in stl_load_modes:
            try:
                loaded_mesh = mesh.Mesh.from_file(file_to_load, **mode_params)
                self.stl_mesh_data = loaded_mesh
                
                model_dimensions_xyz = loaded_mesh.max_ - loaded_mesh.min_
                volume_mm3, center_of_gravity, _ = loaded_mesh.get_mass_properties()
                self.model_center_of_gravity = center_of_gravity
                total_surface_area_mm2 = loaded_mesh.areas.sum()
                
                self.information_panel_text = (
                    f"[bold]File:[/bold] {file_to_load.name}\n"
                    f"[bold]Triangles:[/bold] {len(loaded_mesh.vectors):,}\n"
                    f"[bold]Dimensions (mm):[/bold] X:{model_dimensions_xyz[0]:.2f} Y:{model_dimensions_xyz[1]:.2f} Z:{model_dimensions_xyz[2]:.2f}\n"
                    f"[bold]Volume:[/bold] {volume_mm3 / 1000:.2f} cm³  [bold]Area:[/bold] {total_surface_area_mm2:.2f} mm²"
                )
                self.query_one("#stats", Static).update(self.information_panel_text)
                mesh_loaded_successfully = True
                self.update_ascii_preview()
                break
            except Exception as e:
                continue
        
        if not mesh_loaded_successfully:
            self.stl_mesh_data = None
            error_message = f"[red]Error: Failed to load STL file '{file_to_load.name}'.[/red]"
            self.query_one("#stats", Static).update(error_message)
            self.query_one("#preview", Static).update("")

    def on_mount(self):
        initial_dir_for_explorer = Path(".")

        if self.start_path.is_file() and self.start_path.suffix.lower() == ".stl":
            initial_dir_for_explorer = self.start_path.parent
            self.current_stl_file_path = self.start_path
        elif self.start_path.is_dir():
            initial_dir_for_explorer = self.start_path
            self.current_stl_file_path = None 
        else:
            self.query_one("#stats", Static).update(f"[red]Error: Invalid start path '{self.start_path}'.[/red]")
        
        self.current_directory = initial_dir_for_explorer.resolve()

        try:
            dt_widget = self.query_one(FilteredDirectoryTree)
            dt_widget.path = str(self.current_directory)
            self.query_one("#preview", Static).can_focus = True
        except Exception as e:
            self.query_one("#stats", Static).update(f"[red]Error setting up file explorer: {e}[/red]")
            return

        self._update_stl_files_in_current_directory()

        if self.current_stl_file_path:
            self.load_stl_file(self.current_stl_file_path)
        elif self.stl_files_in_directory:
            self.load_stl_file(self.stl_files_in_directory[0])
            self.current_stl_index_in_dir = 0
        else:
            self.load_stl_file(None)
            self.query_one("#stats", Static).update(
                f"No STL files found in '{self.current_directory}'.\nSelect an STL file or directory."
            )
            self.stl_mesh_data = None

    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        self._clear_pending_deletion_confirmation()
        selected_path = Path(event.path)
        if selected_path.is_file() and selected_path.suffix.lower() == ".stl":
            self._update_stl_files_in_current_directory(selected_path.parent)
            self.load_stl_file(selected_path)
            self.query_one("#preview", Static).focus()
        elif selected_path.is_dir():
            self._update_stl_files_in_current_directory(selected_path)
            if self.stl_files_in_directory:
                self.load_stl_file(self.stl_files_in_directory[0])
            else:
                self.load_stl_file(None)
            self.query_one("#preview", Static).focus()
        
    async def on_ready(self) -> None:
        pass

    def render_model_to_ascii(self, canvas_width: int, canvas_height: int) -> str:
        if not self.stl_mesh_data:
            return ""
        
        cos_rot_x, sin_rot_x = np.cos(self.camera_rotation_x_radians), np.sin(self.camera_rotation_x_radians)
        cos_rot_y, sin_rot_y = np.cos(self.camera_rotation_y_radians), np.sin(self.camera_rotation_y_radians)
        cos_rot_z, sin_rot_z = np.cos(self.camera_rotation_z_radians), np.sin(self.camera_rotation_z_radians)

        rotation_matrix_x_axis = np.array([[1, 0, 0], [0, cos_rot_x, -sin_rot_x], [0, sin_rot_x, cos_rot_x]])
        rotation_matrix_y_axis = np.array([[cos_rot_y, 0, sin_rot_y], [0, 1, 0], [-sin_rot_y, 0, cos_rot_y]])
        rotation_matrix_z_axis = np.array([[cos_rot_z, -sin_rot_z, 0], [sin_rot_z, cos_rot_z, 0], [0, 0, 1]])
        
        combined_rotation_matrix = rotation_matrix_z_axis @ rotation_matrix_y_axis @ rotation_matrix_x_axis

        centered_mesh_triangles = self.stl_mesh_data.vectors - self.model_center_of_gravity
        rotated_mesh_triangles = centered_mesh_triangles @ combined_rotation_matrix.T

        projected_triangles_xy_coords = rotated_mesh_triangles[:, :, :2]
        projected_triangles_z_values = rotated_mesh_triangles[:, :, 2]

        all_projected_xy_vertices = projected_triangles_xy_coords.reshape(-1, 2)
        overall_min_xy_projected = all_projected_xy_vertices.min(axis=0)
        overall_max_xy_projected = all_projected_xy_vertices.max(axis=0)
        
        projected_xy_span = np.where(overall_max_xy_projected - overall_min_xy_projected == 0, 1.0, overall_max_xy_projected - overall_min_xy_projected)

        CHARACTER_ASPECT_RATIO_CORRECTION = 2.0 
        scale_x_to_fit_canvas = (canvas_width - 1) / (projected_xy_span[0] * CHARACTER_ASPECT_RATIO_CORRECTION) * self.current_zoom_level
        scale_y_to_fit_canvas = (canvas_height - 1) / projected_xy_span[1] * self.current_zoom_level
        
        uniform_scale_to_fit = min(scale_x_to_fit_canvas, scale_y_to_fit_canvas)
        
        offset_x_to_center = (canvas_width - projected_xy_span[0] * uniform_scale_to_fit * CHARACTER_ASPECT_RATIO_CORRECTION) / 2
        offset_y_to_center = (canvas_height - projected_xy_span[1] * uniform_scale_to_fit) / 2

        depth_buffer_result = rasterize_triangles_to_depth_buffer(
            projected_triangles_xy_coords, projected_triangles_z_values, 
            canvas_width, canvas_height,
            overall_min_xy_projected[0], overall_min_xy_projected[1],
            uniform_scale_to_fit * CHARACTER_ASPECT_RATIO_CORRECTION, uniform_scale_to_fit,
            offset_x_to_center, offset_y_to_center
        )

        output_ascii_canvas = np.full((canvas_height, canvas_width), ' ', dtype='<U1')
        pixels_with_depth_info_mask = depth_buffer_result > -1e19
        
        if pixels_with_depth_info_mask.any():
            min_rendered_depth = depth_buffer_result[pixels_with_depth_info_mask].min()
            max_rendered_depth = depth_buffer_result[pixels_with_depth_info_mask].max()
            rendered_depth_range = max_rendered_depth - min_rendered_depth if max_rendered_depth > min_rendered_depth else 1.0
            
            available_shading_chars = np.array(list(ASCII_SHADING_CHARACTERS[1:]))
            
            for y_val in range(canvas_height):
                for x_val in range(canvas_width):
                    if pixels_with_depth_info_mask[y_val, x_val]:
                        normalized_pixel_depth = (depth_buffer_result[y_val, x_val] - min_rendered_depth) / rendered_depth_range
                        selected_shading_char_index = int(np.clip(normalized_pixel_depth * (available_shading_chars.size - 1), 0, available_shading_chars.size - 1))
                        output_ascii_canvas[y_val, x_val] = available_shading_chars[selected_shading_char_index]
                        
        return "\n".join("".join(row) for row in output_ascii_canvas)

    def update_ascii_preview(self):
        preview_widget = self.query_one("#preview", Static)
        width, height = preview_widget.content_size
        if width > 1 and height > 1:
            if self.stl_mesh_data:
                preview_widget.update(self.render_model_to_ascii(width, height))
            else:
                preview_widget.update("")

    def request_throttled_update(self):
        if not self._throttle_active:
            self._throttle_active = True
            self.set_timer(0.05, self._execute_update_and_reset_throttle)

    def _execute_update_and_reset_throttle(self):
        self.update_ascii_preview()
        self._throttle_active = False

    def action_adjust_zoom_level(self, zoom_factor: float):  
        self.current_zoom_level *= zoom_factor
        self.request_throttled_update()

    def action_set_view(self, view: str):
        self._clear_pending_deletion_confirmation()
        self._stop_auto_rotation()
        self._apply_view_preset(view)
        self.request_throttled_update()

    def action_rotate_x(self, delta_radians: float):
        self._clear_pending_deletion_confirmation()
        self._stop_auto_rotation()
        self.camera_rotation_x_radians += delta_radians
        self.request_throttled_update()

    def action_rotate_y(self, delta_radians: float):
        self._clear_pending_deletion_confirmation()
        self._stop_auto_rotation()
        self.camera_rotation_y_radians += delta_radians
        self.request_throttled_update()

    def action_rotate_z(self, delta_radians: float):
        self._clear_pending_deletion_confirmation()
        self._stop_auto_rotation()
        self.camera_rotation_z_radians += delta_radians
        self.request_throttled_update()

    def auto_rotate_step(self):
        if self.auto_rotate_mode == 1:
            self.camera_rotation_y_radians += 0.01
        elif self.auto_rotate_mode == 2:
            self.camera_rotation_x_radians += 0.01
        elif self.auto_rotate_mode == 3:
            self.camera_rotation_y_radians += 0.01
            self.camera_rotation_x_radians += 0.01
        self.request_throttled_update()

    def action_toggle_auto_rotation(self):
        self.auto_rotate_mode = (self.auto_rotate_mode + 1) % 4
        if self.auto_rotate_mode > 0:
            if self.auto_rotate_timer is None:
                self.auto_rotate_timer = self.set_interval(1/60, self.auto_rotate_step)
        else:
            if self.auto_rotate_timer:
                self.auto_rotate_timer.stop()
                self.auto_rotate_timer = None
        
    def action_quit_application(self):
        self.exit()

    def action_next_stl(self) -> None:
        self._clear_pending_deletion_confirmation()
        if not self.stl_files_in_directory:
            return
        
        num_files = len(self.stl_files_in_directory)
        if num_files < 2:
            return 
        self.current_stl_index_in_dir = (self.current_stl_index_in_dir + 1) % num_files
        next_file_to_load = self.stl_files_in_directory[self.current_stl_index_in_dir]
        self.load_stl_file(next_file_to_load)

    def action_previous_stl(self) -> None:
        self._clear_pending_deletion_confirmation()
        if not self.stl_files_in_directory:
            return

        num_files = len(self.stl_files_in_directory)
        if num_files < 2:
            return

        self.current_stl_index_in_dir = (self.current_stl_index_in_dir - 1 + num_files) % num_files
        prev_file_to_load = self.stl_files_in_directory[self.current_stl_index_in_dir]
        self.load_stl_file(prev_file_to_load)

    def action_delete_current_stl(self) -> None:
        if not self.current_stl_file_path or not self.current_stl_file_path.is_file():
            self.notify("No STL file is currently loaded to delete.", severity="error")
            self._clear_pending_deletion_confirmation() 
            return

        file_to_delete = self.current_stl_file_path
        file_name = file_to_delete.name

        if self.file_pending_deletion_confirmation == file_to_delete:
            self._clear_pending_deletion_confirmation() 
            try:
                os.remove(file_to_delete)
                self.notify(f"File '{file_name}' deleted successfully.", severity="information")
                
                original_index = self.current_stl_index_in_dir
                self._update_stl_files_in_current_directory()

                if not self.stl_files_in_directory:
                    self.load_stl_file(None)
                else:
                    new_index = min(original_index, len(self.stl_files_in_directory) - 1)
                    if new_index >= 0 :
                        self.load_stl_file(self.stl_files_in_directory[new_index])
                    else: 
                        self.load_stl_file(None)
                self.query_one(FilteredDirectoryTree).reload()
            except OSError as e:
                self.notify(f"Error deleting file '{file_name}': {e}", severity="error")
            except Exception as e:
                self.notify(f"An unexpected error occurred during deletion: {e}", severity="error")
        else:
            self._clear_pending_deletion_confirmation() 
            self.file_pending_deletion_confirmation = file_to_delete
            self.notify(f"Press Delete again to confirm deletion of '{file_name}'. (5s)", severity="warning", timeout=5.5)
            
            self.delete_confirmation_timer_object = self.set_timer(5.0, self._clear_pending_deletion_confirmation)

    def _clear_pending_deletion_confirmation(self) -> None:
        if self.delete_confirmation_timer_object:
            try:
                self.delete_confirmation_timer_object.stop()
            except Exception: 
                pass 
            self.delete_confirmation_timer_object = None
        if self.file_pending_deletion_confirmation:
            self.file_pending_deletion_confirmation = None

    def on_mouse_down(self, event: MouseDown) -> None:
        self._clear_pending_deletion_confirmation()
        self._stop_auto_rotation()
        if self.query_one("#preview", Static).region.contains(event.x, event.y):
            self.dragging = True
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y
            self.query_one("#preview", Static).focus()

    def on_mouse_move(self, event: MouseMove) -> None:
        if self.dragging:
            delta_x = event.x - self.last_mouse_x
            delta_y = event.y - self.last_mouse_y
            self.last_mouse_x = event.x
            self.last_mouse_y = event.y

            self.camera_rotation_y_radians += delta_x * 0.01
            self.camera_rotation_x_radians += delta_y * 0.01
            self.request_throttled_update()

    def on_mouse_up(self, event: MouseUp) -> None:
        self.dragging = False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python termistl.py <path_to_model.stl_or_directory>")
        sys.exit(1)
    
    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: Path not found at '{input_path}'")
        sys.exit(1)
        
    app = TermiSTL(input_path)
    app.run()