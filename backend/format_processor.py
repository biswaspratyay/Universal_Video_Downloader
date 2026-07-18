from backend.models import VideoFormat


class FormatProcessor:
    CODECS = {
        "avc1": "H.264",
        "vp09": "VP9",
        "vp9": "VP9",
        "av01": "AV1",
        "hev1": "H.265",
        "hvc1": "H.265",
    }

    @classmethod
    def process(cls, raw_formats):

        cleaned = []

        for fmt in raw_formats:
            # Ignore storyboard images
            if fmt.get("ext") == "mhtml":
                continue

            # Ignore missing IDs
            if not fmt.get("format_id"):
                continue

            width = fmt.get("width") or 0
            height = fmt.get("height") or 0

            vcodec = fmt.get("vcodec") or "none"
            acodec = fmt.get("acodec") or "none"

            is_video = vcodec != "none"
            is_audio = acodec != "none"

            if is_video:
                quality = f"{height}p"
            else:
                quality = "Audio"

            video_codec = cls.codec_name(vcodec)

            display = cls.build_display_name(
                quality,
                fmt.get("ext", ""),
                video_codec,
                fmt.get("fps"),
                is_video,
            )

            cleaned.append(
                VideoFormat(
                    format_id=fmt["format_id"],
                    quality=quality,
                    extension=fmt.get("ext", ""),
                    width=width,
                    height=height,
                    fps=fmt.get("fps"),
                    filesize=fmt.get("filesize"),
                    video_codec=video_codec,
                    audio_codec=acodec,
                    is_video=is_video,
                    is_audio=is_audio,
                    display_name=display,
                    bitrate=fmt.get("vbr"),
                    tbr=fmt.get("tbr"),
                )
            )

        cleaned.sort(
            key=lambda x: (
                x.height,
                x.fps or 0,
            ),
            reverse=True,
        )

        return cleaned

    @classmethod
    def codec_name(cls, codec):

        for key in cls.CODECS:
            if codec.startswith(key):
                return cls.CODECS[key]

        return codec

    @staticmethod
    def build_display_name(
        quality,
        ext,
        codec,
        fps,
        is_video,
    ):

        if not is_video:
            return f"Audio • {ext.upper()}"

        text = f"{quality} • {ext.upper()}"

        if codec:
            text += f" • {codec}"

        if fps:
            text += f" • {int(fps)} FPS"

        return text
