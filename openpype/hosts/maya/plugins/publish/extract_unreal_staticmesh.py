# -*- coding: utf-8 -*-
"""Create Unreal Static Mesh data to be extracted as FBX."""
import openpype.api
import pyblish.api
from maya import cmds  # noqa


class ExtractUnrealStaticMesh(openpype.api.Extractor):
    """Extract FBX from Maya. """

    order = pyblish.api.ExtractorOrder - 0.1
    label = "Extract Unreal Static Mesh"
    families = ["unrealStaticMesh"]

    def process(self, instance):
        to_combine = instance.data.get("membersToCombine")
        static_mesh_name = instance.data.get("staticMeshCombinedName")
        duplicates = []

        # if we have more objects, combine them into one
        # or just duplicate the single one
        if len(to_combine) > 1:
            self.log.info(
                "merging {} into {}".format(
                    " + ".join(to_combine), static_mesh_name))
            duplicates = cmds.duplicate(to_combine, ic=True)
            cmds.polyUnite(
                *duplicates,
                n=static_mesh_name, ch=False)
        else:
            self.log.info(
                "duplicating {} to {} for export".format(
                    to_combine[0], static_mesh_name)
            )
            cmds.duplicate(to_combine[0], name=static_mesh_name, ic=True)

        if not instance.data.get("cleanNodes"):
            instance.data["cleanNodes"] = []

        instance.data["cleanNodes"].append(static_mesh_name)
        instance.data["cleanNodes"] += duplicates

        instance.data["setMembers"] = [static_mesh_name]
        instance.data["setMembers"] += instance.data["collisionMembers"]
