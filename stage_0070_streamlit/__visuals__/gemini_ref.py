import folium
import streamlit as st
from streamlit_folium import st_folium

# Configuração da Página para modo Wide (aproveita melhor a largura)
st.set_page_config(
    page_title="Trânsito Recife - Monitoramento", layout="wide"
)

# --- ESTILIZAÇÃO CSS CUSTOMIZADA (Tons claros, degradês e visual moderno) ---
st.markdown(
    """
    <style>
    /* Fundo geral da aplicação com tom claro e suave */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4ecf5 100%);
    }
    
    /* Estilização do Sidebar / Painel de Câmeras */
    [data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    /* Cartões de Câmera com efeito de sombra suave e borda arredondada */
    .camera-card {
        background: #ffffff;
        padding: 12px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0, 123, 255, 0.08);
        margin-bottom: 16px;
        transition: transform 0.2s ease;
    }
    .camera-card:hover {
        transform: translateY(-2px);
    }
    
    /* Títulos e textos */
    h1, h2, h3 {
        color: #1e3c72;
        font-family: 'Inter', sans-serif;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- PAINEL LATERAL (CÂMERAS COM MAIOR DESTAQUE) ---
with st.sidebar:
  st.markdown("### 🚦 Trânsito Recife")
  st.markdown(
      "<p style='color: #64748b; font-size: 14px;'>Monitoramento em Tempo"
      " Real</p>",
      unsafe_allow_html=True,
  )

  # Seletor de Região
  regiao = st.selectbox(
      "Selecione a Região",
      ["Zona Norte", "Centro", "Zona Oeste", "Zona Sul", "Zona Leste"],
  )

  st.markdown(f"#### 🎥 Câmeras ao Vivo - {regiao}")
  st.markdown("---")

  # Simulação de feeds de câmeras maiores e mais visíveis
  # Em um app real, você pode substituir por st.image ou streams RTSP/WebRTC
  cameras_por_regiao = {
      "Zona Norte": [
          ("Av. Norte - Câmera 01", "https://picsum.photos/600/350?random=1"),
          (
              "Av. Agamenon Magalhães - Câmera 02",
              "https://picsum.photos/600/350?random=2",
          ),
      ],
      "Centro": [
          ("Ponte Duarte Coelho", "https://picsum.photos/600/350?random=3"),
          ("Rua da Aurora", "https://picsum.photos/600/350?random=4"),
      ],
      "Zona Oeste": [
          ("Av. Caxangá - Trecho 1", "https://picsum.photos/600/350?random=5"),
          ("BR-101 - Reta da Várzea", "https://picsum.photos/600/350?random=6"),
      ],
      "Zona Sul": [
          ("Boa Viagem - Av. Boa Viagem", "https://picsum.photos/600/350?random=7"),
          (
              "Via Mangue - Sentido Centro",
              "https://picsum.photos/600/350?random=8",
          ),
      ],
      "Zona Leste": [
          ("Av. Mascarenhas de Morais", "https://picsum.photos/600/350?random=9"),
      ],
  }

  # Renderiza as câmeras de forma limpa e maior no sidebar
  for nome_cam, url_img in cameras_por_regiao.get(regiao, []):
    st.markdown(
        f"""
        <div class="camera-card">
            <b style="color: #334155; font-size: 13px;">{nome_cam}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.image(url_img, use_container_width=True)

# --- CONTEÚDO PRINCIPAL (MAPA DE RECIFE) ---
st.markdown("### 🗺️ Mapa Interativo de Recife")
st.markdown(
    "<p style='color: #64748b; margin-top: -10px;'>Selecione a zona no mapa"
    " ou explore as áreas com efeito visual em tons claros e"
    " azulados.</p>",
    unsafe_allow_html=True,
)

# Criação do Mapa centralizado em Recife com Folium
# Usamos um tileset limpo (CartoDB Positron) que combina perfeitamente com o estilo minimalista
m = folium.Map(
    location=[-8.0476, -34.8770],
    zoom_start=13,
    tiles="CartoDB positron",
)

# Coordenadas aproximadas para marcação das zonas no mapa de Recife
zonas_recife = {
    "Zona Norte": [-8.0250, -34.9000],
    "Centro": [-8.0631, -34.8711],
    "Zona Oeste": [-8.0500, -34.9300],
    "Zona Sul": [-8.1150, -34.9050],
}

# Adicionando marcadores estilizados para cada zona
for nome_zona, coords in zonas_recife.items():
  folium.Marker(
      location=coords,
      popup=nome_zona,
      tooltip=f"Ver câmeras: {nome_zona}",
      icon=folium.Icon(color="blue", icon="video-camera", prefix="fa"),
  ).to_dict()

  # Círculos com gradientes visuais simulados (efeito de radar/glow)
  folium.Circle(
      location=coords,
      radius=1800,
      color="#007bff",
      fill=True,
      fill_color="#00d2ff",
      fill_opacity=0.2,
      weight=1.5,
      popup=nome_zona,
  ).add_to(m)

# Exibindo o mapa no Streamlit
output_mapa = st_folium(m, width="100%", height=600)