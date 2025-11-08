"""
Test script for the adaptive learning system

Tests the complete flow:
1. Diagnostic test
2. Adaptive learning session
3. Progress tracking
"""

import requests
import json

BASE_URL = "http://localhost:5000"
STUDENT_ID = "test_student_001"


def print_section(title):
    """Print section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_diagnostic():
    """Test diagnostic flow"""
    print_section("TESTE DIAGNÓSTICO")

    # 1. Start diagnostic
    print("\n1. Iniciando teste diagnóstico...")
    response = requests.post(
        f"{BASE_URL}/diagnostic/start",
        json={"student_id": STUDENT_ID, "questions_per_topic": 2}
    )

    if response.status_code != 201:
        print(f"❌ Erro ao iniciar diagnóstico: {response.json()}")
        return False

    result = response.json()
    print(f"✓ Diagnóstico iniciado: {result['total_questions']} questões")

    # 2. Get and answer diagnostic questions
    questions_answered = 0

    while questions_answered < result['total_questions']:
        # Get next question
        response = requests.get(f"{BASE_URL}/diagnostic/{STUDENT_ID}/next")

        if response.status_code != 200:
            print(f"❌ Erro ao obter próxima questão: {response.json()}")
            break

        data = response.json()

        if data.get('status') == 'test_completed':
            print("\n✓ Teste diagnóstico completo!")
            print(f"\nResultados:")
            results = data.get('diagnostic_results', {})
            print(f"  Acurácia geral: {results.get('overall_accuracy', 0):.1%}")
            print(f"  Caminho recomendado: {results.get('recommended_path', {}).get('path_title', 'N/A')}")
            print(f"  Tópicos dominados: {len(results.get('mastered_topics', []))}")
            return True

        question = data.get('question', {})
        print(f"\n  Questão {data.get('question_number')}/{data.get('total_questions')}")
        print(f"  Tópico: {question.get('topic_name', 'N/A')}")
        print(f"  Problema: {question.get('problem', 'N/A')}")

        # Submit answer (using correct answer for testing)
        answer = question.get('answer', '0')

        response = requests.post(
            f"{BASE_URL}/diagnostic/{STUDENT_ID}/submit",
            json={
                "question_id": question['question_id'],
                "answer": str(answer)
            }
        )

        if response.status_code == 200:
            result = response.json()
            is_correct = result.get('is_correct', False)
            print(f"  {'✓ Correto' if is_correct else '✗ Incorreto'}")
            questions_answered += 1
        else:
            print(f"❌ Erro ao submeter resposta: {response.json()}")
            break

    return True


def test_adaptive_learning():
    """Test adaptive learning flow"""
    print_section("APRENDIZAGEM ADAPTATIVA")

    # 1. Start adaptive session
    print("\n1. Iniciando sessão adaptativa...")
    response = requests.post(
        f"{BASE_URL}/adaptive/start",
        json={"student_id": STUDENT_ID}
    )

    if response.status_code != 201:
        print(f"❌ Erro ao iniciar sessão: {response.json()}")
        return False

    result = response.json()
    print(f"✓ Sessão iniciada")
    print(f"  Tópico atual: {result.get('topic_name', 'N/A')}")
    print(f"  Dificuldade: {result.get('difficulty', 'N/A')}")

    # 2. Get and answer a few questions
    for i in range(3):
        print(f"\n2.{i+1}. Obtendo questão adaptativa...")

        response = requests.get(f"{BASE_URL}/adaptive/{STUDENT_ID}/next")

        if response.status_code != 200:
            print(f"❌ Erro ao obter questão: {response.json()}")
            break

        question = response.json()

        if question.get('error'):
            print(f"❌ {question['error']}")
            break

        print(f"  Problema: {question.get('problem', 'N/A')[:50]}...")
        print(f"  Tipo: {question.get('type', 'N/A')}")
        print(f"  Dificuldade: {question.get('difficulty', 'N/A')}")

        # Submit answer (correct for testing)
        response = requests.post(
            f"{BASE_URL}/adaptive/{STUDENT_ID}/submit",
            json={
                "question_id": str(i),
                "question": question['problem'],
                "student_answer": str(question['answer']),
                "correct_answer": str(question['answer']),
                "solution_steps": question.get('steps', []),
                "concepts_tested": question.get('concepts', question.get('topic_id', '').split('_'))
            }
        )

        if response.status_code == 200:
            result = response.json()
            print(f"  Status: {result.get('status', 'N/A')}")
            print(f"  {'✓ Correto!' if result.get('is_correct') else '✗ Incorreto'}")

            if result.get('status') == 'topic_mastered':
                print(f"  🎉 Tópico dominado!")
        else:
            print(f"❌ Erro ao submeter: {response.json()}")

    return True


def test_progress_tracking():
    """Test progress tracking"""
    print_section("RASTREAMENTO DE PROGRESSO")

    # 1. Get overall progress
    print("\n1. Obtendo progresso geral...")
    response = requests.get(f"{BASE_URL}/progress/{STUDENT_ID}")

    if response.status_code != 200:
        print(f"❌ Erro ao obter progresso: {response.json()}")
        return False

    progress = response.json()
    print(f"✓ Progresso obtido")
    print(f"  Tópicos dominados: {progress.get('mastered_count', 0)}/{progress.get('total_topics', 0)}")
    print(f"  Conclusão: {progress.get('completion_percentage', 0):.1f}%")
    print(f"  Tópico atual: {progress.get('current_topic', 'N/A')}")

    # 2. Get recommendations
    print("\n2. Obtendo recomendações...")
    response = requests.get(f"{BASE_URL}/progress/{STUDENT_ID}/recommendations")

    if response.status_code == 200:
        data = response.json()
        recommendations = data.get('recommendations', [])
        print(f"✓ {len(recommendations)} tópicos recomendados:")

        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec.get('name', 'N/A')} (dificuldade: {rec.get('difficulty', 'N/A')})")
            print(f"     {rec.get('why_recommended', 'N/A')}")
    else:
        print(f"❌ Erro ao obter recomendações: {response.json()}")

    # 3. Get topic-specific progress
    print("\n3. Obtendo progresso por tópico...")
    response = requests.get(f"{BASE_URL}/progress/{STUDENT_ID}/topic/operacoes_basicas")

    if response.status_code == 200:
        topic_progress = response.json()
        print(f"✓ Progresso do tópico: {topic_progress.get('topic_name', 'N/A')}")

        mastery = topic_progress.get('mastery', {})
        print(f"  Acurácia: {mastery.get('accuracy_rate', 0):.1%}")
        print(f"  Questões respondidas: {mastery.get('questions_answered', 0)}")
        print(f"  Dominado: {'✓ Sim' if mastery.get('is_mastered') else '✗ Não'}")
    else:
        print(f"❌ Erro ao obter progresso do tópico: {response.json()}")

    return True


def test_api_health():
    """Test basic API health"""
    print_section("VERIFICAÇÃO DA API")

    try:
        response = requests.get(f"{BASE_URL}/")

        if response.status_code == 200:
            data = response.json()
            print(f"✓ API está rodando")
            print(f"  Serviço: {data.get('service', 'N/A')}")
            print(f"  Versão: {data.get('version', 'N/A')}")
            print(f"  Swagger: {data.get('swagger_ui', 'N/A')}")
            return True
        else:
            print(f"❌ API retornou código {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API")
        print("   Certifique-se de que o servidor está rodando em http://localhost:5000")
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  TESTE DO SISTEMA ADAPTATIVO Q-EDU")
    print("=" * 60)

    # Test API health first
    if not test_api_health():
        return

    # Run tests
    tests = [
        ("Diagnóstico", test_diagnostic),
        ("Aprendizagem Adaptativa", test_adaptive_learning),
        ("Rastreamento de Progresso", test_progress_tracking)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Erro durante teste '{test_name}': {str(e)}")
            results.append((test_name, False))

    # Summary
    print_section("RESUMO DOS TESTES")

    passed = sum(1 for _, success in results if success)
    total = len(results)

    print()
    for test_name, success in results:
        status = "✓ PASSOU" if success else "✗ FALHOU"
        print(f"  {status}: {test_name}")

    print(f"\nResultado: {passed}/{total} testes passaram")

    if passed == total:
        print("\n🎉 Todos os testes passaram! Sistema adaptativo funcionando corretamente.")
    else:
        print("\n⚠️  Alguns testes falharam. Revise os erros acima.")


if __name__ == "__main__":
    main()
