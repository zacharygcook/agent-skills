---
name: local-html-pdf-reports
description: Create polished local review artifacts as a Markdown source, self-contained HTML report, PDF, and rendered page images. Use for planning sheets, research summaries, run reports, probe results, or any disposable local document that benefits from visual review.
---

# Local HTML and PDF Reports

Build a review folder containing a complete Markdown record, a designed self-contained HTML view, a PDF generated from that HTML, and page images used for visual verification.

## Layout

```text
notes/<topic>-<yyyy-mm-dd>/
  report.md
  report.html
  report.pdf
  render-check/
  command-output/   # optional raw evidence
```

Use the repository's preferred scratch location and naming when one exists. Do not promote disposable reports into tracked documentation without user approval.

## Content Contract

- Markdown is the complete evidence record: bottom line, scope, criteria, results, commands, artifacts, limitations, and next steps.
- HTML is the designed review surface. It may be a concise executive view or a full-text review when the user needs to inspect every detail.
- PDF must be regenerated after the final HTML edit.
- Raw logs belong in separate files when they would overwhelm the report.

## Design

Use a restrained print-friendly system: strong typographic hierarchy, high contrast, one intentional accent color, compact cards, readable tables, semantic status labels, and no external runtime dependencies. Add navigation/search or collapsible sections for long reports. Preserve accessibility, selectable text, and useful print behavior.

See [references/style-guide.md](references/style-guide.md) for a reusable visual baseline. Adapt it to an established repository house style when one exists.

## Generate and Verify

1. Format Markdown and HTML with repository-native tooling.
2. Print HTML to PDF with an installed browser using the intended page size and no browser headers/footers.
3. Inspect PDF metadata and page size.
4. Render every PDF page to an image.
5. Actually inspect the images for clipping, overflow, illegible code, broken tables, awkward page breaks, or nearly empty spill pages.
6. Fix, regenerate, and reinspect until clean.

Example tools include Chromium/Chrome headless printing, `pdfinfo`, and `pdftoppm`; discover installed commands rather than assuming exact paths.

## Handoff

Open the HTML when the user requests local review and provide clickable absolute paths to the Markdown, HTML, and PDF. State the PDF page count and that rendered pages were visually checked.
