/*
 * PHQ-9 Quiz JS
 */
const labels = ["Not at all", "Several days", "More than half the days", "Nearly every day"];
const phq9Data = [
    { q: "Little interest or pleasure in doing things.", scores: [0,1,2,3] },
    { q: "Feeling down, depressed, or hopeless.", scores: [0,1,2,3] },
    { q: "Trouble falling or staying asleep, or sleeping too much.", scores: [0,1,2,3] },
    { q: "Feeling tired or having little energy.", scores: [0,1,2,3] },
    { q: "Poor appetite or overeating.", scores: [0,1,2,3] },
    { q: "Feeling bad about yourself or that you are a failure or have let yourself or your family down.", scores: [0,1,2,3] },
    { q: "Trouble concentrating on things, such as reading the newspaper or watching television.", scores: [0,1,2,3] },
    { q: "Moving or speaking so slowly that other people could have noticed. Or the opposite - being so fidgety or restless that you have been moving around a lot more than usual.", scores: [0,1,2,3] },
    { q: "Thoughts that you would be better off dead, or of hurting yourself in some way.", scores: [0,1,2,3] },
];

let currentQuestionIndex = 0;
const answers = new Array(phq9Data.length).fill(null);

document.addEventListener('DOMContentLoaded', () => {
    renderQuestion(currentQuestionIndex);

    document.getElementById('phq9PrevBtn').addEventListener('click', () => {
        if(currentQuestionIndex>0){
            currentQuestionIndex--;
            renderQuestion(currentQuestionIndex);
        }
    });

    document.getElementById('phq9NextBtn').addEventListener('click', () => {
        if(currentQuestionIndex < phq9Data.length-1){
            currentQuestionIndex++;
            renderQuestion(currentQuestionIndex);
        } else {
            showResults();
        }
    });

    document.getElementById('phq9CloseBtn').addEventListener('click', () => {
        submitPHQ9Close();
    });
});

function renderQuestion(index){
    const stage = document.getElementById('phq9Stage');
    stage.classList.add('fade-out');

    setTimeout(()=>{
        const questionData = phq9Data[index];
        document.getElementById('phq9Question').textContent = `${index+1}. ${questionData.q}`;
        document.getElementById('phq9ProgressText').textContent = `${index+1} / ${phq9Data.length}`;
        document.getElementById('phq9ProgressBar').style.width = `${((index+1)/phq9Data.length)*100}%`;
        document.getElementById('phq9PrevBtn').disabled = index===0;

        const nextBtn = document.getElementById('phq9NextBtn');
        nextBtn.textContent = (index===phq9Data.length-1)?'See results':'Next';
        nextBtn.disabled = answers[index]===null;

        renderOptions(questionData.scores, index);

        stage.classList.remove('fade-out');
        stage.classList.add('fade-in');
    },300);
}

function renderOptions(scores,index){
    const optionsGroup = document.getElementById('phq9Options');
    optionsGroup.innerHTML='';

    scores.forEach((score,i)=>{
        const circle = document.createElement('div');
        circle.className='option-circle phq9-circle neutral-border';
        circle.dataset.value = score;
        circle.innerHTML = `<span>${labels[i]}</span>`;

        if(answers[index]===score){
            circle.classList.add('active');
        }

        circle.addEventListener('click',()=>{
            optionsGroup.querySelectorAll('.option-circle').forEach(c=>c.classList.remove('active'));
            circle.classList.add('active');
            answers[index]=score;
            document.getElementById('phq9NextBtn').disabled=false;
        });

        optionsGroup.appendChild(circle);
    });
}

function showResults(){
    document.getElementById('phq9Stage').hidden=true;
    document.getElementById('phq9Result').hidden=false;
    document.getElementById('phq9ProgressBar').style.width='100%';

    const totalScore = answers.reduce((sum,score)=>sum+score,0);
    document.getElementById('phq9TotalScore').textContent=totalScore;

    let description='', tips=[];

    if(totalScore<=4){
        description='Minimal depression';
        tips=['Continue with your self-care practices.'];
    } else if(totalScore<=9){
        description='Mild depression';
        tips=['Consider talking to a healthcare professional if symptoms persist.'];
    } else if(totalScore<=14){
        description='Moderate depression';
        tips=['It is recommended to speak with a healthcare provider.'];
    } else if(totalScore<=19){
        description='Moderately severe depression';
        tips=['Professional help is strongly recommended.'];
    } else {
        description='Severe depression';
        tips=['It is important to seek immediate professional help.'];
    }

    document.getElementById('phq9ScoreDesc').textContent=description;

    const tipsContainer = document.getElementById('phq9Tips');
    tipsContainer.innerHTML='';
    tips.forEach(tip=>{
        const chip = document.createElement('span');
        chip.className='chip';
        chip.textContent=tip;
        tipsContainer.appendChild(chip);
    });
}

// --- NEW: Submit on Close and update main chat ---
document.getElementById('phq9CloseBtn').addEventListener('click', (e) => {
    e.preventDefault(); // prevent the default form submission
    closePHQ9();
});

function closePHQ9() {
    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/submit_phq9";  // normal POST
    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "answers";
    input.value = JSON.stringify(answers);
    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();  // browser will redirect to index.html after Flask route returns
}



// --- Optional: Retake test ---
function retakeTest(){
    currentQuestionIndex=0;
    answers.fill(null);
    document.getElementById('phq9Result').hidden=true;
    document.getElementById('phq9Stage').hidden=false;
    renderQuestion(currentQuestionIndex);
}
