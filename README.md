# EcoTrack - Smart Household Waste & Recycling Manager

**Hack-AI-Thon 2026 | Group 15**  
**Team:** Jivraj Singh · Aaditya Sorout · Homor Azeem

EcoTrack is a Python desktop application for recording household waste, analysing waste patterns, tracking recycling, generating an explainable sustainability score, and producing actionable recommendations and period reports.

The official challenge requires a functional Python/OOP prototype with waste-record CRUD, total/category statistics, recycling rate, sustainability score, recommendations, and a selected-period report. The application implements those requirements and adds persistent SQLite storage, multi-user authentication, user-isolated records, password recovery, charts, themes, an Ideas/Green Coach page, and an optional impact-reward system.  

## Technology

- Python 3.10+ (tested with Python 3.13.5 in the build environment)
- Tkinter / ttk
- SQLite3
- Python standard library only
- Pillow is used only by the screenshot-generation helper in this build environment, not by the app itself.

No web framework, JavaScript, React, or external API is required for the application. Optional `requirements-dev.txt` lists tooling for rebuilding the presentation/report assets.

## Repository layout

```text
Group15_EcoTrack/
├── main.py
├── database.py
├── models.py
├── logic.py
├── security.py
├── ui/
│   ├── __init__.py
│   ├── app.py
│   ├── theme.py
│   └── widgets.py
├── tests/
│   ├── __init__.py
│   ├── test_app.py
│   ├── test_database.py
│   ├── test_logic.py
│   └── test_security.py
├── assets/
│   └── screenshots/
├── docs/
│   ├── project_report.md
│   ├── demo_script.md
│   └── test_cases.md
├── presentation/
│   └── Group15_EcoTrack_Presentation.pptx
├── .gitignore
└── README.md
```

## Run

From the project directory:

```bash
python main.py
```

The SQLite database (`ecotrack.db`) is created automatically in the project directory on first run.

### Demo account

- Username: `demo`
- Password: `EcoTrack@15`

The demo account is created automatically if it does not exist. Its password and security answers are stored only as salted PBKDF2-HMAC-SHA256 hashes.

## Core workflow

1. Sign in or create an account.
2. Add waste records with date, category, weight and recycled status.
3. Review records with search/filter support.
4. Inspect Analytics for actual category and trend data.
5. Use Recyclable / Non-Recyclable views for focused review.
6. Open Report and choose a date range.
7. Read Green Coach recommendations and save custom ideas.
8. Review optional Impact Rewards.
9. Switch Light/Dark mode from the header or Settings.

## OOP design

- `Household` models the user's household context and exposes record-domain operations.
- `WasteReport` encapsulates report calculations and recommendations.
- `Record`, `UserSession`, `Idea`, and `RewardTransaction` are data models.
- Tkinter page classes encapsulate UI responsibilities.
- The application coordinator (`EcoTrackApp`) manages session, navigation and theme state.

The design uses composition and encapsulation heavily; inheritance is limited to meaningful Tkinter page/widget relationships rather than artificial inheritance added only for a checklist.

## Sustainability calculations

The required report includes:

- total waste
- category-wise kilogram totals and percentages
- recycling rate
- sustainability score out of 100
- actionable recommendations

The sample logic supplied with the challenge describes an explainable score that weights recycling rate at 70% and waste volume at 30%. EcoTrack keeps that transparent scoring model and makes the period selection explicit.

## Impact reward enhancement

This project also implements the requested EcoTrack reward enhancement:

**15 kg recycled = 1 point = Rs 1**

Only recycled records create reward transactions, and each waste record can contribute at most one reward transaction. Editing a record removes its previous reward contribution before recalculating it; deleting a record removes the related contribution automatically through the database relationship.

## Security

- Passwords are never stored in plaintext.
- Security answers are never stored in plaintext.
- PBKDF2-HMAC-SHA256 with random salts is used for stored secrets.
- `secrets` is used for generated password material.
- SQL statements use placeholders.
- Waste records, ideas and rewards are queried using the authenticated `user_id`.
- Record IDs are scoped per user and remain stable after deletion of other records.
- Normal users receive friendly error messages rather than Python tracebacks.

This is a secure educational/local desktop implementation, not a claim of enterprise identity management.

## Password policy

A new/reset password must satisfy:

- minimum 9 characters
- uppercase letter
- lowercase letter
- number
- special character
- not a common password
- not an obvious sequence or repeated pattern

The registration interface shows a live green/red checklist, includes show/hide controls, and can generate a secure password using `secrets`.

## Testing

Run:

```bash
python -m unittest discover -v
```

The build environment has a virtual X display for Tkinter smoke testing. The final verification run passed **17/17 automated tests** under `xvfb-run`, covering authentication helpers, password policy, password hashing, generated passwords, OOP/domain calculations, date filtering, validation, reward calculations, database isolation and UI construction.

## Screenshots

See `assets/screenshots/` for actual application renders including:

- Dashboard
- Analytics
- Settings
- Dark-mode Settings

## Limitations

- Desktop Tkinter application; it is resizable and scrollable but is not a mobile-browser application.
- The sustainability score is a simple heuristic rather than a calibrated municipal benchmark.
- Security-question recovery is suitable for a local educational application; production systems would normally use stronger account-recovery infrastructure.
- The reward system is an optional product enhancement rather than a required challenge criterion.

## Future improvements

- municipal benchmark comparison
- exportable PDF/CSV reports
- local-authority recycling rules by location
- barcode/photo-assisted logging
- stronger account-recovery mechanisms for production deployments
- richer long-term trend analysis

## Team contributions

### Jivraj Singh
UI / Frontend / visual formatting / UX / dashboard composition

### Aaditya Sorout
Core logic / algorithms / data processing / application integration

### Homor Azeem
Testing / documentation / report / presentation / demo preparation

All three members should be prepared to explain the complete application, including the modules outside their primary responsibility.
