// Small date helpers. Dates travel through the API as "YYYY-MM-DD" strings.

// Today's date in the user's time zone, as "YYYY-MM-DD".
// (The "en-CA" locale happens to format dates exactly like that.)
export function todayString() {
  return new Date().toLocaleDateString("en-CA");
}

// "2026-11-06" -> "Fri, Nov 6"
export function formatDate(isoDate) {
  // Adding a time makes JavaScript read the date in local time. Without it,
  // "2026-11-06" means midnight UTC, which is Nov 5 in the Americas.
  return new Date(`${isoDate}T00:00:00`).toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

// "YYYY-MM-DD" strings sort like dates, so plain < works.
export function isOverdue(isoDate, today = todayString()) {
  return Boolean(isoDate) && isoDate < today;
}
