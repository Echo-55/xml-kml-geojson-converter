# XML, KML, GeoJSON Converter

A Python tool for converting location data between XML, KML, and GeoJSON formats.

## 🚀 Features

* Convert XML to KML and GeoJSON
* Convert KML to XML and GeoJSON
* Convert GeoJSON to XML and KML
* Batch processing for multiple files in a directory
* Optional output directory for converted files that retains the original file structure
* Handles coordinate order differences (KML uses [longitude, latitude], others use [latitude, longitude])
* Command-line interface for easy use
* Uses lxml for efficient XML/KML handling

## 📦 Installation

1. Clone the repository

 ```bash
 git clone https://github.com/Echo-55/xml-kml-geojson-converter.git
 cd xml-kml-geojson-converter
 ```

2. Install dependencies

 ```bash
pip install -r requirements.txt
```

## ⚡ Usage

### Command-Line Interface

Convert a single file or all files in a directory:

```bash
python main.py -i <input_path> -x -g -k
```

📌 **<input_path>** can be:

    A single file (file.xml, file.geojson, file.kml)
    A directory (converts all XML, KML, and GeoJSON files inside)

## 🔹 Arguments

| Flag                       | Description                                    |
|----------------------------|------------------------------------------------|
| -i, --input <input_file>   | (Required) Input file or directory             |
| -x, --xml                  | Convert to XML                                 |
| -g, --geojson              | Convert to GeoJSON                             |
| -k, --kml                  | Convert to KML                                 |
| -o, --output <output_file> | (Optional) Specify an output file or directory |

---

## 🔄 Example Conversions

### Convert a Single File

#### Convert XML -> GeoJSON and KML

```bash
python main.py -i examples/aircraft_graveyards.xml -g -k
```

#### Output:

```css
Saved data to aircraft_graveyards.geojson
Saved data to aircraft_graveyards.kml
```

#### Convert KML -> XML and GeoJSON

```bash
python main.py -i examples/aircraft_graveyards.kml -x -g
```

#### Convert GeoJSON -> XML

```bash
python main.py -i examples/aircraft_graveyards.geojson -x
```

---

### Batch Convert an Entire Directory

#### Convert all XML, KML, and GeoJSON files in `./data/`

```bash
python main.py -i ./data/ -x -g -k
```

#### ✅ All matching files in ./data/ will be converted.

#### Convert and save results to a specific directory

```bash
python main.py -i ./data/ -x -g -k -o ./converted_data/
```

#### ✅ All converted files will be saved in `./converted_data/`.

---

## 🛠 How It Works

1. Detects the input format based on file extension (.xml, .json, .kml).
2. Parses the file and extracts location data.
3. Converts the data to the requested formats.
4. Handles coordinate order differences for KML.
5. Processes batch conversions if a directory is provided.

---

## 📜 Project Structure

```pgsql
xml-kml-geojson-converter/
│── examples/                    # Example dataset
│   ├── aircraft_graveyards.xml
│   ├── aircraft_graveyards.kml
│   ├── aircraft_graveyards.geojson
│── src/
│   ├── utils/                   
    │   ├── __init__.py              
    │   ├── logger.py            # Logging utility
    │   ├── config.py            # Configuration settings
│   ├── converter.py             # Core conversion logic
│   ├── main.py                  # CLI interface
│── tests/                       # Unit tests
│   ├── test_converter.py        # Tests for conversion functions
│   ├── test_main.py             # Tests for CLI interface
│   │── test_files/              # Sample test files
│   │   ├── test.xml
│   │   ├── test.kml
│   │   ├── test.geojson
│── config.ini                   # Some configuration settings for user
│── .gitignore                   # Git ignore file
│── requirements.txt             # Dependencies
│── LICENSE                      # License file
│── README.md                    # Documentation
```

---

## ✅ Planned Improvements

1. [ ✔ ]  Batch conversion support
2. [ ✔ ] Unit tests for conversion functions
3. [  ] Enhanced error handling and logging
4. [  ] Support for more formats (e.g., CSV, Shapefile)
5. [  ] GUI interface for easier use

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Got any cool or interesting GIS datasets to work with? Drop me a message! I'd love to see what you're working on.

Let me know if you have any questions or suggestions! Happy exploring! 😊