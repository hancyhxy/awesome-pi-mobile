// Build README.md from data/projects.json.
//   node scripts/build.mjs           use the star counts saved in the data
//   node scripts/build.mjs --stars   refresh star counts from GitHub first (needs the gh CLI)
// Order inside a section: open-source projects by stars, then the others by name.
import { readFileSync, writeFileSync } from "node:fs";
import { execFileSync } from "node:child_process";

const root = new URL("..", import.meta.url).pathname;
const file = root + "data/projects.json";
const db = JSON.parse(readFileSync(file, "utf8"));

if (process.argv.includes("--stars")) {
  for (const p of db.projects.filter(p => p.repo)) {
    try { p.stars = Number(execFileSync("gh", ["api", `repos/${p.repo}`, "-q", ".stargazers_count"], { encoding: "utf8" }).trim()); }
    catch { console.warn("no stars for", p.repo); }
  }
  db.updated = new Date().toISOString().slice(0, 10);
  writeFileSync(file, JSON.stringify(db, null, 2) + "\n");
}

const link = p => p.url || `https://github.com/${p.repo}`;
const star = p => (p.repo ? (p.stars != null ? `⭐ ${p.stars >= 1000 ? (p.stars / 1000).toFixed(1) + "k" : p.stars}` : "open source") : "—");
const order = (a, b) => (b.repo ? 1 : 0) - (a.repo ? 1 : 0) || (b.stars || 0) - (a.stars || 0) || a.name.localeCompare(b.name);
const anchor = t => t.toLowerCase().replace(/[^a-z0-9 -]/g, "").trim().replace(/ +/g, "-");

// A card for each project with a screenshot: picture, name, stars, one line, and where the picture comes from.
const card = p => `<td width="33%" valign="top"><a href="${link(p)}"><img src="${p.shot}" alt="${p.name} on a phone" width="100%"></a><br><b><a href="${link(p)}">${p.name}</a></b>${p.ours ? " ¹" : ""} ${p.repo ? "· " + star(p) : ""}<br>${p.what}<br><sub>Screenshot: <a href="${p.shotFrom || link(p)}">${p.ours ? "sample" : "from the project"}</a></sub></td>`;
const cards = list => { const withShot = list.filter(p => p.shot); if (!withShot.length) return ""; const rows = []; for (let i = 0; i < withShot.length; i += 3) { const cells = withShot.slice(i, i + 3).map(card); while (cells.length < 3) cells.push(`<td width="33%"></td>`); rows.push(`<tr>${cells.join("")}</tr>`); } return `<table>\n${rows.join("\n")}\n</table>\n\n`; };

const sections = db.sections.map(s => {
  const list = db.projects.filter(p => p.section === s.id).sort(order);
  const rows = list
    .map(p => `| [${p.name}](${link(p)})${p.ours ? " ¹" : ""} | ${p.platforms} | ${p.reach} | ${star(p)} | ${p.what} |`);
  return `## ${s.name}\n\n${s.intro}\n\n${cards(list)}| Project | Platforms | How the phone reaches Pi | Stars | What you get |\n|---|---|---|---|---|\n${rows.join("\n")}\n`;
}).join("\n");

const n = db.projects.length;
const readme = `# Awesome Pi Mobile

<img src="media/wall.png" alt="Screenshots of Pi phone apps and web UIs side by side" width="100%">

Every way to use the [Pi coding agent](https://github.com/earendil-works/pi) from your phone: native apps, phone-first web apps, notifications, multi-agent clients and plain SSH.

Pi runs in a terminal on your computer and has no official phone app. These ${n} projects keep Pi where your code is and bring the session to your pocket: follow the work, answer its questions, steer it or start a new run.

Updated ${db.updated}. Star counts come from GitHub on that date.

## Contents

${db.sections.map(s => `- [${s.name}](#${anchor(s.name)}) (${db.projects.filter(p => p.section === s.id).length})`).join("\n")}
- [Choosing one](#choosing-one)
- [Guides and discussions](#guides-and-discussions)
- [Contributing](#contributing)

${sections}
## Choosing one

| If you want | Look at |
|---|---|
| No port, no VPN, no server to run | Projects that use a relay: Hey Atu, Remote Pi, Paseo, pi.dev remote |
| Everything open source and self-hosted | Pi Pocket, pi-agent-dashboard, pi-mobile (web), pi pod |
| Only to know when Pi needs you | pi-knock, Pi Pulse |
| Android | Remote Pi, Pi Mobile (Android), π Remote, Muxflow |
| More than coding from the phone | Hey Atu (to-dos, scheduled updates, a wiki) |
| Nothing new to install | SSH + mosh + tmux |

A remote client can make commands run on your computer. Check how each one authenticates and whether its relay can read your messages before you pair it.

## Guides and discussions

${db.guides.map(g => `- [${g.name}](${g.url}) — ${g.by}`).join("\n")}

## Contributing

Know a project that is missing, or a detail that changed? Open an issue or a pull request. Edit [\`data/projects.json\`](data/projects.json) and run \`node scripts/build.mjs\`; the README is generated from it.

An entry needs to work with Pi from a phone and be available to try today, or say clearly when it is coming.

---

¹ Hey Atu is made by the maintainers of this list. It is listed with the same fields as every other project. Its picture is sample content; the iPhone app is coming soon.

Screenshots come from each project's App Store page, README or site, and belong to their owners. Want yours changed or removed? Open an issue.

[CC0](LICENSE): to the extent possible under law, the authors have waived all copyright to this list.
`;
writeFileSync(root + "README.md", readme);
console.log(`README.md: ${n} projects in ${db.sections.length} sections`);
