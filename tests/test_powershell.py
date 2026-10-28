import shutil
import subprocess
import sys

import pytest
import tree_sitter
import tree_sitter_powershell
from validate_mod import ROOT

PS_FILES = sorted(
    [
        *ROOT.glob("*.ps1"),
        *(ROOT / "scripts").glob("*.psm1"),
        *(ROOT / "tests").glob("*.ps1"),
    ]
)


@pytest.mark.parametrize("path", PS_FILES, ids=lambda p: p.name)
def test_powershell_syntax(path):
    parser = tree_sitter.Parser(tree_sitter.Language(tree_sitter_powershell.language()))
    tree = parser.parse(path.read_bytes())
    assert not tree.root_node.has_error, path


@pytest.mark.skipif(
    sys.platform != "win32" or not shutil.which("powershell.exe"),
    reason="Native Windows PowerShell is not available; this is not a Windows runtime test.",
)
def test_installer_on_isolated_windows_documents():
    subprocess.run(
        [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(ROOT / "tests/Test-Installer.ps1"),
        ],
        cwd=ROOT,
        check=True,
        timeout=300,
    )
