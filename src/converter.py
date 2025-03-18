import json
import pathlib
import shutil
from enum import Enum
from typing import Any, Dict, List, Tuple, TYPE_CHECKING
import lxml.etree as et

if TYPE_CHECKING:
    from src.utils import Logger, Config


class EConverterType(Enum):
    XML = "xml"
    GEOJSON = "geojson"
    KML = "kml"


class Converter:
    def __init__(self, input_file: str | pathlib.Path, logger: "Logger", config: "Config") -> None:
        self._input_file = pathlib.Path(input_file)
        self._data = self._parse_input_file()
        self._logger = logger
        self._config = config

    def _parse_input_file(self):
        if self._input_file.suffix == ".xml":
            return self._parse_xml()
        elif self._input_file.suffix == ".json" or self._input_file.suffix == ".geojson":
            return self._parse_geojson()
        elif self._input_file.suffix == ".kml":
            return self._parse_kml()
        else:
            raise ValueError("Unsupported file format")

    @property
    def input_file(self) -> pathlib.Path:
        """Returns the input file path."""
        return self._input_file

    @property
    def data(self) -> List[Dict[str, Any]]:
        """Returns the parsed data as a list of dictionaries."""
        return self._data

    def _parse_xml(self) -> List[Dict[str, Any]]:
        """Parses XML file dynamically, ensuring all metadata fields are preserved."""
        tree = et.parse(self._input_file)
        root = tree.getroot()
        markers = []

        for marker in root.findall("marker") + root.findall("item"):  # Handle both <marker> and <item>
            entry = {"geo": (0.0, 0.0)}  # Default geo

            for child in marker:
                tag = child.tag.lower()  # Normalize tag names
                text = child.text.strip() if child.text else ""

                if tag == "geo":
                    entry["geo"] = self._parse_coordinates(text)  # Handle coordinates separately
                else:
                    entry[tag] = text  # Store all other metadata dynamically

            markers.append(entry)

        if not markers:
            raise ValueError("No valid markers found in the XML file.")

        return markers

    def _parse_geojson(self) -> List[Dict[str, Any]]:
        """Parses GeoJSON file dynamically, ensuring all metadata fields are preserved."""
        with open(self._input_file, "r", encoding="utf-8-sig") as f:
            geojson = json.load(f)

        markers = []
        for feature in geojson["features"]:
            lon, lat = feature["geometry"]["coordinates"]  # GeoJSON uses [longitude, latitude]
            entry = {"geo": (lat, lon)}  # Store as (latitude, longitude)

            # Copy all properties dynamically
            for key, value in feature["properties"].items():
                if value is not None:
                    entry[key.lower()] = value  # Normalize keys

            markers.append(entry)

        return markers

    def _parse_kml(self) -> List[Dict[str, Any]]:
        """Parses KML file dynamically, ensuring all metadata fields are preserved."""
        tree = et.parse(self._input_file)
        root = tree.getroot()
        ns = {"kml": "http://www.opengis.net/kml/2.2"}

        markers = []
        for placemark in root.findall(".//kml:Placemark", ns):
            entry = {"geo": (0.0, 0.0)}  # Default geo

            name = placemark.find("kml:name", ns)
            if name is not None:
                entry["name"] = name.text.strip()

            coordinates = placemark.find(".//kml:coordinates", ns)
            if coordinates is not None:
                lon, lat = self._parse_coordinates(coordinates.text.strip())
                entry["geo"] = (lat, lon)  # Swap KML [longitude, latitude] -> (latitude, longitude)

            # Extract ExtendedData fields dynamically
            extended_data = placemark.find("kml:ExtendedData", ns)
            if extended_data is not None:
                for data in extended_data.findall("kml:Data", ns):
                    key = data.get("name")
                    value = data.find("kml:value", ns)
                    if key and value is not None:
                        entry[key.lower()] = value.text.strip()  # Normalize keys

            markers.append(entry)

        return markers

    def convert(self, new_type: EConverterType) -> str | None:
        """Converts the current data to the requested format. Returns None if conversion is unnecessary."""
        current_type = None
        if self._input_file.suffix == ".xml":
            current_type = EConverterType.XML
        elif self._input_file.suffix == ".json" or self._input_file.suffix == ".geojson":
            current_type = EConverterType.GEOJSON
        elif self._input_file.suffix == ".kml":
            current_type = EConverterType.KML

        # Skip conversion if already in the requested format
        if current_type == new_type:
            self._logger.print(f"Skipped: {self.input_file} is already in {new_type.value} format.")
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
        for entry in self._data:
            lat, lon = entry["geo"]
            properties = {key: value for key, value in entry.items() if key not in ["geo"]}

            # Ensure 'adr' is correctly renamed to 'address' in GeoJSON
            if "adr" in properties:
                properties["address"] = properties.pop("adr")

            feature = {
                "type": "Feature",
                "properties": properties,
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
        for entry in self._data:
            marker = et.SubElement(root, "marker")
            et.SubElement(marker, "name").text = entry["name"]
            et.SubElement(marker, "adr").text = entry.get("address", "")
            lat, lon = entry["geo"]
            et.SubElement(marker, "geo").text = f"{lat}, {lon}"  # Keep (latitude, longitude)
            et.SubElement(marker, "note").text = entry.get("note", "")

        return et.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True).decode("utf-8")

    def _to_kml(self) -> str:
        """Converts data to KML format, preserving all metadata."""
        kml = et.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
        doc = et.SubElement(kml, "Document")

        for entry in self._data:
            placemark = et.SubElement(doc, "Placemark")
            et.SubElement(placemark, "name").text = entry["name"]

            # Add extended metadata
            extended_data = et.SubElement(placemark, "ExtendedData")
            for key, value in entry.items():
                if key not in ["name", "geo"] and value:  # Skip name and geo
                    data_element = et.SubElement(extended_data, "Data", name=key)
                    et.SubElement(data_element, "value").text = str(value)

            # Add coordinates
            point = et.SubElement(placemark, "Point")
            lat, lon = entry["geo"]
            et.SubElement(point, "coordinates").text = f"{lon},{lat}"

        return et.tostring(kml, encoding="utf-8", xml_declaration=True, pretty_print=True).decode("utf-8")

    @staticmethod
    def _parse_coordinates(coord_text: str) -> Tuple[float, float]:
        """Parses coordinate string and ensures correct order."""
        if coord_text == "" or coord_text is None:
            return 0.0, 0.0
        try:
            coords = [float(c) for c in coord_text.split(",")[:2]]
        except ValueError:
            raise ValueError(f"Invalid coordinate format: {coord_text}")
        if len(coords) < 2:
            raise ValueError(f"Invalid coordinates: {coord_text}")
        return coords[0], coords[1]
