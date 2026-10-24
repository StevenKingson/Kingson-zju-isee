const assert = require("node:assert/strict");
const ShuffleBag = require("../../docs/javascripts/music-shuffle.js");

for (const size of [1, 2, 20, 21]) {
  const ids = Array.from({ length: size }, (_, i) => `song-${i}`);
  let bag = new ShuffleBag(ids);
  let previous = null;
  for (let round = 0; round < 30; round++) {
    const heard = new Set();
    for (let i = 0; i < size; i++) {
      const next = bag.next(previous);
      assert(!heard.has(next), "Every song must be selected before a repeat");
      if (size > 1) assert.notEqual(next, previous, "No consecutive repeats across rounds");
      heard.add(next);
      previous = next;
      // Model a refresh or a switch away and back after every song.
      bag = new ShuffleBag(ids, JSON.parse(JSON.stringify(bag.snapshot())));
    }
    assert.equal(heard.size, size);
  }
}
const manual = new ShuffleBag(["a", "b", "c"]);
manual.consume("b");
assert.deepEqual(new Set([manual.next("b"), manual.next()]), new Set(["a", "c"]));
const updated = new ShuffleBag(["a", "c", "new"], { known: ["a", "b", "c"], remaining: ["b", "c"] });
assert.deepEqual(new Set([updated.next(), updated.next()]), new Set(["c", "new"]));
assert.equal(new ShuffleBag([]).next(), null);
assert.equal(new ShuffleBag(["a"], { remaining: "invalid" }).next(), "a");
const first = new ShuffleBag(["a", "b"]);
const second = new ShuffleBag(["c", "d"]);
first.next();
assert.equal(second.snapshot().remaining.length, 2, "Playlists keep independent progress");
console.log("Passed: nonrepeating rounds, reloads, manual selection, catalogue updates and independent playlists.");
