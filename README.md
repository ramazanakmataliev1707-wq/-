<!DOCTYPE html>
<html lang="ky">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OmniLingua - Тил үйрөнүү</title>
    <style>
        :root {
            --duo-green: #58cc02;
            --duo-dark-green: #46a302;
            --duo-blue: #1cb0f6;
            --duo-red: #ff4b4b;
            --duo-gray: #e5e5e5;
            --text-dark: #4b4b4b;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #fff;
            color: var(--text-dark);
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
        }

        /* Прогресс бар */
        .header {
            width: 100%;
            max-width: 600px;
            padding: 20px;
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .close-btn { font-size: 24px; cursor: pointer; color: #afafaf; }

        .progress-container {
            flex-grow: 1;
            height: 16px;
            background-color: var(--duo-gray);
            border-radius: 10px;
            overflow: hidden;
        }

        #progress-bar {
            width: 0%;
            height: 100%;
            background-color: var(--duo-green);
            transition: width 0.3s ease;
        }

        /* Негизги мазмун */
        .container {
            width: 90%;
            max-width: 500px;
            margin-top: 50px;
            text-align: center;
        }

        h2 { font-size: 28px; margin-bottom: 30px; }

        .options {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
        }

        .option-card {
            border: 2px solid var(--duo-gray);
            border-bottom: 4px solid var(--duo-gray);
            border-radius: 15px;
            padding: 15px;
            font-size: 18px;
            cursor: pointer;
            transition: all 0.1s;
            background: white;
        }

        .option-card:hover { background-color: #f7f7f7; }

        .option-card.selected {
            border-color: var(--duo-blue);
            background-color: #ddf4ff;
            color: var(--duo-blue);
        }

        /* Текшерүү баскычы */
        .footer {
            position: fixed;
            bottom: 0;
            width: 100%;
            padding: 20px;
            border-top: 2px solid var(--duo-gray);
            display: flex;
            justify-content: center;
            background: white;
        }

        #check-btn {
            width: 100%;
            max-width: 400px;
            padding: 15px;
            border: none;
            border-radius: 12px;
            background-color: var(--duo-gray);
            color: #afafaf;
            font-weight: bold;
            font-size: 18px;
            cursor: not-allowed;
            text-transform: uppercase;
        }

        #check-btn.active {
            background-color: var(--duo-green);
            color: white;
            cursor: pointer;
            box-shadow: 0 4px 0 var(--duo-dark-green);
        }

        /* Жыйынтык билдирүүсү */
        #feedback {
            position: fixed;
            bottom: -100px;
            left: 0;
            width: 100%;
            padding: 30px;
            transition: bottom 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
        }

        .correct { background-color: #d7ffb8; color: #58a700; bottom: 0 !important; }
        .wrong { background-color: #ffdfe0; color: #ea2b2b; bottom: 0 !important; }
    </style>
</head>
<body>

    <div class="header">
        <span class="close-btn">✕</span>
        <div class="progress-container">
            <div id="progress-bar"></div>
        </div>
    </div>

    <div class="container" id="game-box">
        <h2 id="question">"Apple" сөзүнүн котормосу кандай?</h2>
        <div class="options" id="options-container">
            <!-- Варианттар ушул жерге келет -->
        </div>
    </div>

    <div id="feedback">Туура! Азаматсыз!</div>

    <div class="footer">
        <button id="check-btn" onclick="checkAnswer()">Текшерүү</button>
    </div>

    <script>
        const questions = [
            { q: '"Apple" сөзүнүн котормосу?', options: ['Алма', 'Өрүк', 'Нан'], correct: 0 },
            { q: '"Book" сөзү кыргызча эмнени билдирет?', options: ['Суу', 'Китеп', 'Калем'], correct: 1 },
            { q: '"Hello" дегенди кантип айтабыз?', options: ['Кош бол', 'Жакшы', 'Салам'], correct: 2 }
        ];

        let currentStep = 0;
        let selectedIdx = null;

        function loadQuestion() {
            if (currentStep >= questions.length) {
                document.getElementById('game-box').innerHTML = "<h2>Куттуктайбыз! Сиз курсту бүттүңүз! 🏆</h2>";
                document.querySelector('.footer').style.display = 'none';
                return;
            }

            const qData = questions[currentStep];
            document.getElementById('question').innerText = qData.q;
            const optionsDiv = document.getElementById('options-container');
            optionsDiv.innerHTML = '';
            selectedIdx = null;
            updateBtnStatus();

            qData.options.forEach((opt, idx) => {
                const card = document.createElement('div');
                card.className = 'option-card';
                card.innerText = opt;
                card.onclick = () => selectOption(idx, card);
                optionsDiv.appendChild(card);
            });
        }

        function selectOption(idx, element) {
            selectedIdx = idx;
            document.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
            element.classList.add('selected');
            updateBtnStatus();
        }

        function updateBtnStatus() {
            const btn = document.getElementById('check-btn');
            if (selectedIdx !== null) {
                btn.classList.add('active');
                btn.disabled = false;
            } else {
                btn.classList.remove('active');
                btn.disabled = true;
            }
        }

        function checkAnswer() {
            const feedback = document.getElementById('feedback');
            const isCorrect = selectedIdx === questions[currentStep].correct;
            
            if (isCorrect) {
                feedback.innerText = "Туура! Азаматсыз! ✨";
                feedback.className = 'correct';
                currentStep++;
                updateProgress();
            } else {
                feedback.innerText = "Ката! Кайра аракет кылыңыз ❌";
                feedback.className = 'wrong';
            }

            setTimeout(() => {
                feedback.className = '';
                if (isCorrect) loadQuestion();
            }, 1500);
        }

        function updateProgress() {
            const percent = (currentStep / questions.length) * 100;
            document.getElementById('progress-bar').style.width = percent + '%';
        }

        loadQuestion();
    </script>
</body>
</html># -
Абдимажидов
