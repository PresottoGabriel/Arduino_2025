# Arduino_2025 - RBEF Codees

This repository contains Codees A, B, and C of the Arduino_2025 project, developed for automation and data analysis using Arduino and Python.

## 📁 Structure

- `Code A.ino` — Code to be uploaded to the Arduino board.
- `Code B.py` — Python script for reading data via serial port.
- `Code C.py` — Script for statistical analysis of acquired data.

## 🛠️ Requirements

### For Arduino (Code A.ino):
- [Arduino IDE](https://www.arduino.cc/en/software)
- Compatible Arduino board (e.g.: Uno, Nano)
- Standard Serial library (`Serial.begin`, etc.)

## ⚠️ Warning: Serial Port

Before running the `Code B.py` script, **carefully check the serial port used by your Arduino board**.

- On **Windows**, it will normally be something like: `COM3`, `COM4`, etc.
- On **Linux**, it will be something like: `/dev/ttyUSB0` or `/dev/ttyACM0`

You can check the correct port:
- Through the **Tools > Port** menu in Arduino IDE
- Or with the command in Linux terminal:

```bash
dmesg | grep tty
```

### For Python (Appendices B and C):
- Python 3.8+
- Packages:
  - `pyserial`
  - `numpy`
  - `matplotlib`
  - `pandas`
  - `scikit-learn`
  - `scipy`

Install with:

```
pip install pyserial pandas matplotlib numpy scipy scikit-learn
```

