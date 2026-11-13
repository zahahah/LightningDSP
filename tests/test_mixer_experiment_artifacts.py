from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MixerExperimentArtifactTests(unittest.TestCase):
    def test_workflow_is_branch_limited_and_artifact_only(self):
        workflow = (ROOT / '.github/workflows/main-module-artifacts.yml').read_text()
        self.assertIn("github.repository == 'zahahah/LightningDSP'", workflow)
        self.assertIn("github.ref == 'refs/heads/master'", workflow)
        self.assertIn('contents: read', workflow)
        self.assertNotIn('contents: write', workflow)
        self.assertNotIn('gh-release', workflow)
        self.assertNotIn('tags:', workflow)
        self.assertIn('actions/upload-artifact@v4', workflow)
        self.assertIn('python3 tools/package_lightningdsp.py', workflow)
        self.assertIn("archive.read('common/files/LightningDSP.apk') ==", workflow)
        self.assertIn('dist/TEST-NOTES.md', workflow)

    def test_testing_notes_do_not_claim_runtime_validation(self):
        notes = (ROOT / 'docs/all-mixers-test.md').read_text()
        self.assertIn('not a new stable or prerelease publication', notes)
        self.assertIn('does not claim that window is', notes)
        self.assertIn('fixed', notes)
        self.assertIn('native driver and ldspctl are unchanged', notes)
        self.assertIn('Host tests and compilation are not audio validation', notes)


if __name__ == '__main__':
    unittest.main()
