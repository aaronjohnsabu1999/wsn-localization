# Mobile WSN Localization: Tag-Aided Uncertainty Reduction  
![Python](https://img.shields.io/badge/python-3.9+-blue?logo=python)
![License](https://img.shields.io/badge/license-MIT-green)
![Build](https://img.shields.io/badge/build-passing-brightgreen)
![Platform](https://img.shields.io/badge/platform-Matplotlib%20%7C%20NumPy-lightgrey)

**Mobile WSN Localization** is a Python-based simulation framework that models how **tag-to-tag linkages** affect uncertainty in mobile wireless sensor networks. Using a geometric approach to uncertainty and neighbor-based trilateration, the system demonstrates how mobility and communication reduce localization error in sparse fixed-anchor environments.

## Project Structure

```
mobile-wsn-localization/
├── main.py                    # Core simulation and visualization
├── report.pdf                 # Technical documentation
├── presentation.pdf           # Presentation slides
├── README.md
└── LICENSE
```

## Features

- **Mobile + fixed sensor modeling** with configurable sensing radii
- **Real-time uncertainty visualization** using `matplotlib`
- **Neighbor-based updates** with optional tag-to-tag communication
- **Custom coordinate and sensor classes** with basic physics support
- **Simulation toggle** for enabling/disabling tag links

## Getting Started

### 🔧 Dependencies

This project requires Python 3.9+ and the following packages:

```bash
pip install numpy matplotlib
```

### ▶️ Run the Simulation

```bash
python main.py
```

This will launch a fullscreen live simulation showing:
- Fixed anchors (colored ×)
- Mobile tags (colored circles)
- Dynamic links (anchor–tag, tag–tag)
- Marker size ∝ uncertainty

## Output Snapshots

| Without Tag Links | With Tag Links |
|-------------------|----------------|
| ![](./results/plots/notaglinks_end.jpg) | ![](./results/plots/taglinks_end.jpg) |

> The presence of inter-tag communication prevents uncertainty divergence over time.

## Configuration

Edit the following parameters directly in `main.py`:

```python
tagLinks      = True    # Enable/disable tag-to-tag communication
finalTime     = 800     # Total simulation time
sensingRadius = 7       # Sensor range in meters
tick          = 1       # Time increment per step
```

## Applications

- **Wildlife localization and monitoring**
- **Ad hoc sensor networks in urban environments**
- **Low-power distributed positioning systems**
- **Indoor GPS-denied navigation**

## Project Context

> Developed as part of the course project for *EE 617: Sensors in Instrumentation* at **IIT Bombay**.

**Author:**  
Aaron John Sabu  
Department of Electrical Engineering  
Indian Institute of Technology Bombay  

## License

MIT License © 2020  
Indian Institute of Technology Bombay