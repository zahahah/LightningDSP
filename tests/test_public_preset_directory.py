"""The installer creates the public library even with no bundled presets."""
from pathlib import Path
import subprocess
import tempfile
import unittest


class PublicPresetDirectoryTests(unittest.TestCase):
    def test_public_directory_creation_is_idempotent(self):
        installer = (Path(__file__).resolve().parents[1] / 'common/install.sh').read_text()
        command = next(line for line in installer.splitlines()
                       if line.startswith('mkdir -p /storage/emulated/0/LightningDSP/Presets'))
        with tempfile.TemporaryDirectory() as root:
            command = command.replace('/storage/emulated/0', root)
            for _ in range(2):
                subprocess.run(['sh', '-c', command], check=True)
            self.assertTrue((Path(root) / 'LightningDSP/Presets').is_dir())
