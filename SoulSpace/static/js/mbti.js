const mbtiData = [
  { q: "You enjoy being the center of attention.", dim: ["E", "I"] },
  { q: "You are energized by social gatherings.", dim: ["E", "I"] },
  { q: "You find it easy to approach and talk to new people.", dim: ["E", "I"] },
  { q: "After a busy day, you prefer to recharge alone rather than with others.", dim: ["I", "E"] },
  { q: "You rely more on facts and past experience than theories.", dim: ["S", "N"] },
  { q: "You prefer practical tasks over exploring abstract possibilities.", dim: ["S", "N"] },
  { q: "You focus more on present details than future possibilities.", dim: ["S", "N"] },
  { q: "You enjoy imagining what could be rather than what is.", dim: ["N", "S"] },
  { q: "You make decisions using logic and consistency over empathy.", dim: ["T", "F"] },
  { q: "You value fairness and principles over personal circumstances.", dim: ["T", "F"] },
  { q: "You prioritize harmony and people’s feelings in decisions.", dim: ["F", "T"] },
  { q: "You tend to consider the human impact before the numbers.", dim: ["F", "T"] },
  { q: "You prefer a structured plan over going with the flow.", dim: ["J", "P"] },
  { q: "You like closing tasks early rather than keeping options open.", dim: ["J", "P"] },
  { q: "You are flexible and comfortable adapting plans last minute.", dim: ["P", "J"] },
  { q: "You feel best when your schedule is organized and decided.", dim: ["J", "P"] },
];

let currentQuestionIndex = 0;
const answers = [];

document.addEventListener('DOMContentLoaded', () => {
  renderQuestion(currentQuestionIndex);

  document.getElementById('mbtiPrevBtn').addEventListener('click', () => {
    if (currentQuestionIndex > 0) {
      currentQuestionIndex--;
      renderQuestion(currentQuestionIndex);
    }
  });

  document.getElementById('mbtiNextBtn').addEventListener('click', () => {
    if (currentQuestionIndex < mbtiData.length - 1) {
      currentQuestionIndex++;
      renderQuestion(currentQuestionIndex);
    } else {
      showResults();
    }
  });
});

function renderQuestion(index) {
  const stage = document.getElementById('mbtiStage');
  stage.classList.add('fade-out');

  setTimeout(() => {
    const questionData = mbtiData[index];
    document.getElementById('mbtiQuestion').textContent = `${index + 1}. ${questionData.q}`;
    document.getElementById('mbtiProgressText').textContent = `${index + 1} / ${mbtiData.length}`;
    document.getElementById('mbtiProgressBar').style.width = `${((index + 1) / mbtiData.length) * 100}%`;
    document.getElementById('mbtiPrevBtn').disabled = index === 0;

    const nextBtn = document.getElementById('mbtiNextBtn');
    nextBtn.textContent = (index === mbtiData.length - 1) ? 'See results' : 'Next';
    nextBtn.disabled = !answers[index];

    renderOptions(questionData.dim, index);

    stage.classList.remove('fade-out');
    stage.classList.add('fade-in');
  }, 300);
}

function renderOptions(dim, index) {
  const optionsGroup = document.getElementById('mbtiOptions');
  optionsGroup.innerHTML = `
    <span class="option-label agree-text">Agree</span>
    <div class="option-circle agree-border" data-value="${dim[0]}3" data-dim="${dim[0]}"><i class="fas fa-check"></i></div>
    <div class="option-circle agree-border" data-value="${dim[0]}2" data-dim="${dim[0]}"><i class="fas fa-check"></i></div>
    <div class="option-circle neutral-border" data-value="${dim[0]}1" data-dim="${dim[0]}"><i class="fas fa-check"></i></div>
    <div class="option-circle disagree-border" data-value="${dim[1]}2" data-dim="${dim[1]}"><i class="fas fa-check"></i></div>
    <div class="option-circle disagree-border" data-value="${dim[1]}3" data-dim="${dim[1]}"><i class="fas fa-check"></i></div>
    <span class="option-label disagree-text">Disagree</span>
  `;

  optionsGroup.querySelectorAll('.option-circle').forEach(circle => {
    if (answers[index] === circle.dataset.value) circle.classList.add('active');

    circle.addEventListener('click', () => {
      optionsGroup.querySelectorAll('.option-circle').forEach(c => c.classList.remove('active'));
      circle.classList.add('active');
      answers[index] = circle.dataset.value;
      document.getElementById('mbtiNextBtn').disabled = false;
    });
  });
}

function computeScores() {
  const score = { E: 0, I: 0, S: 0, N: 0, T: 0, F: 0, J: 0, P: 0 };
  answers.forEach(ans => {
    const dim = ans.charAt(0);
    const val = parseInt(ans.charAt(1));
    score[dim] += val;
  });
  return score;
}

function showResults() {
  const score = computeScores();
  let type = '';
  type += (score.E >= score.I) ? 'E' : 'I';
  type += (score.S >= score.N) ? 'S' : 'N';
  type += (score.T >= score.F) ? 'T' : 'F';
  type += (score.J >= score.P) ? 'J' : 'P';

  // Store globally for form submission
  window.lastMBTIType = type;

  document.getElementById('mbtiTypeBadge').textContent = type;
  document.getElementById('mbtiTypeName').textContent = `${type} — ${getTypeName(type)}`;
  document.getElementById('mbtiTypeDesc').textContent = getTypeDescription(type);

  document.getElementById('mbtiStage').hidden = true;
  document.getElementById('mbtiResult').hidden = false;
}

function getTypeName(type) {
  const names = { INTP: "Logician", ENTP: "Debater", INTJ: "Architect", ENTJ: "Commander" };
  return names[type] || "Thinker";
}

function getTypeDescription(type) {
  return `As a ${type} personality, you excel at analyzing ideas, solving problems, and seeking knowledge. Embrace your curiosity and creativity!`;
}

function retakeMBTI() {
  currentQuestionIndex = 0;
  answers.length = 0;
  window.lastMBTIType = '';
  document.getElementById('mbtiStage').hidden = false;
  document.getElementById('mbtiResult').hidden = true;
  renderQuestion(0);
}

document.addEventListener("DOMContentLoaded", () => {
  const closeBtn = document.getElementById("mbtiCloseBtn");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      submitMBTI();
    });
  }
});

function submitMBTI() {
  if (!window.lastMBTIType) {
    alert("Please complete the MBTI test before submitting.");
    return;
  }

  const form = document.createElement("form");
  form.method = "POST";
  form.action = "/submit_mbti";

  const input = document.createElement("input");
  input.type = "hidden";
  input.name = "mbti_type";
  input.value = window.lastMBTIType;
  form.appendChild(input);

  document.body.appendChild(form);
  form.submit(); // redirect to /index with AI reply
}
