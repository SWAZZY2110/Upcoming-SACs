# VCE Focus Dashboard

A local, browser-based dashboard for the subjects English, Mathematical Methods, Specialist Mathematics, Physics and Chemistry.

It includes:

- SAC dates from the existing calendar, narrowed to the selected subjects.
- 2026 VCAA exam timetable entries for English, Methods, Specialist, Physics and Chemistry.
- Local progress tracking using browser `localStorage`.
- A clean responsive UI that runs without a backend or database.

## Run locally

```bash
npm start
```

Then open <http://localhost:4173> in your browser.

If you do not have npm installed, you can run the same server directly:

```bash
python3 -m http.server 4173
```

## VCAA source

Exam dates are based on the VCAA VCE examination timetable:

<https://www.vcaa.vic.edu.au/administration/key-dates/vce-examination-timetable>
