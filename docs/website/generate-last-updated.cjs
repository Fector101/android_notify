// const { execSync } = require("child_process");
const fs = require("fs");
const path = require("path");
  

try {
  // Use Vercel's auto-injected commit timestamp
  const rawDate = process.env.VERCEL_GIT_COMMIT_TIMESTAMP || new Date().toString();
  // const rawDate = execSync('git log -1 --format="%cd"').toString().trim();
 
  const date = new Date(rawDate);

  const formatted = new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium", // e.g. Jul 17, 2025
    timeStyle: "short",  // e.g. 2:45 PM
    hour12: true
  }).format(date);

  const outputPath = path.join(__dirname, "public", "last-updated.txt");
  fs.writeFileSync(outputPath, formatted, "utf8");

  console.log(`✅ Last updated written as: ${formatted}`);
} catch (err) {
  console.error("❌ Failed to write last updated date:", err);
}
