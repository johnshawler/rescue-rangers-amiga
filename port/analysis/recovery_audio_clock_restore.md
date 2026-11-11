# Restore the additive callback-clock correction

Restore only the explicit public_allowlist and dependencies in
recovery_audio_clock_manifest.json, plus that manifest. The closure is flat;
do not recursively expand historical manifests. Preserve the old nominal-clock
reports as superseded evidence. Never package ROM/firmware, targets, PCM, captured
RAM, screenshots, original disassembly or unrelated experimental Paula source.

Source-only checks need the existing Python/NumPy dependencies, not cartridge,
firmware, emulator, compiler or original-code oracle:

```
export PYTHONDONTWRITEBYTECODE=1
export OPENBLAS_NUM_THREADS=1
bash port/tools/recovery_audio_clock_public.sh
```

Private revalidation uses the FOUR EXISTING immutable capture directories, the
approved original cartridge for original-derived gameplay window selection, and
the approved core/source/frontend identities. It does not start an emulator or
write inside any capture. Choose a fresh separate output directory:

```
python port/tests/recovery_audio_clock_verify.py --output port/build/audio-clock-fresh
```

If running from an isolated source-only restoration, explicitly point to the
existing read-only inputs and tool installation:

```
python port/tests/recovery_audio_clock_verify.py \
  --capture-root /path/to/original/recovery/port/build \
  --rom /path/to/original/recovery/input/rescue-rangers-europe.nes \
  --core-root /path/to/amiga-recovery-tools/libretro-uae \
  --frontend /path/to/original/recovery/port/build/experimental-direct-paula/headless \
  --output /path/to/new/separate/audio-clock-results
```

Do not copy corrected reports over stage-target-noise-pcm.json,
stage-background-noise-pcm.json, play-target-pcm.json or any other historical
result. Every output embeds the immutable capture identities, model/source/log
attestation, corrected boundary indices, historical omitted scale displacement,
capture-specific endpoint/quantization bound, unchanged criteria and scope.

Unsupported tool identities, rates, sample formats, configurations, clock changes
or captures fail closed. This bounded restore supports the four hash-pinned
captures only; new capture qualification requires explicit review, not guessed
clock constants. The approved cartridge is independently hash-checked by the
unchanged original-code oracle. This layer never alters hardware-equivalent
performance conversion or authorizes a fresh capture/publication.
