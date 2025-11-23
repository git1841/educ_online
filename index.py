from flask import Flask, render_template_string, jsonify, request
import random
import time

app = Flask(__name__)

class QuizManager:
    def __init__(self):
        self.current_question = None
        self.user_score = 0
        self.question_start_time = time.time()
        self.correct_answer = None
        self.user_answer = None
        self.feedback_message = ""
        self.show_feedback = False
        self.is_answered = False
        self.generate_new_question()
   
    def generate_new_question(self):
        # Choisir un niveau au hasard
        level = random.choice(["collège", "lycée", "universitaire"])
        self.current_question = self.generate_question(level)
        self.correct_answer = self.current_question["correct"]
        self.question_start_time = time.time()
        self.show_feedback = False
        self.user_answer = None
        self.is_answered = False
   
    def generate_question(self, level):
        if level == "collège":
            return self.generate_college_question()
        elif level == "lycée":
            return self.generate_lycee_question()
        else:
            return self.generate_universitaire_question()
   
    def generate_college_question(self):
        question_types = [
            "calcul_simple", "factorisation", "developpement", "equation_simple",
            "pourcentage", "geometrie", "fraction"
        ]
        q_type = random.choice(question_types)
       
        if q_type == "calcul_simple":
            a, b = random.randint(1, 50), random.randint(1, 50)
            op = random.choice(["+", "-", "×"])
            if op == "+":
                result = a + b
                question = f"Calculer : {a} + {b}"
            elif op == "-":
                result = a - b
                question = f"Calculer : {a} - {b}"
            else:
                result = a * b
                question = f"Calculer : {a} × {b}"
           
        elif q_type == "factorisation":
            a, b = random.randint(2, 12), random.randint(1, 10)
            question = f"Factoriser : {a}x + {a*b}"
            result = f"{a}(x + {b})"
           
        elif q_type == "developpement":
            a, b, c = random.randint(1, 6), random.randint(1, 6), random.randint(1, 10)
            question = f"Développer : {a}(x + {b}) + {c}"
            result = f"{a}x + {a*b + c}"
           
        elif q_type == "equation_simple":
            a, b = random.randint(1, 10), random.randint(1, 20)
            question = f"Résoudre : {a}x + {b} = {a*2 + b}"
            result = "2"
           
        elif q_type == "pourcentage":
            a, b = random.randint(10, 100), random.randint(5, 20)
            question = f"Calculer {b}% de {a}"
            result = str(round(a * b / 100))
           
        elif q_type == "geometrie":
            a = random.randint(3, 15)
            question = f"Quel est le périmètre d'un carré de côté {a} cm ?"
            result = f"{4*a} cm"
           
        else: # fraction
            a, b = random.randint(1, 5), random.randint(2, 8)
            question = f"Simplifier la fraction : {a*b}/{b}"
            result = str(a)
       
        answers = [str(result)]
        # Générer des mauvaises réponses plausibles
        while len(answers) < 4:
            if q_type in ["calcul_simple", "equation_simple", "pourcentage"]:
                wrong = str(result + random.choice([-5, -2, -1, 1, 2, 5]))
            elif q_type == "factorisation":
                wrong = f"{a}(x + {b + random.choice([-2, -1, 1, 2])})"
            elif q_type == "developpement":
                wrong = f"{a}x + {a*b + c + random.choice([-3, -1, 1, 3])}"
            elif q_type == "geometrie":
                wrong = f"{random.choice([2*a, 3*a, a*a])} cm"
            else:
                wrong = str(result + random.choice([-2, -1, 1, 2]))
           
            if wrong not in answers and wrong != str(result):
                answers.append(wrong)
       
        random.shuffle(answers)
        correct_index = answers.index(str(result))
       
        return {
            "question": question,
            "answers": answers,
            "correct": correct_index,
            "level": "collège",
            "points": 10
        }
   
    def generate_lycee_question(self):
        question_types = [
            "derivation", "integration", "equation_diff", "logarithme",
            "exponentielle", "trigonometrie", "probabilite"
        ]
        q_type = random.choice(question_types)
       
        if q_type == "derivation":
            funcs = ["x²", "√x", "1/x", "sin(x)", "cos(x)", "e^x", "ln(x)"]
            func = random.choice(funcs)
            if func == "x²":
                question = "Dérivée de f(x) = x²"
                result = "2x"
            elif func == "√x":
                question = "Dérivée de f(x) = √x"
                result = "1/(2√x)"
            elif func == "1/x":
                question = "Dérivée de f(x) = 1/x"
                result = "-1/x²"
            elif func == "sin(x)":
                question = "Dérivée de f(x) = sin(x)"
                result = "cos(x)"
            elif func == "cos(x)":
                question = "Dérivée de f(x) = cos(x)"
                result = "-sin(x)"
            elif func == "e^x":
                question = "Dérivée de f(x) = e^x"
                result = "e^x"
            else:
                question = "Dérivée de f(x) = ln(x)"
                result = "1/x"
               
        elif q_type == "integration":
            funcs = ["2x", "x²", "1", "cos(x)", "sin(x)", "e^x"]
            func = random.choice(funcs)
            if func == "2x":
                question = "∫ 2x dx"
                result = "x² + C"
            elif func == "x²":
                question = "∫ x² dx"
                result = "x³/3 + C"
            elif func == "1":
                question = "∫ 1 dx"
                result = "x + C"
            elif func == "cos(x)":
                question = "∫ cos(x) dx"
                result = "sin(x) + C"
            elif func == "sin(x)":
                question = "∫ sin(x) dx"
                result = "-cos(x) + C"
            else:
                question = "∫ e^x dx"
                result = "e^x + C"
               
        elif q_type == "equation_diff":
            types = ["y' = y", "y' = -y", "y' = 2y"]
            eq_type = random.choice(types)
            if eq_type == "y' = y":
                question = "Solution de y' = y"
                result = "y = Ce^x"
            elif eq_type == "y' = -y":
                question = "Solution de y' = -y"
                result = "y = Ce^(-x)"
            else:
                question = "Solution de y' = 2y"
                result = "y = Ce^(2x)"
               
        elif q_type == "logarithme":
            question = "Résoudre : ln(x) = 1"
            result = "e"
           
        elif q_type == "exponentielle":
            question = "Résoudre : e^x = 1"
            result = "0"
           
        elif q_type == "trigonometrie":
            question = "cos(π/3) = ?"
            result = "1/2"
           
        else: # probabilite
            question = "Probabilité d'obtenir un 6 avec un dé équilibré"
            result = "1/6"
       
        answers = [result]
        wrong_answers = {
            "2x": ["x²", "2", "x", "2x²"],
            "1/(2√x)": ["√x", "1/√x", "2√x", "x/2"],
            "-1/x²": ["1/x²", "ln|x|", "x", "-x"],
            "cos(x)": ["-cos(x)", "sin(x)", "-sin(x)", "1"],
            "-sin(x)": ["sin(x)", "cos(x)", "-cos(x)", "0"],
            "e^x": ["xe^x", "ln(x)", "1", "0"],
            "1/x": ["-1/x", "ln(x)", "x", "0"],
            "x² + C": ["2x + C", "x²", "2 + C", "x³/3 + C"],
            "x³/3 + C": ["3x² + C", "x²/2 + C", "x³ + C", "x⁴/4 + C"],
            "x + C": ["1 + C", "0 + C", "C", "x²/2 + C"],
            "sin(x) + C": ["-sin(x) + C", "cos(x) + C", "-cos(x) + C", "tan(x) + C"],
            "-cos(x) + C": ["cos(x) + C", "sin(x) + C", "-sin(x) + C", "cot(x) + C"],
            "e^x + C": ["xe^x + C", "ln|x| + C", "1 + C", "e^(x+1) + C"],
            "y = Ce^x": ["y = e^x", "y = Cx", "y = ln|x| + C", "y = x² + C"],
            "y = Ce^(-x)": ["y = e^(-x)", "y = -Cx", "y = -ln|x| + C", "y = -x² + C"],
            "y = Ce^(2x)": ["y = e^(2x)", "y = 2Cx", "y = 2ln|x| + C", "y = 2x² + C"],
            "e": ["1", "0", "2", "10"],
            "0": ["1", "-1", "e", "∞"],
            "1/2": ["√3/2", "√2/2", "1", "0"],
            "1/6": ["1/3", "1/2", "5/6", "0.166"]
        }
       
        while len(answers) < 4:
            wrong_list = wrong_answers.get(result, [f"Option {len(answers)}", f"Réponse {len(answers)}", f"Solution {len(answers)}"])
            wrong = random.choice(wrong_list)
            if wrong not in answers:
                answers.append(wrong)
       
        random.shuffle(answers)
        correct_index = answers.index(result)
       
        return {
            "question": question,
            "answers": answers,
            "correct": correct_index,
            "level": "lycée",
            "points": 20
        }
   
    def generate_universitaire_question(self):
        question_types = [
            "suite", "ensemble", "mesure", "fourier", "algebre",
            "analyse", "topologie", "statistique"
        ]
        q_type = random.choice(question_types)
       
        if q_type == "suite":
            question = "La suite uₙ = (-1)ⁿ est :"
            result = "Bornée mais non convergente"
           
        elif q_type == "ensemble":
            question = "L'ensemble {x ∈ ℝ | x² < 4} est :"
            result = "]-2, 2["
           
        elif q_type == "mesure":
            question = "La mesure de Lebesgue de ℚ ∩ [0,1] est :"
            result = "0"
           
        elif q_type == "fourier":
            question = "La transformée de Fourier de f(x) = cos(2πx) est :"
            result = "(δ(ω-2π) + δ(ω+2π))/2"
           
        elif q_type == "algebre":
            question = "Le groupe (ℤ, +) est :"
            result = "Abélien infini"
           
        elif q_type == "analyse":
            question = "La fonction f(x) = |x| est :"
            result = "Continue mais non dérivable en 0"
           
        elif q_type == "topologie":
            question = "Un ensemble fini dans ℝ est :"
            result = "Compact"
           
        else: # statistique
            question = "L'espérance d'une variable aléatoire constante c est :"
            result = "c"
       
        answers = [result]
        wrong_answers = {
            "Bornée mais non convergente": ["Convergente", "Divergente", "Croissante", "Décroissante"],
            "]-2, 2[": ["[-2, 2]", "[0, 4]", "]-∞, ∞[", "]-4, 4]"],
            "0": ["1", "0.5", "∞", "0.25"],
            "(δ(ω-2π) + δ(ω+2π))/2": ["δ(ω)", "sin(2πω)", "1/(2π)", "e^(i2πω)"],
            "Abélien infini": ["Non abélien", "Fini", "Cyclique", "Simple"],
            "Continue mais non dérivable en 0": ["Dérivable partout", "Discontinue en 0", "Analytique", "Linéaire"],
            "Compact": ["Ouvert", "Non borné", "Dense", "Convexe"],
            "c": ["0", "1", "c²", "1/c"]
        }
       
        while len(answers) < 4:
            wrong_list = wrong_answers.get(result, [f"Proposition {len(answers)}", f"Théorie {len(answers)}", f"Concept {len(answers)}"])
            wrong = random.choice(wrong_list)
            if wrong not in answers:
                answers.append(wrong)
       
        random.shuffle(answers)
        correct_index = answers.index(result)
       
        return {
            "question": question,
            "answers": answers,
            "correct": correct_index,
            "level": "universitaire",
            "points": 30
        }
   
    def submit_answer(self, answer_index):
        self.user_answer = int(answer_index)
        self.is_answered = True
       
        is_correct = (self.user_answer == self.correct_answer)
       
        if is_correct:
            self.feedback_message = random.choice([
                "🎉 Excellent ! Vous êtes très intelligent !",
                "🌟 Bravo ! Réponse parfaite !",
                "💫 Formidable ! Vous maîtrisez parfaitement !",
                "🚀 Impressionnant ! Continuez comme ça !",
                "🏆 Génial ! Votre raisonnement est excellent !"
            ])
        else:
            self.feedback_message = random.choice([
                "💡 Presque ! Continuez à vous exercer.",
                "📚 Pas tout à fait, mais ne vous découragez pas !",
                "🎯 Bonne tentative ! La prochaine sera la bonne.",
                "🔍 Attention au raisonnement, vous y êtes presque !",
                "💪 Ce n'est pas ça, mais persévérez !"
            ])
       
        return is_correct
   
    def check_and_score_question(self):
        """Vérifie la réponse et score à la fin du timer"""
        negative_feedbacks = [
            "💡 Presque ! Continuez à vous exercer.",
            "📚 Pas tout à fait, mais ne vous découragez pas !",
            "🎯 Bonne tentative ! La prochaine sera la bonne.",
            "🔍 Attention au raisonnement, vous y êtes presque !",
            "💪 Ce n'est pas ça, mais persévérez !"
        ]
        if self.user_answer is not None:
            is_correct = (self.user_answer == self.correct_answer)
            if is_correct:
                self.user_score += self.current_question["points"]
                return True, self.current_question["points"]
            else:
                self.feedback_message = random.choice(negative_feedbacks)
                return False, 0
        else:
            # Pas de réponse fournie
            self.feedback_message = random.choice(negative_feedbacks)
            return False, 0

quiz_manager = QuizManager()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quiz Mathématique - Site en Développement</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
       
        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: white;
            min-height: 100vh;
            padding: 20px;
        }
       
        .development-banner {
            background: linear-gradient(90deg, #ff6b6b, #ffa726);
            color: white;
            text-align: center;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 10px;
            font-weight: bold;
            font-size: 1.2rem;
            box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        }
       
        .container {
            max-width: 1000px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
       
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
       
        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #4facfe, #00f2fe);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        }
       
        .subtitle {
            font-size: 1.2rem;
            opacity: 0.8;
            margin-bottom: 20px;
        }
       
        .stats {
            display: flex;
            justify-content: space-around;
            background: rgba(255, 255, 255, 0.08);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
       
        .stat-item {
            text-align: center;
            flex: 1;
        }
       
        .stat-label {
            font-size: 0.9rem;
            opacity: 0.8;
            margin-bottom: 5px;
        }
       
        .stat-value {
            font-size: 1.8rem;
            font-weight: bold;
            color: #00f2fe;
        }
       
        .quiz-container {
            background: rgba(255, 255, 255, 0.08);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
       
        .question-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 10px;
        }
       
        .level-badge {
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
       
        .level-college {
            background: linear-gradient(90deg, #4CAF50, #45a049);
            box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        }
        .level-lycee {
            background: linear-gradient(90deg, #FF9800, #f57c00);
            box-shadow: 0 4px 15px rgba(255, 152, 0, 0.3);
        }
        .level-universitaire {
            background: linear-gradient(90deg, #f44336, #d32f2f);
            box-shadow: 0 4px 15px rgba(244, 67, 54, 0.3);
        }
       
        .timer-container {
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 1.1rem;
        }
       
        .timer {
            font-weight: bold;
            color: #ffa726;
        }
       
        .question-text {
            font-size: 1.4rem;
            margin-bottom: 30px;
            text-align: center;
            line-height: 1.5;
            padding: 20px;
            background: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
            border-left: 4px solid #4facfe;
        }
       
        .answers-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
            margin-bottom: 25px;
        }
       
        @media (max-width: 768px) {
            .answers-grid {
                grid-template-columns: 1fr;
            }
        }
       
        .answer-btn {
            background: rgba(255, 255, 255, 0.1);
            border: 2px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            padding: 20px;
            color: white;
            font-size: 1.1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: left;
        }
       
        .answer-btn:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
            border-color: rgba(255, 255, 255, 0.3);
        }
       
        .answer-btn.selected {
            background: rgba(79, 172, 254, 0.2);
            border-color: #4facfe;
            transform: translateY(-2px);
        }
       
        .answer-btn.correct {
            background: rgba(76, 175, 80, 0.3) !important;
            border-color: #4CAF50 !important;
        }
       
        .answer-btn.incorrect {
            background: rgba(244, 67, 54, 0.3) !important;
            border-color: #f44336 !important;
        }
       
        .answer-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
       
        .answer-btn:disabled:hover {
            background: rgba(255, 255, 255, 0.1);
            transform: none;
        }
       
        .feedback-container {
            margin-top: 25px;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            font-size: 1.2rem;
            display: none;
            border: 2px solid transparent;
        }
       
        .feedback-container.show {
            display: block;
            animation: fadeIn 0.5s ease;
        }
       
        .feedback-correct {
            background: rgba(76, 175, 80, 0.15);
            border-color: #4CAF50;
            color: #a5d6a7;
        }
       
        .feedback-incorrect {
            background: rgba(244, 67, 54, 0.15);
            border-color: #f44336;
            color: #ef9a9a;
        }
       
        .progress-container {
            margin: 25px 0;
        }
       
        .progress-bar {
            width: 100%;
            height: 10px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            overflow: hidden;
        }
       
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ffa726);
            border-radius: 5px;
            transition: width 1s linear;
            width: 100%;
        }
       
        .points-earned {
            text-align: center;
            font-size: 1.1rem;
            margin-top: 10px;
            color: #ffa726;
            display: none;
        }
       
        .points-earned.show {
            display: block;
            animation: bounce 0.5s ease;
        }
       
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
       
        @keyframes bounce {
            0%, 20%, 50%, 80%, 100% {transform: translateY(0);}
            40% {transform: translateY(-10px);}
            60% {transform: translateY(-5px);}
        }
       
        .next-question-info {
            text-align: center;
            margin-top: 20px;
            font-size: 1rem;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="development-banner">
        🚧 Site en Cours de Développement - Version Beta 🚧
    </div>
   
    <div class="container">
        <div class="header">
            <h1>Plateforme d'Apprentissage de Mathématiques</h1>
            <div class="subtitle">Quiz Mathématique Interactif - Testez vos connaissances !</div>
        </div>
       
        <div class="stats">
            <div class="stat-item">
                <div class="stat-label">Score Total</div>
                <div class="stat-value" id="totalScore">0</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Niveau Actuel</div>
                <div class="stat-value" id="currentLevel">-</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Points Possible</div>
                <div class="stat-value" id="questionPoints">0</div>
            </div>
        </div>
       
        <div class="quiz-container">
            <div class="question-header">
                <div class="level-badge" id="levelBadge">Niveau</div>
                <div class="timer-container">
                    ⏱️ Temps restant : <span class="timer" id="timeLeft">30s</span>
                </div>
            </div>
           
            <div class="progress-container">
                <div class="progress-bar">
                    <div class="progress-fill" id="progressFill"></div>
                </div>
            </div>
           
            <div class="question-text" id="questionText">
                Chargement de la question...
            </div>
           
            <div class="answers-grid" id="answersGrid">
                <!-- Les réponses seront ajoutées ici par JavaScript -->
            </div>
           
            <div class="points-earned" id="pointsEarned">
                <!-- Points gagnés affichés ici -->
            </div>
           
            <div class="feedback-container" id="feedback">
                <!-- Feedback sera ajouté ici -->
            </div>
           
            <div class="next-question-info">
                Prochaine question dans : <span id="nextQuestionTimer">30</span> secondes
            </div>
        </div>
    </div>
    <script>
        let currentQuestion = null;
        let selectedAnswer = null;
        let timeLeft = 30;
        let timerInterval = null;
        let isQuestionActive = true;
       
        function loadQuestion() {
            fetch('/get_question')
                .then(response => response.json())
                .then(data => {
                    currentQuestion = data;
                    updateDisplay();
                    startTimer();
                    resetQuestionState();
                });
        }
       
        function updateDisplay() {
            // Mettre à jour le texte de la question
            document.getElementById('questionText').textContent = currentQuestion.question;
           
            // Mettre à jour le niveau et les points
            document.getElementById('currentLevel').textContent =
                currentQuestion.level.charAt(0).toUpperCase() + currentQuestion.level.slice(1);
            document.getElementById('questionPoints').textContent = currentQuestion.points;
           
            // Mettre à jour le badge de niveau
            const levelBadge = document.getElementById('levelBadge');
            levelBadge.textContent = currentQuestion.level.charAt(0).toUpperCase() + currentQuestion.level.slice(1);
            levelBadge.className = 'level-badge level-' + currentQuestion.level;
           
            // Mettre à jour les réponses
            const answersGrid = document.getElementById('answersGrid');
            answersGrid.innerHTML = '';
           
            currentQuestion.answers.forEach((answer, index) => {
                const button = document.createElement('button');
                button.className = 'answer-btn';
                button.textContent = answer;
                button.onclick = () => selectAnswer(index);
                answersGrid.appendChild(button);
            });
        }
       
        function selectAnswer(index) {
            if (!isQuestionActive) return;
           
            selectedAnswer = index;
           
            // Mettre en surbrillance la réponse sélectionnée
            const buttons = document.querySelectorAll('.answer-btn');
            buttons.forEach((btn, i) => {
                btn.classList.toggle('selected', i === index);
                btn.disabled = true; // Désactiver tous les boutons après sélection
            });
           
            // Enregistrer la réponse
            fetch('/submit_answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({answer: index})
            });
           
            isQuestionActive = false;
        }
       
        function resetQuestionState() {
            selectedAnswer = null;
            isQuestionActive = true;
            document.getElementById('feedback').className = 'feedback-container';
            document.getElementById('pointsEarned').className = 'points-earned';
            const buttons = document.querySelectorAll('.answer-btn');
            buttons.forEach(btn => {
                btn.disabled = false;
                btn.classList.remove('selected', 'correct', 'incorrect');
            });
        }
       
        function showResults() {
            fetch('/check_answer')
                .then(response => response.json())
                .then(data => {
                    const feedback = document.getElementById('feedback');
                    const pointsEarned = document.getElementById('pointsEarned');
                   
                    if (data.correct) {
                        feedback.className = 'feedback-container feedback-correct show';
                        pointsEarned.className = 'points-earned show';
                        pointsEarned.textContent = `+${data.points_earned} points gagnés !`;
                    } else {
                        feedback.className = 'feedback-container feedback-incorrect show';
                        pointsEarned.className = 'points-earned';
                    }
                   
                    feedback.textContent = data.feedback;
                   
                    // Mettre à jour le score total
                    document.getElementById('totalScore').textContent = data.total_score;
                   
                    // Highlight correct and incorrect answers
                    const buttons = document.querySelectorAll('.answer-btn');
                    buttons.forEach((btn, i) => {
                        if (i === currentQuestion.correct) {
                            btn.classList.add('correct');
                        } else if (selectedAnswer !== null && i === selectedAnswer) {
                            btn.classList.add('incorrect');
                        }
                    });
                });
        }
       
        function startTimer() {
            timeLeft = 30;
            clearInterval(timerInterval);
           
            timerInterval = setInterval(() => {
                timeLeft--;
                document.getElementById('timeLeft').textContent = timeLeft + 's';
                document.getElementById('nextQuestionTimer').textContent = timeLeft;
               
                // Mettre à jour la barre de progression
                const progressPercent = (timeLeft / 30) * 100;
                document.getElementById('progressFill').style.width = progressPercent + '%';
               
                if (timeLeft <= 0) {
                    clearInterval(timerInterval);
                    isQuestionActive = false;
                    // Disable buttons
                    const buttons = document.querySelectorAll('.answer-btn');
                    buttons.forEach(btn => btn.disabled = true);
                    showResults(); // Afficher les résultats
                    setTimeout(() => {
                        loadQuestion(); // Charger une nouvelle question après 3 secondes
                    }, 3000);
                }
            }, 1000);
        }
       
        // Charger la première question au démarrage
        loadQuestion();
       
        // Mettre à jour le score initial
        fetch('/get_score')
            .then(response => response.json())
            .then(data => {
                document.getElementById('totalScore').textContent = data.score;
            });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_question')
def get_question():
    quiz_manager.generate_new_question()
    return jsonify(quiz_manager.current_question)

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    data = request.json
    quiz_manager.submit_answer(data['answer'])
    return jsonify({'status': 'answer_submitted'})

@app.route('/check_answer')
def check_answer():
    is_correct, points_earned = quiz_manager.check_and_score_question()
    return jsonify({
        'correct': is_correct,
        'points_earned': points_earned,
        'total_score': quiz_manager.user_score,
        'feedback': quiz_manager.feedback_message
    })

@app.route('/get_score')
def get_score():
    return jsonify({'score': quiz_manager.user_score})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
