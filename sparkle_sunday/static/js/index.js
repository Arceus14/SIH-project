let lastMBTIType = null;


 function confirmNewChat() {
      return confirm("Are you sure you want to start a new chat? This will clear your conversation history.");
    }




/* 16 questions: {q, dim:[proLetter, conLetter]} */
const mbtiData = [
  {q:"You enjoy being the center of attention.", dim:["E","I"]},
  {q:"You are energized by social gatherings.", dim:["E","I"]},
  {q:"You find it easy to approach and talk to new people.", dim:["E","I"]},
  {q:"After a busy day, you prefer to recharge alone rather than with others.", dim:["I","E"]},

  {q:"You rely more on facts and past experience than theories.", dim:["S","N"]},
  {q:"You prefer practical tasks over exploring abstract possibilities.", dim:["S","N"]},
  {q:"You focus more on present details than future possibilities.", dim:["S","N"]},
  {q:"You enjoy imagining what could be rather than what is.", dim:["N","S"]},

  {q:"You make decisions using logic and consistency over empathy.", dim:["T","F"]},
  {q:"You value fairness and principles over personal circumstances.", dim:["T","F"]},
  {q:"You prioritize harmony and people’s feelings in decisions.", dim:["F","T"]},
  {q:"You tend to consider the human impact before the numbers.", dim:["F","T"]},

  {q:"You prefer a structured plan over going with the flow.", dim:["J","P"]},
  {q:"You like closing tasks early rather than keeping options open.", dim:["J","P"]},
  {q:"You are flexible and comfortable adapting plans last minute.", dim:["P","J"]},
  {q:"You feel best when your schedule is organized and decided.", dim:["J","P"]},
];

/* Type profiles */
const mbtiProfiles = {
  ISTJ:{name:"Logistician",desc:"Responsible, detail-focused, and reliable. Prefers structure and clear expectations.",tips:["Use checklists and timelines.","Break tasks into well-defined steps.","Study in quiet, predictable spaces."]},
  ISFJ:{name:"Defender",desc:"Supportive, observant, and patient. Motivated by helping and duty.",tips:["Create gentle routines and reward milestones.","Study with purpose—link tasks to people helped.","Use tidy, calm environments."]},
  INFJ:{name:"Advocate",desc:"Insightful, idealistic, and purpose-driven. Seeks meaning and depth.",tips:["Tie study goals to your values.","Alternate deep work with reflective breaks.","Summarize concepts in your own words."]},
  INTJ:{name:"Architect",desc:"Strategic, independent, and future-focused. Loves systems and mastery.",tips:["Plan backwards from outcomes.","Use spaced repetition and concept maps.","Protect long, interruption-free blocks."]},
  ISTP:{name:"Virtuoso",desc:"Hands-on, analytical, and adaptable. Learns best by doing.",tips:["Apply theory to mini-projects.","Use short, intense sprints.","Keep tools and examples nearby."]},
  ISFP:{name:"Adventurer",desc:"Sensitive, creative, and spontaneous. Values authenticity and experience.",tips:["Make study visually engaging.","Use short sessions with variety.","Link topics to real-life interests."]},
  INFP:{name:"Mediator",desc:"Imaginative, empathetic, and values-driven. Motivated by meaning.",tips:["Set heartfelt reasons for each goal.","Journal brief reflections after sessions.","Use gentle structure with flexibility."]},
  INTP:{name:"Logician",desc:"Curious, theoretical, and independent. Loves patterns and puzzles.",tips:["Teach concepts to an imaginary class.","Use whiteboards and mind maps.","Schedule breaks to avoid rabbit holes."]},
  ESTP:{name:"Entrepreneur",desc:"Energetic, pragmatic, and action-oriented. Thrives on real results.",tips:["Turn studying into challenges or timers.","Use practical examples and case studies.","Move between tasks to stay engaged."]},
  ESFP:{name:"Entertainer",desc:"Outgoing, warm, and present-focused. Enjoys social learning.",tips:["Study with peers; discuss out loud.","Use colorful, interactive materials.","Reward progress with short fun breaks."]},
  ENFP:{name:"Campaigner",desc:"Enthusiastic, imaginative, and people-centered. Loves possibilities.",tips:["Capture ideas; then choose one path.","Use variety but limit task switching.","Anchor sessions with a simple plan."]},
  ENTP:{name:"Debater",desc:"Inventive, quick, and loves to challenge ideas.",tips:["Debate topics or play devil’s advocate.","Prototype ideas quickly.","Time-box exploration to ship results."]},
  ESTJ:{name:"Executive",desc:"Organized, direct, and practical. Values efficiency and standards.",tips:["Set measurable targets per session.","Use calendars and checklists.","Review outcomes weekly."]},
  ESFJ:{name:"Consul",desc:"Caring, cooperative, and dependable. Team-oriented and structured.",tips:["Study with accountability partners.","Use clear schedules and shared goals.","Teach others to reinforce learning."]},
  ENFJ:{name:"Protagonist",desc:"Encouraging, organized, and inspiring. Leads with vision and care.",tips:["Set meaningful goals tied to impact.","Mix solo focus with guided group sessions.","Reflect on progress to stay aligned."]},
  ENTJ:{name:"Commander",desc:"Strategic, decisive, and goal-driven. Thrives on challenge.",tips:["Plan objectives and KPIs for study.","Tackle hardest tasks first.","Delegate or automate low-value work."]},
};

let mbtiIndex = 0;                 // current question index
const answers = [];                // store values like "E3", "I2", etc.
let renderedOnce = false;          // ensure options wired up once

function openMBTIModal() {
  const modal = document.getElementById('mbtiModal');
  modal.classList.add('show');
  modal.setAttribute('aria-hidden','false');
  document.addEventListener('keydown', escClose);

  if (!renderedOnce) {
    renderCurrentQuestion(true);
    renderedOnce = true;
  } else {
    renderCurrentQuestion(false);
  }
}


function escClose(e){ if (e.key === 'Escape') closeMBTIModal(); }

function renderCurrentQuestion(initialFade) {
  const q = mbtiData[mbtiIndex];
  const qEl = document.getElementById('mbtiQuestion');
  const optsEl = document.getElementById('mbtiOptions');
  const nextBtn = document.getElementById('mbtiNextBtn');
  const prevBtn = document.getElementById('mbtiPrevBtn');

  // Progress
  const pct = ((mbtiIndex) / mbtiData.length) * 100;
  document.getElementById('mbtiProgressBar').style.width = `${pct}%`;
  document.getElementById('mbtiProgressText').textContent = `${mbtiIndex+1} / ${mbtiData.length}`;

  // Text
  qEl.textContent = q.q;

  // Options (Likert)
  optsEl.innerHTML = '';
  const opts = [
    {label:'Strongly agree', val:`${q.dim[0]}3`},
    {label:'Agree',          val:`${q.dim[0]}2`},
    {label:'Neutral',        val:`${q.dim[0]}1`},
    {label:'Disagree',       val:`${q.dim[1]}2`},
    {label:'Strongly disagree', val:`${q.dim[1]}3`},
  ];
  opts.forEach((o,i)=>{
    const id = `q${mbtiIndex}_opt${i}`;
    const checked = answers[mbtiIndex] === o.val ? 'checked' : '';
    optsEl.insertAdjacentHTML('beforeend', `
      <label for="${id}">
        <input type="radio" id="${id}" name="mbti_${mbtiIndex}" value="${o.val}" ${checked}>
        <span>${o.label}</span>
      </label>
    `);
  });

  // Buttons
  prevBtn.disabled = mbtiIndex === 0;
  nextBtn.textContent = (mbtiIndex === mbtiData.length - 1) ? 'See results' : 'Next';
  nextBtn.disabled = !answers[mbtiIndex];

  // Enable Next on selection
  optsEl.querySelectorAll('input[type="radio"]').forEach(r=>{
    r.addEventListener('change', ()=>{
      answers[mbtiIndex] = r.value;
      document.getElementById('mbtiNextBtn').disabled = false;
    });
  });

  // Fade
  const stage = document.getElementById('mbtiStage');
  if (!initialFade) {
    stage.classList.remove('fade-in'); // reset
    void stage.offsetWidth;            // reflow to restart animation
    stage.classList.add('fade-in');
  }
}

function nextMBTI() {
  const stage = document.getElementById('mbtiStage');
  stage.classList.remove('fade-in');
  stage.classList.add('fade-out');

  setTimeout(()=>{
    stage.classList.remove('fade-out');

    if (mbtiIndex < mbtiData.length - 1) {
      mbtiIndex++;
      renderCurrentQuestion(false);
    } else {
      // Completed
      showMBTIResult(computeType(), computeScores());
    }
  }, 160);
}

function prevMBTI() {
  if (mbtiIndex === 0) return;
  const stage = document.getElementById('mbtiStage');
  stage.classList.remove('fade-in');
  stage.classList.add('fade-out');

  setTimeout(()=>{
    stage.classList.remove('fade-out');
    mbtiIndex--;
    renderCurrentQuestion(false);
  }, 160);
}

function computeScores(){
  const scores = {E:0,I:0,S:0,N:0,T:0,F:0,J:0,P:0};
  answers.forEach(v=>{
    const letter = v.charAt(0);
    const weight = parseInt(v.charAt(1),10);
    scores[letter] += weight;
  });
  return scores;
}

function computeType(){
  const s = computeScores();
  return (s.E >= s.I ? 'E' : 'I') +
         (s.S >= s.N ? 'S' : 'N') +
         (s.T >= s.F ? 'T' : 'F') +
         (s.J >= s.P ? 'J' : 'P');
}

function showMBTIResult(type, scores){
  lastMBTIType = type // store for later when Close is clicked

  // Fill progress to 100%
  document.getElementById('mbtiProgressBar').style.width = '100%';
  document.getElementById('mbtiProgressText').textContent = `${mbtiData.length} / ${mbtiData.length}`;

  // Toggle views
  document.getElementById('mbtiStage').hidden = true;
  const result = document.getElementById('mbtiResult');
  result.hidden = false;

  // Content
  const profile = mbtiProfiles[type] || {name:"Your type",desc:"A balanced mix of preferences.",tips:[]};
  document.getElementById('mbtiTypeBadge').textContent = type;
  document.getElementById('mbtiTypeName').textContent = profile.name;
  document.getElementById('mbtiTypeDesc').textContent = profile.desc;

  const chips = [
    scores.E >= scores.I ? `Extraversion (E)` : `Introversion (I)`,
    scores.S >= scores.N ? `Sensing (S)` : `Intuition (N)`,
    scores.T >= scores.F ? `Thinking (T)` : `Feeling (F)`,
    scores.J >= scores.P ? `Judging (J)` : `Perceiving (P)`,
  ];
  const chipsEl = document.getElementById('mbtiChips');
  chipsEl.innerHTML = '';
  chips.forEach(c=>{
    const el = document.createElement('span');
    el.className = 'chip';
    el.textContent = c;
    chipsEl.appendChild(el);
  });

  const tipsEl = document.getElementById('mbtiTips');
  tipsEl.innerHTML = '';
  (profile.tips || []).forEach(t=>{
    const li = document.createElement('li');
    li.textContent = t;
    tipsEl.appendChild(li);
  });
}

function retakeMBTI(){
  // Reset
  mbtiIndex = 0;
  answers.length = 0;
  document.getElementById('mbtiResult').hidden = true;
  document.getElementById('mbtiStage').hidden = false;
  document.getElementById('mbtiProgressBar').style.width = '0%';
  document.getElementById('mbtiProgressText').textContent = `1 / ${mbtiData.length}`;
  renderCurrentQuestion(true);
}


//bismilah hirrahman nirraheem
















// 1) Helper to append an assistant bubble to the chat
function appendAssistantBubble(text) {
  const chatContainer = document.querySelector("#chatBody"); // <- use your real container
  if (!chatContainer) {
    console.warn("⚠️ No #chatBody container found — cannot display AI reply.");
    return;
  }

  const aiMsg = document.createElement("div");
  aiMsg.className = "bubble bot"; // match your CSS/HTML
  aiMsg.textContent = text;

  chatContainer.appendChild(aiMsg);

  // Smooth scroll to newest message
  aiMsg.scrollIntoView({ behavior: "smooth", block: "end" });
  chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 2) Waiter that resolves when the MBTI modal is actually closed (Option A)
function waitForModalClosed() {
  return new Promise((resolve) => {
    const modal = document.getElementById("mbtiModal");
    if (!modal) return resolve();
    const hidden = modal.getAttribute("aria-hidden") === "true";
    const showing = modal.classList.contains("show");
    if (hidden || !showing) return resolve();
    modal.addEventListener("mbti:closed", () => resolve(), { once: true });
  });
}

// 3) Your close function (Option A): dispatch custom event after animations end
function closeMBTIModal() {
  const modal = document.getElementById("mbtiModal");
  if (!modal) return;

  // Avoid "Blocked aria-hidden" warning by removing focus
  if (document.activeElement) document.activeElement.blur();

  modal.classList.remove("show");
  modal.setAttribute("aria-hidden", "true");
  document.body.classList.remove("modal-open"); // if you use this

  const done = () => modal.dispatchEvent(new CustomEvent("mbti:closed"));

  const cleanup = () => {
    modal.removeEventListener("transitionend", onEnd, true);
    modal.removeEventListener("animationend", onEnd, true);
    clearTimeout(fallback);
  };

  const onEnd = () => {
    cleanup();
    done();
  };

  modal.addEventListener("transitionend", onEnd, true);
  modal.addEventListener("animationend", onEnd, true);

  // Fallback if no animation/transition event fires
  const fallback = setTimeout(() => {
    cleanup();
    done();
  }, 6000);
}

// 4) Submit-on-close flow
async function submitMBTIAndClose() {
  if (!lastMBTIType) {
    console.warn("No MBTI type stored — cannot submit.");
    closeMBTIModal();
    await waitForModalClosed();
    return;
  }

  try {
    const res = await fetch("/submit_mbti", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ type: lastMBTIType })
    });
    const data = await res.json();
    console.log("MBTI submit response:", data);

    // Close modal first, then wait for actual close
    closeMBTIModal();
    await waitForModalClosed();

    if (data && data.ai_reply) {
      let reply = data.ai_reply;
      // If reply is wrapped in quotes, strip them
      if (typeof reply === "string" && reply.startsWith('"') && reply.endsWith('"')) {
        reply = reply.slice(1, -1);
      }
      appendAssistantBubble(reply);
    } else {
      console.warn("⚠️ No AI reply in server response.");
    }
  } catch (err) {
    console.error("Error submitting MBTI:", err);
    closeMBTIModal();
    await waitForModalClosed();
  }
}




