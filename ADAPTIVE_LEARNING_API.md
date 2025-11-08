# Adaptive Learning API - Documentação

Sistema de aprendizagem adaptativa personalizada que ajusta automaticamente a dificuldade, identifica lacunas de conhecimento e recomenda o melhor caminho de aprendizado baseado no desempenho do estudante.

---

## Índice

1. [Iniciar Sessão Adaptativa](#1-iniciar-sessão-adaptativa)
2. [Obter Próxima Questão](#2-obter-próxima-questão)
3. [Submeter Resposta](#3-submeter-resposta)
4. [Mudar de Tópico](#4-mudar-de-tópico)
5. [Obter Progresso do Estudante](#5-obter-progresso-do-estudante)
6. [Obter Tópicos Recomendados](#6-obter-tópicos-recomendados)
7. [Fluxo de Uso](#fluxo-de-uso)
8. [Tipos de Erro](#tipos-de-erro)
9. [Recursos Adaptativos](#recursos-adaptativos)

---

## Base URL

```
http://localhost:5000
```

**Swagger UI:** http://localhost:5000/docs

---

## 1. Iniciar Sessão Adaptativa

Inicia uma nova sessão de aprendizagem adaptativa para um estudante.

### Endpoint

```http
POST /adaptive/start
```

### Request Body

```json
{
  "student_id": "student_123",
  "learning_path": "intermediate"
}
```

### Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `student_id` | string | ✅ Sim | Identificador único do estudante |
| `learning_path` | string | ❌ Não | Caminho: `beginner`, `intermediate`, `advanced` |

### Respostas

#### ✅ 201 Created - Sessão pronta

```json
{
  "status": "ready",
  "current_topic": "equacoes_lineares_uma_etapa",
  "topic_name": "Equações Lineares - Uma Etapa",
  "topic_description": "Equações que requerem apenas uma operação para resolver",
  "difficulty": "medium",
  "message": "Vamos começar com: Equações Lineares - Uma Etapa"
}
```

#### ⚠️ 201 Created - Diagnóstico necessário

```json
{
  "status": "diagnostic_required",
  "message": "Complete o teste diagnóstico primeiro",
  "action": "start_diagnostic"
}
```

#### 🎉 201 Created - Tudo completo

```json
{
  "status": "completed",
  "message": "Parabéns! Você dominou todos os tópicos disponíveis!",
  "mastered_topics": ["operacoes_basicas", "equacoes_lineares_uma_etapa"]
}
```

### Exemplo cURL

```bash
curl -X POST http://localhost:5000/adaptive/start \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "student_123",
    "learning_path": "intermediate"
  }'
```

---

## 2. Obter Próxima Questão

Retorna a próxima questão adaptada ao nível atual do estudante.

### Endpoint

```http
GET /adaptive/{student_id}/next
```

### Parâmetros de Path

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `student_id` | string | ID do estudante |

### Resposta

#### ✅ 200 OK

```json
{
  "id": "q_12345",
  "problem": "Resolva para x: 3x - 7 = 14",
  "equation": "3x - 7 = 14",
  "answer": "7",
  "steps": [
    "3x - 7 = 14",
    "3x = 14 + 7",
    "3x = 21",
    "x = 21 / 3",
    "x = 7"
  ],
  "difficulty": "medium",
  "type": "two_step",
  "topic": "Equações de duas etapas",
  "concepts": ["addition", "division"],
  "topic_id": "equacoes_lineares_duas_etapas",
  "adaptive_context": {
    "current_difficulty": "medium",
    "mastered_topics": ["operacoes_basicas", "equacoes_lineares_uma_etapa"],
    "session_question_number": 3
  }
}
```

### Exemplo cURL

```bash
curl -X GET http://localhost:5000/adaptive/student_123/next
```

---

## 3. Submeter Resposta

Submete a resposta do estudante e recebe feedback adaptativo com análise de erros.

### Endpoint

```http
POST /adaptive/{student_id}/submit
```

### Parâmetros de Path

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `student_id` | string | ID do estudante |

### Request Body

```json
{
  "question_id": "q_12345",
  "question": "Resolva para x: 3x - 7 = 14",
  "student_answer": "7",
  "correct_answer": "7",
  "solution_steps": [
    "3x - 7 = 14",
    "3x = 14 + 7",
    "3x = 21",
    "x = 21 / 3",
    "x = 7"
  ],
  "concepts_tested": ["addition", "division"]
}
```

### Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `question_id` | string | ✅ Sim | ID da questão |
| `question` | string | ✅ Sim | Texto da questão |
| `student_answer` | string | ✅ Sim | Resposta do estudante |
| `correct_answer` | string | ✅ Sim | Resposta correta |
| `solution_steps` | array | ✅ Sim | Passos da solução |
| `concepts_tested` | array | ✅ Sim | Conceitos testados |

### Respostas

#### ✅ 200 OK - Resposta correta - continuar

```json
{
  "status": "continue",
  "is_correct": true,
  "message": "Correto!",
  "mastery_info": {
    "is_mastered": false,
    "accuracy_rate": 0.75,
    "questions_answered": 4,
    "correct_count": 3
  },
  "solution_steps": ["..."],
  "action": "continue"
}
```

#### 🎉 200 OK - Tópico dominado

```json
{
  "status": "topic_mastered",
  "is_correct": true,
  "message": "Parabéns! Você dominou: Equações Lineares - Uma Etapa",
  "mastery_info": {
    "is_mastered": true,
    "accuracy_rate": 0.90,
    "questions_answered": 10,
    "correct_count": 9
  },
  "next_topic": "equacoes_lineares_duas_etapas",
  "next_topic_name": "Equações Lineares - Duas Etapas",
  "solution_steps": ["..."],
  "action": "advance_topic"
}
```

#### ❌ 200 OK - Resposta incorreta - continuar

```json
{
  "status": "continue",
  "is_correct": false,
  "message": "Não desanime! Vamos tentar outra.",
  "error_analysis": {
    "error_type": "ARITHMETIC",
    "explanation": "Erro ao calcular 3 + 7 = 11 (deveria ser 10)",
    "severity": "LOW",
    "affected_concepts": ["addition"]
  },
  "solution_steps": ["..."],
  "hint": "Dica: Verifique seus cálculos aritméticos novamente.",
  "action": "continue"
}
```

#### ⬇️ 200 OK - Reduzir dificuldade

```json
{
  "status": "difficulty_reduced",
  "is_correct": false,
  "message": "Vamos tentar questões mais simples para reforçar os conceitos",
  "error_analysis": {
    "error_type": "CONCEPTUAL",
    "explanation": "Não compreendeu a operação inversa da multiplicação",
    "severity": "MEDIUM",
    "affected_concepts": ["division", "inverse_operations"]
  },
  "next_action": {
    "action": "REDUCE_DIFFICULTY",
    "reason": "Múltiplos erros conceituais consecutivos"
  },
  "solution_steps": ["..."],
  "new_difficulty": "easy",
  "action": "reduce_difficulty"
}
```

#### 🔙 200 OK - Revisar pré-requisito

```json
{
  "status": "prerequisite_required",
  "is_correct": false,
  "message": "Vamos revisar primeiro: Operações Inversas",
  "error_analysis": {
    "error_type": "CONCEPTUAL",
    "explanation": "Falta de domínio em operações inversas",
    "severity": "HIGH",
    "affected_concepts": ["inverse_operations"]
  },
  "next_action": {
    "action": "REVIEW_PREREQUISITE",
    "target_topic": "operacoes_inversas",
    "reason": "Lacuna em conceito fundamental"
  },
  "solution_steps": ["..."],
  "new_topic": "operacoes_inversas",
  "new_topic_name": "Operações Inversas",
  "action": "change_topic"
}
```

### Exemplo cURL

```bash
curl -X POST http://localhost:5000/adaptive/student_123/submit \
  -H "Content-Type: application/json" \
  -d '{
    "question_id": "q_12345",
    "question": "Resolva para x: 3x - 7 = 14",
    "student_answer": "7",
    "correct_answer": "7",
    "solution_steps": ["3x - 7 = 14", "3x = 21", "x = 7"],
    "concepts_tested": ["addition", "division"]
  }'
```

---

## 4. Mudar de Tópico

Permite mudar manualmente para um tópico específico (se pré-requisitos forem atendidos).

### Endpoint

```http
POST /adaptive/{student_id}/change-topic
```

### Parâmetros de Path

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `student_id` | string | ID do estudante |

### Request Body

```json
{
  "topic_id": "equacoes_lineares_duas_etapas"
}
```

### Respostas

#### ✅ 200 OK - Sucesso

```json
{
  "status": "topic_changed",
  "current_topic": "equacoes_lineares_duas_etapas",
  "topic_name": "Equações Lineares - Duas Etapas",
  "topic_description": "Equações que requerem duas operações para resolver",
  "difficulty": "medium"
}
```

#### ⚠️ 200 OK - Pré-requisitos faltando

```json
{
  "status": "prerequisites_required",
  "message": "Você precisa dominar os pré-requisitos primeiro",
  "missing_prerequisites": ["operacoes_inversas", "simplificacao_algebrica"],
  "missing_names": ["Operações Inversas", "Simplificação Algébrica"]
}
```

### Exemplo cURL

```bash
curl -X POST http://localhost:5000/adaptive/student_123/change-topic \
  -H "Content-Type: application/json" \
  -d '{
    "topic_id": "equacoes_lineares_duas_etapas"
  }'
```

---

## 5. Obter Progresso do Estudante

Retorna um resumo completo do progresso do estudante.

### Endpoint

```http
GET /progress/{student_id}
```

### Parâmetros de Path

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `student_id` | string | ID do estudante |

### Resposta

#### ✅ 200 OK

```json
{
  "student_id": "student_123",
  "mastered_count": 5,
  "total_topics": 15,
  "completion_percentage": 33.33,
  "current_topic": "equacoes_lineares_duas_etapas",
  "learning_path": "intermediate",
  "progress_by_topic": {
    "operacoes_basicas": {
      "name": "Operações Básicas",
      "is_mastered": true,
      "questions_answered": 12,
      "accuracy_rate": 0.92,
      "can_start": true
    },
    "equacoes_lineares_uma_etapa": {
      "name": "Equações Lineares - Uma Etapa",
      "is_mastered": true,
      "questions_answered": 10,
      "accuracy_rate": 0.90,
      "can_start": true
    },
    "equacoes_lineares_duas_etapas": {
      "name": "Equações Lineares - Duas Etapas",
      "is_mastered": false,
      "questions_answered": 3,
      "accuracy_rate": 0.67,
      "can_start": true
    }
  },
  "next_available": ["equacoes_lineares_duas_etapas", "simplificacao_algebrica"]
}
```

### Exemplo cURL

```bash
curl -X GET http://localhost:5000/progress/student_123
```

---

## 6. Obter Tópicos Recomendados

Retorna os tópicos recomendados para o estudante com base no progresso atual.

### Endpoint

```http
GET /progress/{student_id}/recommendations
```

### Parâmetros de Path

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `student_id` | string | ID do estudante |

### Resposta

#### ✅ 200 OK

```json
{
  "recommendations": [
    {
      "topic_id": "equacoes_lineares_duas_etapas",
      "name": "Equações Lineares - Duas Etapas",
      "description": "Equações que requerem duas operações para resolver",
      "difficulty": 2,
      "estimated_questions": 8,
      "why_recommended": "Você tem todos os pré-requisitos - sequência natural"
    },
    {
      "topic_id": "simplificacao_algebrica",
      "name": "Simplificação Algébrica",
      "description": "Simplificar expressões algébricas",
      "difficulty": 2,
      "estimated_questions": 10,
      "why_recommended": "Próximo desafio - você está preparado"
    }
  ]
}
```

### Exemplo cURL

```bash
curl -X GET http://localhost:5000/progress/student_123/recommendations
```

---

## Fluxo de Uso

```
1. POST /adaptive/start
   └─> Iniciar sessão adaptativa

2. GET /adaptive/{student_id}/next
   └─> Obter questão personalizada

3. POST /adaptive/{student_id}/submit
   └─> Submeter resposta
   └─> Sistema analisa e adapta:
       ├─> ✅ Correto: Continuar ou avançar tópico
       └─> ❌ Incorreto:
           ├─> Continuar com dica
           ├─> Reduzir dificuldade
           └─> Voltar para pré-requisito

4. Repetir passos 2-3 até dominar tópicos

5. GET /progress/{student_id}
   └─> Acompanhar progresso geral
```

---

## Tipos de Erro

O sistema analisa erros e os classifica automaticamente:

| Tipo | Descrição | Ação Adaptativa |
|------|-----------|-----------------|
| **CONCEPTUAL** | Erro de compreensão de conceito | Revisar pré-requisito ou reduzir dificuldade |
| **PROCEDURAL** | Erro nos passos da resolução | Fornecer dica sobre o procedimento correto |
| **ARITHMETIC** | Erro de cálculo aritmético | Dica para revisar cálculos |
| **CARELESS** | Erro por descuido/distração | Encorajamento para ter mais atenção |

### Severidade dos Erros

- **LOW**: Erro pontual, estudante pode continuar
- **MEDIUM**: Requer redução de dificuldade
- **HIGH**: Requer revisão de pré-requisitos

---

## Recursos Adaptativos

### 🧠 Análise de Erros com IA
- Usa Google Gemini para análise profunda de erros
- Identifica padrões de erro e lacunas conceituais
- Fornece explicações personalizadas

### 📊 Ajuste Dinâmico de Dificuldade
- **Aumenta**: Quando acurácia > 90% após 3+ questões
- **Reduz**: Quando erros conceituais consecutivos
- **Mantém**: Performance adequada no nível atual

### 🔍 Detecção de Lacunas
- Identifica pré-requisitos não dominados
- Redireciona automaticamente para tópicos fundamentais
- Previne avanço sem base sólida

### 🎯 Rastreamento de Domínio
- Monitora progresso por tópico
- Calcula taxa de acerto e domínio
- Threshold configurável por tópico (geralmente 75%)

### 💡 Recomendações Personalizadas
- Sugere próximos tópicos baseado em:
  - Tópicos já dominados
  - Pré-requisitos completados
  - Dificuldade apropriada
  - Caminho de aprendizado escolhido

### 📈 Sistema de Progresso
- Tracking completo por estudante
- Histórico de tentativas
- Conceitos com dificuldade
- Taxa de conclusão geral

---

## Códigos de Status HTTP

| Código | Descrição |
|--------|-----------|
| 200 | Sucesso |
| 201 | Recurso criado (sessão iniciada) |
| 400 | Requisição inválida (parâmetros faltando) |
| 404 | Recurso não encontrado (sessão não existe) |
| 500 | Erro interno do servidor |

---

## Tópicos Disponíveis

### Nível Básico (Beginner)
- `operacoes_basicas` - Operações Básicas
- `numeros_inteiros` - Números Inteiros
- `fracoes` - Frações

### Nível Intermediário (Intermediate)
- `variaveis_expressoes` - Variáveis e Expressões
- `simplificacao_algebrica` - Simplificação Algébrica
- `operacoes_inversas` - Operações Inversas
- `manipulacao_equacoes` - Manipulação de Equações

### Nível Avançado (Advanced)
- `equacoes_lineares_uma_etapa` - Equações Lineares - Uma Etapa
- `equacoes_lineares_duas_etapas` - Equações Lineares - Duas Etapas
- `equacoes_lineares_variaveis_ambos_lados` - Equações com Variáveis em Ambos os Lados
- `equacoes_lineares` - Equações Lineares Complexas

---

## Notas Importantes

1. **Diagnóstico Obrigatório**: Estudantes devem completar o teste diagnóstico antes de iniciar aprendizagem adaptativa
2. **Pré-requisitos**: O sistema valida pré-requisitos antes de permitir acesso a tópicos avançados
3. **Sessões Persistentes**: Sessões são mantidas em memória durante execução do servidor
4. **Análise com IA**: Requer `GEMINI_API_KEY` configurada para análise de erros
5. **CORS Habilitado**: Frontend pode fazer requisições de diferentes origens

---

## Exemplos de Integração

### JavaScript/TypeScript

```javascript
// Iniciar sessão
const response = await fetch('http://localhost:5000/adaptive/start', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    student_id: 'student_123',
    learning_path: 'intermediate'
  })
});
const session = await response.json();

// Obter próxima questão
const questionResponse = await fetch(
  `http://localhost:5000/adaptive/student_123/next`
);
const question = await questionResponse.json();

// Submeter resposta
const submitResponse = await fetch(
  `http://localhost:5000/adaptive/student_123/submit`,
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      question_id: question.id,
      question: question.problem,
      student_answer: '7',
      correct_answer: question.answer,
      solution_steps: question.steps,
      concepts_tested: question.concepts
    })
  }
);
const feedback = await submitResponse.json();
```

### Python

```python
import requests

# Iniciar sessão
response = requests.post(
    'http://localhost:5000/adaptive/start',
    json={
        'student_id': 'student_123',
        'learning_path': 'intermediate'
    }
)
session = response.json()

# Obter próxima questão
question = requests.get(
    'http://localhost:5000/adaptive/student_123/next'
).json()

# Submeter resposta
feedback = requests.post(
    'http://localhost:5000/adaptive/student_123/submit',
    json={
        'question_id': question['id'],
        'question': question['problem'],
        'student_answer': '7',
        'correct_answer': question['answer'],
        'solution_steps': question['steps'],
        'concepts_tested': question['concepts']
    }
).json()
```

---

## Suporte

Para dúvidas ou problemas:
- Acesse a documentação interativa: http://localhost:5000/docs
- Verifique os logs do servidor para detalhes de erros
- Consulte o código fonte em: `app.py` e `adaptive_engine.py`

---

**Versão da API:** 1.0.0
**Última atualização:** Novembro 2025
