# Flipper Zero on PC

# Flipper Windows

**Flipper Windows** is a Windows-based software project inspired by the concept, modular architecture, and user experience of the **Flipper Zero**.

The goal of this project is to bring a collection of hardware-oriented, security, networking, and automation tools into a single modular application that can run directly on a Windows PC.

Instead of requiring a dedicated handheld device for every experiment, Flipper Windows provides a software environment where different tools can be developed, tested, managed, and extended through independent modules.

> **This project is inspired by Flipper Zero and is not an official Flipper Zero product or an official Flipper Devices project.**

---

## ✨ Features

Flipper Windows is built around a modular architecture, allowing individual features to be developed independently and loaded by the main application.

Current modules include:

* **BadUSB**

  * Ducky Script parsing
  * Script execution
  * Built-in example scripts
  * Configurable delays and commands

* **GPIO**

  * GPIO-oriented functionality
  * Designed as an extensible hardware interface module

* **iButton**

  * iButton-related functionality
  * Modular architecture for future hardware integration

* **Infrared**

  * Infrared functionality
  * Designed to support future IR hardware integrations

* **Network Scanner**

  * Network discovery and scanning
  * Network information gathering
  * Dedicated scanner module

* **NFC**

  * NFC-related functionality
  * Structured as an independent module for future expansion

* **RFID**

  * RFID-related functionality
  * Designed for future hardware communication and expansion

* **Sub-GHz**

  * Sub-GHz-oriented functionality
  * Modular architecture prepared for compatible hardware integrations

* **U2F**

  * U2F-related functionality
  * Designed as an extensible authentication/security module

---

## 🧩 Modular Architecture

One of the main goals of Flipper Windows is to keep the system highly modular.

The application is separated into several major components:

```text
Flipper Windows
│
├── Core
│   ├── Kernel
│   ├── Plugin Loader
│   ├── State Manager
│   ├── Task Runner
│   └── Result System
│
├── Modules
│   ├── BadUSB
│   ├── GPIO
│   ├── iButton
│   ├── Infrared
│   ├── Network Scanner
│   ├── NFC
│   ├── RFID
│   ├── Sub-GHz
│   └── U2F
│
├── UI
│   ├── Main Window
│   ├── Theme System
│   └── Windows Effects
│
└── Data
    └── SQLite Database
```

This architecture makes it possible to add new functionality without having to rewrite the entire application.

Each module can have its own logic while communicating with the core system through the common module architecture.

---

## ⚙️ Core System

The core of Flipper Windows is responsible for coordinating the different parts of the application.

### Kernel

The kernel acts as the central part of the application and provides the foundation required by the modules.

### Plugin Loader

The plugin loader allows modules to be discovered and loaded dynamically.

This makes the project easier to expand as new features are added.

### State Manager

The state manager handles application and module state, allowing different components to maintain and update their current status.

### Task Runner

The task runner provides a centralized mechanism for executing operations and managing background tasks.

### Result System

The result system provides a structured way for modules and core components to return information back to the application.

---

## 🖥️ Windows UI

Flipper Windows includes a dedicated graphical interface designed specifically for Windows.

The UI contains:

* Custom main window
* Custom theme system
* Windows-specific visual effects
* Module navigation
* Integrated tool execution
* Application state presentation

The interface is designed around the idea of keeping the experience simple while still providing access to multiple tools.

---

## 💾 Data Storage

The project includes an internal SQLite database:

```text
data/flipper.db
```

The database provides a foundation for persistent application data and can be expanded as the project grows.

---

## 🔌 Hardware Integration

The long-term goal of Flipper Windows is not limited to software-only functionality.

The modular architecture is designed so that compatible external hardware can eventually be connected to the Windows application and controlled through dedicated modules.

This makes it possible to develop a Windows-based environment that can work alongside external hardware while keeping the user experience centralized inside the application.

---

## 🛠️ Technology

The current project is primarily implemented in **Python** and uses a modular Python architecture.

The project structure includes:

* Python
* SQLite
* Modular plugins
* Custom Windows UI
* Independent feature modules
* Core task management
* Dynamic module loading

---

## 📁 Project Structure

```text
.
├── core/
│   ├── kernel.py
│   ├── plugin_loader.py
│   ├── result.py
│   ├── state_manager.py
│   └── task_runner.py
│
├── modules/
│   ├── badusb/
│   ├── gpio/
│   ├── ibutton/
│   ├── infrared/
│   ├── netscanner/
│   ├── nfc/
│   ├── rfid/
│   ├── subghz/
│   ├── u2f/
│   └── base_module.py
│
├── ui/
│   ├── main_window.py
│   ├── theme.py
│   └── win_effects.py
│
├── data/
│   └── flipper.db
│
└── main.py
```

---

## 🚀 Project Vision

The current version is the foundation of a much larger project.

The long-term vision is to create a powerful **Flipper-inspired Windows platform** where users can access different hardware, networking, security, automation, and protocol-related tools from one unified interface.

Future development may include:

* Additional modules
* More hardware integrations
* Improved networking tools
* Expanded NFC/RFID functionality
* More Sub-GHz functionality
* Better BadUSB support
* Device communication
* External hardware support
* Improved plugin management
* Module marketplace/installer
* Configuration management
* More advanced UI
* Cross-device communication
* Better data management
* Automated updates
* Additional Windows integrations

---

## ⚠️ Responsible Use

This project is intended for **educational purposes, authorized security research, hardware development, testing, and experimentation**.

Users are responsible for ensuring that they have permission to test or interact with the systems, devices, networks, and hardware they use with this software.

Do not use the project against systems or devices that you do not own or have explicit authorization to test.

---

## 📌 Development Status

Flipper Windows is an **active work in progress**.

Some modules are currently functional while others are still being expanded and prepared for deeper hardware integration.

The architecture, UI, modules, tools, and hardware support are expected to evolve significantly as development continues.

**This project is continuously updated and actively evolving. New features, improvements, fixes, modules, and hardware integrations are being added regularly. Stay tuned for future updates.**

---

## 🌐 Disclaimer

Flipper Windows is an independent community project inspired by the ideas and general experience of Flipper Zero.

It is **not affiliated with, endorsed by, sponsored by, or officially connected to Flipper Devices**.

---

## ⭐ Support the Project

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

Contributions, ideas, testing, bug reports, and feature requests are welcome as the project continues to evolve.
2
