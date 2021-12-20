""" compatibility OpenTimelineIO 0.12.0 and newer
"""

import os
import re
import sys
import json
import logging
import opentimelineio as otio
from . import utils

import flame
from pprint import pformat

reload(utils)  # noqa

log = logging.getLogger(__name__)


TRACK_TYPES = {
    "video": otio.schema.TrackKind.Video,
    "audio": otio.schema.TrackKind.Audio
}
MARKERS_COLOR_MAP = {
    "magenta": otio.schema.MarkerColor.MAGENTA,
    "red": otio.schema.MarkerColor.RED,
    "yellow": otio.schema.MarkerColor.YELLOW,
    "green": otio.schema.MarkerColor.GREEN,
    "cyan": otio.schema.MarkerColor.CYAN,
    "white": otio.schema.MarkerColor.WHITE,
    "orange": otio.schema.MarkerColor.ORANGE,
    "blue": otio.schema.MarkerColor.BLUE,
    "purple": otio.schema.MarkerColor.PURPLE,
    "pink": otio.schema.MarkerColor.PINK,
    "black": otio.schema.MarkerColor.BLACK,
}
MARKERS_INCLUDE = True


class CTX:
    _fps = None
    _tl_start_frame = None
    project = None
    clips = None

    @classmethod
    def set_fps(cls, new_fps):
        if not isinstance(new_fps, float):
            raise TypeError("Invalid fps type {}".format(type(new_fps)))
        if cls._fps != new_fps:
            cls._fps = new_fps

    @classmethod
    def get_fps(cls):
       return cls._fps

    @classmethod
    def set_tl_start_frame(cls, number):
        if not isinstance(number, int):
            raise TypeError("Invalid timeline start frame type {}".format(
                type(number)))
        if cls._tl_start_frame != number:
            cls._tl_start_frame = number

    @classmethod
    def get_tl_start_frame(cls):
       return cls._tl_start_frame


def flatten(_list):
    for item in _list:
        if isinstance(item, (list, tuple)):
            for sub_item in flatten(item):
                yield sub_item
        else:
            yield item


def get_current_flame_project():
    project = flame.project.current_project
    return project


def create_otio_rational_time(frame, fps):
    return otio.opentime.RationalTime(
        float(frame),
        float(fps)
    )


def create_otio_time_range(start_frame, frame_duration, fps):
    return otio.opentime.TimeRange(
        start_time=create_otio_rational_time(start_frame, fps),
        duration=create_otio_rational_time(frame_duration, fps)
    )


def _get_metadata(item):
    if hasattr(item, 'metadata'):
        if not item.metadata:
            return {}
        return {key: value for key, value in dict(item.metadata)}
    return {}


def create_time_effects(otio_clip, item):
    # todo #2426: add retiming effects to export
    pass
    # get all subtrack items
    # subTrackItems = flatten(track_item.parent().subTrackItems())
    # speed = track_item.playbackSpeed()

    # otio_effect = None
    # # retime on track item
    # if speed != 1.:
    #     # make effect
    #     otio_effect = otio.schema.LinearTimeWarp()
    #     otio_effect.name = "Speed"
    #     otio_effect.time_scalar = speed
    #     otio_effect.metadata = {}

    # # freeze frame effect
    # if speed == 0.:
    #     otio_effect = otio.schema.FreezeFrame()
    #     otio_effect.name = "FreezeFrame"
    #     otio_effect.metadata = {}

    # if otio_effect:
    #     # add otio effect to clip effects
    #     otio_clip.effects.append(otio_effect)

    # # loop trought and get all Timewarps
    # for effect in subTrackItems:
    #     if ((track_item not in effect.linkedItems())
    #             and (len(effect.linkedItems()) > 0)):
    #         continue
    #     # avoid all effect which are not TimeWarp and disabled
    #     if "TimeWarp" not in effect.name():
    #         continue

    #     if not effect.isEnabled():
    #         continue

    #     node = effect.node()
    #     name = node["name"].value()

    #     # solve effect class as effect name
    #     _name = effect.name()
    #     if "_" in _name:
    #         effect_name = re.sub(r"(?:_)[_0-9]+", "", _name)  # more numbers
    #     else:
    #         effect_name = re.sub(r"\d+", "", _name)  # one number

    #     metadata = {}
    #     # add knob to metadata
    #     for knob in ["lookup", "length"]:
    #         value = node[knob].value()
    #         animated = node[knob].isAnimated()
    #         if animated:
    #             value = [
    #                 ((node[knob].getValueAt(i)) - i)
    #                 for i in range(
    #                     track_item.timelineIn(),
    #                     track_item.timelineOut() + 1)
    #             ]

    #         metadata[knob] = value

    #     # make effect
    #     otio_effect = otio.schema.TimeEffect()
    #     otio_effect.name = name
    #     otio_effect.effect_name = effect_name
    #     otio_effect.metadata = metadata

    #     # add otio effect to clip effects
    #     otio_clip.effects.append(otio_effect)


def _get_marker_color(flame_colour):
    if flame_colour in MARKERS_COLOR_MAP:
        return MARKERS_COLOR_MAP[flame_colour]

    return otio.schema.MarkerColor.RED


def _get_flame_markers(item):
    output_markers = []

    time_in = item.record_in.relative_frame

    for marker in item.markers:
        log.debug(marker)
        start_frame = marker.location.get_value().relative_frame

        start_frame = (start_frame - time_in) + 1

        marker_data = {
            "name": marker.name.get_value(),
            "duration": marker.duration.get_value().relative_frame,
            "comment": marker.comment.get_value(),
            "start_frame": start_frame,
            "colour": marker.colour.get_value()
        }

        output_markers.append(marker_data)

    return output_markers


def create_otio_markers(otio_item, item):
    markers = _get_flame_markers(item)
    for marker in markers:
        frame_rate = CTX.get_fps()

        marked_range = otio.opentime.TimeRange(
            start_time=otio.opentime.RationalTime(
                marker["start_frame"],
                frame_rate
            ),
            duration=otio.opentime.RationalTime(
                marker["duration"],
                frame_rate
            )
        )

        # testing the comment if it is not containing json string
        check_if_json = re.findall(
            re.compile(r"[{:}]"),
            marker["comment"]
        )

        # to identify this as json, at least 3 items in the list should
        # be present ["{", ":", "}"]
        metadata = {}
        if len(check_if_json) >= 3:
            # this is json string
            try:
                # capture exceptions which are related to strings only
                metadata.update(
                    json.loads(marker["comment"])
                )
            except ValueError as msg:
                log.error("Marker json conversion: {}".format(msg))
        else:
            metadata["comment"] = marker["comment"]

        marker = otio.schema.Marker(
            name=marker["name"],
            color=_get_marker_color(
                marker["colour"]),
            marked_range=marked_range,
            metadata=metadata
        )

        otio_item.markers.append(marker)


def create_otio_reference(clip_data):
    metadata = _get_metadata(clip_data)

    # get file info for path and start frame
    frame_start = 0
    fps = CTX.get_fps()

    path = clip_data["fpath"]

    reel_clip = None
    match_reel_clip = [
        clip for clip in CTX.clips
        if clip["fpath"] == path
    ]
    if match_reel_clip:
        reel_clip = match_reel_clip.pop()
        fps = reel_clip["fps"]

    file_name = os.path.basename(path)
    file_head, extension = os.path.splitext(file_name)

    # get padding and other file infos
    log.debug("_ path: {}".format(path))

    is_sequence = padding = utils.get_frame_from_path(path)
    if is_sequence:
        number = utils.get_frame_from_path(path)
        file_head = file_name.split(number)[:-1]
        frame_start = int(number)

    frame_duration = clip_data["source_duration"]

    if is_sequence:
        metadata.update({
            "isSequence": True,
            "padding": padding
        })

    otio_ex_ref_item = None

    if is_sequence:
        # if it is file sequence try to create `ImageSequenceReference`
        # the OTIO might not be compatible so return nothing and do it old way
        try:
            dirname = os.path.dirname(path)
            otio_ex_ref_item = otio.schema.ImageSequenceReference(
                target_url_base=dirname + os.sep,
                name_prefix=file_head,
                name_suffix=extension,
                start_frame=frame_start,
                frame_zero_padding=padding,
                rate=fps,
                available_range=create_otio_time_range(
                    frame_start,
                    frame_duration,
                    fps
                )
            )
        except AttributeError:
            pass

    if not otio_ex_ref_item:
        reformat_path = utils.get_reformated_path(path, padded=False)
        # in case old OTIO or video file create `ExternalReference`
        otio_ex_ref_item = otio.schema.ExternalReference(
            target_url=reformat_path,
            available_range=create_otio_time_range(
                frame_start,
                frame_duration,
                fps
            )
        )

    # add metadata to otio item
    add_otio_metadata(otio_ex_ref_item, clip_data, **metadata)

    return otio_ex_ref_item


def create_otio_clip(clip_data):
    segment = clip_data["PySegment"]

    # create media reference
    media_reference = create_otio_reference(clip_data)

    # calculate source in
    first_frame = utils.get_frame_from_path(clip_data["fpath"]) or 0
    source_in = int(clip_data["source_in"]) - int(first_frame)

    # creatae source range
    source_range = create_otio_time_range(
        source_in,
        clip_data["record_duration"],
        CTX.get_fps()
    )

    otio_clip = otio.schema.Clip(
        name=clip_data["segment_name"],
        source_range=source_range,
        media_reference=media_reference
    )

    # Add markers
    if MARKERS_INCLUDE:
        create_otio_markers(otio_clip, segment)

    return otio_clip


def create_otio_gap(gap_start, clip_start, tl_start_frame, fps):
    return otio.schema.Gap(
        source_range=create_otio_time_range(
            gap_start,
            (clip_start - tl_start_frame) - gap_start,
            fps
        )
    )


def get_clips_in_reels(project):
    output_clips = []
    project_desktop = project.current_workspace.desktop

    for reel_group in project_desktop.reel_groups:
        for reel in reel_group.reels:
            for clip in reel.clips:
                clip_data = {
                    "PyClip": clip,
                    "fps": float(str(clip.frame_rate)[:-4])
                }

                attrs = [
                    "name", "width", "height",
                    "ratio", "sample_rate", "bit_depth"
                ]

                for attr in attrs:
                    val = getattr(clip, attr)
                    clip_data[attr] = val

                version = clip.versions[-1]
                track = version.tracks[-1]
                for segment in track.segments:
                    segment_data = _get_segment_attributes(segment)
                    clip_data.update(segment_data)

                output_clips.append(clip_data)

    return output_clips


def _get_colourspace_policy():

    output = {}
    # get policies project path
    policy_dir = "/opt/Autodesk/project/{}/synColor/policy".format(
        CTX.project.name
    )
    log.debug(policy_dir)
    policy_fp = os.path.join(policy_dir, "policy.cfg")

    if not os.path.exists(policy_fp):
        return output

    with open(policy_fp) as file:
        dict_conf = dict(line.strip().split(' = ', 1) for line in file)
        output.update(
            {"openpype.flame.{}".format(k): v for k, v in dict_conf.items()}
        )
    return output


def _create_otio_timeline(sequence):

    metadata = _get_metadata(sequence)

    # find colour policy files and add them to metadata
    colorspace_policy = _get_colourspace_policy()
    metadata.update(colorspace_policy)

    metadata.update({
        "openpype.timeline.width": int(sequence.width),
        "openpype.timeline.height": int(sequence.height),
        "openpype.timeline.pixelAspect": 1
    })

    rt_start_time = create_otio_rational_time(
        CTX.get_tl_start_frame(), CTX.get_fps())

    return otio.schema.Timeline(
        name=str(sequence.name)[1:-1],
        global_start_time=rt_start_time,
        metadata=metadata
    )


def create_otio_track(track_type, track_name):
    return otio.schema.Track(
        name=track_name,
        kind=TRACK_TYPES[track_type]
    )


def add_otio_gap(clip_data, otio_track, prev_out):
    gap_length = clip_data["record_in"] - prev_out
    if prev_out != 0:
        gap_length -= 1

    gap = otio.opentime.TimeRange(
        duration=otio.opentime.RationalTime(
            gap_length,
            CTX.get_fps()
        )
    )
    otio_gap = otio.schema.Gap(source_range=gap)
    otio_track.append(otio_gap)


def add_otio_metadata(otio_item, item, **kwargs):
    metadata = _get_metadata(item)

    # add additional metadata from kwargs
    if kwargs:
        metadata.update(kwargs)

    # add metadata to otio item metadata
    for key, value in metadata.items():
        otio_item.metadata.update({key: value})


def _get_shot_tokens_values(clip, tokens):
    old_value = None
    output = {}

    if not clip.shot_name:
        return output

    old_value = clip.shot_name.get_value()

    for token in tokens:
        clip.shot_name.set_value(token)
        _key = re.sub("[ <>]", "", token)

        try:
            output[_key] = int(clip.shot_name.get_value())
        except TypeError:
            output[_key] = clip.shot_name.get_value()

    clip.shot_name.set_value(old_value)

    return output


def _get_segment_attributes(segment):
    # log.debug(dir(segment))

    if str(segment.name)[1:-1] == "":
        return None

    # Add timeline segment to tree
    clip_data = {
        "segment_name": segment.name.get_value(),
        "segment_comment": segment.comment.get_value(),
        "tape_name": segment.tape_name,
        "source_name": segment.source_name,
        "fpath": segment.file_path,
        "PySegment": segment
    }

    # add all available shot tokens
    shot_tokens = _get_shot_tokens_values(segment, [
        "<colour space>", "<width>", "<height>", "<depth>",
    ])
    clip_data.update(shot_tokens)

    # populate shot source metadata
    segment_attrs = [
        "record_duration", "record_in", "record_out",
        "source_duration", "source_in", "source_out"
    ]
    segment_attrs_data = {}
    for attr in segment_attrs:
        if not hasattr(segment, attr):
            continue
        _value = getattr(segment, attr)
        segment_attrs_data[attr] = str(_value).replace("+", ":")

        if attr in ["record_in", "record_out"]:
            clip_data[attr] = _value.relative_frame
        else:
            clip_data[attr] = _value.frame

    clip_data["segment_timecodes"] = segment_attrs_data

    return clip_data


def create_otio_timeline(sequence):
    log.info(dir(sequence))
    log.info(sequence.attributes)

    CTX.project = get_current_flame_project()
    CTX.clips = get_clips_in_reels(CTX.project)

    log.debug(pformat(
        CTX.clips
    ))

    # get current timeline
    CTX.set_fps(
        float(str(sequence.frame_rate)[:-4]))

    tl_start_frame = utils.timecode_to_frames(
        str(sequence.start_time).replace("+", ":"),
        CTX.get_fps()
    )
    CTX.set_tl_start_frame(tl_start_frame)

    # convert timeline to otio
    otio_timeline = _create_otio_timeline(sequence)

    # create otio tracks and clips
    for ver in sequence.versions:
        for track in ver.tracks:
            if len(track.segments) == 0 and track.hidden:
                return None

            # convert track to otio
            otio_track = create_otio_track(
                "video", str(track.name)[1:-1])

            all_segments = []
            for segment in track.segments:
                clip_data = _get_segment_attributes(segment)
                if not clip_data:
                    continue
                all_segments.append(clip_data)

            segments_ordered = {
                itemindex: clip_data
                for itemindex, clip_data in enumerate(
                    all_segments)
            }
            log.debug("_ segments_ordered: {}".format(
                pformat(segments_ordered)
            ))
            if not segments_ordered:
                continue

            for itemindex, segment_data in segments_ordered.items():
                log.debug("_ itemindex: {}".format(itemindex))

                # Add Gap if needed
                if itemindex == 0:
                    # if it is first track item at track then add
                    # it to previouse item
                    prev_item = segment_data

                else:
                    # get previouse item
                    prev_item = segments_ordered[itemindex - 1]

                log.debug("_ segment_data: {}".format(segment_data))

                # calculate clip frame range difference from each other
                clip_diff = segment_data["record_in"] - prev_item["record_out"]

                # add gap if first track item is not starting
                # at first timeline frame
                if itemindex == 0 and segment_data["record_in"] > 0:
                    add_otio_gap(segment_data, otio_track, 0)

                # or add gap if following track items are having
                # frame range differences from each other
                elif itemindex and clip_diff != 1:
                    add_otio_gap(
                        segment_data, otio_track, prev_item["record_out"])

                # create otio clip and add it to track
                otio_clip = create_otio_clip(segment_data)
                otio_track.append(otio_clip)

                log.debug("_ otio_clip: {}".format(otio_clip))

                # create otio marker
                # create otio metadata

            # add track to otio timeline
            otio_timeline.tracks.append(otio_track)

    return otio_timeline


def write_to_file(otio_timeline, path):
    otio.adapters.write_to_file(otio_timeline, path)
