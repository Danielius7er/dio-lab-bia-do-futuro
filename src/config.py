import os
from dotenv import load_dotenv
 
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))
 
# ── API ──────────────────────────────────────────────────────────────────────
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL_NAME   = "llama-3.3-70b-versatile"
MAX_TOKENS   = 1024
 
# ── Caminhos dos dados ────────────────────────────────────────────────────────
DATA_DIR = os.path.join(BASE_DIR, "data")
 
TRANSACOES_PATH = os.path.join(DATA_DIR, "transacoes.csv")
HISTORICO_PATH  = os.path.join(DATA_DIR, "historico_atendimento.csv")
PERFIL_PATH     = os.path.join(DATA_DIR, "perfil_investidor.json")
PRODUTOS_PATH   = os.path.join(DATA_DIR, "produtos_financeiros.json")
# ── Agente ────────────────────────────────────────────────────────────────────
AGENT_NAME        = "FIN_AIBooks"
MAX_HISTORY_TURNS = 20          # máximo de turnos mantidos no contexto