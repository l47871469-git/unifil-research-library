# UNIFIL Research Library

A structured research portal for the UN DPO UNIFIL Lessons Learned exercise (2026).
Built with Streamlit. Maintained by the Policy & Best Practices Service (PBPS / KMG).

## Setup

```bash
# Clone and enter project
cd unifil-research-library

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Updating the corpus

To add a new source:

1. Run the UNIFIL scanner prompt in a Claude session to produce the structured scan output
2. At the end of the scan, ask Claude: *"Now output this as a JSON record in the sources schema"*
3. Open `data/sources.json` in VS Code
4. Paste the new JSON object into the array (add a comma after the previous last entry)
5. Save — the app will reflect it on next load

## Project structure

```
unifil-research-library/
├── app.py                  # Main entry point + navigation + global CSS
├── pages/
│   ├── library.py          # Source library with filters and detail panel
│   ├── thematic.py         # Thematic navigator
│   └── gaps.py             # Gaps register (manual + auto-inferred)
├── utils/
│   └── data_utils.py       # Data loading, filtering, gap inference
├── data/
│   ├── sources.json        # Master source database
│   └── gaps.json           # Manual gaps register
├── .streamlit/
│   └── config.toml         # Theme configuration
└── requirements.txt
```

## Phases

- **Phase 1 (current):** Source library, thematic navigator, gaps register
- **Phase 2:** Timeline — source coverage (1978–2026)
- **Phase 3:** Timeline — key events with source linkage
- **Phase 4:** Actors & Entities index
- **Phase 5:** Lessons Mind Map

## Data schema reference

Each source record in `sources.json` follows this structure:

```json
{
  "id": "author_year",
  "author": "Last, First",
  "title": "Full title",
  "year": 2024,
  "source_type": "Academic | Think Tank | UN Document | Opinion / Primary | Media | NGO | Other",
  "publisher": "Publisher name",
  "country_of_origin": "Country",
  "tags": ["tag1", "tag2"],
  "abstract": "100-word summary",
  "key_arguments": ["argument 1", "argument 2"],
  "unifil_relevance": "Why this matters for the LL exercise",
  "bias_flag": "Institutional affiliation and potential bias",
  "thematic_clusters": ["Cluster name"],
  "timeline_coverage": [start_year, end_year],
  "timeline_events": [
    {"date": "YYYY", "event": "Description", "source": "id"}
  ],
  "lessons_learned": [
    {"text": "Lesson text", "tag": "SOURCE-DERIVED | ANALYTICAL INFERENCE"}
  ],
  "actors": ["Actor 1", "Actor 2"],
  "gaps_addressed": []
}
```
