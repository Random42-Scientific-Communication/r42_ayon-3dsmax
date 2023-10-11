# -*- coding: utf-8 -*-
import pyblish.api
from openpype.pipeline import PublishValidationError
from openpype.hosts.houdini.api.action import SelectInvalidAction

import hou


class ValidateFrameRange(pyblish.api.InstancePlugin):
    """Validate Frame Range.

    Due to the usage of start and end handles,
    then Frame Range must be >= (start handle + end handle)
    which results that frameEnd be smaller than frameStart
    """

    order = pyblish.api.ValidatorOrder - 0.1
    hosts = ["houdini"]
    label = "Validate Frame Range"
    actions = [SelectInvalidAction]

    def process(self, instance):

        invalid = self.get_invalid(instance)
        if invalid:
            node = invalid[0].path()
            raise PublishValidationError(
                title="Invalid Frame Range",
                message=(
                    "Invalid frame range because the instance start frame ({0[frameStart]}) "
                    "is higher than the end frame ({0[frameEnd]})"
                    .format(instance.data)
                ),
                description=(
                    "## Invalid Frame Range\n"
                    "The frame range for the instance is invalid because the "
                    "start frame is higher than the end frame.\n\nThis is likely "
                    "due to asset handles being applied to your instance or may "
                    "be because the ROP node's start frame is set higher than the "
                    "end frame.\n\nIf your ROP frame range is correct and you do "
                    "not want to apply asset handles make sure to disable Use "
                    "asset handles on the publish instance.\n\n"
                    "Associated Node: \"{0}\"".format(node)
                )
            )

    @classmethod
    def get_invalid(cls, instance):

        if not instance.data.get("instance_node"):
            return

        rop_node = hou.node(instance.data["instance_node"])
        if instance.data["frameStart"] > instance.data["frameEnd"]:
            cls.log.info(
                "The ROP node render range is set to "
                "{0[frameStartHandle]} - {0[frameEndHandle]} "
                "The asset handles applied to the instance are start handle "
                "{0[handleStart]} and end handle {0[handleEnd]}"
                .format(instance.data)
            )
            return [rop_node]
