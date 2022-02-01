# stdlib
import pathlib
import re
import tarfile
from typing import IO, TYPE_CHECKING, Dict, Type, TypeVar, Union

# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture

_TF = TypeVar("_TF", bound="TarFile")


class TarFile(tarfile.TarFile):

	def extractfile(self, member: Union[str, tarfile.TarInfo]) -> IO[bytes]:
		fd = super().extractfile(member)

		if fd is None:
			raise FileNotFoundError(member)
		else:
			return fd

	def read_text(self, member: Union[str, tarfile.TarInfo]) -> str:
		return self.read_binary(member).decode("UTF-8")

	def read_binary(self, member: Union[str, tarfile.TarInfo]) -> bytes:
		fd = self.extractfile(member)

		return fd.read()

	if TYPE_CHECKING:

		def __enter__(self: _TF) -> _TF:
			return super().__enter__()

		@classmethod  # noqa: A001  # pylint: disable=redefined-builtin
		def open(
				cls: Type[_TF],
				*args,
				**kwargs,
				) -> _TF:
			return super().open(
					*args,
					**kwargs,
					)


class TarFileRegressionFixture(AdvancedFileRegressionFixture):

	def check_archive(self, tar_file: TarFile, filename: str, **kwargs):
		self.check(tar_file.read_text(filename), **kwargs)


def get_stdouterr(capsys, tmpdir: pathlib.Path) -> Dict[str, str]:

	outerr = capsys.readouterr()

	stdout_lines = outerr.out.replace(tmpdir.as_posix(), "...").splitlines()
	stdout_lines = filter(re.compile("^(?!Looking in indexes: |Processing )").match, stdout_lines)

	return {
			"stdout": '\n'.join(stdout_lines),
			"stderr": outerr.err,
			}
