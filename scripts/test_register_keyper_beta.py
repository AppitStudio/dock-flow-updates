import io
import json
import os
import tempfile
import unittest
import urllib.error
from unittest import mock

import register_keyper_beta as beta
from register_keyper_beta import beta_payload, load_event

REPOSITORY = "AppitStudio/dock-flow-updates"


def release():
    return {
        "tag_name": "beta",
        "prerelease": True,
        "name": "B1.88",
        "published_at": "2026-10-19T09:53:27Z",
        "assets": [{"name": "DockFlow.dmg"}],
    }


def event():
    return {"repository": {"full_name": REPOSITORY}, "release": release()}


EXPECTED = {
    "version": "1.88",
    "released_at": "2026-10-19T09:53:27Z",
    "is_prerelease": True,
}


class FakeResponse(io.BytesIO):
    def __init__(self, body: bytes, status: int = 200):
        super().__init__(body)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
        return False


class BetaRegistrationTest(unittest.TestCase):
    def test_published_beta_registers_without_mutable_download_url(self):
        self.assertEqual(beta_payload(event()), EXPECTED)

    def test_rejects_wrong_repository(self):
        payload = event()
        payload["repository"]["full_name"] = "AppitStudio/extra-bar-updates"
        with self.assertRaises(ValueError):
            beta_payload(payload)

    def test_rejects_wrong_release_or_missing_asset(self):
        for change in (
            {"prerelease": False},
            {"tag_name": "prod"},
            {"tag_name": "v1.88"},
            {"name": "B1.88;echo unsafe"},
            {"name": "B1.88.1"},
            {"name": "B2.0"},
            {"name": "v1.88"},
            {"name": "1.88"},
            {"name": None},
            {"assets": []},
            {"assets": [{"name": "ExtraBar.dmg"}]},
            {"published_at": "2026-10-19T09:53:27"},
            {"published_at": None},
        ):
            with self.subTest(change=change):
                payload = event()
                payload["release"].update(change)
                with self.assertRaises(ValueError):
                    beta_payload(payload)


class DispatchPathTest(unittest.TestCase):
    def environ(self, **extra):
        values = {
            "GITHUB_EVENT_NAME": "workflow_dispatch",
            "GITHUB_REPOSITORY": REPOSITORY,
            "GITHUB_API_URL": "https://api.github.com",
            "GITHUB_TOKEN": "gh-test-token",
        }
        values.update(extra)
        return values

    def test_dispatch_fetches_beta_release_from_api(self):
        api_release = dict(release(), id=1, html_url="https://github.com/x")
        response = FakeResponse(json.dumps(api_release).encode("utf-8"))
        with mock.patch.object(beta.urllib.request, "urlopen", return_value=response) as urlopen:
            loaded = load_event(self.environ())
        self.assertEqual(beta_payload(loaded), EXPECTED)
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            f"https://api.github.com/repos/{REPOSITORY}/releases/tags/beta",
        )
        self.assertEqual(request.get_method(), "GET")
        self.assertEqual(request.get_header("Authorization"), "Bearer gh-test-token")

    def test_dispatch_applies_the_same_validation(self):
        api_release = dict(release(), prerelease=False)
        response = FakeResponse(json.dumps(api_release).encode("utf-8"))
        with mock.patch.object(beta.urllib.request, "urlopen", return_value=response):
            loaded = load_event(self.environ())
        with self.assertRaises(ValueError):
            beta_payload(loaded)

    def test_dispatch_rejects_other_repository_before_fetching(self):
        with mock.patch.object(beta.urllib.request, "urlopen") as urlopen:
            with self.assertRaises(ValueError):
                load_event(self.environ(GITHUB_REPOSITORY="someone/fork"))
        urlopen.assert_not_called()

    def test_dispatch_reports_missing_beta_release(self):
        error = urllib.error.HTTPError("https://api.github.com", 404, "Not Found", {}, None)
        with mock.patch.object(beta.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(RuntimeError):
                load_event(self.environ())

    def test_release_event_is_read_from_event_path(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(event(), handle)
        self.addCleanup(os.unlink, handle.name)
        with mock.patch.object(beta.urllib.request, "urlopen") as urlopen:
            loaded = load_event({"GITHUB_EVENT_NAME": "release", "GITHUB_EVENT_PATH": handle.name})
        urlopen.assert_not_called()
        self.assertEqual(beta_payload(loaded), EXPECTED)


class MainTest(unittest.TestCase):
    def test_main_posts_payload_to_keyper(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(event(), handle)
        self.addCleanup(os.unlink, handle.name)
        environ = {
            "GITHUB_EVENT_NAME": "release",
            "GITHUB_EVENT_PATH": handle.name,
            "KEYPER_RELEASE_TOKEN": "kpr-test-token",
            "KEYPER_RELEASE_ENDPOINT": "",
        }
        response = FakeResponse(b"{}", status=201)
        with mock.patch.dict(os.environ, environ, clear=True), mock.patch.object(
            beta.urllib.request, "urlopen", return_value=response
        ) as urlopen, mock.patch("sys.stdout", new_callable=io.StringIO) as stdout:
            self.assertEqual(beta.main(), 0)
        request = urlopen.call_args.args[0]
        self.assertEqual(request.full_url, beta.DEFAULT_ENDPOINT)
        self.assertEqual(json.loads(request.data), EXPECTED)
        self.assertEqual(request.get_header("Authorization"), "Bearer kpr-test-token")
        self.assertIn("Registered DockFlow beta 1.88 (HTTP 201)", stdout.getvalue())
        self.assertNotIn("kpr-test-token", stdout.getvalue())

    def test_main_requires_token(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump(event(), handle)
        self.addCleanup(os.unlink, handle.name)
        environ = {"GITHUB_EVENT_NAME": "release", "GITHUB_EVENT_PATH": handle.name}
        with mock.patch.dict(os.environ, environ, clear=True), mock.patch.object(
            beta.urllib.request, "urlopen"
        ) as urlopen, mock.patch("sys.stderr", new_callable=io.StringIO):
            self.assertEqual(beta.main(), 1)
        urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
