from __future__ import print_function
import re

from streamlink import PluginError
from streamlink.plugin import Plugin
from streamlink.plugin.api import validate
from streamlink.stream import HLSStream
from streamlink.stream import RTMPStream


class TVRBy(Plugin):
    url_re = re.compile(r"""https?://(?:www\.)?tvr.by/plugines/online-tv-main\.php\?channel=tv&chan_id=""")
    file_re = re.compile(r"""(?P<q1>["']?)file(?P=q1)\s*:\s*(?P<q2>["'])(?P<url>(?:http[^,]*))(?P=q2)""")

    stream_schema = validate.Schema(
        validate.all(
            validate.transform(file_re.finditer),
            validate.transform(list),
            [validate.get("url")]
        ),
    )

    def __init__(self, url):
        # ensure the URL ends with a /
        super(TVRBy, self).__init__(url)

    @classmethod
    def can_handle_url(cls, url):
        return cls.url_re.match(url) is not None

    def _get_streams(self):
        res = self.session.http.get(self.url)
        stream_urls = self.stream_schema.validate(res.text)
        self.logger.debug("Found {0} stream URL{1}", len(stream_urls),
                          "" if len(stream_urls) == 1 else "s")
        for stream_url in stream_urls:
            if "m3u8" in stream_url:
                for _, s in HLSStream.parse_variant_playlist(self.session, stream_url).items():
                    yield "live", s

__plugin__ = TVRBy
