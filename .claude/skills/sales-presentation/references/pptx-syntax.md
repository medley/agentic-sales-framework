# HTML to PowerPoint Syntax Reference

Complete guide for creating HTML slides that convert to PowerPoint using html2pptx.js.

## Layout Dimensions

Must be specified on `<body>` element:

- **16:9** (default): `width: 720pt; height: 405pt`
- **4:3**: `width: 720pt; height: 540pt`
- **16:10**: `width: 720pt; height: 450pt`

## Supported Elements

### Text Elements (REQUIRED for all text)

**CRITICAL: ALL text MUST be inside text elements:**

- `<p>` - Paragraphs
- `<h1>` through `<h6>` - Headings
- `<ul>`, `<ol>` - Lists
- `<li>` - List items

**Common errors:**
- ❌ `<div>Text here</div>` - Text will NOT appear in PowerPoint
- ❌ `<span>Text</span>` - Text will NOT appear in PowerPoint
- ✅ `<div><p>Text here</p></div>` - Correct

### Inline Formatting

Works inside text elements:

- `<b>`, `<strong>` - Bold text
- `<i>`, `<em>` - Italic text
- `<u>` - Underlined text
- `<span style="...">` - Custom styling
  - Supported: `font-weight: bold`, `font-style: italic`, `text-decoration: underline`, `color: #rrggbb`
  - NOT supported: `margin`, `padding`
- `<br>` - Line breaks

### Layout Elements

- `<div>` - Containers (with background/border become shapes)
- `<img>` - Images (PNG, JPG)
- `class="placeholder"` - Reserved space for manual content insertion

## Font Restrictions

**ONLY use web-safe fonts:**

✅ Supported:
- Arial (recommended fallback for Flama)
- Helvetica
- Times New Roman
- Georgia
- Courier New
- Verdana
- Tahoma
- Trebuchet MS

❌ DO NOT use:
- Segoe UI
- SF Pro
- Roboto
- Flama (rasterize or use Arial fallback)
- Custom fonts

## Styling

### Text Styling

```html
<p style="font-size: 14pt; color: #4E4E50; line-height: 1.5;">
  Regular text with <span style="font-weight: bold; color: [Brand Primary Color];">bold teal</span>
</p>
```

### Shape Styling (DIV only)

**Backgrounds:**
```html
<div style="background: [Brand Primary Color];">
  <p>Text on teal background</p>
</div>
```

**Borders:**
```html
<!-- Uniform border -->
<div style="border: 2px solid #333333;">
  <p>Bordered box</p>
</div>

<!-- Partial border (renders as line shape) -->
<div style="border-left: 8pt solid [Brand Secondary Color];">
  <p>Purple left accent</p>
</div>
```

**Border Radius:**
```html
<!-- Rounded corners -->
<div style="border-radius: 8pt; background: #DDEEFF;">
  <p>Rounded box</p>
</div>

<!-- Circle -->
<div style="border-radius: 50%; width: 100pt; height: 100pt; background: [Brand Primary Color];">
</div>
```

**Box Shadows:**
```html
<div style="box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3); background: white;">
  <p>Card with shadow</p>
</div>
```

**CRITICAL:** Box shadows, borders, backgrounds only work on `<div>` elements, NOT on `<p>`, `<h1>`, `<ul>`, etc.

### Layout with Flexbox

```html
<body style="width: 720pt; height: 405pt; display: flex; flex-direction: column;">
  <div class="header" style="height: 60pt; background: [Brand Primary Color];">
    <h1 style="color: white;">Slide Title</h1>
  </div>

  <div class="content" style="flex: 1; display: flex; padding: 20pt;">
    <div class="left-column" style="flex: 1; margin-right: 20pt;">
      <p>Left content</p>
    </div>
    <div class="right-column" style="flex: 1;">
      <p>Right content</p>
    </div>
  </div>
</body>
```

## Lists

**NEVER use manual bullet symbols (•, -, *):**

❌ Wrong:
```html
<p>• Item 1</p>
<p>• Item 2</p>
```

✅ Correct:
```html
<ul>
  <li>Item 1</li>
  <li>Item 2</li>
</ul>
```

## Images

```html
<img src="logo.png" style="width: 150pt; height: 50pt;" />
```

## Placeholders for Manual Content

```html
<div class="placeholder" style="width: 300pt; height: 200pt; background: #E8E6DC;">
  <!-- Reserved space for chart/image insertion -->
</div>
```

Returns `{ id, x, y, w, h }` for programmatic insertion.

## Icons & Gradients

**CRITICAL: Never use CSS gradients or icon fonts**

❌ Wrong:
```html
<div style="background: linear-gradient(to right, [Brand Primary Color], [Brand Secondary Color]);">
```

✅ Correct:
```javascript
// First rasterize gradient to PNG using Sharp
const sharp = require('sharp');
await sharp({
  create: {
    width: 720,
    height: 405,
    channels: 4,
    background: { r: 59, g: 148, b: 163, alpha: 1 }
  }
}).png().toFile('gradient-bg.png');
```

```html
<!-- Then use as background image -->
<div style="background-image: url('gradient-bg.png'); width: 720pt; height: 405pt;">
```

## Color Format

Always use hex colors with `#` prefix:

✅ Correct: `color: [Brand Primary Color]`
❌ Wrong: `color: rgb(59, 148, 163)`
❌ Wrong: `color: 3B94A3` (missing #)

## Common Patterns

### Slide Header with Teal Background

```html
<div class="header" style="background: [Brand Primary Color]; padding: 20pt;">
  <h1 style="margin: 0; color: white; font-size: 32pt;">Slide Title</h1>
</div>
```

### Two-Column Layout

```html
<div style="display: flex; padding: 20pt;">
  <div style="flex: 1; margin-right: 20pt;">
    <p>Left column content</p>
  </div>
  <div style="flex: 1;">
    <p>Right column content</p>
  </div>
</div>
```

### Highlighted Box

```html
<div style="background: #DDEEFF; border-left: 8pt solid [Brand Primary Color]; padding: 15pt;">
  <p style="font-size: 14pt; color: #4E4E50;">
    <span style="font-weight: bold;">Key Point:</span> Important information here
  </p>
</div>
```

### Bulleted List with Styling

```html
<ul style="font-size: 14pt; color: #4E4E50; line-height: 1.8;">
  <li><span style="font-weight: bold;">First point</span>: Details here</li>
  <li><span style="font-weight: bold;">Second point</span>: More details</li>
  <li><span style="font-weight: bold;">Third point</span>: Even more details</li>
</ul>
```

## Validation

Before converting to PowerPoint:

1. ✅ All text inside `<p>`, `<h1>`-`<h6>`, `<ul>`, or `<ol>` tags
2. ✅ Only web-safe fonts used
3. ✅ No CSS gradients (use PNG backgrounds)
4. ✅ No icon fonts (rasterize to PNG)
5. ✅ Body dimensions specified
6. ✅ All colors in hex format with `#` prefix
7. ✅ Lists use `<ul>`/`<ol>`, not manual bullets
