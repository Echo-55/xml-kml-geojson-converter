# XML, KML, GeoJSON Converter

A Python tool for converting location data between XML, KML, and GeoJSON formats.

## 🚀 Features

- Convert XML → KML, GeoJSON
- Convert KML → XML, GeoJSON
- Convert GeoJSON → XML, KML
- Handles coordinate order differences (KML uses [longitude, latitude], others use [latitude, longitude])
- Command-line interface for easy use
- Uses lxml for efficient XML/KML

## 📦 Installation

1. Clone the repository
    ```bash
    git clone https://github.com/echo55/xml-kml-geojson-converter.git
    cd xml-kml-geojson-converter
    ```

---

2. Install dependencies
    ```bash
   pip install -r requirements.txt
   ```

## ⚡ Usage

### Command-Line Interface

Run the script with:

```bash
python main.py -i <input_file> -x -g -k
```

---

## Arguments

| Flag                       | Description                                  |
|----------------------------|----------------------------------------------|
| -i, --input <input_file>   | (Required) Input file (XML, KML, or GeoJSON) |
| -x, --xml                  | Convert to XML                               |
| -g, --geojson              | Convert to GeoJSON                           |
| -k, --kml                  | Convert to KML                               |
| -o, --output <output_file> | (Optional) Specify an output filename        |

---

## 🔄 Example Conversions

### Convert XML to GeoJSON and KML

```bash
python main.py -i examples\aircraft_graveyards.xml -g -k
```

### Output:

```css
Saved data to aircraft_graveyards.geojson
Saved data to aircraft_graveyards.kml
```

### Convert KML to XML

```bash
python main.py -i examples\aircraft_graveyards.kml -x
```

### Convert GeoJSON to XML

```bash
python main.py -i examples\aircraft_graveyards.geojson -x
```

---

## 🛠 How It Works

1. Detects the input format based on file extension (.xml, .json, .kml).
2. Parses the file and extracts location data.
3. Converts the data to the requested formats.
4. Swaps coordinate order for KML (ensures compatibility).

---

## 📜 Project Structure

```pgsql
converter-tool/
│── src/
│   ├── converter.py        # Core conversion logic
│   ├── main.py             # CLI interface
│── examples                # Example dataset
│── requirements.txt        # Dependencies
│── README.md               # Documentation
```

---

## ✅ Planned Improvements

- Add support for more formats (e.g., CSV, Shapefile)
- Implement unit tests for conversion functions
- Enhance error handling and logging
- Support for batch conversions
- Add a GUI interface

---

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Let me know if you have any questions or suggestions! Happy exploring! 😊