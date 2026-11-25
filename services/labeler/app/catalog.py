"""Flag catalog: one YAML file per flag plus an index that groups flags into sets.

Layout:

    <catalog>/
        index.yaml              catalog version and sets
        EXAMPLE_FLAG.yaml   one file per flag, file name = flag code
        ...
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, StringConstraints, ValidationError, model_validator

INDEX_FILE = "index.yaml"

FlagCode = Annotated[str, StringConstraints(pattern=r"^[A-Z][A-Z0-9_]*$")]
SetName = Annotated[str, StringConstraints(pattern=r"^[a-z0-9][a-z0-9-]*$")]


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class FlagDefinition(_Model):
    """A single flag.

    The assessment stage (before / after purchase) and the data a flag needs are deliberately
    not part of the definition: the stage is a run parameter and the model fetches data via tools.
    """

    code: FlagCode = Field(description="Flag code: uppercase letters, digits and underscores; equals the file name.")
    version: int = Field(ge=1, description="Definition version; bump whenever what the flag detects changes.")
    flag_when: str = Field(min_length=1, description="One-sentence, human-readable description of when the flag fires.")
    severity: Literal["low", "medium", "high", "critical"] = Field(description="Default severity in the base profile.")
    instructions: str | None = Field(
        default=None, description="Instructions for the model. Without them the flag is not executed yet."
    )


class FlagSet(_Model):
    """A named list of flags. May include other sets."""

    description: str = Field(min_length=1)
    flags: list[FlagCode] = Field(default_factory=list, description="Flag codes in execution order.")
    includes: list[SetName] = Field(default_factory=list, description="Sets included as a whole.")

    @model_validator(mode="after")
    def _not_empty(self) -> FlagSet:
        if not self.flags and not self.includes:
            raise ValueError("a set needs flags or includes")
        return self


class CatalogIndex(_Model):
    """Contents of index.yaml."""

    catalog_version: str = Field(min_length=1, description='E.g. "2026.11". Quote it in YAML, otherwise it is a number.')
    sets: dict[SetName, FlagSet] = Field(min_length=1)


class CatalogError(Exception):
    """All catalog problems at once, so they can be fixed in one pass."""

    def __init__(self, problems: list[str]):
        self.problems = problems
        super().__init__("\n".join(problems))


@dataclass(frozen=True)
class Catalog:
    path: Path
    index: CatalogIndex
    flags: dict[str, FlagDefinition]
    hash: str

    @property
    def version(self) -> str:
        """Version recorded in results: index version plus a short content hash."""
        return f"{self.index.catalog_version}+{self.hash[:12]}"

    def flag_set(self, name: str) -> list[FlagDefinition]:
        """Flags of a set with includes expanded, without duplicates, in index order."""
        if name not in self.index.sets:
            raise KeyError(f"no such set: {name!r}")
        return [self.flags[code] for code in _expand(self.index, name)]

    def unassigned(self) -> list[str]:
        """Codes of flags that are not listed in any set."""
        used = {code for s in self.index.sets.values() for code in s.flags}
        return sorted(set(self.flags) - used)


def load_catalog(path: str | Path) -> Catalog:
    path = Path(path)
    problems: list[str] = []

    index_file = path / INDEX_FILE
    if not index_file.is_file():
        raise CatalogError([f"{index_file}: index file not found"])

    files = sorted(p for p in path.glob("*.yaml") if p.name != INDEX_FILE)
    if list(path.glob("*.yml")):
        problems.append(f"{path}: .yml files are ignored, use the .yaml extension")

    index = _validate(index_file, CatalogIndex, problems)

    flags: dict[str, FlagDefinition] = {}
    for file in files:
        definition = _validate(file, FlagDefinition, problems)
        if definition is None:
            continue
        if definition.code != file.stem:
            problems.append(f"{file.name}: code {definition.code} does not match the file name")
            continue
        flags[definition.code] = definition

    if index is not None:
        for name, flag_set in index.sets.items():
            for code in flag_set.flags:
                if code not in flags and not any(p.stem == code for p in files):
                    problems.append(f"{INDEX_FILE}: set {name} references unknown flag {code}")
            for other in flag_set.includes:
                if other not in index.sets:
                    problems.append(f"{INDEX_FILE}: set {name} includes unknown set {other}")
        if not problems:
            for name in index.sets:
                try:
                    _expand(index, name)
                except CatalogError as e:
                    problems.extend(e.problems)
                    break

    if problems:
        raise CatalogError(problems)

    assert index is not None
    return Catalog(path=path, index=index, flags=flags, hash=_hash(index_file, files))


def _validate(file: Path, model: type[_Model], problems: list[str]):
    try:
        data = yaml.safe_load(file.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        problems.append(f"{file.name}: invalid YAML: {e}")
        return None
    try:
        return model.model_validate(data)
    except ValidationError as e:
        for error in e.errors():
            field = ".".join(str(x) for x in error["loc"]) or "(root)"
            problems.append(f"{file.name}: {field}: {error['msg']}")
        return None


def _expand(index: CatalogIndex, name: str, stack: tuple[str, ...] = ()) -> list[str]:
    if name in stack:
        cycle = " -> ".join((*stack, name))
        raise CatalogError([f"{INDEX_FILE}: set cycle: {cycle}"])
    flag_set = index.sets[name]
    result: list[str] = []
    for code in flag_set.flags:
        if code not in result:
            result.append(code)
    for other in flag_set.includes:
        for code in _expand(index, other, (*stack, name)):
            if code not in result:
                result.append(code)
    return result


def _hash(index_file: Path, files: list[Path]) -> str:
    h = hashlib.sha256()
    for file in [index_file, *files]:
        h.update(file.name.encode())
        h.update(b"\0")
        h.update(file.read_bytes())
        h.update(b"\0")
    return h.hexdigest()
