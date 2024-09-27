import pandas as pd
import streamlit as st
import streamlit_js_eval
import folium
from streamlit_folium import st_folium, folium_static

# Configurações da página
st.set_page_config(
    page_title="Mapeamento de Soros Antiveneno em Pernambuco",
    page_icon='doc/cobra.png',
    layout="wide",
    initial_sidebar_state='collapsed'
)

col1, col2, col3 = st.columns([1,4,1])

col1.image('doc/cobra.png', width=200)
col2.title('Mapeamento de Soros Antiveneno em Pernambuco')
#col3.image('doc/deptEngBio.png', width=300)

st.markdown(
    """
    <style>
    p {
        font-weight: bold; /* Negrito */
    }
    .st-emotion-cache-10trblm.e1nzilvr1 {
        color: #FF5733; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with col2: 

    tab1, tab2, tab3, tab4 = st.tabs([ "Buscador de Soros", "CEATOX-PE", "Sobre", "Contato"])

    with tab1:
        st.markdown(
            """
            <h2 style="text-align: center;">🐍Buscador de Soros</h2><br><br>
            """,
            unsafe_allow_html=True,
        )


        dados_geral = pd.read_csv('doc/hospital_mais_proximo.csv')
        cidades = pd.read_csv('doc/latitude-longitude-cidades.csv')
        cidades = cidades[cidades['uf'] == 'PE']

        lista_mun_distinct = sorted(cidades['municipio'].unique())

        #municipios
        col5,espaco2,col4 = st.columns([5,1,7]) 
        with col5:  
            st.markdown(
            """
            <br><br><br>
            """,
            unsafe_allow_html=True,
            )
            animal = st.selectbox("Qual tipo de animal causou o acidente?", dados_geral['animal'].unique(), index=None, placeholder="Selecione o animal")
            soro = st.selectbox('Soro Antiveneno', dados_geral[dados_geral['animal']==animal]['soro'].unique(), index=None, placeholder="Selecione o Soro Antiveneno")

            try: 
                container = st.container(border=True)
                with container: 
                     st.write(soro, dicionario_explicacao[soro])
            except: 
                st.write("")

            mun_origem = st.selectbox('Município onde está o paciente', lista_mun_distinct, index=None, placeholder="Selecione o município onde está o paciente")

            try:

                #Filtro destino
                filtro = (dados_geral['soro'] == soro)&(dados_geral['cidade_origem'] == mun_origem)
                municipio_origem = dados_geral[filtro]
                municipio_origem['Legenda'] = 'Origem'

                #municipio_origem = municipio_origem.reset_index(drop=True)
                mun_destino = municipio_origem.dropna()['cidade_hospital'].values[0]

                filtro_destino = (dados_geral['soro'] == soro)&(dados_geral['cidade_origem'] == mun_destino)
                municipio_destino = dados_geral[filtro_destino].dropna()
                municipio_destino['Legenda'] = 'Destino'

                latitude_media = (municipio_origem['latitude_origem'].values[0] + municipio_destino['latitude_hospital'].values[0])/2
                longitude_media = (municipio_origem['longitude_origem'].values[0] + municipio_destino['longitude_hospital'].values[0])/2 

                mapa = folium.Map([latitude_media,  longitude_media], zoom_start=9.6)

                folium.Marker(
                    location= [municipio_origem['latitude_origem'].values, municipio_origem['longitude_origem'].values],
                    tooltip="Origem",
                    popup="Você está aqui",
                    icon=folium.Icon(color="green",icon="house",prefix="fa"),
                ).add_to(mapa)

                folium.Marker(
                    location= [municipio_destino['latitude_hospital'].values, municipio_destino['longitude_hospital'].values],
                    tooltip="Destino",
                    popup=f"O soro está aqui, na cidade de {municipio_destino['cidade_hospital'].values[0]}, {municipio_destino['hospital'].values[0]}",
                    icon=folium.Icon(color="red", icon="hospital",prefix="fa"),
                ).add_to(mapa)

                #folium.TileLayer('MapQuest Open Aerial').add_to(mapa)

                with col4: 
                    st.subheader('Hospital mais próximo')
                    st_data = folium_static(mapa, width=710, height=500)
                with col5:
                    mun_destino = municipio_origem.dropna()['cidade_hospital'].values[0]
                    distancia = municipio_origem.dropna()['distancia_km'].values[0]
                    local = municipio_origem.dropna()['hospital'].values[0]
                    endereco = municipio_origem.dropna()['endereco'].values[0]
                    telefone = municipio_origem.dropna()['telefone'].values[0]
                    container_respostas = st.container(border=True)
                    with container_respostas: 
                        st.write(f'Município onde está o soro mais próximo: **{mun_destino}**')
                        st.write(f'Local: **{local}**')
                        st.write(f'Endereço: **{endereco}**')
                        st.write(f'Telefone: **{telefone}**')
                        st.write(f'Distância: **{distancia} km**')
                        st.write('**ATENÇÃO**: ligue para o local para fazer a confirmação da disponibilidade do soro.')
            except:
                with col4:
                    if soro:
                        filtro = (dados_geral['soro'] == soro)&(dados_geral['animal'] == animal)
                        dados_mapa_vazio = dados_geral[filtro]

                    elif animal:
                        filtro = (dados_geral['animal'] == animal)
                        dados_mapa_vazio = dados_geral[filtro] 

                    else:
                        dados_mapa_vazio = dados_geral.copy()

                    pontos = dados_mapa_vazio.drop_duplicates(['hospital'])

                    mapa_vazio = folium.Map([-8.3831638, -37.7753284], zoom_start=7)


                    for latitude, longitude, hospital, endereco  in zip(pontos['latitude_hospital'], pontos['longitude_hospital'], pontos['hospital'], pontos['endereco']):
                        folium.Marker(
                            location= [latitude, longitude],
                            tooltip=hospital,
                            popup=endereco,
                            icon=folium.Icon(color="red", icon="hospital",prefix="fa"),
                        ).add_to(mapa_vazio)


                    ceatox_html = """
                                <h3>CEATOX - Centro de Assistência Toxicológica</h3>
                                <img src="https://jconlineimagem.ne10.uol.com.br/imagem/noticia/2015/10/23/normal/1a3b2a2d26969a75ed8ec04bb58fec8f.jpg" alt="Logo CEATOX" style="width: 200px; height: auto;"/>
                                <p>O Ceatox faz o acompanhamento dos pacientes por meio de evolução clínica diária, 
                                até a alta médica. Além da assistência aos casos de intoxicações e acidentes por animais 
                                peçonhentos, o Centro de Informação e Assistência Toxicológica de Pernambuco (CIAtox) 
                                desenvolve atividades de ensino e pesquisa através de parcerias com instituições de 
                                ensino e pesquisa.
                                <b>Telefone: 0800.722.6001 (tele-atendimento 24h por dia)</b></p>
                                """

                    folium.Marker(
                        location= [-8.053771365450142, -34.89005840177061],
                        tooltip="CEATOX - PE",  
                        popup=ceatox_html,              
                        icon=folium.Icon(color="lightblue",icon="hospital",prefix="fa"),
                    ).add_to(mapa_vazio)





                    st.subheader('Todos os hospitais')
                    st_data = folium_static(mapa_vazio, width=710, height=400)



creditos = st.container(border=True)
with creditos:
    col6,espaco3,col7,col8,espaco4 = st.columns([7,2,1,1,1])  
    with col6:
         st.write('Aplicação desenvolvida pelo Departamento de Engenharia Biomédica da Universidade Federal de Pernambuco.')
         st.write('Integrantes: José Filipe....')
    with col7:
        st.image('https://upload.wikimedia.org/wikipedia/commons/a/ae/Logo-ufpe-2-2.jpg',width=100)
    with col8:
        st.image('doc/deptEngBio.png', width=150)
