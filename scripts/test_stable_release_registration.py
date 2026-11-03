import io
import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

from sync_keyper_releases import Release, register_release


class Response(io.BytesIO):
    status = 200


class StableRegistrationTest(unittest.TestCase):
    @patch("sync_keyper_releases.urllib.request.urlopen")
    def test_appcast_registration_explicitly_promotes_stable_release(self, urlopen):
        release = Release(
            "5.0.8", "62", datetime(2026, 10, 20, tzinfo=timezone.utc),
            "https://example.com/v5.0.8/App.dmg",
        )
        urlopen.return_value = Response(json.dumps({
            "product": "extradock", "track": "v5-stable", "version": release.version,
            "download_url": release.download_url, "is_prerelease": False,
        }).encode())

        self.assertEqual(register_release(
            "https://keyper.example/api/releases", "test-token", release,
        ), 200)

        request = urlopen.call_args.args[0]
        self.assertEqual(json.loads(request.data), {
            "version": release.version,
            "released_at": release.released_at.isoformat(),
            "download_url": release.download_url,
            "is_prerelease": False,
        })
        self.assertEqual(request.get_method(), "POST")
        self.assertEqual(request.get_header("Authorization"), "Bearer test-token")


if __name__ == "__main__":
    unittest.main()
