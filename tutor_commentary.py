"""
Tutor Commentary Generator

Generates contextual tutor messages for the adaptive learning interface.
Provides greetings, feedback, progressive hints, and encouragement.
"""

import random
from typing import Dict, List


class TutorCommentary:
    """Generates tutor messages for adaptive learning"""

    # Greeting templates for new questions
    GREETINGS = [
        "Ótimo! Vamos resolver esta questão juntos. {question_type}",
        "Legal! Aqui está o próximo desafio. {question_type}",
        "Vamos lá! {question_type}",
        "Preparado? {question_type}",
        "Bora começar! {question_type}",
    ]

    # Question type hints for greetings
    QUESTION_HINTS = {
        "one_step": "Esta é uma equação de uma etapa. Você consegue resolver sozinho?",
        "two_step": "Esta equação tem dois passos. Pense em qual operação fazer primeiro.",
        "variables_both_sides": "Vejo variáveis dos dois lados! Como podemos simplificar isso?",
        "basic_operations": "Operações básicas! Você sabe isso.",
        "integers": "Números inteiros. Cuidado com os sinais!",
        "variables_expressions": "Vamos trabalhar com variáveis. Lembre-se de substituir!",
        "algebraic_simplification": "Simplificar! Procure termos semelhantes.",
        "inverse_operations": "Operações inversas. O que 'desfaz' esta operação?",
    }

    # Correct answer responses
    CORRECT_RESPONSES = [
        "✓ Perfeito! Você entendeu bem. {explanation}",
        "✓ Excelente! Isso mesmo. {explanation}",
        "✓ Muito bem! Resposta correta. {explanation}",
        "✓ Mandou bem! {explanation}",
        "✓ Isso aí! Continue assim. {explanation}",
    ]

    # Incorrect answer responses
    INCORRECT_RESPONSES = [
        "Não foi dessa vez, mas vamos aprender com isso. {explanation}",
        "Hmm, não é bem assim. Deixa eu te ajudar. {explanation}",
        "Quase! Mas há um detalhe. {explanation}",
        "Não se preocupe, errar faz parte. Vamos ver juntos. {explanation}",
        "Ops! Vamos revisar. {explanation}",
    ]

    # Encouragement messages
    ENCOURAGEMENTS = {
        "streak_3": "🔥 Três seguidas! Você está pegando o jeito!",
        "streak_5": "🔥🔥 Cinco acertos! Excelente sequência!",
        "streak_10": "🔥🔥🔥 DEZ SEGUIDAS! Você é fera!",
        "first_try": "De primeira! Muito bom!",
        "improvement": "Vi que você está melhorando! Continue assim!",
        "mastery_close": "Está quase dominando este tópico!",
    }

    # Hint templates by level
    HINT_TEMPLATES = {
        1: {  # Gentle hints
            "one_step": [
                "Pense: qual operação está sendo feita com x?",
                "O que você precisa fazer para isolar x?",
                "Qual é a operação inversa aqui?",
            ],
            "two_step": [
                "Que tal começar resolvendo o termo constante primeiro?",
                "Pense em duas etapas: primeiro o termo sem x, depois o coeficiente.",
                "Qual parte você consegue resolver primeiro?",
            ],
            "variables_both_sides": [
                "E se você juntasse todos os x de um lado só?",
                "Pense: como trazer todas as variáveis para o mesmo lado?",
                "Você pode mover os termos com x para a esquerda.",
            ],
        },
        2: {  # Specific hints
            "one_step": [
                "Se tem x + {num}, você deve subtrair {num} dos dois lados.",
                "Para desfazer a multiplicação por {num}, divida ambos os lados.",
                "Use a operação inversa: {operation}.",
            ],
            "two_step": [
                "Primeiro, elimine o {constant} usando {operation}.",
                "Depois de remover {constant}, você terá {coefficient}x = algo.",
                "Etapa 1: {step1}. Etapa 2: {step2}.",
            ],
            "variables_both_sides": [
                "Subtraia {term} de ambos os lados para juntar os x.",
                "Mova {term} para a esquerda. O que sobra?",
                "Depois de mover os x, você terá uma equação mais simples.",
            ],
        },
        3: {  # Directive hints
            "one_step": [
                "Faça: {step}. Isso dará x = {answer}.",
                "Execute esta operação: {operation}. Resultado: x = {answer}.",
                "Passo a passo: {detailed_step}",
            ],
            "two_step": [
                "Passo 1: {step1}. Você obtém: {intermediate}.",
                "Passo 2: {step2}. Resultado final: x = {answer}.",
                "Siga: {step1}, depois {step2}.",
            ],
            "variables_both_sides": [
                "1) {step1} → você terá: {result1}",
                "2) {step2} → você terá: {result2}",
                "3) {step3} → resposta: x = {answer}",
            ],
        },
    }

    @staticmethod
    def generate_greeting(question: Dict) -> str:
        """
        Generate greeting message when presenting a new question

        Args:
            question: Question dictionary

        Returns:
            Greeting message
        """
        question_type = question.get("type", "one_step")
        hint = TutorCommentary.QUESTION_HINTS.get(question_type, "Vamos ver o que conseguimos fazer!")

        template = random.choice(TutorCommentary.GREETINGS)
        return template.format(question_type=hint)

    @staticmethod
    def generate_commentary(is_correct: bool, question: Dict, student_answer: str, error_analysis: Dict = None) -> str:
        """
        Generate commentary after student submits answer

        Args:
            is_correct: Whether answer was correct
            question: Question dictionary
            student_answer: What the student answered
            error_analysis: Error analysis from error_analyzer (if incorrect)

        Returns:
            Commentary message
        """
        if is_correct:
            explanations = [
                "Você aplicou o conceito perfeitamente!",
                "Segui o raciocínio e estava certo!",
                "Dominou essa!",
                "Processo correto, resultado correto!",
                "Isso mostra que você entendeu o conceito!",
            ]
            template = random.choice(TutorCommentary.CORRECT_RESPONSES)
            explanation = random.choice(explanations)
            return template.format(explanation=explanation)
        else:
            # Use error analysis to give specific feedback
            if error_analysis:
                error_type = error_analysis.get("error_type", "unknown")
                explanation_texts = {
                    "conceptual": "Parece que há uma confusão no conceito. Vamos revisar a ideia fundamental.",
                    "procedural": "O conceito você sabe, mas os passos ficaram trocados. Vamos organizar!",
                    "arithmetic": "Foi um erro de cálculo. Você sabe fazer, só revise a conta!",
                    "careless": "Opa, erro bobo! Você sabe isso. Concentração!",
                }
                explanation = explanation_texts.get(error_type, "Vamos analisar onde foi o erro.")

                # Add specific concept feedback
                if error_analysis.get("affected_concepts"):
                    concepts = error_analysis["affected_concepts"][:1]
                    explanation += f" Revise: {', '.join(concepts)}."
            else:
                explanation = f"A resposta correta é {question.get('answer')}. Vamos ver por quê."

            template = random.choice(TutorCommentary.INCORRECT_RESPONSES)
            return template.format(explanation=explanation)

    @staticmethod
    def generate_progressive_hint(question: Dict, hint_level: int) -> Dict:
        """
        Generate progressive hint based on level (1, 2, or 3)

        Args:
            question: Question dictionary
            hint_level: 1 (gentle), 2 (specific), or 3 (directive)

        Returns:
            Dictionary with hint message and level info
        """
        question_type = question.get("type", "one_step")
        hints_for_type = TutorCommentary.HINT_TEMPLATES.get(hint_level, {})

        # Get hints for this question type, or use generic ones
        hint_options = hints_for_type.get(question_type, hints_for_type.get("one_step", []))

        if not hint_options:
            # Fallback hints
            fallback_hints = {
                1: "Pense sobre qual operação ajudaria a resolver isso.",
                2: "Tente aplicar a operação inversa.",
                3: f"A resposta é {question.get('answer')}. Veja os passos da solução.",
            }
            hint_message = fallback_hints.get(hint_level, "Continue tentando!")
        else:
            hint_message = random.choice(hint_options)

        # Try to fill in placeholders with question data
        try:
            # Extract numbers and operations from question for more specific hints
            equation = question.get("equation", "")
            answer = question.get("answer", "?")

            hint_message = hint_message.format(
                answer=answer,
                num=answer,
                operation="operação inversa",
                step="resolva a equação",
                step1="primeiro passo",
                step2="segundo passo",
                constant="termo constante",
                coefficient="coeficiente",
                term="termo",
                intermediate="resultado intermediário",
                result1="resultado 1",
                result2="resultado 2",
                detailed_step="siga os passos da solução",
            )
        except (KeyError, IndexError):
            # If formatting fails, use hint as is
            pass

        level_names = {1: "Dica Suave", 2: "Dica Específica", 3: "Dica Diretiva"}

        return {
            "hint": hint_message,
            "level": hint_level,
            "level_name": level_names.get(hint_level, "Dica"),
            "max_level": 3,
        }

    @staticmethod
    def generate_encouragement(context: Dict) -> str:
        """
        Generate encouraging message based on student performance

        Args:
            context: Dictionary with:
                - streak: Number of correct answers in a row
                - first_try: Boolean if first try was correct
                - improvement: Boolean if showing improvement
                - mastery_close: Boolean if close to mastery

        Returns:
            Encouragement message
        """
        streak = context.get("streak", 0)
        first_try = context.get("first_try", False)
        improvement = context.get("improvement", False)
        mastery_close = context.get("mastery_close", False)

        # Check for streaks first
        if streak >= 10:
            return TutorCommentary.ENCOURAGEMENTS["streak_10"]
        elif streak >= 5:
            return TutorCommentary.ENCOURAGEMENTS["streak_5"]
        elif streak >= 3:
            return TutorCommentary.ENCOURAGEMENTS["streak_3"]

        # Other encouragements
        if first_try:
            return TutorCommentary.ENCOURAGEMENTS["first_try"]
        if mastery_close:
            return TutorCommentary.ENCOURAGEMENTS["mastery_close"]
        if improvement:
            return TutorCommentary.ENCOURAGEMENTS["improvement"]

        # Default encouragement
        return "Você está no caminho certo!"

    @staticmethod
    def generate_topic_intro(topic_name: str, topic_description: str) -> str:
        """
        Generate introduction when student starts a new topic

        Args:
            topic_name: Name of the topic
            topic_description: Description of the topic

        Returns:
            Introduction message
        """
        intros = [
            f"Bem-vindo ao tópico '{topic_name}'! {topic_description}",
            f"Vamos estudar '{topic_name}' agora. {topic_description}",
            f"Novo tópico: '{topic_name}'. {topic_description} Preparado?",
            f"Hora de '{topic_name}'! {topic_description} Vamos lá!",
        ]

        return random.choice(intros)

    @staticmethod
    def generate_mastery_celebration(topic_name: str) -> str:
        """
        Generate celebration message when topic is mastered

        Args:
            topic_name: Name of the mastered topic

        Returns:
            Celebration message
        """
        celebrations = [
            f"🎉 PARABÉNS! Você dominou '{topic_name}'! Isso é incrível!",
            f"🏆 Domínio alcançado em '{topic_name}'! Você é fera!",
            f"🎊 WOW! '{topic_name}' completamente dominado! Orgulho!",
            f"⭐ Excelente! '{topic_name}' está no bolso! Próximo desafio?",
        ]

        return random.choice(celebrations)
