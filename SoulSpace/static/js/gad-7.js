/*
 * Questions extracted from the provided PHQ-9 and GAD-7 Form.
 * Each question has 4 options with scores from 0 to 3.
 */
const labels = ["Not at all", "Several days", "More than half the days", "Nearly every day"];
const gad7Data = [
    { q: "Feeling nervous, anxious, or on edge.", scores: [0, 1, 2, 3] },
    { q: "Not being able to stop or control worrying.", scores: [0, 1, 2, 3] },
    { q: "Worrying too much about different things.", scores: [0, 1, 2, 3] },
    { q: "Trouble relaxing.", scores: [0, 1, 2, 3] },
    { q: "Being so restless that it's hard to sit still.", scores: [0, 1, 2, 3] },
    { q: "Becoming easily annoyed or irritable.", scores: [0, 1, 2, 3] },
    { q: "Feeling afraid as if something awful might happen.", scores: [0, 1, 2, 3] },
];

let currentQuestionIndex = 0;
const answers = new Array(gad7Data.length).fill(null);

document.addEventListener('DOMContentLoaded', () => {
    renderQuestion(currentQuestionIndex);

    document.getElementById('gad7PrevBtn').addEventListener('click', () => {
        if (currentQuestionIndex > 0) {
            currentQuestionIndex--;
            renderQuestion(currentQuestionIndex);
        }
    });

    document.getElementById('gad7NextBtn').addEventListener('click', () => {
        if (currentQuestionIndex < gad7Data.length - 1) {
            currentQuestionIndex++;
            renderQuestion(currentQuestionIndex);
        } else {
            showResults();
        }
    });
});

function renderQuestion(index) {
    const stage = document.getElementById('gad7Stage');
    stage.classList.add('fade-out');

    setTimeout(() => {
        const questionData = gad7Data[index];
        document.getElementById('gad7Question').textContent = `${index + 1}. ${questionData.q}`;
        document.getElementById('gad7ProgressText').textContent = `${index + 1} / ${gad7Data.length}`;
        document.getElementById('gad7ProgressBar').style.width = `${((index + 1) / gad7Data.length) * 100}%`;
        document.getElementById('gad7PrevBtn').disabled = index === 0;

        const nextBtn = document.getElementById('gad7NextBtn');
        nextBtn.textContent = (index === gad7Data.length - 1) ? 'See results' : 'Next';
        nextBtn.disabled = answers[index] === null;

        renderOptions(questionData.scores, index);

        stage.classList.remove('fade-out');
        stage.classList.add('fade-in');
    }, 300);
}

function renderOptions(scores, index) {
    const optionsGroup = document.getElementById('gad7Options');
    optionsGroup.innerHTML = '';

    scores.forEach((score, i) => {
        const circle = document.createElement('div');
        circle.className = 'option-circle phq9-circle neutral-border';
        circle.dataset.value = score;
        circle.innerHTML = `<span>${labels[i]}</span>`;

        if (answers[index] === score) {
            circle.classList.add('active');
        }

        circle.addEventListener('click', () => {
            optionsGroup.querySelectorAll('.option-circle').forEach(c => c.classList.remove('active'));
            circle.classList.add('active');
            answers[index] = score;
            document.getElementById('gad7NextBtn').disabled = false;
        });

        optionsGroup.appendChild(circle);
    });
}

function showResults() {
    document.getElementById('gad7Stage').hidden = true;
    document.getElementById('gad7Result').hidden = false;
    document.getElementById('gad7ProgressBar').style.width = '100%';

    const totalScore = answers.reduce((sum, score) => sum + score, 0);
    document.getElementById('gad7TotalScore').textContent = totalScore;

    let description = '';
    let tips = [];

    if (totalScore <= 4) {
        description = 'Minimal anxiety';
        tips = ['Continue with your current coping strategies.'];
    } else if (totalScore <= 9) {
        description = 'Mild anxiety';
        tips = ['Consider self-care or speaking with a professional if symptoms worsen.'];
    } else if (totalScore <= 14) {
        description = 'Moderate anxiety';
        tips = ['It is recommended to speak with a healthcare provider.'];
    } else {
        description = 'Severe anxiety';
        tips = ['It is important to seek immediate professional help.'];
    }

    document.getElementById('gad7ScoreDesc').textContent = description;

    const tipsContainer = document.getElementById('gad7Tips');
    tipsContainer.innerHTML = '';
    tips.forEach(tip => {
        const chip = document.createElement('span');
        chip.className = 'chip';
        chip.textContent = tip;
        tipsContainer.appendChild(chip);
    });
}

function retakeTest() {
    currentQuestionIndex = 0;
    answers.fill(null);
    document.getElementById('gad7Result').hidden = true;
    document.getElementById('gad7Stage').hidden = false;
    renderQuestion(currentQuestionIndex);
}
document.addEventListener("DOMContentLoaded", () => {
  const closeBtn = document.getElementById("gad7CloseBtn");
  if (closeBtn) {
    closeBtn.addEventListener("click", () => {
      submitGAD7();
    });
  }
});

function submitGAD7() {
  const form = document.createElement("form");
  form.method = "POST";
  form.action = "/submit_gad7";

  const input = document.createElement("input");
  input.type = "hidden";
  input.name = "answers";
  input.value = JSON.stringify(answers || []);
  form.appendChild(input);

  document.body.appendChild(form);
  form.submit(); // normal POST → Flask redirects to /index
}
