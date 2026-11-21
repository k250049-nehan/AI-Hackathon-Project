---
name: Last Mile — Public Help Window (PROTOTYPE)
description: An Urdu-first, voice-led service counter on a black field with gray foreground surfaces and drawn SVG icons.
colors:
  paper: "#000000"
  card: "#1b1f1c"
  surface: "#242a26"
  input-bg: "#101310"
  ink: "#f2f6f3"
  ink-soft: "#d8e3dc"
  muted: "#9fb0a6"
  green: "#22b56a"
  green-deep: "#178a4f"
  green-active: "#116b3e"
  green-wash: "#12281e"
  green-wash-hover: "#193526"
  on-green: "#04190f"
  amber: "#d98a1f"
  amber-wash: "#2a1d08"
  amber-line: "#6b4a16"
  amber-ink: "#ffcf8a"
  on-amber: "#1a1005"
  red: "#ff6b5e"
  red-wash: "#2a1210"
  red-ink: "#ffb3aa"
  on-red: "#1a0806"
  line: "#303a34"
  line-strong: "#4a6556"
  strip-bg: "#0a0f0c"
  strip-ink: "#f4e2b8"
  strip-icon: "#ffd97a"
  online: "#a9e6c2"
  offline: "#ffb4a8"
  progress-track: "#24382c"
  meter-track: "#2b352f"
  focus: "rgba(34, 181, 106, .42)"
  selection: "#22b56a"
  selection-ink: "#04190f"
  scrollbar: "#3a4b41"
  shadow: "0 3px 16px rgba(0, 0, 0, .55)"
  mic-shadow: "0 6px 22px rgba(0, 0, 0, .55)"
typography:
  display:
    fontFamily: '"Noto Nastaliq Urdu", "Segoe UI", Tahoma, sans-serif'
    fontSize: "32px"
    fontWeight: 800
    lineHeight: 1.15
  status-title:
    fontFamily: '"Noto Nastaliq Urdu", "Segoe UI", Tahoma, sans-serif'
    fontSize: "18px"
    fontWeight: 700
    lineHeight: 1.55
  body:
    fontFamily: '"Noto Nastaliq Urdu", "Segoe UI", Tahoma, sans-serif'
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.55
  label:
    fontFamily: '"Noto Nastaliq Urdu", "Segoe UI", Tahoma, sans-serif'
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 1.55
  mic:
    fontFamily: '"Noto Nastaliq Urdu", "Segoe UI", Tahoma, sans-serif'
    fontSize: "23px"
    fontWeight: 800
    lineHeight: 1.55
  small:
    fontFamily: '"Noto Nastaliq Urdu", "Segoe UI", Tahoma, sans-serif'
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.55
  case-id:
    fontFamily: '"Noto Nastaliq Urdu", "Segoe UI", Tahoma, sans-serif'
    fontSize: "15px"
    fontWeight: 700
    lineHeight: 1.55
rounded:
  card: "14px"
  control: "10px"
  case-row: "12px"
  seal: "12px"
  brand-mark: "8px"
  status-icon: "10px"
  case-mark: "9px"
  progress: "8px"
  meter: "6px"
  toast: "10px"
spacing:
  gutter: "16px"
  gutter-wide: "24px"
  card-padding: "20px"
  login-padding: "26px"
  mic-height: "96px"
  button-height: "50px"
  icon-button: "46px"
  chip-height: "52px"
  nav-item: "56px"
  list-gap: "10px"
  section-gap: "24px"
components:
  primary-button:
    backgroundColor: "{colors.green}"
    textColor: "{colors.on-green}"
    rounded: "{rounded.control}"
    minHeight: "{spacing.button-height}"
  mic-button:
    backgroundColor: "{colors.green}"
    textColor: "{colors.on-green}"
    rounded: "{rounded.card}"
    minHeight: "{spacing.mic-height}"
  card:
    backgroundColor: "{colors.card}"
    borderColor: "{colors.line}"
    rounded: "{rounded.card}"
    padding: "{spacing.card-padding}"
  status-card:
    backgroundColor: "{colors.green-wash}"
    borderColor: "{colors.line-strong}"
    rounded: "{rounded.card}"
  case-row:
    backgroundColor: "{colors.card}"
    borderColor: "{colors.line}"
    rounded: "{rounded.case-row}"
    padding: "14px"
  bottom-nav:
    backgroundColor: "{colors.card}"
    borderColor: "{colors.line}"
    minHeight: "{spacing.nav-item}"
---

# Design System: Last Mile — Public Help Window (PROTOTYPE)

## Overview

**North Star: the public help window.** Last Mile presents itself as a service counter that happens to be powered by careful automation: plainly signed, generously printed, and always watched by a human who makes the final call. The screen is a small, centered counter — not a dashboard, not a chat toy, not a marketing page.

The interface uses **drawn inline SVG icons** and no emoji anywhere. In the dark edition, the page field is true black (`#000000`) and every foreground surface — cards, top bar, chips, case rows, navigation, and icon buttons — is a neutral dark gray (`#1b1f1c` or `#242a26`). Green is reserved for action and progress; amber for listening and voice-capability notices; red for blocked states and errors. The result reads as a night-service counter: high contrast, low glare, and unmistakable hierarchy.

The prototype strip is the topmost permanent element. The signed-in counter is split into **three separate pages — Home, Cases, and Help** — switched by the sticky bottom navigation and addressed by hash routes (`#/home`, `#/cases`, `#/help`). Only one page is mounted at a time; the back/forward buttons work. Home holds the status ticket, the single microphone action, seven labelled claim fields, and a separate request box. Cases holds the case list. Help holds the question form and a voice-diagnostics panel. **The language toggle is available on both the sign-in card and the counter top bar**, so a citizen can choose Urdu or English before logging in and keep that choice afterwards. Urdu is the default and the layout mirrors with `dir="rtl"`.

## Color

- **Paper** `#000000` — the only page background.
- **Card** `#1b1f1c` — cards, top bar, case rows, bottom navigation.
- **Surface** `#242a26` — chips, icon buttons, secondary buttons.
- **Input** `#101310` — fields and the help answer; slightly darker than Card for a recessed feel.
- **Ink** `#f2f6f3`, **Ink Soft** `#d8e3dc`, **Muted** `#9fb0a6` — three text levels, all ≥7:1 on Card.
- **Green** `#22b56a` — the only action color, paired with near-black **On Green** `#04190f` text (6.8:1). Hover `#178a4f`, active `#116b3e`.
- **Green Wash** `#12281e` — status ticket, icon wells, active navigation, hover fills.
- **Amber** `#d98a1f` with **Amber Wash** `#2a1d08` and **Amber Ink** `#ffcf8a` — listening state and the voice-capability notice only.
- **Red** `#ff6b5e` with **Red Wash** `#2a1210` — blocked/rejected states and error toasts only.
- **Line** `#303a34` / **Line Strong** `#4a6556` — resting and hover borders.
- **Strip** `#0a0f0c` with `#f4e2b8` text and `#ffd97a` icon — permanent prototype honesty.
- **Online** `#a9e6c2`, **Offline** `#ffb4a8` — network badge states.

### Rules

**Black Field, Gray Counter.** The page is never tinted; only the foreground surfaces are gray. Do not introduce a second page background color.

**One Green Rule.** Green invites action. If a control is not the next step, it is gray, wash, or outlined.

**Fixed Signals.** Amber means listening or a voice-capability notice; red means stopped/blocked/error; near-black with gold means prototype notice. None are decorative.

## Typography

One family throughout: `"Noto Nastaliq Urdu", "Segoe UI", Tahoma, sans-serif`. Nastaliq gives Urdu correct ligatures; the Latin fallback stays compact.

- **Display** — 32px / 800 / 1.15: brand name on the sign-in card.
- **Status title** — 18px / 700 / 1.55: "Your progress".
- **Body** — 17px / 400 / 1.55: prompts, inputs, status, buttons, chips. Drops to 16px below 360px.
- **Label** — 15px / 700: fields, section labels, pills.
- **Mic** — 23px / 800: the microphone prompt.
- **Small** — 14px: strip, badge, hints, confidence, navigation, voice note.
- **Case ID** — 15px / 700: case number inside a case row.

No user-facing text is below 14px. Latin text is uppercased only for role and strip labels; Urdu copy is never transformed.

## Icons

All icons are inline `<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">` with `fill: none`, `stroke: currentColor`, `stroke-width: 1.8`, round caps and joins. Default size is 20px; the mic is 32px, status icon 24px, seal 28px, and navigation 21px.

| State / action | Drawn glyph |
| --- | --- |
| Approved | check in a green wash well |
| Blocked / rejected / auto-blocked | cross in a red wash well |
| Needs information / human review | information circle in amber wash |
| Waiting for officer / escalated | clock in amber wash |
| New / assigned / neutral | clipboard |
| Speak | microphone with stand |
| Sign in / Send / Ask | right arrow |
| Refresh / Sync | circular arrows |
| Language | globe with meridian, on both screens |
| Sign out | door and arrow |
| Help | question circle |
| Prototype notice | warning triangle |

Icons are always paired with localized text or an `aria-label`; they never carry meaning alone.

## Layout

A centered column of `max-width: 720px` sits on black. Gutter is 16px, widening to 24px at ≥700px. The prototype strip is full-bleed and sticky at `top: 0`; the top bar sticks at `top: 38px` so it never covers the strip. The bottom navigation is sticky at the bottom.

- Sign-in: one gray card at `margin-top: 5vh`, with a seal, brand, **language toggle**, divider, form, and a wrapping grid of role chips.
- Persistent counter chrome: top bar above the page area, sticky bottom navigation below it.
- **Home** (`#/home`): status ticket → intake (mic + typed fallback) → claim details → separate request box → actions. Login always lands here.
- **Cases** (`#/cases`): a 10px-gap list of 14px-padded rows with a 38px status well, case number, status pill, and confidence meter; its own refresh button shares `refreshDashboard()`.
- **Help** (`#/help`): a question card with its answer area, then a voice-setup card with Check voices / Test Urdu and a live diagnostics line.

A `.view` is hidden with `hidden` and shown with `.active`; `applyView()` reads the hash, toggles the three views, and sets the active nav item. Logging in forces Home; logging out clears the hash.

- Status ticket: a 44px icon well, flexible copy, a 9px progress track, and a read-aloud button.
- Intake: full-width 96px mic, centered hint, optional voice note, a two-column claim-details grid (one column below 560px), separate request textarea, then Send (flex 2) and Refresh (flex 1).

Direction is set from `state.lang`; every margin, icon, and arrow follows logical properties or RTL mirroring. No control is pinned to a physical side.

### Status rendering

The status line is dynamic and must never carry a static `data-i18n` attribute. `renderStatus()` reads `state.statusCase`, `state.statusError`, and `state.statusLoading`, so toggling language translates the live case status instead of resetting it to "Loading…".

## Elevation & Shape

Shadows are shallow and neutral: cards use `0 3px 16px rgba(0,0,0,.55)`; the microphone uses a deeper offset neutral shadow `0 6px 22px rgba(0,0,0,.55)`; the toast uses the deepest neutral shadow. No colored glow is used on the dark field. Buttons, chips, inputs, rows, and navigation are separated with borders and tints, not shadows.

Cards and the mic use 14px corners; controls use 10px; case rows 12px; the brand seal 12px; the brand mark 8px; progress 8px; confidence meter 6px; toast 10px. Focus is a 3px semi-transparent green outline, never a shadow.

## Components

### Primary Button & Mic

Both use Green `#22b56a` with near-black 800-weight text. Primary is at least 50px tall; the mic is 96px tall and 23px text. Hover deepens to Green Deep, active darkens further, disabled is 55% opacity with a rotating border spinner. While listening, the mic switches to Amber and pulses gently; `prefers-reduced-motion` removes the pulse.

A full-width **Stop recording** button appears directly beneath the mic only while listening. It uses Red `#ff6b5e` with a filled square SVG glyph and near-black text, so the red signal is reserved for "stop now" and blocked/error states. Recognition is continuous, so this button is the normal completion signal: pressing it calls `recognition.stop()`, which keeps the captured audio and asks for a final result. `setListening()` / `updateMicControls()` own the three-way state (idle, listening, submitting) so the mic cannot be started twice and the stop button never lingers.

**Live level meter.** Microphone access is requested and a Web Audio `AnalyserNode` is opened *before* recognition starts. Nine bars react to RMS volume while listening, turning amber when loud, with a localized line that says "Microphone is on — speak now" until voice is detected, then "Your voice is coming through." Peak level is retained until the next recording so the app can tell whether audio was actually captured. The stream, context, and animation frame are released on stop, result, error, end, and logout.

**Voice-led completion.** The microphone is the primary intake path, not just a dictation toy. Starting it opens a `voiceSession`; as the citizen speaks, recognized words are written to the request textarea and `fillClaimFields()` fills every labelled field it can recognize. When the red Stop button ends that first recording, `continueVoiceCompletion()` validates the form and looks for the first missing required field. It asks one specific, localized question ("Please tell me your CNIC number." / "براہِ کرم اپنا شناختی نمبر بتائیں۔") through a toast, a live mic-hint line, and TTS when an honest voice exists. `speakThen()` starts the follow-up recording after the prompt finishes — or immediately when no Urdu voice exists — so the question is never silently skipped. The follow-up answer goes only into that one labelled field: `onresult` calls `fillSingleClaimField()` and deliberately leaves the original request text intact. If a Stop press captures no answer, the same field is asked again. A `no-speech` error politely re-asks after a short pause; other errors end the session and keep what was already filled. When no required field remains, the app says all details are ready and moves focus to Send. Nothing is created by voice alone: the citizen still reviews the fields and presses **Send**, which stops the microphone immediately through `stopActiveRecognition(true)` so a late final result cannot overwrite submitted text. The red Stop button uses the same helper without `preserveText`, so its normal review flow is unchanged. `onend` waits 700 ms before reporting a failure, and `onresult` cancels that check, so a slow final result is no longer misreported as "no words." If no words truly arrive, the notice distinguishes "no voice picked up" from "voice picked up but not recognised"; for Urdu it points to typing or switching to English instead of blaming the speaker.

### Claim Details & Request

Seven labelled fields stay visible on a Surface panel beneath the mic: full name, CNIC, district, category, monthly income, claim amount, and optional dependents. They are intentionally secondary to the 96px microphone — a citizen who can read and type can use them directly, while the voice session fills and asks for the same values. A filled Green-Wash note says when values came from the citizen's words. Required fields are marked with an asterisk, carry `aria-required`, and describe their inline error containers with `aria-describedby`; the select uses the same dark control tokens as inputs and textareas. The citizen's own request stays in a separate textarea below the panel, so the two meanings — evidence and message — are never confused.

`extractClaimFields()` reads the request text on a 450 ms debounce and as recognition results arrive. `normaliseDigits()` first converts Arabic-Indic (`٠-٩`) and Persian (`۰-۹`) digits to ASCII, so a 5-7-1 CNIC with spaces, dashes, or either Urdu digit set fills the same field as an English-spoken CNIC; income and claim amounts follow the same bilingual path. `cleanExtractedName()` and `cleanExtractedDistrict()` trim Urdu copulas and sentence punctuation, and `رہائش` is accepted alongside `ضلع`, `شہر`, `district`, `in`, and `from` as a district cue. `fillClaimFields()` only writes untouched inputs and clears their errors; `markClaimEdited()` records edits from `input` and `change` events so later speech cannot overwrite them, and `fillSingleClaimField()` respects the same `claimTouched` map during follow-up questions. A follow-up answer may be a bare value ("Fatima Bibi", "12000", `١٢٣٤٥-٦٧٨٩٠١٢-٣`), so `extractSingleClaimField()` uses the same normaliser and cleaners before accepting it. `validateClaimFields()` checks required values, 13-digit CNIC, whole numbers, a positive claim amount, and a generous maximum before blocking Send with inline errors; during a voice session a failed validation re-opens the next missing-field question instead of just focusing the input. `readClaimForm()` sends the explicit `claim_data` object to `/api/ai/voice/intake` and offline `voice_intake` operations. The server merges those explicit values over any transcript guesses and validates them with `ClaimForm` before `create_case()`, so rules, identity, anomaly, and officer approval all use the same structure.

**Complete demo claim.** The default text-box example is a full mock claim with every extractable field: English uses Muhammad Ahmed (mock CNIC `12345-6789012-3`, unemployed, Lahore, income 18000, claim 5000); Urdu uses a clean Nastaliq sentence — "میرا نام Aisha Khatoon ہے۔ شناختی نمبر 11111-2222233-3۔ میں کم آمدنی والی ہوں اور میری رہائش Hyderabad میں ہے۔ میری ماہانہ آمدنی 9000 روپے ہے۔ مجھے 3000 روپے چاہیے۔ یہ میری رلیف ادائیگی کی درخواست ہے۔" — with Aisha Khatoon (mock CNIC `11111-2222233-3`, low income, Hyderabad, income 9000, claim 3000). The mock name stays in Latin script because identity verification matches that exact mock record; the surrounding Urdu reads naturally instead of mixing in broken English fragments. Different mock CNICs keep the duplicate-claim check quiet. Structured extraction fills every field, identity verification succeeds, no anomaly is flagged, and all rule checks pass, so the case is routed automatically (`approve` / `auto_handle`) and the citizen sees "Waiting for officer" instead of "We are not sure." This does not bypass the approval gate: an officer still decides before any mock payment.

**Error wording.** Speech errors are mapped to their real cause before they reach the citizen. `language-not-supported` says that Urdu dictation is unavailable or that the chosen dictation language is unsupported, and `audio-capture` points to the microphone device. `aborted` is silent because it usually means the citizen pressed Stop before any speech. The generic fallback says "voice recognition stopped" rather than "I could not hear you," so no error is shown as a hearing judgment before the citizen has spoken. A `network` error is never automatically blamed on the citizen's connection: `micNetwork` checks `navigator.onLine`. Offline keeps the honest "needs an internet connection" wording; online says the recognition service is unavailable right now. For Urdu, Edge can return `network` for an unsupported locale even on a healthy connection, so `tryNextUrduRecognitionLocale()` retries `ur-PK` → `ur` → `ur-IN` once with a visible "Trying another Urdu recognition setting…" hint. If all Urdu tags fail, the citizen is told that Urdu recognition is not working in this browser, that their internet is online, and to type or switch the app language to English. English dictation is never substituted for Urdu speech, keeping the language toggle truthful.

### Password Visibility Toggle

An inline SVG eye button sits at the inline end of the password input, so it stays beside the typed characters in both LTR and RTL. It is hidden by default (`type="password"`, `aria-pressed="false"`) and toggles the field to plain text when pressed. The icon swaps from an open eye to a crossed-out eye; the accessible name and tooltip switch between localized "Show password" and "Hide password" in English and Urdu. The 44×44px touch target uses the muted token at rest and Green Wash with a Green border on hover, matching the quick-login chips without becoming a second dominant action. The label and status field remain outside the wrapper, so validation and `aria-describedby` are unchanged. Visibility resets to hidden after sign-in and sign-out.

### Language Toggle

One globe icon button on the sign-in card and one in the counter top bar. Both call the same `toggleLang()` helper, persist `lm_lang`, and call `applyLang()`. The choice survives login, logout, and reload.

### Quick-Login Chips

Surface gray with a 1px Line border, 52px minimum height, green 19px icon plus label, 8px gap, wrapping grid. Hover fills with Green Wash and tightens the border to Green. Chips fill the email field; they never auto-submit.

### Role Workspace

The five quick-login chips deliberately lead to five different Home workspaces, not one shared citizen screen. A gray banner under the top bar carries the localized role title, one-line purpose, and the note that permissions are checked on the server. For citizens, the status ticket and voice/text intake stay in place. For helpers, officers, admins, and auditors, those citizen controls are hidden and a server-backed panel takes their place: 40 mock families and consent notice, officer review queue with approve/ask-info/reject actions, active rule version with thresholds, or recent read-only audit events. Cases and Help remain common. The role label in the top bar is localized, and the whole workspace re-renders on language toggle. Client-side role chrome is explanatory only; every action still passes the server's RBAC and consent checks.

### Status Ticket

Green Wash surface with a Card-colored 44px icon well. Contains a localized heading, live status text (`aria-live="polite"`), a progress bar with `role="progressbar"` and `aria-valuenow`, and a 46px read-aloud button.

### Case Row

Card-gray row with a status-colored 38px icon well, bold case number, a pill with localized status, and a small confidence percentage with a 58×6px meter. Status color and glyph come from one shared `statusMarkup()` function, so the ticket and list can never disagree.

### Voice Note

An Amber Wash strip on Home, shown only when Urdu is selected and no installed Urdu voice is available. It says the words are visible on screen, typing still works, and that opening the demo in **Microsoft Edge** on Windows provides online Urdu voices with no device-settings changes. This is an honest capability notice, not an error.

### Voice Setup Card (Help page)

The practical answer to "I cannot find an Urdu voice package in Settings": Windows built-in SAPI voices rarely ship Urdu, but **Microsoft Edge exposes online natural Urdu voices** (`Microsoft Asad Online (Natural) - Urdu (Pakistan)`, `Microsoft Uzma Online (Natural) - Urdu (Pakistan)`) to `speechSynthesis` without any Windows Settings install. The Help card explains this and offers two controls:

- **Check voices** re-reads `speechSynthesis.getVoices()`, then reports the total voice count and either the matching Urdu voice name(s) or the Edge guidance.
- **Test Urdu** speaks a short Urdu sentence only when a genuine Urdu voice exists; otherwise it repeats the Edge guidance. It never falls back to an English/default voice.

`renderVoiceDiag()` owns the `#voiceDiag` live region; results update in place as the language changes.

### Prototype Strip

Permanent near-black band with a drawn warning triangle and localized all-caps copy. The network badge sits opposite it with `role="status"` and changes color and label on `online`/`offline` events.

## Voice Behavior

Setting `utter.lang = "ur-PK"` is not enough: browsers happily read Urdu with an English voice. The UI now:

1. Reads `speechSynthesis.getVoices()` and refreshes on `voiceschanged`.
2. Selects a voice whose language code actually begins with `ur`.
3. Refuses to speak Urdu if no such voice is installed, showing the actionable voice note instead.
4. Uses the same explicit selection for English (`en-*`), so neither language falls back silently.
5. Sets recognition language to `ur-PK` or `en-US` with the toggle.
6. Exposes Check voices / Test Urdu on the Help page so the citizen can verify capability themselves.

Windows users who cannot find an Urdu pack in Settings should open the demo in **Microsoft Edge**: Edge supplies online Urdu natural voices to the browser directly, so no OS voice pack is required. Where no Urdu voice exists at all, typed requests remain the honest fallback.

This makes the language toggle truthful: Urdu text is only spoken when an Urdu voice exists.

## Do's and Don'ts

### Do

- Keep the page black and the foreground surfaces gray.
- Keep the language toggle on both the sign-in card and the top bar.
- Pair every drawn icon with localized text or an accessible name.
- Keep the strip at the top in both languages.
- Keep body text ≥16px and every prompt ≥14px.
- Mirror the full layout when `dir` flips.
- Keep `prefers-reduced-motion` collapsing animation and transitions.
- Select a real installed voice before speaking.

### Don't

- Don't reintroduce emoji anywhere in the interface or design artifacts.
- Don't tint the page background or make cards white.
- Don't use amber, red, or the strip colors decoratively.
- Don't add a second dominant action beside the microphone.
- Don't put `data-i18n` on the live status line.
- Don't read Urdu with a non-Urdu voice.
