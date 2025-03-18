import pytest
import json
import lxml.etree as et
from argparse import Namespace
from main import Main
from src.converter import EConverterType


# 🔹 Helper function to create a test directory with sample files
@pytest.fixture
def setup_test_directory(tmp_path):
    """Creates a temporary directory with sample XML, KML, and GeoJSON files."""
    test_dir = tmp_path / "batch_test"
    test_dir.mkdir()

    # Create subdirectories
    subdir = test_dir / "nested"
    subdir.mkdir()

    # Sample XML file
    xml_content = """<?xml version="1.0"?>
    <markers>
        <item>
            <name>Test Location</name>
            <adr>123 Test Street</adr>
            <state>TX</state>
            <geo>30.123456, -97.123456</geo>
            <type>A</type>
            <note>Test note</note>
        </item>
    </markers>"""
    (test_dir / "test.xml").write_text(xml_content)

    # Sample GeoJSON file
    geojson_content = json.dumps({
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "name": "Test Location",
                    "address": "123 Test Street",
                    "state": "TX",
                    "type": "A",
                    "note": "Test note"
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [-97.123456, 30.123456]
                }
            }
        ]
    }, indent=2)
    (subdir / "test.geojson").write_text(geojson_content)

    return test_dir


# 🔹 Fix: Ensure files exist before instantiating `Main`
def test_cli_argument_parsing(tmp_path):
    """Test that CLI arguments are correctly parsed into the Main class."""
    input_dir = tmp_path / "input_dir"
    input_dir.mkdir()

    # Create a dummy file so Main doesn't raise an error
    (input_dir / "dummy.xml").write_text("<markers></markers>")

    args = Namespace(
        input=str(input_dir),
        output=str(tmp_path / "output_dir"),
        xml=True,
        geojson=True,
        kml=True
    )

    main = Main(args)

    assert main.input_path == input_dir
    assert main.output_dir == tmp_path / "output_dir"
    assert set(main.target_types) == {EConverterType.XML, EConverterType.GEOJSON, EConverterType.KML}


def test_batch_processing(setup_test_directory, tmp_path):
    """Tests batch processing by converting multiple files, including those in subdirectories."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    args = Namespace(
        input=str(setup_test_directory),
        output=str(output_dir),
        xml=True,
        geojson=True,
        kml=True
    )

    main = Main(args)
    main.run()

    # Check if converted files exist in correct locations
    assert (output_dir / "test.geojson").exists()
    assert (output_dir / "test.kml").exists()
    assert (output_dir / "test.xml").exists()
    assert (output_dir / "nested/test.xml").exists()
    assert (output_dir / "nested/test.kml").exists()

    # Validate JSON Output
    geojson_data = json.loads((output_dir / "test.geojson").read_text())
    assert geojson_data["type"] == "FeatureCollection"
    assert len(geojson_data["features"]) == 1

    # Validate XML Output
    xml_data = et.parse(output_dir / "test.xml").getroot()
    assert xml_data.find(".//name") is not None


def test_no_input_file():
    """Test that the script raises an error when no input file or directory is provided."""
    args = Namespace(
        input="non_existent_dir",
        output="output_dir",
        xml=True,
        geojson=False,  # ✅ Explicitly set to False
        kml=False
    )

    with pytest.raises(ValueError, match="No valid files found for conversion."):
        Main(args)
