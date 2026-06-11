import importlib.util
import pathlib
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "usr/share/domainjoinmint/domain_discovery.py"

spec = importlib.util.spec_from_file_location("domain_discovery", MODULE_PATH)
domain_discovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(domain_discovery)


class FakeResult:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


class DomainDiscoveryTests(unittest.TestCase):
    def test_build_discovery_message_prefers_stderr_when_stdout_is_empty(self):
        result = FakeResult(stdout="", stderr="No default realm")
        self.assertEqual(domain_discovery.build_discovery_message(result), "No default realm")

    def test_collect_discovery_candidates_includes_search_domains_from_resolv_conf(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as handle:
            handle.write("search example.local corp.example.local\n")
            handle.flush()
            candidates = domain_discovery.collect_discovery_candidates(handle.name, hostname="")

        self.assertEqual(candidates, ["example.local", "corp.example.local"])


if __name__ == "__main__":
    unittest.main()
