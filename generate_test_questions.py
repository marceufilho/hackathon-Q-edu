"""
Gera um banco completo de questões de teste para todos os tópicos
"""

import json
from question_bank import LinearEquationGenerator, QuestionGenerator, Difficulty

def generate_comprehensive_question_bank():
    """Gera questões para todos os tópicos e dificuldades"""

    question_bank = {
        "metadata": {
            "total_questions": 0,
            "created_at": "2025-01-08",
            "description": "Banco de questões completo para sistema adaptativo"
        },
        "questions_by_topic": {}
    }

    # Definir tipos de questões por tópico
    topic_generators = {
        "operacoes_basicas": {
            "name": "Operações Básicas",
            "generator": QuestionGenerator.generate_basic_operations,
            "questions_per_difficulty": 10
        },
        "numeros_inteiros": {
            "name": "Números Inteiros",
            "generator": QuestionGenerator.generate_integers,
            "questions_per_difficulty": 10
        },
        "variaveis_expressoes": {
            "name": "Variáveis e Expressões",
            "generator": QuestionGenerator.generate_variables_expressions,
            "questions_per_difficulty": 10
        },
        "simplificacao_algebrica": {
            "name": "Simplificação Algébrica",
            "generator": QuestionGenerator.generate_algebraic_simplification,
            "questions_per_difficulty": 10
        },
        "operacoes_inversas": {
            "name": "Operações Inversas",
            "generator": QuestionGenerator.generate_inverse_operations,
            "questions_per_difficulty": 10
        },
        "equacoes_lineares_uma_etapa": {
            "name": "Equações Lineares - Uma Etapa",
            "generator": LinearEquationGenerator.generate_one_step,
            "questions_per_difficulty": 15
        },
        "equacoes_lineares_duas_etapas": {
            "name": "Equações Lineares - Duas Etapas",
            "generator": LinearEquationGenerator.generate_two_step,
            "questions_per_difficulty": 15
        },
        "equacoes_lineares_variaveis_ambos_lados": {
            "name": "Equações Lineares - Variáveis em Ambos os Lados",
            "generator": LinearEquationGenerator.generate_variables_both_sides,
            "questions_per_difficulty": 15
        }
    }

    total_questions = 0

    print("Gerando banco de questões...\n")

    for topic_id, config in topic_generators.items():
        print(f"📚 Tópico: {config['name']}")

        topic_questions = {
            "topic_id": topic_id,
            "topic_name": config["name"],
            "questions": {
                "easy": [],
                "medium": [],
                "hard": []
            },
            "total": 0
        }

        # Gerar questões para cada dificuldade
        for difficulty in [Difficulty.EASY, Difficulty.MEDIUM, Difficulty.HARD]:
            count = config["questions_per_difficulty"]

            print(f"  - Gerando {count} questões de dificuldade {difficulty.value}...")

            for i in range(count):
                try:
                    question = config["generator"](difficulty)

                    # Adicionar ID e metadados
                    question["id"] = f"{topic_id}_{difficulty.value}_{i+1}"
                    question["topic_id"] = topic_id

                    topic_questions["questions"][difficulty.value].append(question)
                    total_questions += 1

                except Exception as e:
                    print(f"    ⚠️  Erro ao gerar questão {i+1}: {str(e)}")

        topic_questions["total"] = sum(
            len(topic_questions["questions"][diff])
            for diff in ["easy", "medium", "hard"]
        )

        print(f"  ✓ {topic_questions['total']} questões geradas\n")

        question_bank["questions_by_topic"][topic_id] = topic_questions

    question_bank["metadata"]["total_questions"] = total_questions

    return question_bank


def save_question_bank(question_bank, filename="test_question_bank.json"):
    """Salva o banco de questões em arquivo JSON"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(question_bank, f, indent=2, ensure_ascii=False)

    print(f"✓ Banco de questões salvo em: {filename}")


def print_summary(question_bank):
    """Imprime resumo do banco de questões"""
    print("\n" + "="*60)
    print("RESUMO DO BANCO DE QUESTÕES")
    print("="*60)

    print(f"\nTotal de questões: {question_bank['metadata']['total_questions']}")
    print(f"\nQuestões por tópico:")

    for topic_id, data in question_bank["questions_by_topic"].items():
        print(f"\n  {data['topic_name']} ({topic_id})")
        print(f"    Total: {data['total']} questões")
        print(f"    - Fácil: {len(data['questions']['easy'])}")
        print(f"    - Médio: {len(data['questions']['medium'])}")
        print(f"    - Difícil: {len(data['questions']['hard'])}")


def show_sample_questions(question_bank, samples_per_topic=2):
    """Mostra exemplos de questões geradas"""
    print("\n" + "="*60)
    print("EXEMPLOS DE QUESTÕES GERADAS")
    print("="*60)

    for topic_id, data in question_bank["questions_by_topic"].items():
        print(f"\n📚 {data['topic_name']}")

        # Mostrar 2 exemplos de cada dificuldade
        for difficulty in ["easy", "medium", "hard"]:
            questions = data["questions"][difficulty][:samples_per_topic]

            if questions:
                print(f"\n  Dificuldade: {difficulty.upper()}")

                for i, q in enumerate(questions, 1):
                    print(f"\n  Exemplo {i}:")
                    print(f"    Problema: {q['problem']}")
                    print(f"    Resposta: {q['answer']}")
                    if len(q.get('steps', [])) <= 3:
                        print(f"    Passos: {' → '.join(q.get('steps', []))}")


def test_all_generators():
    """Testa todos os geradores de questões"""
    print("="*60)
    print("TESTANDO GERADORES DE QUESTÕES")
    print("="*60 + "\n")

    generators = [
        ("Operações Básicas", QuestionGenerator.generate_basic_operations),
        ("Números Inteiros", QuestionGenerator.generate_integers),
        ("Variáveis e Expressões", QuestionGenerator.generate_variables_expressions),
        ("Simplificação Algébrica", QuestionGenerator.generate_algebraic_simplification),
        ("Operações Inversas", QuestionGenerator.generate_inverse_operations),
        ("Equações Lineares (1 Etapa)", LinearEquationGenerator.generate_one_step),
        ("Equações Lineares (2 Etapas)", LinearEquationGenerator.generate_two_step),
        ("Equações Lineares (Variáveis Ambos Lados)", LinearEquationGenerator.generate_variables_both_sides),
    ]

    all_passed = True

    for name, generator in generators:
        try:
            # Testar com dificuldade média
            question = generator(Difficulty.MEDIUM)

            # Verificar campos obrigatórios
            required_fields = ["problem", "answer", "steps", "difficulty", "type", "topic"]
            missing_fields = [f for f in required_fields if f not in question]

            if missing_fields:
                print(f"❌ {name}: Campos faltando: {missing_fields}")
                all_passed = False
            else:
                print(f"✓ {name}")
                print(f"  Problema: {question['problem'][:60]}...")

        except Exception as e:
            print(f"❌ {name}: Erro - {str(e)}")
            all_passed = False

    print()
    if all_passed:
        print("🎉 Todos os geradores funcionando corretamente!")
    else:
        print("⚠️  Alguns geradores apresentaram problemas.")

    return all_passed


def main():
    print("\n" + "="*60)
    print("  GERADOR DE BANCO DE QUESTÕES DE TESTE")
    print("="*60 + "\n")

    # Testar geradores primeiro
    if not test_all_generators():
        print("\n⚠️  Corrija os erros antes de gerar o banco completo.")
        return

    # Gerar banco de questões
    print("\n")
    question_bank = generate_comprehensive_question_bank()

    # Salvar em arquivo
    save_question_bank(question_bank)

    # Mostrar resumo
    print_summary(question_bank)

    # Mostrar exemplos
    show_sample_questions(question_bank, samples_per_topic=1)

    print("\n" + "="*60)
    print(f"✅ Banco de questões criado com sucesso!")
    print(f"   Total: {question_bank['metadata']['total_questions']} questões")
    print(f"   Arquivo: test_question_bank.json")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
