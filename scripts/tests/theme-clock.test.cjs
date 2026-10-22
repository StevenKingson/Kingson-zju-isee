const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const source = fs.readFileSync(path.resolve(__dirname, "../../docs/javascripts/theme-clock.js"), "utf8");

function createClock(hour, minute = 0, second = 0, options = {}) {
  let now = new Date(2026, 9, 22, hour, minute, second).getTime();
  const listeners = {};
  const saved = new Map([["tea-theme", "day"]]); // Legacy choices must not disable the clock.
  const document = { documentElement: { dataset: {} }, body: { dataset: {} },
    addEventListener(name, listener) { listeners[name] = listener; } };
  const window = { addEventListener(name, listener) { listeners[name] = listener; },
    dispatchEvent(event) { listeners[event.type]?.(event); } };
  class ClockDate extends Date {
    constructor(...args) { if (args.length) super(...args); else super(now); }
    static now() { return now; }
  }
  vm.runInNewContext(source, { window, document, Date: ClockDate,
    localStorage: {
      getItem(key) { if (options.blockStorage) throw Error("blocked"); return saved.get(key) ?? null; },
      setItem(key, value) { if (options.blockStorage) throw Error("blocked"); saved.set(key, value); }
    },
    CustomEvent: class { constructor(type, init) { this.type = type; this.detail = init.detail; } },
    setTimeout() { return 1; }, clearTimeout() {} });
  return { controller: window.teaThemeClock, document, listeners,
    advance(day, hour, minute = 0) { now = new Date(2026, 9, day, hour, minute).getTime(); window.teaThemeClock.sync(); } };
}

for (const [hour, minute, second, expected] of [
  [5, 59, 59, "night"], [6, 0, 0, "day"], [17, 59, 59, "day"], [18, 0, 0, "night"]
]) {
  const clock = createClock(hour, minute, second);
  assert.equal(clock.controller.theme, expected, `Local ${hour}:${minute}:${second}`);
  assert.equal(clock.document.body.dataset.mdColorScheme, expected === "day" ? "default" : "slate");
}
const daytime = createClock(12);
daytime.controller.setManualTheme("night");
daytime.advance(22, 17, 59);
assert.equal(daytime.controller.theme, "night", "Keep manual choice for the current period");
daytime.advance(22, 18);
daytime.advance(23, 6);
assert.equal(daytime.controller.theme, "day", "Expired override must not survive the next morning");
const overnight = createClock(23);
overnight.controller.setManualTheme("day");
overnight.advance(23, 0);
assert.equal(overnight.controller.theme, "day", "Midnight must not end the current night period");
overnight.advance(23, 6);
overnight.advance(23, 18);
assert.equal(overnight.controller.theme, "night", "Clock resumes after an override expires");
const privateMode = createClock(12, 0, 0, { blockStorage: true });
privateMode.controller.setManualTheme("night");
privateMode.advance(22, 13);
assert.equal(privateMode.controller.theme, "night", "Manual switching works without localStorage");
privateMode.advance(23, 6);
assert.equal(privateMode.controller.theme, "day", "Automatic switching works without localStorage");
console.log("Passed: local 06:00/18:00 boundaries, manual choice expiry, midnight continuity, legacy preference, blocked storage.");
