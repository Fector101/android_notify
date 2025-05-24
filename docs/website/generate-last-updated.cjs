const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");

try {
  const rawDate = execSync('git log -1 --format="%cd"').toString().trim();
  const date = new Date(rawDate);

  // Format to 12-hour format with full date
  const formatted = new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',      // e.g., May 24, 2025
    timeStyle: 'short',       // e.g., 9:05 PM
    hour12: true
  }).format(date);

  const outputPath = path.join(__dirname, "public", "last-updated.txt");
  fs.writeFileSync(outputPath, formatted, "utf8");

  console.log(`✅ Last updated written as: ${formatted}`);
} catch (err) {
  console.error("❌ Failed to write last updated date:", err);
}
