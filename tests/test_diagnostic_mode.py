from pathlib import Path
import os
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DiagnosticModeTests(unittest.TestCase):
    def test_default_does_not_create_trace_or_change_umask(self):
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, MODPATH=tmp, LDSP_DIAGNOSTIC_DIR=tmp + '/state',
                       LDSP_GETPROP_BIN='/usr/bin/false', LDSP_SETPROP_BIN='/usr/bin/false')
            cmd = f'before=$(umask); . "{ROOT}/diagnostic-mode.sh"; ldsp_trace_to "$MODPATH/logs/trace" || :; [ "$(umask)" = "$before" ]; [ ! -e "$MODPATH/logs/trace" ]'
            self.assertEqual(subprocess.run(['sh', '-c', cmd], env=env).returncode, 0)

    def test_explicit_marker_enables_private_trace_and_disabled_next_invocation_is_quiet(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / 'state'; state.mkdir(); (state / 'enabled').touch()
            env = dict(os.environ, MODPATH=tmp, LDSP_DIAGNOSTIC_DIR=str(state),
                       LDSP_GETPROP_BIN='/usr/bin/false', LDSP_SETPROP_BIN='/usr/bin/false')
            cmd = f'. "{ROOT}/diagnostic-mode.sh"; ldsp_trace_to "$MODPATH/logs/trace"; echo trace-test >/dev/null; ldsp_finish_trace'
            self.assertEqual(subprocess.run(['sh', '-c', cmd], env=env).returncode, 0)
            trace = Path(tmp) / 'logs/trace'
            self.assertIn('trace-test', trace.read_text())
            self.assertEqual(trace.stat().st_mode & 0o777, 0o600)
            self.assertEqual(trace.parent.stat().st_mode & 0o777, 0o700)
            (state / 'enabled').unlink()
            cmd = f'. "{ROOT}/diagnostic-mode.sh"; ldsp_trace_to "$MODPATH/logs/second" || :'
            self.assertEqual(subprocess.run(['sh', '-c', cmd], env=env).returncode, 0)
            self.assertFalse(trace.with_name('second').exists())

    def test_module_entrypoints_gate_tracing_without_gating_recovery_guards(self):
        for file in ('service.sh', 'post-fs-data.sh', 'common/functions.sh'):
            source = (ROOT / file).read_text()
            self.assertIn('diagnostic-mode.sh', source)
            self.assertIn('ldsp_trace_to ', source)
            self.assertNotRegex(source, r'(?m)^set -x$')
        self.assertNotIn('set -x', (ROOT / 'common/install.sh').read_text())
        recovery = (ROOT / 'aidl-audio-recovery.sh').read_text()
        self.assertIn('diagnostic_snapshot=/dev/null', recovery)
        self.assertIn('diagnostic_probe="$LOGDIR/aidl-recovery-probe.txt"', recovery)
        self.assertIn('diagnostic_status=/dev/null', recovery)
        self.assertIn('GUARD=', recovery)
        self.assertIn('sys.audio.restart.hal 1', recovery)
        self.assertIn("'diagnostic-mode.sh': 0o100755", (ROOT / 'tools/package_lightningdsp.py').read_text())
        self.assertNotIn('debug.ldsp.diagnostics 1', (ROOT / 'diagnostic-mode.sh').read_text())


if __name__ == '__main__':
    unittest.main()
