# ⚡ uBlock → Stylus Converter

A desktop utility for converting uBlock Origin cosmetic filters into Stylus-compatible UserCSS files.

![Python](https://img.shields.io/badge/Python-3.7+-3776ab?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)

## ✨ Features

- **Live Statistics** — Real-time parsing feedback as you type
- **Multiple Export Formats**
  - Individual `.user.css` files per domain
  - Single ZIP archive with all files
  - Stylus-compatible JSON for bulk import
- **Style Injection Support** — Converts `:style()` rules with custom CSS
- **Smart Filter Detection** — Automatically skips network filters (`||`, `@@`, `$`)
- **Dark Professional UI** — Modern interface with accent colors
- **Smart Domain Handling** — Automatically groups rules by domain
- **Global Rules Support** — Handles site-agnostic `##` selectors
- **Persistent Settings** — Remembers your output folder between sessions

## 📸 Screenshot

<img width="1134" height="980" alt="2026-01-18 07_59_20-uBlock → Stylus Converter" src="https://github.com/user-attachments/assets/aee17637-e179-44df-b301-84d3031ca35f" />


## 🚀 Installation

### Prerequisites
- Python 3.7 or higher
- Tkinter (included with most Python installations)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/ublock-to-stylus-converter.git
cd ublock-to-stylus-converter

# Run the application
python ublocktoCSS_pro.py
```

No additional dependencies required — uses only Python standard library.

## 📖 Usage

### Basic Workflow

1. **Paste your uBlock filters** into the input area (or use File → Load)
2. **Select an output folder** (or use Stylus JSON export for direct import)
3. **Click "Convert & Save"** or press `Ctrl+Enter`

### Supported Filter Syntax

| Format | Description | Output CSS |
|--------|-------------|------------|
| `domain.com##.selector` | Hide elements | `display: none !important` |
| `domain.com##div:style(color: red)` | Style injection | `color: red` |
| `domain1.com,domain2.com##.ad` | Multi-domain | Separate files per domain |
| `##.global-ad` | Global rule | Applies to all sites |

### Automatically Skipped

These uBlock filter types are **not** cosmetic and are automatically skipped:

| Filter Type | Example | Reason |
|-------------|---------|--------|
| Network blocks | `\|\|ads.example.com^` | Blocks requests, not CSS |
| Exception rules | `@@\|\|example.com^` | Allowlist rules |
| Resource filters | `\|\|cdn.com/ad.js$script` | Blocks specific resources |

Lines starting with `!` are treated as comments.

### Export Options

| Button | Output | Use Case |
|--------|--------|----------|
| **✨ Convert & Save** | Individual `.user.css` files | Manual installation per-site |
| **📦 ZIP** | Single `.zip` archive | Backup or sharing |
| **📋 Stylus JSON** | Stylus backup `.json` | **Bulk import all styles at once** |

### Importing Stylus JSON

The Stylus JSON export creates a file compatible with Stylus's native backup/restore:

1. Open the **Stylus** browser extension
2. Click **Manage** (or go to `chrome-extension://[id]/manage.html`)
3. Scroll to the **Backup** section
4. Click **Import** and select your exported `.json` file
5. All styles are imported with proper domain targeting

## 🔧 How It Works

### Input Processing
```
! Comment line - ignored
example.com##.ad-banner
example.com##.popup:style(display: none !important; opacity: 0)
||tracking.com/pixel.gif$image    ← skipped (network filter)
##.global-advertisement
```

### Output Structure

**Individual UserCSS files:**
```css
/* ==UserStyle==
@name           example.com - Cleanup
@namespace      ublock-to-stylus-converter
@version        1.0.0
@description    Converted from uBlock Origin cosmetic filters
@author         uBlock Converter
@license        MIT
==/UserStyle== */

@-moz-document domain("example.com") {
    .ad-banner {
        display: none !important;
    }

    .popup {
        display: none !important; opacity: 0;
    }
}
```

**Stylus JSON format:**
```json
[
  { "settings": { ... } },
  {
    "enabled": true,
    "name": "example.com",
    "sections": [{
      "code": "/* Rules for example.com */\n\n    .ad-banner { display: none !important; }\n\n    .popup { display: none !important; opacity: 0; }",
      "domains": ["example.com", "www.example.com"]
    }],
    "_id": "uuid-here",
    "id": 1
  }
]
```

## 📊 Live Statistics

The stats bar updates in real-time as you type:

| Stat | Description |
|------|-------------|
| 📊 Rules | Total valid cosmetic rules |
| 🌐 Domains | Unique domains detected |
| 🌍 Global | Rules without domain (apply everywhere) |
| 🎨 Styles | Rules using `:style()` injection |
| ⏭️ Network | Skipped network/blocking filters |
| ⚠️ Invalid | Malformed or unsupported rules |

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+V` | Paste from clipboard |
| `Ctrl+Enter` | Convert and save |

## 🎨 Customization

The color scheme is defined in the `COLORS` dictionary and can be easily modified:

```python
COLORS = {
    'bg_dark': '#020617',
    'bg_card': '#0f172a',
    'accent_green': '#22c55e',
    'accent_blue': '#60a5fa',
    # ...
}
```

## 📁 Project Structure

```
ublock-to-stylus-converter/
├── ublocktoCSS.py        # Main application
├── README.md             # This file
└── LICENSE               # MIT License
```

## 🤝 Contributing

Contributions are welcome! Feel free to:

- Report bugs
- Suggest features
- Submit pull requests

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

## 🔗 Related Links

- [Stylus Extension](https://add0n.com/stylus.html) — The userstyle manager
- [uBlock Origin](https://github.com/gorhill/uBlock) — The ad blocker
- [UserCSS Specification](https://github.com/openstyles/stylus/wiki/UserCSS) — Format documentation
