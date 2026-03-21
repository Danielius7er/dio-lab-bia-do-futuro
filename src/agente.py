import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import pandas as pd
from groq import Groq

from config import (
    MODEL_NAME,
    MAX_TOKENS,
    AGENT_NAME,
    TRANSACOES_PATH,
    HISTORICO_PATH,
    PERFIL_PATH,
    PRODUTOS_PATH,
)

# ── Carregamento dos dados ────────────────────────────────────────────────────

def carregar_perfil() -> dict:
    with open(PERFIL_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def carregar_produtos() -> list:
    with open(PRODUTOS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def carregar_transacoes() -> str:
    df = pd.read_csv(TRANSACOES_PATH, parse_dates=["data"])
    resumo = (
        df.groupby("categoria")["valor"]
        .sum()
        .sort_values(ascending=False)
    )
    linhas = [f"- {cat}: R$ {valor:,.2f}" for cat, valor in resumo.items()]
    return "\n".join(linhas)


def carregar_historico() -> str:
    df = pd.read_csv(HISTORICO_PATH, parse_dates=["data"])
    df = df.sort_values("data", ascending=False).head(5)
    linhas = [
        f"- [{row['data'].strftime('%d/%m/%Y')}] {row['tema']} via {row['canal']}: {row['resumo']}"
        for _, row in df.iterrows()
    ]
    return "\n".join(linhas)


# ── System Prompt ─────────────────────────────────────────────────────────────

def montar_system_prompt(perfil: dict, transacoes: str, historico: str, produtos: list) -> str:
    produtos_texto = "\n".join(
        f"- {p['nome']} ({p['categoria']}) | Risco: {p['risco']} | Rentabilidade: {p['rentabilidade']} | Aporte mínimo: R$ {p['aporte_minimo']:.2f}"
        for p in produtos
    )

    return f"""# IDENTIDADE E PAPEL

Você é {AGENT_NAME}, assistente de planejamento financeiro pessoal.
Seu papel é ajudar o cliente a entender sua situação financeira, identificar
padrões de comportamento e construir juntos um plano para atingir suas metas.

Você é consultiva, empática e direta. Não usa jargão desnecessário. Fala como
uma amiga que entende muito de finanças — não como um robô ou gerente formal.

---

# REGRAS INVIOLÁVEIS (ANTI-ALUCINAÇÃO)

1. NUNCA invente dados, números, saldos ou projeções que não estejam nos dados fornecidos.
2. Se não tiver informação suficiente, diga: "Não tenho esse dado disponível agora,
   mas posso te ajudar a analisar o que temos."
3. NUNCA prometa rentabilidade, retorno garantido ou resultados futuros como certeza.
4. Se o cliente perguntar algo fora do escopo financeiro, redirecione gentilmente.
5. Toda sugestão de produto deve ser baseada no perfil de investidor do cliente.
   Nunca recomende produtos incompatíveis com o perfil declarado.

---

# CONTEXTO DO CLIENTE

## Perfil
- Nome: {perfil.get('nome')}
- Perfil de Investidor: {perfil.get('tipo')}
- Objetivo Principal: {perfil.get('objetivo_principal')}
- Horizonte de Investimento: {perfil.get('horizonte')}
- Renda Mensal Estimada: R$ {perfil.get('renda_mensal'):,.2f}
- Tolerância a Risco: {perfil.get('tolerancia_risco')}

## Resumo de Transações (últimos 90 dias)
{transacoes}

## Histórico de Atendimentos Recentes
{historico}

## Produtos Disponíveis para Recomendação
{produtos_texto}

---

# COMPORTAMENTO

- Ao iniciar, cumprimente pelo nome e destaque algo relevante do histórico proativamente.
- Ao analisar gastos, sempre contextualize (% da renda, variação vs mês anterior).
- Ao recomendar produtos, apresente no máximo 2-3 opções com linguagem simples.
- Respostas curtas e diretas — máximo 4-5 parágrafos.
- Use emojis com moderação (1-2 por mensagem).
- Nunca seja condescendente sobre escolhas financeiras passadas do cliente.
"""


# ── Agente ────────────────────────────────────────────────────────────────────

class AgenteFinanceiro:
    def __init__(self):
        # Lê a key diretamente do .env
        env_path = r"C:\Users\danie_4kpxbtv\dio-lab-bia-do-futuro\.env"
        api_key = ""
        with open(env_path) as f:
            for line in f:
                if "GROQ_API_KEY" in line:
                    api_key = line.strip().split("=", 1)[1].strip()
                    break

        self.client = Groq(api_key=api_key)
        self.perfil = carregar_perfil()

        transacoes = carregar_transacoes()
        historico  = carregar_historico()
        produtos   = carregar_produtos()

        self.system_prompt = montar_system_prompt(
            self.perfil, transacoes, historico, produtos
        )

        # Histórico inclui sempre o system prompt no início
        self.historico_conversa = [
            {"role": "system", "content": self.system_prompt}
        ]

    def chat(self, mensagem_usuario: str) -> str:
        self.historico_conversa.append({
            "role": "user",
            "content": mensagem_usuario,
        })

        resposta = self.client.chat.completions.create(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            messages=self.historico_conversa,
        )

        conteudo = resposta.choices[0].message.content

        self.historico_conversa.append({
            "role": "assistant",
            "content": conteudo,
        })

        # Limita histórico mantendo sempre o system prompt
        from config import MAX_HISTORY_TURNS
        if len(self.historico_conversa) > MAX_HISTORY_TURNS * 2 + 1:
            self.historico_conversa = (
                [self.historico_conversa[0]] +
                self.historico_conversa[-(MAX_HISTORY_TURNS * 2):]
            )

        return conteudo

    def resetar(self):
        self.historico_conversa = [
            {"role": "system", "content": self.system_prompt}
        ]