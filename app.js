const vcaaSource = "https://www.vcaa.vic.edu.au/administration/key-dates/vce-examination-timetable";

const assessments = [
  { date: "2026-03-16T09:00:00+11:00", subject: "English", type: "SAC", title: "Analytical text response" },
  { date: "2026-05-08T09:00:00+10:00", subject: "English", type: "SAC", title: "Comparative / argument analysis" },
  { date: "2026-06-22T09:00:00+10:00", subject: "English", type: "SAC", title: "Creating texts" },
  { date: "2026-08-24T09:00:00+10:00", subject: "English", type: "SAC", title: "Oral presentation" },
  { date: "2026-09-10T09:00:00+10:00", subject: "English", type: "SAC", title: "Final English SAC" },
  { date: "2026-10-27T09:00:00+11:00", subject: "English", type: "Exam", title: "English examination", duration: "9:00 am – 12:15 pm", source: vcaaSource },

  { date: "2026-05-01T09:00:00+10:00", subject: "Methods", type: "SAC", title: "Calculus application" },
  { date: "2026-05-11T09:00:00+10:00", subject: "Methods", type: "SAC", title: "Functions and graphs" },
  { date: "2026-07-20T09:00:00+10:00", subject: "Methods", type: "SAC", title: "Probability and statistics" },
  { date: "2026-09-11T09:00:00+10:00", subject: "Methods", type: "SAC", title: "Final Methods SAC" },
  { date: "2026-11-05T09:00:00+11:00", subject: "Methods", type: "Exam", title: "Mathematical Methods Examination 1", duration: "9:00 am – 10:15 am", source: vcaaSource },
  { date: "2026-11-06T11:45:00+11:00", subject: "Methods", type: "Exam", title: "Mathematical Methods Examination 2", duration: "11:45 am – 2:00 pm", source: vcaaSource },

  { date: "2026-04-24T09:00:00+10:00", subject: "Specialist", type: "SAC", title: "Vectors and proof" },
  { date: "2026-07-31T09:00:00+10:00", subject: "Specialist", type: "SAC", title: "Mechanics / complex numbers" },
  { date: "2026-09-14T09:00:00+10:00", subject: "Specialist", type: "SAC", title: "Final Specialist SAC" },
  { date: "2026-11-09T09:00:00+11:00", subject: "Specialist", type: "Exam", title: "Specialist Mathematics Examination 1", duration: "9:00 am – 10:15 am", source: vcaaSource },
  { date: "2026-11-11T11:45:00+11:00", subject: "Specialist", type: "Exam", title: "Specialist Mathematics Examination 2", duration: "11:45 am – 2:00 pm", source: vcaaSource },

  { date: "2026-03-13T09:00:00+11:00", subject: "Physics", type: "SAC", title: "Fields and motion" },
  { date: "2026-05-06T09:00:00+10:00", subject: "Physics", type: "SAC", title: "Electric power" },
  { date: "2026-06-05T09:00:00+10:00", subject: "Physics", type: "SAC", title: "Light and matter" },
  { date: "2026-09-15T09:00:00+10:00", subject: "Physics", type: "SAC", title: "Final Physics SAC" },
  { date: "2026-11-12T09:00:00+11:00", subject: "Physics", type: "Exam", title: "Physics examination", duration: "9:00 am – 11:45 am", source: vcaaSource },

  { date: "2026-03-06T09:00:00+11:00", subject: "Chemistry", type: "SAC", title: "Chemical analysis" },
  { date: "2026-04-01T09:00:00+11:00", subject: "Chemistry", type: "SAC", title: "Organic pathways" },
  { date: "2026-05-12T09:00:00+10:00", subject: "Chemistry", type: "SAC", title: "Energy and equilibrium" },
  { date: "2026-08-07T09:00:00+10:00", subject: "Chemistry", type: "SAC", title: "Practical investigation" },
  { date: "2026-09-16T09:00:00+10:00", subject: "Chemistry", type: "SAC", title: "Final Chemistry SAC" },
  { date: "2026-11-10T09:00:00+11:00", subject: "Chemistry", type: "Exam", title: "Chemistry examination", duration: "9:00 am – 11:45 am", source: vcaaSource },
];

const $ = (selector) => document.querySelector(selector);
const progressKey = "vce-focus-complete";
let completed = JSON.parse(localStorage.getItem(progressKey) || "[]");

const subjects = ["All subjects", ...new Set(assessments.map((item) => item.subject))];
subjectFilter.innerHTML = subjects.map((subject) => `<option value="${subject}">${subject}</option>`).join("");

dateStamp.textContent = new Intl.DateTimeFormat("en-AU", { dateStyle: "full", timeStyle: "short" }).format(new Date());

function formatDate(date) {
  return new Intl.DateTimeFormat("en-AU", { weekday: "short", day: "numeric", month: "short", year: "numeric" }).format(date);
}

function daysUntil(date) {
  return Math.ceil((date - new Date()) / 86400000);
}

function getFiltered() {
  const subject = subjectFilter.value;
  const type = typeFilter.value;
  return assessments
    .filter((item) => subject === "All subjects" || item.subject === subject)
    .filter((item) => type === "all" || item.type === type)
    .sort((a, b) => new Date(a.date) - new Date(b.date));
}

function save() {
  localStorage.setItem(progressKey, JSON.stringify(completed));
}

function render() {
  const filtered = getFiltered();
  const now = new Date();
  const next = assessments.map((item) => ({ ...item, realDate: new Date(item.date) })).filter((item) => item.realDate >= now).sort((a, b) => a.realDate - b.realDate)[0];

  nextCard.innerHTML = next ? `<p class="eyebrow">Next up</p><h2>${next.subject}</h2><p>${next.title}</p><strong>${formatDate(next.realDate)}</strong><span>${daysUntil(next.realDate)} days away</span>` : `<p class="eyebrow">Finished</p><h2>All done 🎉</h2><p>No upcoming dates remain.</p>`;

  const total = filtered.length;
  const done = filtered.filter((item) => completed.includes(item.date) || new Date(item.date) < now).length;
  const upcoming = filtered.filter((item) => new Date(item.date) >= now).length;
  stats.innerHTML = [
    ["Tracked", total],
    ["Completed", done],
    ["Upcoming", upcoming],
    ["Progress", `${total ? Math.round((done / total) * 100) : 0}%`],
  ].map(([label, value]) => `<article><span>${label}</span><strong>${value}</strong></article>`).join("");

  timeline.innerHTML = filtered.map((item) => {
    const date = new Date(item.date);
    const id = item.date;
    const isDone = completed.includes(id) || date < now;
    const sourceLink = item.source ? `<a href="${item.source}" target="_blank" rel="noreferrer">VCAA source</a>` : "";
    return `<article class="event ${isDone ? "done" : ""}">
      <input type="checkbox" ${isDone ? "checked" : ""} data-id="${id}" aria-label="Mark ${item.title} complete" />
      <div class="event-main"><span class="pill ${item.type.toLowerCase()}">${item.type}</span><h3>${item.subject}: ${item.title}</h3><p>${formatDate(date)}${item.duration ? ` • ${item.duration}` : ""}</p>${sourceLink}</div>
      <strong>${isDone ? "Done" : `${daysUntil(date)}d`}</strong>
    </article>`;
  }).join("");

  subjectGrid.innerHTML = [...new Set(assessments.map((item) => item.subject))].map((subject) => {
    const items = assessments.filter((item) => item.subject === subject);
    const doneCount = items.filter((item) => completed.includes(item.date) || new Date(item.date) < now).length;
    const percent = Math.round((doneCount / items.length) * 100);
    return `<article><h3>${subject}</h3><div class="bar"><span style="width:${percent}%"></span></div><p>${doneCount}/${items.length} complete</p></article>`;
  }).join("");
}

document.addEventListener("change", (event) => {
  if (!event.target.matches("input[type='checkbox'][data-id]")) return;
  const id = event.target.dataset.id;
  completed = event.target.checked ? [...new Set([...completed, id])] : completed.filter((item) => item !== id);
  save();
  render();
});

subjectFilter.addEventListener("change", render);
typeFilter.addEventListener("change", render);
resetBtn.addEventListener("click", () => { completed = []; save(); render(); });

render();
setInterval(render, 60000);
