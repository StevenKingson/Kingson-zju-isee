/* Real-time musical onsets, with a damped spring for the companion's movement. */
((global) => {
  "use strict";
  const clamp = (value, low, high) => Math.max(low, Math.min(high, value));

  class OnsetDetector {
    constructor(sampleRate, fftSize) {
      this.previous = new Float32Array(fftSize / 2);
      this.weights = new Float32Array(fftSize / 2);
      this.bassBins = [];
      this.weightSum = 0;
      for (let i = 0; i < this.weights.length; i++) {
        const frequency = i * sampleRate / fftSize;
        const weight = frequency < 40 || frequency > 6000 ? 0
          : frequency < 220 ? 2.5 : frequency < 2000 ? 0.65 : 0.2;
        this.weights[i] = weight;
        this.weightSum += weight;
        if (frequency >= 40 && frequency < 220) this.bassBins.push(i);
      }
      this.reset();
    }
    reset() {
      this.previous.fill(0);
      this.frames = 0;
      this.level = this.bass = this.previousBass = 0;
      this.mean = this.variance = 0;
      this.lastTime = this.lastOnset = -Infinity;
    }
    update(spectrum, waveform, now) {
      const elapsed = Number.isFinite(this.lastTime) ? clamp(now - this.lastTime, 1, 100) : 32;
      this.lastTime = now;
      let flux = 0, level = 0, bass = 0, rms = 0;
      for (let i = 0; i < this.weights.length; i++) {
        if (!this.weights[i]) continue;
        const magnitude = Number.isFinite(spectrum[i]) ? Math.pow(10, spectrum[i] / 20) : 0;
        flux += this.weights[i] * Math.max(0, magnitude - this.previous[i]);
        level += this.weights[i] * magnitude;
        this.previous[i] = magnitude;
      }
      for (const i of this.bassBins) bass += this.previous[i];
      bass /= Math.max(1, this.bassBins.length);
      level /= this.weightSum;
      flux /= this.weightSum;
      for (const sample of waveform) rms += sample * sample;
      rms = Math.sqrt(rms / Math.max(1, waveform.length));
      if (!this.frames) { this.level = level; this.bass = bass; this.previousBass = bass; }
      // Relative spectral flux makes the threshold adapt to different mastering levels.
      const score = clamp(0.65 * flux / Math.max(0.00005, this.level)
        + 0.35 * Math.max(0, bass - this.previousBass) / Math.max(0.00005, this.bass), 0, 6);
      const threshold = this.mean + Math.max(0.12, 1.35 * Math.sqrt(this.variance));
      const onset = this.frames >= 8 && rms > 0.002 && score > threshold && now - this.lastOnset >= 240;
      const strength = onset ? clamp(0.35 + 0.4 * (score - threshold) / Math.max(0.15, threshold), 0.35, 1) : 0;
      if (onset) this.lastOnset = now;
      const energyAlpha = 1 - Math.exp(-elapsed / 650);
      const statisticsAlpha = 1 - Math.exp(-elapsed / 900);
      this.level += energyAlpha * (level - this.level);
      this.bass += energyAlpha * (bass - this.bass);
      const difference = score - this.mean;
      this.mean += statisticsAlpha * difference;
      this.variance += statisticsAlpha * (difference * difference - this.variance);
      this.previousBass = bass;
      this.frames++;
      return { onset, strength, rms };
    }
  }

  class BeatSpring {
    constructor() { this.reset(); }
    reset() { this.position = this.velocity = 0; }
    step(seconds, strength = 0) {
      this.velocity = clamp(this.velocity + strength * 6.5, -9, 9);
      // Substeps keep slow frames from destabilizing the spring.
      let remaining = clamp(seconds, 0, 0.05);
      while (remaining > 0) {
        const dt = Math.min(remaining, 1 / 120);
        this.velocity += (-160 * this.position - 9 * this.velocity) * dt;
        this.position = clamp(this.position + this.velocity * dt, -0.35, 0.35);
        remaining -= dt;
      }
      if (Math.abs(this.position) < 0.0001 && Math.abs(this.velocity) < 0.001) this.reset();
      return { x: 1 + this.position * 0.4, y: 1 - this.position * 0.45 };
    }
  }

  function attach(audio, pet, image, { enabled = true } = {}) {
    let followEnabled = Boolean(enabled);
    const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)");
    const spring = new BeatSpring();
    let context, source, analyser, detector, spectrum, waveform, preparation;
    let frame = 0, lastFrame = 0, lastSample = -Infinity, beatCount = 0;
    const canAnimate = () => followEnabled && !pet.hidden && !document.hidden && !reducedMotion.matches
      && !audio.paused && !audio.ended && audio.readyState >= 3 && !audio.seeking;
    function resetPose() {
      spring.reset();
      image.style.removeProperty("transform");
    }
    function stop() {
      cancelAnimationFrame(frame);
      frame = lastFrame = 0;
      resetPose();
      pet.dataset.rhythm = followEnabled ? "idle" : "disabled";
    }
    function tick(now) {
      if (!canAnimate() || context?.state !== "running") { stop(); return; }
      const seconds = lastFrame ? (now - lastFrame) / 1000 : 1 / 60;
      lastFrame = now;
      let strength = 0;
      // FFT at about 30 Hz; the inexpensive spring still renders every animation frame.
      if (now - lastSample >= 30) {
        lastSample = now;
        analyser.getFloatFrequencyData(spectrum);
        analyser.getFloatTimeDomainData(waveform);
        const result = detector.update(spectrum, waveform, now);
        if (result.onset) {
          strength = result.strength;
          pet.dataset.rhythmBeats = String(++beatCount);
        }
      }
      if (pet.classList.contains("is-dragging")) resetPose();
      else {
        const scale = spring.step(seconds, strength);
        image.style.transform = `scale(${scale.x.toFixed(5)}, ${scale.y.toFixed(5)})`;
      }
      frame = requestAnimationFrame(tick);
    }
    function sync() {
      if (!analyser || context.state !== "running" || !canAnimate()) { stop(); return; }
      if (frame) return;
      detector.reset();
      lastSample = -Infinity;
      pet.dataset.rhythm = "live";
      frame = requestAnimationFrame(tick);
    }
    async function prepare() {
      const AudioContext = global.AudioContext || global.webkitAudioContext;
      // Once routed through Web Audio, retain that audible path even with motion off.
      if (!AudioContext || ((!followEnabled || reducedMotion.matches) && !source)) return false;
      // Autoplay must not be rerouted into a suspended context and become silent.
      if (!context && audio.paused && navigator.userActivation && !navigator.userActivation.hasBeenActive) return false;
      if (preparation) {
        // A previous autoplay attempt can be waiting for the next user gesture.
        if (context.state !== "running" && navigator.userActivation?.isActive) {
          void context.resume().catch(() => {});
        }
        return preparation;
      }
      preparation = (async () => {
        try {
          if (!context) {
            context = new AudioContext();
            context.addEventListener("statechange", sync);
          }
          if (context.state !== "running") await context.resume();
          if (context.state !== "running") return false;
          if (!source && (!followEnabled || reducedMotion.matches)) return false;
          if (!source) {
            analyser = context.createAnalyser();
            analyser.fftSize = 2048;
            analyser.smoothingTimeConstant = 0.25;
            detector = new OnsetDetector(context.sampleRate, analyser.fftSize);
            spectrum = new Float32Array(analyser.frequencyBinCount);
            waveform = new Float32Array(analyser.fftSize);
            source = context.createMediaElementSource(audio);
            // Keep an unfiltered audible path; the analyser is a parallel read-only tap.
            source.connect(context.destination);
            source.connect(analyser);
          }
          sync();
          return true;
        } catch {
          // A missing analyser must never prevent ordinary music playback.
          stop();
          return false;
        }
      })().finally(() => { preparation = null; });
      return preparation;
    }
    audio.addEventListener("playing", () => { sync(); void prepare(); });
    for (const name of ["pause", "ended", "waiting", "emptied", "error", "seeking"]) {
      audio.addEventListener(name, stop);
    }
    audio.addEventListener("seeked", sync);
    audio.addEventListener("loadstart", () => {
      stop();
      beatCount = 0;
      pet.dataset.rhythmBeats = "0";
    });
    document.addEventListener("visibilitychange", sync);
    document.addEventListener("pointerdown", () => {
      if (!audio.paused) void prepare();
    }, { passive: true });
    reducedMotion.addEventListener("change", sync);
    new MutationObserver(sync).observe(pet, { attributes: true, attributeFilter: ["hidden"] });
    global.addEventListener("pagehide", stop);
    pet.dataset.rhythmBeats = "0";
    pet.dataset.rhythm = followEnabled ? "idle" : "disabled";
    function setEnabled(value) {
      followEnabled = Boolean(value);
      sync();
      if (followEnabled && !audio.paused) void prepare();
    }
    return { prepare, setEnabled };
  }

  const api = { OnsetDetector, BeatSpring, attach };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else global.TeaMusicRhythm = api;
})(typeof window === "undefined" ? globalThis : window);
