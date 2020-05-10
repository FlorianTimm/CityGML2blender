 
bl_info = {
    "name": "CityGML2blender",
    "blender": (2, 82, 0),
    "category": "Import-Export",
}

import os
from xml.etree import ElementTree as et
import bpy
from bpy_extras.io_utils import ExportHelper
import bmesh


def read_some_data(context, filepath):
    print("running read_some_data...")
    collection = bpy.data.collections.new("LoD")
    bpy.context.scene.collection.children.link(collection)

    tree = et.parse(filepath)

    buildings = tree.findall('.//{http://www.opengis.net/citygml/building/1.0}Building')
    print('Hallo')

    # Ecke
    firstXML = tree.find('.//{http://www.opengis.net/gml}lowerCorner')
    first = [float(i) for i in firstXML.text.split(' ')]

    for buildingXML in buildings:
        m = bpy.data.meshes.new("Mesh")

        obj = bpy.data.objects.new("obj_name", m)
        collection.objects.link(obj)
        
        vertex = []
        faces = []

        bounds = buildingXML.findall('.//{http://www.opengis.net/citygml/building/1.0}boundedBy')

        for bound in bounds:
            polygons = bound.findall('.//{http://www.opengis.net/gml}Polygon')
            for poly in polygons:
                coords = poly.findall('.//{http://www.opengis.net/gml}pos')
                
                coordlist = []
                for coord in coords[:-1]:
                    coordlist.append(len(vertex))
                    v = [float(i) for i in coord.text.split(' ')]
                    v[0] -= first[0]
                    v[1] -= first[1]
                    vertex.append(v)
                #coordlist.append(coordlist[0])
                faces.append(coordlist)
                
            
        print(*vertex)
        print(*faces)
        m.from_pydata(vertex,[],faces)
        m.update()
        
        bm = bmesh.new()
        bm.from_mesh(m)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.01)
        bm.to_mesh(m)
        bm.free()

    return {'FINISHED'}


# ImportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class CityGML2blender(Operator, ImportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "import_test.some_data"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "CityGML importieren"

    # ImportHelper mixin class uses this
    filename_ext = ".xml"

    filter_glob: StringProperty(
        default="*.xml",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped.
    )

    def execute(self, context):
        return read_some_data(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_import(self, context):
    self.layout.operator(CityGML2blender.bl_idname, text="CityGML")


def register():
    bpy.utils.register_class(CityGML2blender)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import)


def unregister():
    bpy.utils.unregister_class(CityGML2blender)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.import_test.some_data('INVOKE_DEFAULT')
