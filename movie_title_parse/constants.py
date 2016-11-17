def _resolution(width, height):
    return {"width": width, "height": height}

resolutions = {
    "720p": _resolution(1280, 720),
    "1080p": {
        "resolutions": [_resolution(1920, 1080)],
        "keys": [
            "1080p"
        ]
    },
    "2k": {
        "resolutions": [
            _resolution(2048, 1080),
            _resolution(1998, 1080),
            _resolution(2048, 858)
        ],
        "keys": [
            "2k",
        ]
    },
    "4k": {
        "resolutions": [
            _resolution(3840, 2160),
            _resolution(5120, 2160),
            _resolution(4096, 2160),
            _resolution(3996, 2160)
        ],
        "keys": [
            "2160p",
            "4k"
        ]
    },
    "SD": [
        "576p",
        "480p"
    ],
}

codecs = [
    "h264",
    "x264",
    "xvid"
]

sources = [
    "hdrip",
    "bluray",
    "dvdrip",
    "dvdr",
    "webrip",
    "brrip",
    "bdrip",
    "sdtv",
    ""
]