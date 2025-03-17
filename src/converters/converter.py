import json
import pathlib
from enum import Enum
from typing import Any, Dict, List, Tuple
import lxml.etree as et


class EConverterType(Enum):
    XML = "xml"
    GEOJSON = "geojson"
    KML = "kml"


class Converter:
    def __init__(self, input_file: str | pathlib.Path) -> None:
        self.input_file = pathlib.Path(input_file)
        self.data = self._parse_input_file()

    def _parse_input_file(self):
        if self.input_file.suffix == ".xml":
            return self._parse_xml()
        elif self.input_file.suffix == ".json":
            return self._parse_geojson()
        elif self.input_file.suffix == ".kml":
            return self._parse_kml()
        else:
            raise ValueError("Unsupported file format")

    def _parse_xml(self) -> List[Dict[str, Any]]:
        """Parses XML file into a list of dictionaries."""
        tree = et.parse(self.input_file)
        root = tree.getroot()
        markers = []
        for marker in root.findall("marker"):
            lat, lon = self._parse_coordinates(marker.findtext("geo", ""))
            entry = {
                "name": marker.findtext("name", ""),
                "address": marker.findtext("adr", ""),
                "geo": (lat, lon),  # Store as (latitude, longitude)
                "note": marker.findtext("note", ""),
            }
            markers.append(entry)
        return markers

    def _parse_geojson(self) -> List[Dict[str, Any]]:
        """Parses GeoJSON file into a list of dictionaries."""
        with open(self.input_file, "r", encoding="utf-8") as f:
            geojson = json.load(f)
        markers = []
        for feature in geojson["features"]:
            lon, lat = feature["geometry"]["coordinates"]  # GeoJSON uses [lon, lat]
            entry = {
                "name": feature["properties"].get("name", ""),
                "address": feature["properties"].get("address", ""),
                "geo": (lat, lon),  # Store as (latitude, longitude)
                "note": feature["properties"].get("note", ""),
            }
            markers.append(entry)
        return markers

    def _parse_kml(self) -> List[Dict[str, Any]]:
        """Parses KML file into a list of dictionaries."""
        tree = et.parse(self.input_file)
        root = tree.getroot()
        ns = {"kml": "http://www.opengis.net/kml/2.2"}

        markers = []
        for placemark in root.findall(".//kml:Placemark", ns):
            name = placemark.find("kml:name", ns)
            coordinates = placemark.find(".//kml:coordinates", ns)

            if name is not None and coordinates is not None:
                lon, lat = self._parse_coordinates(coordinates.text.strip())
                entry = {
                    "name": name.text,
                    "geo": (lat, lon),  # Swap to (latitude, longitude)
                }
                markers.append(entry)
        return markers

    def convert(self, new_type: EConverterType) -> str | None:
        """Converts the current data to the requested format. Returns None if conversion is unnecessary."""
        current_type = None
        if self.input_file.suffix == ".xml":
            current_type = EConverterType.XML
        elif self.input_file.suffix == ".json":
            current_type = EConverterType.GEOJSON
        elif self.input_file.suffix == ".kml":
            current_type = EConverterType.KML

        # Skip conversion if already in the requested format
        if current_type == new_type:
            print(f"Skipping conversion: File is already in {new_type.value} format.")
            return None

        # Perform the conversion
        if new_type == EConverterType.GEOJSON:
            return self._to_geojson()
        elif new_type == EConverterType.XML:
            return self._to_xml()
        elif new_type == EConverterType.KML:
            return self._to_kml()
        else:
            raise ValueError("Unsupported conversion type")

    def _to_geojson(self) -> str:
        """Converts data to GeoJSON format."""
        features = []
        for entry in self.data:
            lat, lon = entry["geo"]
            feature = {
                "type": "Feature",
                "properties": {
                    "name": entry["name"],
                    "address": entry.get("address", ""),
                    "note": entry.get("note", ""),
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat],  # GeoJSON uses [longitude, latitude]
                },
            }
            features.append(feature)
        geojson = {"type": "FeatureCollection", "features": features}
        return json.dumps(geojson, indent=2)

    def _to_xml(self) -> str:
        """Converts data to XML format using lxml.etree."""
        root = et.Element("markers")
        for entry in self.data:
            marker = et.SubElement(root, "marker")
            et.SubElement(marker, "name").text = entry["name"]
            et.SubElement(marker, "adr").text = entry.get("address", "")
            lat, lon = entry["geo"]
            et.SubElement(marker, "geo").text = f"{lat}, {lon}"  # Keep (latitude, longitude)
            et.SubElement(marker, "note").text = entry.get("note", "")

        return et.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True).decode("utf-8")

    def _to_kml(self) -> str:
        """Converts data to KML format using lxml.etree."""
        kml = et.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
        doc = et.SubElement(kml, "Document")

        for entry in self.data:
            placemark = et.SubElement(doc, "Placemark")
            et.SubElement(placemark, "name").text = entry["name"]
            point = et.SubElement(placemark, "Point")
            lat, lon = entry["geo"]
            et.SubElement(point, "coordinates").text = f"{lon},{lat}"  # Swap to (longitude, latitude)

        return et.tostring(kml, encoding="utf-8", xml_declaration=True, pretty_print=True).decode("utf-8")

    @staticmethod
    def _parse_coordinates(coord_text: str) -> Tuple[float, float]:
        """Parses coordinate string and ensures correct order."""
        coords = [float(c) for c in coord_text.split(",")[:2]]
        if len(coords) < 2:
            raise ValueError(f"Invalid coordinates: {coord_text}")
        return coords[0], coords[1]
