import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'tools/audio-policy-probe.sh'


class AudioPolicyProbeTests(unittest.TestCase):
    def fixture(self, root, hint='123', mutate=''):
        proc = root / 'proc'
        process = proc / '123'
        (process / 'ns').mkdir(parents=True)
        (proc / 'sys/kernel').mkdir(parents=True)
        (proc / 'sys/kernel/osrelease').write_text('test-kernel\n')
        # Fields after comm start with field 3; starttime is field 22.
        (process / 'stat').write_text('123 (audioserver) S ' + '0 ' * 18 + '777 0\n')
        (process / 'cmdline').write_bytes(b'/system/bin/audioserver\0')
        (process / 'exe').symlink_to('/system/bin/audioserver')
        (process / 'ns/mnt').symlink_to('mnt:[456]')
        (process / 'maps').write_text('1000-2000 r-xp 00000000 08:01 123 /system/lib64/libaudiopolicymanagerdefault.so\n'
                                     '2000-3000 r-xp 00000000 08:01 124 /system/lib64/libaudioflinger.so (deleted)\n')
        getprop = root / 'getprop'
        # All writes here belong to the test double, not the collector.
        getprop.write_text(f'''#!/bin/sh
case "$1" in
init.svc_debug_pid.audioserver)
    if [ -e '{root}/seen' ]; then {mutate or ':'}; else touch '{root}/seen'; fi
    printf '%s\\n' '{hint}' ;;
ro.build.fingerprint) echo synthetic/fingerprint ;;
ro.build.version.release) echo 17 ;;
ro.build.version.sdk) echo 37 ;;
esac
''')
        getprop.chmod(0o755)
        env = dict(os.environ, LDSP_PROBE_TEST_MODE='1', LDSP_PROBE_TEST_PROC=str(proc),
                   LDSP_PROBE_TEST_GETPROP=str(getprop))
        return proc, process, env

    def run_probe(self, env):
        return subprocess.run(['sh', str(SCRIPT)], env=env, text=True, capture_output=True, timeout=5)

    def test_observes_loaded_namespace_paths_without_claiming_routing_support(self):
        with tempfile.TemporaryDirectory() as tmp:
            proc, process, env = self.fixture(Path(tmp))
            result = self.run_probe(env)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('STATUS=OBSERVED', result.stdout)
            self.assertIn('123|777|/system/bin/audioserver|mnt:[456]', result.stdout)
            self.assertIn('08:01 123 /system/lib64/libaudiopolicy', result.stdout)
            self.assertIn('(deleted)', result.stdout)
            self.assertNotIn('1000-2000', result.stdout)
            self.assertNotIn('2000-3000', result.stdout)
            self.assertIn('PID_HINT_AUTHORITY=NONE', result.stdout)
            self.assertIn('CAPABILITY=UNKNOWN', result.stdout)
            self.assertIn('TRANSPORT=UNKNOWN', result.stdout)
            self.assertIn('PRIVACY=', result.stdout)

    def test_missing_or_multiple_or_nonnumeric_pid_hint_is_unknown(self):
        for hint in ['', '0', '-3', 'abc', '123 124', '123;echo bad']:
            with self.subTest(hint=hint), tempfile.TemporaryDirectory() as tmp:
                _, _, env = self.fixture(Path(tmp), hint)
                result = self.run_probe(env)
                self.assertIn('STATUS=UNKNOWN', result.stdout)
                self.assertNotIn('MAPPINGS_BEGIN', result.stdout)

    def test_changed_start_time_rejects_reused_pid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mutation = f"sed 's/777/888/' '{root}/proc/123/stat' >'{root}/changed'; cat '{root}/changed' >'{root}/proc/123/stat'"
            _, _, env = self.fixture(root, mutate=mutation)
            result = self.run_probe(env)
            self.assertIn('STATUS=UNKNOWN', result.stdout)
            self.assertNotIn('MAPPINGS_BEGIN', result.stdout)

    def test_changed_cmdline_or_mismatched_executable_rejects_hint(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, process, env = self.fixture(Path(tmp))
            (process / 'cmdline').write_bytes(b'/system/bin/other\0')
            self.assertIn('STATUS=UNKNOWN', self.run_probe(env).stdout)

    def test_missing_namespace_or_maps_does_not_invent_evidence(self):
        for name in ['ns/mnt', 'maps', 'stat']:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as tmp:
                _, process, env = self.fixture(Path(tmp))
                (process / name).unlink()
                result = self.run_probe(env)
                self.assertIn('STATUS=UNKNOWN', result.stdout)
                self.assertNotIn('MAPPINGS_BEGIN', result.stdout)

    def test_maps_count_and_input_are_bounded(self):
        for maps in ['a' * 1048577, '\n' * 1048577, '1000-2000 r-xp 0 08:01 1 /system/lib64/libaudioflinger.so\n' * 129]:
            with tempfile.TemporaryDirectory() as tmp:
                _, process, env = self.fixture(Path(tmp))
                (process / 'maps').write_text(maps)
                self.assertIn('STATUS=UNKNOWN', self.run_probe(env).stdout)

    def test_empty_relevant_mappings_are_unknown(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, process, env = self.fixture(Path(tmp))
            (process / 'maps').write_text('1000-2000 r-xp 0 08:01 1 /system/lib64/libc.so\n')
            self.assertIn('STATUS=UNKNOWN', self.run_probe(env).stdout)

    def test_test_seam_cannot_target_real_proc(self):
        env = dict(os.environ, LDSP_PROBE_TEST_MODE='1', LDSP_PROBE_TEST_PROC='/proc')
        self.assertEqual(self.run_probe(env).returncode, 2)

    def test_collector_does_not_change_fixture_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, process, env = self.fixture(Path(tmp))
            before = {p.name: p.read_bytes() for p in process.iterdir() if p.is_file() and not p.is_symlink()}
            self.run_probe(env)
            after = {p.name: p.read_bytes() for p in process.iterdir() if p.is_file() and not p.is_symlink()}
            self.assertEqual(before, after)

    def test_test_seam_rejects_symlink_to_real_proc(self):
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / 'proc-link'
            link.symlink_to('/proc')
            env = dict(os.environ, LDSP_PROBE_TEST_MODE='1', LDSP_PROBE_TEST_PROC=str(link))
            self.assertEqual(self.run_probe(env).returncode, 2)
