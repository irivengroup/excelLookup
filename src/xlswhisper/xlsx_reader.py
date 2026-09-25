from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from .limits import Limits

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"


@dataclass(frozen=True, slots=True)
class SheetRef:
    name: str
    target: str


class XlsxError(ValueError):
    pass


class XlsxReader:
    """Lecteur XLSX en streaming des feuilles."""

    def __init__(self, limits: Limits | None = None) -> None:
        self.limits = limits or Limits()

    def iter_sheets(self, path: Path) -> Iterator[tuple[str, Iterator[list[str]]]]:
        path = path.resolve(strict=True)
        if path.suffix.lower() != ".xlsx":
            raise XlsxError("Seul le format .xlsx est supporté.")
        if path.stat().st_size > self.limits.max_xlsx_bytes:
            raise XlsxError("Fichier XLSX trop volumineux.")

        try:
            archive = ZipFile(path)
        except BadZipFile as exc:
            raise XlsxError("Le fichier n'est pas un XLSX/ZIP valide.") from exc

        try:
            self._validate_archive(archive)
            shared = self._shared_strings(archive)
            workbook = self._parse_small_xml(archive, "xl/workbook.xml")
            rels = self._parse_small_xml(
                archive, "xl/_rels/workbook.xml.rels"
            )
            relationships = {
                rel.attrib["Id"]: rel.attrib["Target"]
                for rel in rels.findall(f"{{{NS_PKG_REL}}}Relationship")
                if rel.attrib.get("Target")
            }
            sheet_nodes = workbook.find(f"{{{NS_MAIN}}}sheets")
            if sheet_nodes is None:
                return
            if len(sheet_nodes) > self.limits.max_sheets:
                raise XlsxError("Nombre de feuilles dépassant la limite.")

            refs: list[SheetRef] = []
            for node in sheet_nodes:
                name = node.attrib.get("name", "Sheet")
                rid = node.attrib.get(f"{{{NS_REL}}}id", "")
                target = relationships.get(rid)
                if not target:
                    raise XlsxError(
                        f"Relation manquante pour la feuille {name!r}."
                    )
                refs.append(SheetRef(name, self._safe_target(target)))

            for ref in refs:
                yield ref.name, self._iter_rows(archive, ref.target, shared)
        finally:
            archive.close()

    def _validate_archive(self, archive: ZipFile) -> None:
        total = 0
        for info in archive.infolist():
            name = info.filename.replace("\\", "/")
            if name.startswith("/"):
                raise XlsxError("Chemin absolu interdit dans le XLSX.")
            if ".." in Path(name).parts:
                raise XlsxError("Traversal de chemin interdit dans le XLSX.")
            if info.file_size > self.limits.max_member_bytes:
                raise XlsxError(f"Entrée XLSX trop volumineuse: {name}")
            if info.compress_size and (
                info.file_size / info.compress_size
                > self.limits.max_compression_ratio
            ):
                raise XlsxError(f"Ratio de compression suspect: {name}")
            total += info.file_size
            if total > self.limits.max_xlsx_bytes * 4:
                raise XlsxError("Taille totale décompressée excessive.")

    def _safe_target(self, target: str) -> str:
        target = target.replace("\\", "/")
        if target.startswith("/"):
            raise XlsxError("Target XML absolue interdite.")
        parts = [part for part in target.split("/") if part not in ("", ".")]
        resolved: list[str] = []
        for part in parts:
            if part == "..":
                if not resolved:
                    raise XlsxError("Traversal de target interdit.")
                resolved.pop()
            else:
                resolved.append(part)
        value = "/".join(resolved)
        return value if value.startswith("xl/") else "xl/" + value

    def _member(self, archive: ZipFile, name: str) -> bytes:
        try:
            info = archive.getinfo(name)
        except KeyError as exc:
            raise XlsxError(f"Élément XLSX manquant: {name}") from exc
        if info.file_size > self.limits.max_xml_bytes:
            raise XlsxError(f"XML trop volumineux: {name}")
        return archive.read(name)

    def _parse_small_xml(self, archive: ZipFile, name: str) -> ET.Element:
        try:
            return ET.fromstring(self._member(archive, name))
        except ET.ParseError as exc:
            raise XlsxError(f"XML XLSX invalide: {name}") from exc

    def _shared_strings(self, archive: ZipFile) -> list[str]:
        try:
            info = archive.getinfo("xl/sharedStrings.xml")
        except KeyError:
            return []
        if info.file_size > self.limits.max_xml_bytes:
            raise XlsxError("sharedStrings.xml trop volumineux.")

        values: list[str] = []
        try:
            with archive.open(info) as stream:
                for event, elem in ET.iterparse(stream, events=("end",)):
                    if elem.tag == f"{{{NS_MAIN}}}si":
                        value = "".join(
                            node.text or ""
                            for node in elem.iter(f"{{{NS_MAIN}}}t")
                        )
                        self._check_string(value)
                        values.append(value)
                        elem.clear()
                        if len(values) > self.limits.max_shared_strings:
                            raise XlsxError("Trop de shared strings.")
        except ET.ParseError as exc:
            raise XlsxError("sharedStrings.xml invalide.") from exc
        return values

    def _iter_rows(
        self,
        archive: ZipFile,
        target: str,
        shared: list[str],
    ) -> Iterator[list[str]]:
        info = archive.getinfo(target)
        if info.file_size > self.limits.max_xml_bytes:
            raise XlsxError(f"XML trop volumineux: {target}")

        row_count = 0
        try:
            with archive.open(info) as stream:
                for event, row in ET.iterparse(stream, events=("end",)):
                    if row.tag != f"{{{NS_MAIN}}}row":
                        continue
                    row_count += 1
                    if row_count > self.limits.max_rows:
                        raise XlsxError(
                            f"Nombre de lignes dépassant la limite dans {target}."
                        )
                    values = self._row_values(row, shared)
                    yield values
                    row.clear()
        except ET.ParseError as exc:
            raise XlsxError(f"XML de feuille invalide: {target}") from exc

    def _row_values(
        self,
        row: ET.Element,
        shared: list[str],
    ) -> list[str]:
        cells = list(row.findall(f"{{{NS_MAIN}}}c"))
        if len(cells) > self.limits.max_cells_per_row:
            raise XlsxError("Trop de cellules sur une ligne.")

        mapped: dict[int, str] = {}
        max_index = -1
        for cell in cells:
            index = self._column_index(cell.attrib.get("r", ""))
            value = self._cell_value(cell, shared)
            mapped[index] = value
            max_index = max(max_index, index)
        if max_index + 1 > self.limits.max_columns:
            raise XlsxError("Nombre de colonnes dépassant la limite.")
        return [mapped.get(i, "") for i in range(max_index + 1)]

    @staticmethod
    def _column_index(reference: str) -> int:
        letters = "".join(c for c in reference if c.isalpha())
        if not letters:
            raise XlsxError(f"Référence de cellule invalide: {reference!r}")
        value = 0
        for char in letters.upper():
            value = value * 26 + ord(char) - 64
        return value - 1

    def _cell_value(self, cell: ET.Element, shared: list[str]) -> str:
        cell_type = cell.attrib.get("t")
        if cell_type == "inlineStr":
            value = "".join(
                node.text or ""
                for node in cell.iter(f"{{{NS_MAIN}}}t")
            )
            self._check_string(value)
            return value

        node = cell.find(f"{{{NS_MAIN}}}v")
        if node is None:
            return ""
        value = node.text or ""
        if cell_type == "s":
            try:
                value = shared[int(value)]
            except (ValueError, IndexError) as exc:
                raise XlsxError("Référence shared string invalide.") from exc
        self._check_string(value)
        return value

    def _check_string(self, value: str) -> None:
        if len(value.encode("utf-8")) > self.limits.max_string_bytes:
            raise XlsxError("Valeur de cellule trop longue.")
