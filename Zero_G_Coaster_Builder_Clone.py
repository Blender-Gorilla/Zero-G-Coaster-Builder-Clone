bl_info = {
    "name": "Zero G Coaster Builder Clone - Enhanced",
    "author": "OpenAI / ChatGPT",
    "version": (1, 1),
    "blender": (3, 0, 0),
    "location": "View3D > Sidebar > Coaster",
    "description": "Build spline-based coasters with mesh, banking, supports, and animation.",
    "category": "Add Mesh",
}

import bpy
import math
from mathutils import Vector

# -----------------------------------
# UTILITY FUNCTIONS
# -----------------------------------

def create_coaster_curve():
    curve_data = bpy.data.curves.new(name='CoasterCurve', type='CURVE')
    curve_data.dimensions = '3D'
    curve_data.resolution_u = 24

    spline = curve_data.splines.new('BEZIER')
    spline.bezier_points.add(4)

    points = [
        Vector((0, 0, 0)),
        Vector((5, 0, 2)),
        Vector((10, 2, 4)),
        Vector((15, -2, 3)),
        Vector((20, 0, 1))
    ]
    for i, pt in enumerate(spline.bezier_points):
        pt.co = points[i]
        pt.handle_left_type = 'AUTO'
        pt.handle_right_type = 'AUTO'
        pt.tilt = 0.0  # Banking

    curve_obj = bpy.data.objects.new('CoasterTrack', curve_data)
    bpy.context.collection.objects.link(curve_obj)
    bpy.context.view_layer.objects.active = curve_obj
    curve_obj.select_set(True)
    return curve_obj

def generate_mesh_from_curve(obj):
    if obj.type != 'CURVE':
        return
    obj.data.bevel_depth = 0.05
    obj.data.bevel_resolution = 4
    obj.data.fill_mode = 'FULL'
    obj.data.resolution_u = 24

def create_supports_along_curve(curve_obj, step=5.0):
    if curve_obj.type != 'CURVE':
        return

    curve = curve_obj.data
    resolution = 100
    collection_name = "Supports"

    # Create or get supports collection
    if collection_name not in bpy.data.collections:
        support_col = bpy.data.collections.new(collection_name)
        bpy.context.scene.collection.children.link(support_col)
    else:
        support_col = bpy.data.collections[collection_name]

    # Clean previous supports
    for obj in support_col.objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    for i in range(0, resolution, int(step)):
        t = i / resolution
        pos = curve_obj.matrix_world @ curve_obj.data.splines[0].evaluate(t)
        height = pos.z
        if height <= 0.05:
            continue
        bpy.ops.mesh.primitive_cylinder_add(radius=0.05, depth=height)
        cyl = bpy.context.active_object
        cyl.location = (pos.x, pos.y, height / 2)
        support_col.objects.link(cyl)
        bpy.context.collection.objects.unlink(cyl)

def apply_banking_to_selected_points(obj, angle_deg):
    if obj and obj.type == 'CURVE' and obj.mode == 'EDIT':
        angle_rad = math.radians(angle_deg)
        bpy.ops.object.mode_set(mode='OBJECT')
        spline = obj.data.splines[0]
        for pt in spline.bezier_points:
            if pt.select_control_point:
                pt.tilt = angle_rad
        bpy.ops.object.mode_set(mode='EDIT')

# -----------------------------------
# UI OPERATORS
# -----------------------------------

class OBJECT_OT_create_coaster(bpy.types.Operator):
    bl_idname = "object.create_coaster_track"
    bl_label = "Create Coaster Track"
    def execute(self, context):
        create_coaster_curve()
        return {'FINISHED'}

class OBJECT_OT_mesh_track(bpy.types.Operator):
    bl_idname = "object.mesh_coaster_track"
    bl_label = "Mesh Track"
    def execute(self, context):
        obj = context.active_object
        generate_mesh_from_curve(obj)
        return {'FINISHED'}

class OBJECT_OT_generate_supports(bpy.types.Operator):
    bl_idname = "object.generate_supports"
    bl_label = "Generate Supports"
    def execute(self, context):
        obj = context.active_object
        create_supports_along_curve(obj)
        return {'FINISHED'}

class OBJECT_OT_apply_banking(bpy.types.Operator):
    bl_idname = "object.apply_banking"
    bl_label = "Apply Banking to Selected Points"
    angle: bpy.props.FloatProperty(name="Bank Angle (°)", default=30.0, min=-180.0, max=180.0)
    def execute(self, context):
        obj = context.active_object
        apply_banking_to_selected_points(obj, self.angle)
        return {'FINISHED'}

# -----------------------------------
# UI PANEL
# -----------------------------------

class VIEW3D_PT_coaster_ui(bpy.types.Panel):
    bl_label = "Coaster Builder"
    bl_idname = "VIEW3D_PT_coaster_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Coaster'

    def draw(self, context):
        layout = self.layout
        layout.label(text="Track Tools:")
        layout.operator("object.create_coaster_track", icon='CURVE_BEZCURVE')
        layout.operator("object.mesh_coaster_track", icon='MOD_CURVE')
        layout.separator()
        layout.label(text="Banking Tools:")
        layout.operator("object.apply_banking", icon='MOD_SIMPLEDEFORM')
        layout.separator()
        layout.label(text="Support Tools:")
        layout.operator("object.generate_supports", icon='MESH_CYLINDER')

# -----------------------------------
# REGISTRATION
# -----------------------------------

classes = (
    OBJECT_OT_create_coaster,
    OBJECT_OT_mesh_track,
    OBJECT_OT_generate_supports,
    OBJECT_OT_apply_banking,
    VIEW3D_PT_coaster_ui,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
