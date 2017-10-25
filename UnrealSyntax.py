bl_info = {
    "name": "UnrealSyntax",
    "description": "Copatibility layer for 3DS Max, Unreal and Blender, using Epic Games level syntax",
    "author": "Mateusz Majda",
    "version": (0, 2, 5),
    "blender": (2, 79, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}

import sys
import os
import bpy
import random
import math

from math import degrees

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Operator,
                       PropertyGroup,
                       )


# ------------------------------------------------------------------------
#   propoetis - przyklady i referencje
# ------------------------------------------------------------------------

class MySettings(PropertyGroup):

    my_bool = BoolProperty(
        name="Enable or Disable",
        description="A bool property",
        default = False
        )

    my_int = IntProperty(
        name = "Int Value",
        description="A integer property",
        default = 23,
        min = 10,
        max = 100
        )

    my_float = FloatProperty(
        name = "Float Value",
        description = "A float property",
        default = 23.7,
        min = 0.01,
        max = 30.0
        )

    my_string = StringProperty(
        name="File Path",
        description=":",
        default=r"W:\Assets\Prototypes2017\Demiurg\_Sources\_3d",
        maxlen=1024,
        )

    my_enum = EnumProperty(
        name="Dropdown:",
        description="Apply Data to attribute.",
        items=[ ('OP1', "Option 1", ""),
                ('OP2', "Option 2", ""),
                ('OP3', "Option 3", ""),
               ]
        )


# ------------------------------------------------------------------------
#    OPERATORS - IMPOR PANEL 
# ------------------------------------------------------------------------

class ImportMeshPanel(bpy.types.Panel):
    bl_label = "Import Mesh Panel"
    bl_idname = "OBJECT_PT_Import"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
    filepath = bpy.props.StringProperty(name="PathInput")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        scene = context.scene
        mytool = scene.my_tool
        
        if obj.type == 'EMPTY':
            row = layout.row()
            row.label(text=r"Always save after making changes")
            row = layout.row()
            row.operator("wm.save", text="Save")
            row = layout.row()
            row.operator("wm.refresh", text="Refresh")
            row = layout.row()
            layout.row().separator()
            row = layout.row()
            row.label(text=r"Import/Export as FBX children of " + obj.name)
            row = layout.row()
            row.prop(context.scene, 'conf_path')
            row = layout.row()
            row.operator("wm.importfbx", text="Import FBX")
            row = layout.row()
            row.operator("wm.editbx", text="Edit FBX")
            row = layout.row()
            row.operator("wm.exportfbx", text="Export FBX")
            row = layout.row()
            layout.row().separator()
            row = layout.row()
            row.label(text=r"Settigs for Unreal Syntax export")
            row = layout.row()
            row.prop(context.scene, 'collision')
            row = layout.row()
            row.prop(context.scene, 'phys')
            row = layout.row()
            row.prop(context.scene, 'mobility')
            row = layout.row()
            row.prop(context.scene, 'folder')
            if context.scene.folder==True:
                row = layout.row()
                row.prop(context.scene, 'foldername')


# ------------------------------------------------------------------------
#    OPERATORS - SAVE ACTION
# ------------------------------------------------------------------------  

class wm_save(bpy.types.Operator):
    bl_idname="wm.save"
    bl_label="Minimal Operator"
    
    def execute(self,context):
        tosave=bpy.context.scene.objects.active
        
        tosave['source']=str(context.scene.conf_path)
        tosave['collisions']=context.scene.collision
        tosave['mobility']=context.scene.mobility
        tosave['folder']=context.scene.folder
        tosave['foldername']=str(context.scene.foldername)
        
        return {'FINISHED'}
  


# ------------------------------------------------------------------------
#    OPERATORS - REFRESH ACTION
# ------------------------------------------------------------------------  


class wm_refresh(bpy.types.Operator):
    bl_idname="wm.refresh"
    bl_label="Minimal Operator"
    
    def execute(self,context):
        torefresh=bpy.context.scene.objects.active
        
        context.scene.conf_path=torefresh['source']
        context.scene.collision=torefresh['collisions']
        context.scene.mobility=torefresh['mobility']
        context.scene.folder=torefresh['folder']
        context.scene.foldername=torefresh['foldername']
        
        return {'FINISHED'}
  

# ------------------------------------------------------------------------
#    OPERATORS - IMPORT ACTION
# ------------------------------------------------------------------------            
    
class wm_Import_FBX(bpy.types.Operator):
    bl_idname="wm.importfbx"
    bl_label="Minimal Operator"
    
    def execute(self,context):
        path=context.scene.conf_path
        base=bpy.context.scene.objects.active
        sel=len(bpy.context.scene.objects.active.children)
        
        torefresh=bpy.context.scene.objects.active
                
        context.scene.conf_path=torefresh['source']
        context.scene.collision=torefresh['collisions']
        context.scene.mobility=torefresh['mobility']
        context.scene.folder=torefresh['folder']
        context.scene.foldername=torefresh['foldername']
        
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 10000
                        s.clip_start=10
        
        bpy.context.scene.unit_settings.system='METRIC'
        bpy.context.scene.unit_settings.scale_length = 0.01
        
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
        tmp=bpy.context.scene.objects.active
        
        tmp.location=torefresh.location
        tmp.rotation_euler=torefresh.rotation_euler
        tmp.scale=torefresh.scale
        
        torefresh.location=(0,0,0)
        torefresh.rotation_euler=(0, 0, 0)
        torefresh.scale=(1,1,1)

        if sel is 1:
            todel=bpy.context.scene.objects.active.children[0]
        
            todel.hide_select=False
        
            bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
            bpy.ops.object.delete()

        str(path)
        
        bpy.ops.import_scene.fbx(filepath=path, axis_forward='-Z', axis_up='Y')
        
        toblock=bpy.context.selected_objects
        
        blocklist=len(toblock)
        
        bpy.context.scene.objects.active.select=True
        bpy.ops.object.parent_set()
        bpy.context.object.show_x_ray=True
        
        torefresh.location=tmp.location
        torefresh.rotation_euler=tmp.rotation_euler
        torefresh.scale=tmp.scale
        
        x=0
        
        while x<blocklist:
            toblock[x].hide_select=True
            x=x+1
        
        bpy.ops.object.select_all(action='DESELECT')
        
        tmp.select = True
        bpy.ops.object.delete()
        
        bpy.context.scene.objects.active=torefresh
        bpy.context.scene.objects.active.select=True


        return {'FINISHED'}


# ------------------------------------------------------------------------
#    OPERATORS - EDIT ACTION
# ------------------------------------------------------------------------

class wm_Edit_FBX(bpy.types.Operator):
    bl_idname="wm.editbx"
    bl_label="Minimal Operator"
    
    def execute(self,context):
        bpy.ops.object.select_all(action='DESELECT')
        toedit=bpy.context.scene.objects.active.children
        
        torefresh=bpy.context.scene.objects.active
                
        context.scene.conf_path=torefresh['source']
        context.scene.collision=torefresh['collisions']
        context.scene.mobility=torefresh['mobility']
        context.scene.folder=torefresh['folder']
        context.scene.foldername=torefresh['foldername']
        
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 10000
                        s.clip_start=10
        
        bpy.context.scene.unit_settings.system='METRIC'
        bpy.context.scene.unit_settings.scale_length = 0.01
        
        blocklist=len(toedit)
        
        x=0
        
        while x<blocklist:
            toedit[x].hide_select=not toedit[x].hide_select
        
            if toedit[x].hide_select is True:
                bpy.context.scene.objects.active.select=True
            if toedit[x].hide_select is False:
                bpy.context.scene.objects.active=toedit[x]
                bpy.context.scene.objects.active.select=True
                
            x=x+1
        

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    OPERATORS - EXPORT ACTION
# ------------------------------------------------------------------------

class wm_Export_FBX(bpy.types.Operator):
    bl_idname="wm.exportfbx"
    bl_label="Minimal Operator"
    
    def execute(self,context):
        path=context.scene.conf_path
        secpath=open("C:\DemiPath.ms", "r")
        line=secpath.readline()
        base=bpy.context.scene.objects.active
        toexp=bpy.context.scene.objects.active.children
        
        torefresh=bpy.context.scene.objects.active
                
        context.scene.conf_path=torefresh['source']
        context.scene.collision=torefresh['collisions']
        context.scene.mobility=torefresh['mobility']
        context.scene.folder=torefresh['folder']
        context.scene.foldername=torefresh['foldername']
        
        finalpath=path.replace(os.sep, "/")
        
        pathlenght=len(finalpath.split("/"))
        x=5
        patharray=""
            
        while x<pathlenght:
            patharray=patharray+os.sep+finalpath.split("/")[x]
            x=x+1
        
        secex=line.split('"')[1]+patharray
        
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 10000
                        s.clip_start=10
        
        bpy.context.scene.unit_settings.system='METRIC'
        bpy.context.scene.unit_settings.scale_length = 0.01
        
        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
        
        tmp=bpy.context.scene.objects.active
        
        explist=len(toexp)
        
        x=0
        
        while x<explist:
            toexp[x].hide_select=False
            x=x+1
        
        tmp.location=base.location
        tmp.rotation_euler=base.rotation_euler
        tmp.scale=base.scale
        
        base.location=(0,0,0)
        base.rotation_euler=(0, 0, 0)
        base.scale=(1,1,1)
        
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects.active=base
        base.select = True
        bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        
        str(path)
        str(secex)
        
        bpy.ops.export_scene.fbx(filepath=path, use_selection=True)
        bpy.ops.export_scene.fbx(filepath=secex, use_selection=True)
        bpy.ops.object.select_all(action='DESELECT')
        
        base.location=tmp.location
        base.rotation_euler=tmp.rotation_euler
        base.scale=tmp.scale
        
        tmp.select = True
        bpy.ops.object.delete()
        
        x=0
        
        while x<explist:
            toexp[x].hide_select=True
            x=x+1
        
        bpy.context.scene.objects.active=base
        bpy.context.scene.objects.active.select=True
            

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    OPERATORS - CREATE STATIC MESH
# ------------------------------------------------------------------------

class CreateAssetOperator(bpy.types.Operator):
    bl_idname = "wm.createstatic"
    bl_label = "Create StaticMesh"

    def execute(self, context):
        scene = context.scene
        mytool = scene.my_tool
        
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 10000
                        s.clip_start=10
        
        bpy.context.scene.unit_settings.system='METRIC'
        bpy.context.scene.unit_settings.scale_length = 0.01

        bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
        bpy.context.object.empty_draw_size = 30
        
        propobj=bpy.context.scene.objects.active
        
        propobj['source']=r'W:\Assets\Prototypes2017\Demiurg\_Sources'
        propobj['collisions']=False
        propobj['phys']=False
        propobj['mobility']='Static'
        propobj['folder']=False
        propobj['foldername']='NewFolder'
        
        tosave=bpy.context.scene.objects.active
        
        tosave['source']=str(context.scene.conf_path)
        tosave['collisions']=context.scene.collision
        tosave['mobility']=context.scene.mobility
        tosave['folder']=context.scene.folder
        tosave['foldername']=str(context.scene.foldername)

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    OPERATORS - IMPORT SCENE
# ------------------------------------------------------------------------

class ImportSceneOperator(bpy.types.Operator):
    bl_idname = "wm.importscene"
    bl_label = "Import Scene"

    def execute(self, context):
        toimport=bpy.context.window_manager.clipboard
        
        impspli=toimport.splitlines()
        
        for a in bpy.context.screen.areas:
            if a.type == 'VIEW_3D':
                for s in a.spaces:
                    if s.type == 'VIEW_3D':
                        s.clip_end = 10000
                        s.clip_start=10
        
        bpy.context.scene.unit_settings.system='METRIC'
        bpy.context.scene.unit_settings.scale_length = 0.01
        
        #count begins and ends and saves them to list
        
        occure=[n for n in range(len(toimport)) if toimport.find('Begin Actor', n) == n]
        occlist=len(occure)
        
        occureend=[m for m in range(len(toimport)) if toimport.find('End Actor', m) == m]
        occlistend=len(occureend)
        
        #import actor loop run
        
        if impspli[0]=="Begin Map":
            
            a=0
            
            z=0
            
            xa=0
            
            done=occure[occlist-1]
            
            while a<done:
                
                a=occure[xa]
                
                z=occureend[xa]
                
                toimportcut=toimport[a:z]
                
                impsplicu=toimportcut.splitlines()
                
                sekeldir=[n for n in range(len(toimportcut)) if toimportcut.find('SkeletalMesh=SkeletalMesh', n) == n]
                statdir=[n for n in range(len(toimportcut)) if toimportcut.find('StaticMesh=StaticMesh', n) == n]
                countskeldir=len(sekeldir)
                countstatdir=len(statdir)
                
                if countskeldir>0:
                     directory=toimportcut[sekeldir[0]:]
                
                if countstatdir>0:
                    directory=toimportcut[statdir[0]:]
            
                # create and name root
                
                aname=directory.split('.')[1].split("'")[0]+"_"+str(random.randint(10,99))
                bpy.ops.object.empty_add(type='PLAIN_AXES', view_align=False, location=(0, 0, 0))
                bpy.context.object.empty_draw_size = 30
                
                propobj=bpy.context.scene.objects.active
        
                propobj['source']=r'W:\Assets\Prototypes2017\Demiurg\_Sources'
                propobj['collisions']=False
                propobj['mobility']='Static'
                propobj['folder']=False
                propobj['foldername']='NewFolder'

                rootempty=bpy.context.scene.objects.active
                rootempty.name=aname
                
                # import asset
                
                anamebase=aname.rsplit("_",1)
                apath=directory.split("'")[1].split(".")[0].split("/")
                
                pathlen=len(apath)
                
                z=2
                patharray=""
                
                while z<pathlen:
                    patharray=patharray+"/"+apath[z]
                    z=z+1
                
                anamenew=impsplicu[4].split('.')[1].split("'")[0]

                apathfinal=r"W:/Assets/Prototypes2017/Demiurg/_Sources"+patharray+".fbx"
                
                str(apathfinal)
                
                bpy.ops.object.select_all(action='DESELECT')
            
                bpy.ops.import_scene.fbx(filepath=apathfinal, axis_forward='-Z', axis_up='Y')
                
                toblock=bpy.context.selected_objects
            
                blocklist=len(toblock)
                
                bpy.context.scene.objects.active.select=True
                bpy.ops.object.parent_set()
                bpy.context.object.show_x_ray=True
                
                x=0
            
                while x<blocklist:
                    toblock[x].hide_select=True
                    x=x+1
                
                bpy.ops.object.select_all(action='DESELECT')
                    
                
                # set transforms
                
                if "RelativeLocation" in toimportcut:
                    alocx=toimportcut.split("RelativeLocation=(X=")[1].split(",")[0]
                    alocy=toimportcut.split("Y=")[1].split(",")[0]
                    alocz=toimportcut.split("Z=")[1].split(")")[0]
                    flx=float(alocx)
                    fly=float(alocy)
                    flz=float(alocz)
                    rootempty.location=(flx,(fly*-1),flz)
                
                if "RelativeRotation" in toimportcut:
                    arotx=toimportcut.split("RelativeRotation=(Pitch=")[1].split(",")[0]
                    aroty=toimportcut.split("Yaw=")[1].split(",")[0]
                    arotz=toimportcut.split("Roll=")[1].split(")")[0]
                    frx=math.radians(float(arotx))
                    fry=math.radians(float(aroty))
                    frz=math.radians(float(arotz))
                    rootempty.rotation_euler=(frz,(frx*-1),(fry*-1))
                    
                if "RelativeScale3D" in toimportcut:
                    if "RelativeLocation" in toimportcut:
                        ascax=toimportcut.split("RelativeScale3D=(X=")[1].split(",")[0]
                        ascay=toimportcut.split("Y=")[2].split(",")[0]
                        ascaz=toimportcut.split("Z=")[2].split(")")[0]
                        fsx=float(ascax)
                        fsy=float(ascay)
                        fsz=float(ascaz)
                        rootempty.scale=(fsx,fsy,fsz)
                    
                    if "RelativeLocation" not in toimportcut:
                        ascax=toimportcut.split("RelativeScale3D=(X=")[1].split(",")[0]
                        ascay=toimportcut.split("Y=")[1].split(",")[0]
                        ascaz=toimportcut.split("Z=")[1].split(")")[0]
                        fsx=float(ascax)
                        fsy=float(ascay)
                        fsz=float(ascaz)
                        rootempty.scale=(fsx,fsy,fsz)
                        
                        
                # set additional settings
                
                if "BodyInstance" in toimportcut:
                    propobj['collisions']=True
                    if "NoCollision" in toimportcut:
                        propobj['collisions']=False
                    if "BlockAll" in toimportcut:
                        propobj['collisions']=True

                if "BodyInstance" not in toimportcut:
                    propobj['collisions']=True
                    
                    
                if "Stationary" in toimportcut:
                    propobj['mobility']='Stationary'
                    
                if "Movable" in toimportcut:
                    propobj['mobility']='Movable'
                
                
                propobj['source']=apathfinal
                
                
                if "FolderPath" in toimportcut:
                    propobj['folder']=True
                    propobj['foldername']=toimportcut.split('FolderPath="')[1].split('"')[0]
                
                
                # finish and offset
                
                xa=xa+1
                        
            
        return {'FINISHED'}
    
    
# ------------------------------------------------------------------------
#    OPERATORS - EXPORT SCENE
# ------------------------------------------------------------------------

class ExportSceneOperator(bpy.types.Operator):
    bl_idname = "wm.exportscene"
    bl_label = "Export Scene"

    def execute(self, context):
        scene = bpy.context.scene
        wholeactor=""
        
        bpy.ops.object.select_all(action='DESELECT')
        
        for ob in scene.objects:
            if ob.type == 'EMPTY':
                if 'source' in ob:
                    ob.select=True
        
        toexport=bpy.context.selected_objects
        
        bpy.ops.object.select_all(action='DESELECT')
        
        exportamount=len(toexport)
        
        
        #create file procedure:
        
        y=0
        
        encoded=bpy.context.window_manager.clipboard.encode('utf8')
        beginstring="Begin Map\n   Begin Level"
        
        while y<exportamount:
            
            bpy.context.scene.objects.active=toexport[y]
            toexport[y].select=True
            
            torefresh=toexport[y]
                
            context.scene.conf_path=torefresh['source']
            context.scene.collision=torefresh['collisions']
            context.scene.mobility=torefresh['mobility']
            context.scene.folder=torefresh['folder']
            context.scene.foldername=torefresh['foldername']
            
            beginactor="\n      Begin Actor Class=/Script/Engine.StaticMeshActor Name="
        
            path=toexport[y][r'source']
            actorname=bpy.path.basename(path).split(".")[0]+"_"+str(random.randint(10,99))
            str(actorname)
            
            actorarchetype=" Archetype=/Script/Engine.StaticMeshActor'/Script/Engine.Default__StaticMeshActor'"
            
            beginobject="""\n         Begin Object Class=/Script/Engine.StaticMeshComponent Name="StaticMeshComponent0" Archetype=StaticMeshComponent'/Script/Engine.Default__StaticMeshActor:StaticMeshComponent0'\n         End Object\n         Begin Object Name="StaticMeshComponent0" """
            
            beginstatic="\n            StaticMesh=StaticMesh'/Game"
            
            str(path)
        
            pathr=path.replace("/", os.sep)
        
            pathlenght=len(pathr.split(os.sep))-1  # -1:ignorowanie nazwy pliku
        
            x=5
            patharray=""
        
            while x<pathlenght:
                patharray=patharray+"/"+pathr.split(os.sep)[x]
                x=x+1
        
            pathname=patharray+"/"+bpy.path.basename(pathr).split(".")[0]+"."+bpy.path.basename(pathr).split(".")[0]+"'"
            
            version="\n            StaticMeshImportVersion=1"
            
            coluse="\n            bUseDefaultCollision=False"
            
            if context.scene.collision==True:
                colbool="""\n            BodyInstance=(CollisionProfileName="BlockAll",ObjectType=ECC_WorldDynamic)"""
                
            if context.scene.collision==False:
                colbool="""\n            BodyInstance=(CollisionProfileName="NoCollision",CollisionResponses=(ResponseArray=((Channel="Visibility",Response=ECR_Ignore),(Channel="Camera",Response=ECR_Ignore))),CollisionEnabled=NoCollision)"""
            
            rootempty=bpy.context.scene.objects.active

            rot_angles = rootempty.matrix_world.to_euler()
            rot_angles_X = math.degrees(rot_angles[0])
            rot_angles_Y = math.degrees(rot_angles[1])
            rot_angles_Z = math.degrees(rot_angles[2])
                    
            objloc="\n            RelativeLocation=(X="+str(round((rootempty.location.x), 6))+",Y="+str(round((rootempty.location.y*-1), 6))+",Z="+str(round((rootempty.location.z), 6))+")"
            objrot="\n            RelativeRotation=(Pitch="+str(round((rot_angles_Y*-1),9))+",Yaw="+str(round((rot_angles_Z*-1),9))+",Roll="+str(round((rot_angles_X),9))+")"
            objsca="\n            RelativeScale3D=(X="+str(round((rootempty.scale.x), 6))+",Y="+str(round((rootempty.scale.y), 6))+",Z="+str(round((rootempty.scale.z), 6))+")"
            
            mob="\n            Mobility="+context.scene.mobility
            
            endobject="\n         End Object"
            
            staticmesh="\n         StaticMeshComponent=StaticMeshComponent0"
            
            rootc="\n         RootComponent=StaticMeshComponent0"
            
            actorl='\n         ActorLabel="'+str(actorname)+'"'
            
            folder=""
            
            if context.scene.folder==True:
                folder='\n         FolderPath="'+context.scene.foldername+'"'
            
            endactor="\n      End Actor"
            
            bpy.ops.object.select_all(action='DESELECT')
            
            wholeactor=wholeactor+beginactor+actorname+actorarchetype+beginobject+beginstatic+pathname+version+coluse+colbool+objloc+objrot+objsca+mob+endobject+staticmesh+rootc+actorl+folder+endactor
            
            y=y+1
            
            
        endstring="\n   End Level\nBegin Surface\nEnd Surface\nEnd Map"
        
        
        
        export=beginstring+wholeactor+endstring
        str(export)
        bpy.context.window_manager.clipboard=export
        

        return {'FINISHED'}
    

# ------------------------------------------------------------------------
#    OPERATORS - EXPORT ACTIVE
# ------------------------------------------------------------------------

class ExportSelectedOperator(bpy.types.Operator):
    bl_idname = "wm.exportselected"
    bl_label = "Export Active"

    def execute(self, context):
        source=bpy.context.scene.objects.active
                
        context.scene.conf_path=source['source']
        context.scene.collision=source['collisions']
        context.scene.mobility=source['mobility']
        context.scene.folder=source['folder']
        context.scene.foldername=source['foldername']
        
        encoded=bpy.context.window_manager.clipboard.encode('utf8')
        beginstring="Begin Map\n   Begin Level"
        
        
        #loop begin
        
        beginactor="\n      Begin Actor Class=/Script/Engine.StaticMeshActor Name="
        
        path=context.scene.conf_path
        actorname=bpy.path.basename(path).split(".")[0]+"_"+str(random.randint(10,99))
        str(actorname)
        
        actorarchetype=" Archetype=/Script/Engine.StaticMeshActor'/Script/Engine.Default__StaticMeshActor'"
        
        beginobject="""\n         Begin Object Class=/Script/Engine.StaticMeshComponent Name="StaticMeshComponent0" Archetype=StaticMeshComponent'/Script/Engine.Default__StaticMeshActor:StaticMeshComponent0'\n         End Object\n         Begin Object Name="StaticMeshComponent0" """
        
        beginstatic="\n            StaticMesh=StaticMesh'/Game"
        
        str(path)
        
        pathr=path.replace("/", os.sep)
        
        pathlenght=len(pathr.split(os.sep))-1  # -1:ignorowanie nazwy pliku
        
        x=5
        patharray=""
        
        while x<pathlenght:
            patharray=patharray+"/"+pathr.split(os.sep)[x]
            x=x+1
        
        pathname=patharray+"/"+bpy.path.basename(pathr).split(".")[0]+"."+bpy.path.basename(pathr).split(".")[0]+"'"

        version="\n            StaticMeshImportVersion=1"
        
        coluse="\n            bUseDefaultCollision=False"
        
        if context.scene.collision==True:
            colbool="""\n            BodyInstance=(CollisionProfileName="BlockAll",ObjectType=ECC_WorldDynamic)"""
            
        if context.scene.collision==False:
            colbool="""\n            BodyInstance=(CollisionProfileName="NoCollision",CollisionResponses=(ResponseArray=((Channel="Visibility",Response=ECR_Ignore),(Channel="Camera",Response=ECR_Ignore))),CollisionEnabled=NoCollision)"""
        
        rootempty=bpy.context.scene.objects.active
        
        rot_angles = rootempty.matrix_world.to_euler()
        rot_angles_X = math.degrees(rot_angles[0])
        rot_angles_Y = math.degrees(rot_angles[1])
        rot_angles_Z = math.degrees(rot_angles[2])
                
        objloc="\n            RelativeLocation=(X="+str(round((rootempty.location.x), 6))+",Y="+str(round((rootempty.location.y*-1), 6))+",Z="+str(round((rootempty.location.z), 6))+")"
        objrot="\n            RelativeRotation=(Pitch="+str(round((rot_angles_Y*-1),9))+",Yaw="+str(round((rot_angles_Z*-1),9))+",Roll="+str(round((rot_angles_X),9))+")"
        objsca="\n            RelativeScale3D=(X="+str(round((rootempty.scale.x), 6))+",Y="+str(round((rootempty.scale.y), 6))+",Z="+str(round((rootempty.scale.z), 6))+")"
        
        mob="\n            Mobility="+context.scene.mobility
        
        endobject="\n         End Object"
        
        staticmesh="\n         StaticMeshComponent=StaticMeshComponent0"
        
        rootc="\n         RootComponent=StaticMeshComponent0"
        
        actorl='\n         ActorLabel="'+str(actorname)+'"'
        
        folder=""
        
        if context.scene.folder==True:
            folder='\n         FolderPath="'+context.scene.foldername+'"'
        
        endactor="\n      End Actor"
        
        #loop end
        
        
        endstring="\n   End Level\nBegin Surface\nEnd Surface\nEnd Map"
        
        
        
        export=beginstring+beginactor+actorname+actorarchetype+beginobject+beginstatic+pathname+version+coluse+colbool+objloc+objrot+objsca+mob+endobject+staticmesh+rootc+actorl+folder+endactor+endstring
        str(export)
        bpy.context.window_manager.clipboard=export

        return {'FINISHED'}


# ------------------------------------------------------------------------
#    my tool in objectmode
# ------------------------------------------------------------------------

class MaxUnrealBlenderScene(bpy.types.Panel):
    bl_idname = "OBJECT_PT_MaxUnrealBlenderScene"
    bl_label = "Unreal Syntax"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "TOOLS"    
    bl_category = "USyntax"
    bl_context = "objectmode"   

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.operator("wm.createstatic")
        layout.row().separator()
        layout.operator("wm.importscene")
        layout.operator("wm.exportscene")
        layout.operator("wm.exportselected")


# ------------------------------------------------------------------------
# register and unregister
# ------------------------------------------------------------------------

def register():
    bpy.utils.register_module(__name__)
    bpy.types.Scene.conf_path=bpy.props.StringProperty \
          (
          name="Asset Source",
          default=r"W:\Assets\Prototypes2017\Demiurg\_Sources\_3d",
          description="Asset FBX",
          subtype='FILE_PATH'
          )
    bpy.types.Scene.collision=bpy.props.BoolProperty \
        (
        name="Collisions",
        description="Enable or Disable collisions",
        default = False
        )
    bpy.types.Scene.phys=bpy.props.BoolProperty \
        (
        name="Simulate Physics",
        description="Enable simulating in real time",
        default = False
        )
    bpy.types.Scene.mobility=bpy.props.EnumProperty \
        (
        name="Mobility",
        description="Set object mobility",
        items=[ ('Static', "Static", ""),
                ('Stationary', "Stationary", ""),
                ('Movable', "Movable", ""),
               ]
        )
    bpy.types.Scene.folder=bpy.props.BoolProperty \
        (
        name="Object in folder",
        description="Exports object in folder",
        default = False
        )
    bpy.types.Scene.foldername=bpy.props.StringProperty \
          (
          name="Folder name",
          default=r"NewFolder",
          description="Export folder name"
          )
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.conf_path
    del bpy.types.Scene.collision
    del bpy.types.Scene.mobility
    del bpy.types.Scene.folder
    del bpy.types.Scene.foldername
    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
