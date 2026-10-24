/* A persistent, separate shuffle bag for each playlist. */
((global) => {
  "use strict";
  class ShuffleBag {
    constructor(ids, saved = null) {
      this.ids = [...new Set(ids)];
      const valid = saved && Array.isArray(saved.known) && Array.isArray(saved.remaining);
      const known = new Set(valid ? saved.known : []);
      const remaining = new Set(valid ? saved.remaining : []);
      this.remaining = new Set(this.ids.filter((id) => !known.has(id) || remaining.has(id)));
    }
    consume(id) {
      this.remaining.delete(id);
    }
    next(previous = null) {
      if (!this.ids.length) return null;
      if (!this.remaining.size) this.remaining = new Set(this.ids);
      let candidates = [...this.remaining];
      // Avoid repeating the last song at the boundary between two rounds.
      if (candidates.length > 1) candidates = candidates.filter((id) => id !== previous);
      const id = candidates[Math.floor(Math.random() * candidates.length)];
      this.consume(id);
      return id;
    }
    snapshot() {
      return { known: this.ids, remaining: [...this.remaining] };
    }
  }
  global.TeaMusicShuffle = ShuffleBag;
  if (typeof module !== "undefined" && module.exports) module.exports = ShuffleBag;
})(globalThis);
