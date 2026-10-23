// Deterministic signal and lifecycle checks; no audio device or packages required.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const {OnsetDetector, BeatSpring} = require('../docs/javascripts/music-rhythm.js');

for (const sampleRate of [44100, 48000]) {
  for (const bpm of [90, 120, 180]) {
    for (const gain of [0.1, 1]) {
      const detector = new OnsetDetector(sampleRate, 2048);
      const spectrum = new Float32Array(1024);
      const waveform = new Float32Array(2048);
      const period = 60000 / bpm;
      const hits = [];
      for (let now = 0; now < 10000; now += 32) {
        const age = now < 500 ? Infinity : (now - 500) % period;
        const envelope = Math.exp(-age / 70);
        for (let i = 0; i < spectrum.length; i++) {
          const frequency = i * sampleRate / 2048;
          const kick = 0.25 * envelope * Math.exp(-0.5 * ((frequency - 85) / 38) ** 2);
          const background = frequency > 300 && frequency < 1000 ? 0.002 : 0;
          const magnitude = gain * (kick + background);
          spectrum[i] = magnitude ? 20 * Math.log10(magnitude) : -Infinity;
        }
        waveform.fill(gain * (0.006 + 0.2 * envelope));
        if (detector.update(spectrum, waveform, now).onset) hits.push(now);
      }
      const expected = Math.ceil(9500 / period);
      assert.ok(Math.abs(hits.length - expected) <= 1, `${sampleRate} Hz, ${bpm} BPM, gain ${gain}: ${hits.length}/${expected}`);
      for (const hit of hits) assert.ok((hit - 500) % period < 65, `Off-beat onset at ${hit} ms`);
    }
  }
}

for (const silent of [false, true]) {
  const detector = new OnsetDetector(48000, 2048);
  const spectrum = new Float32Array(1024).fill(silent ? -Infinity : -35);
  const waveform = new Float32Array(2048).fill(silent ? 0 : 0.1);
  for (let now = 0; now < 5000; now += 32) {
    assert.equal(detector.update(spectrum, waveform, now).onset, false, 'Silence or sustained tone must not invent a beat');
  }
}

const spring = new BeatSpring();
for (let i = 0; i < 600; i++) {
  const scale = spring.step(i % 7 ? 1 / 60 : 1 / 15, i % 20 ? 0 : 1);
  assert.ok(scale.x >= 0.86 && scale.x <= 1.14);
  assert.ok(scale.y >= 0.842 && scale.y <= 1.158);
}
for (let i = 0; i < 180; i++) spring.step(1 / 60);
assert.ok(Math.abs(spring.position) < 0.0002, 'Movement must settle back to the original shape');
spring.reset();
assert.deepEqual(spring.step(1 / 60), {x: 1, y: 1});

async function checkAudioLifecycle() {
  const stats = {contexts: 0, sources: 0, resumes: 0, destinationConnections: 0};
  const active = {hasBeenActive: false, isActive: false};
  const context = {
    module: {exports: {}}, navigator: {userActivation: active},
    document: {hidden: false, addEventListener() {}},
    matchMedia: () => ({matches: false, addEventListener() {}}),
    MutationObserver: class {observe() {}},
    requestAnimationFrame: () => 1, cancelAnimationFrame() {}, addEventListener() {},
    AudioContext: class {
      constructor() {stats.contexts++; stats.context = this; this.state = context.initialState || 'running'; this.sampleRate = 48000; this.destination = {}; this.listener = null;}
      addEventListener(name, listener) {this.listener = listener;}
      resume() {
        stats.resumes++;
        if (!active.isActive) return new Promise(resolve => {
          this.resumeLater = () => {this.state = 'running'; resolve();};
        });
        this.state = 'running';
        this.resumeLater?.();
        return Promise.resolve();
      }
      createAnalyser() {return {frequencyBinCount: 1024};}
      createMediaElementSource() {
        stats.sources++;
        return {connect: (node) => {if (node === this.destination) stats.destinationConnections++;}};
      }
    }
  };
  vm.runInNewContext(fs.readFileSync(require.resolve('../docs/javascripts/music-rhythm.js'), 'utf8'), context);
  const audio = {paused: true, readyState: 4, addEventListener() {}};
  const pet = {hidden: false, dataset: {}};
  const image = {style: {removeProperty(name) {delete this[name];}}};
  const controller = context.module.exports.attach(audio, pet, image);
  assert.equal(await controller.prepare(), false, 'Untouched autoplay must keep the normal audio route');
  assert.equal(stats.contexts, 0);
  active.hasBeenActive = true;
  active.isActive = true;
  assert.equal(await controller.prepare(), true);
  assert.equal(await controller.prepare(), true);
  assert.equal(stats.contexts, 1);
  assert.equal(stats.sources, 1, 'All tracks must reuse one media-element source');
  assert.equal(stats.destinationConnections, 1, 'Audio must retain exactly one audible path');
  stats.context.state = 'suspended';
  assert.equal(await controller.prepare(), true);
  assert.equal(stats.resumes, 1, 'A suspended context must be resumable on a later play action');
  assert.equal(stats.sources, 1);
  audio.paused = false;
  controller.setEnabled(true);
  await controller.prepare();
  image.style.transform = 'scale(1.1, 0.9)';
  controller.setEnabled(false);
  assert.equal(pet.dataset.rhythm, 'disabled');
  assert.equal(image.style.transform, undefined, 'Turning off following must restore the original shape immediately');
  assert.equal(audio.paused, false, 'Turning off following must not pause the music');
  assert.equal(await controller.prepare(), true, 'An existing audible graph must stay usable with following off');
  assert.equal(stats.sources, 1);
  assert.equal(stats.destinationConnections, 1);
  controller.setEnabled(true);
  await controller.prepare();
  assert.equal(pet.dataset.rhythm, 'live');
  assert.equal(stats.sources, 1, 'Re-enabling following must reuse the audio graph');
  controller.setEnabled(false);
  const disabled = context.module.exports.attach(audio, pet, image, {enabled: false});
  assert.equal(await disabled.prepare(), false);
  assert.equal(stats.contexts, 1, 'A saved off setting must not create a new analysis graph');
  audio.paused = true;
  context.initialState = 'suspended';
  active.hasBeenActive = active.isActive = false;
  const autoplay = context.module.exports.attach({...audio, paused: false}, pet, image);
  const pending = autoplay.prepare();
  assert.equal(stats.sources, 1, 'Allowed autoplay must keep its audible route while the audio context is blocked');
  active.hasBeenActive = active.isActive = true;
  assert.equal(await autoplay.prepare(), true);
  assert.equal(await pending, true);
  assert.equal(stats.sources, 2, 'Unlocking a pending context must create only one source');
  assert.equal(stats.destinationConnections, 2);
  context.AudioContext = undefined;
  assert.equal(await context.module.exports.attach(audio, pet, image).prepare(), false);
  assert.equal(audio.paused, true, 'The analyser must not change the player state');
}

checkAudioLifecycle().then(() => console.log('Passed: 12 tempo/gain fixtures, silence, sustained tones, spring stability, audio routing and rhythm on/off.'))
  .catch(error => {console.error(error); process.exitCode = 1;});
