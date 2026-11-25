import shutil
from pathlib import Path

import pytest

from app.catalog import CatalogError, load_catalog
from app.cli import main

FIXTURE = Path(__file__).parent / "fixtures" / "catalog"


@pytest.fixture
def catalog(tmp_path: Path) -> Path:
    target = tmp_path / "catalog"
    shutil.copytree(FIXTURE, target)
    return target


def problems(path: Path) -> str:
    with pytest.raises(CatalogError) as e:
        load_catalog(path)
    return "\n".join(e.value.problems)


def test_loads_valid_catalog():
    cat = load_catalog(FIXTURE)
    assert set(cat.flags) == {"TEST_FLAG_A", "TEST_FLAG_B", "TEST_FLAG_C"}
    assert cat.flags["TEST_FLAG_C"].severity == "low"
    assert cat.version.startswith("test.1+")
    assert cat.unassigned() == []


def test_set_expands_includes_without_duplicates():
    cat = load_catalog(FIXTURE)
    assert [f.code for f in cat.flag_set("telco")] == [
        "TEST_FLAG_A",
        "TEST_FLAG_B",
        "TEST_FLAG_C",
    ]


def test_hash_follows_content(catalog: Path):
    before = load_catalog(catalog).hash
    assert load_catalog(catalog).hash == before
    file = catalog / "TEST_FLAG_C.yaml"
    file.write_text(file.read_text().replace("version: 1", "version: 2"))
    assert load_catalog(catalog).hash != before


def test_code_must_match_file_name(catalog: Path):
    (catalog / "TEST_FLAG_C.yaml").rename(catalog / "OTHER_CODE.yaml")
    result = problems(catalog)
    assert "OTHER_CODE.yaml: code TEST_FLAG_C does not match the file name" in result
    assert "references unknown flag TEST_FLAG_C" in result


def test_unknown_field_and_bad_value(catalog: Path):
    file = catalog / "TEST_FLAG_C.yaml"
    file.write_text(file.read_text().replace("severity: low", "severity: none") + "typo: 1\n")
    result = problems(catalog)
    assert "TEST_FLAG_C.yaml: severity:" in result
    assert "TEST_FLAG_C.yaml: typo:" in result


def test_unquoted_catalog_version_is_an_error(catalog: Path):
    file = catalog / "index.yaml"
    file.write_text(file.read_text().replace('"test.1"', "2026.11"))
    assert "catalog_version" in problems(catalog)


def test_unknown_include_and_cycle(catalog: Path):
    file = catalog / "index.yaml"
    file.write_text(file.read_text().replace("includes: [base, extra]", "includes: [missing]"))
    assert "includes unknown set missing" in problems(catalog)

    file.write_text(
        'catalog_version: "x"\n'
        "sets:\n"
        "  a: {description: a, includes: [b], flags: [TEST_FLAG_A, TEST_FLAG_B, TEST_FLAG_C]}\n"
        "  b: {description: b, includes: [a]}\n"
    )
    assert "set cycle: a -> b -> a" in problems(catalog)


def test_flag_outside_sets_is_reported(catalog: Path):
    file = catalog / "index.yaml"
    file.write_text(file.read_text().replace("flags: [TEST_FLAG_C]", "flags: [TEST_FLAG_A]"))
    assert load_catalog(catalog).unassigned() == ["TEST_FLAG_C"]


def test_cli(catalog: Path, capsys):
    assert main(["catalog", "check", str(catalog)]) == 0
    assert "3 flags, 3 sets" in capsys.readouterr().out

    assert main(["catalog", "set", str(catalog), "extra"]) == 0
    assert capsys.readouterr().out == "TEST_FLAG_C\n"

    (catalog / "TEST_FLAG_C.yaml").write_text("code: [\n")
    assert main(["catalog", "check", str(catalog)]) == 1
    assert "invalid YAML" in capsys.readouterr().err
