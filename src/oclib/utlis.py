import hashlib
import subprocess
from pathlib import Path
from typing import Sequence


def execute_command(cmd: Sequence[str], stdin: bytes | None = None, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE) -> tuple[int, bytes, bytes]:
    """
    Execute a command sequence.
    :return:    returncode, stdout, stderr
    """
    for c in cmd:
        if not isinstance(c, str):
            raise RuntimeError(f'the command sequence contains non-str element: {c}')
    completed: subprocess.CompletedProcess = subprocess.run(
        cmd,
        stdout=stdout,
        stderr=stderr,
        input=stdin)
    return completed.returncode, completed.stdout, completed.stderr


def sha3_512(obj: Path | str, encoding='utf-8') -> str:
    """
    Calculate the sha3_512 hash of a file or a string.
    :param obj:
    :param encoding: the encoding of the string, default utf-8
    :return:    the hash digest
    """
    if isinstance(obj, Path):
        hasher = hashlib.sha3_512()
        with open(obj, "rb") as f:
            for chunk in iter(lambda: f.read(1048576), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    elif isinstance(obj, str):
        obj: str
        digest = hashlib.sha3_512(obj.encode(encoding))
        return digest.hexdigest()
    else:
        raise RuntimeError(f'unsupported type: {type(obj)}')
