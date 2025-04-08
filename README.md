# ColorFilterApp - Filtro de Cores Avançado com OpenCV e Tkinter

## Visão Geral

`ColorFilterApp` é uma aplicação de desktop desenvolvida em Python que utiliza OpenCV para processamento de imagem em tempo real a partir de uma webcam e Tkinter para a interface gráfica do usuário (GUI). A aplicação permite aos usuários filtrar cores específicas no feed de vídeo, ajustar parâmetros de processamento e visualizar os resultados instantaneamente. Esta versão simplifica o manuseio da câmera, focando na funcionalidade principal de filtragem e nas opções avançadas de processamento.

## Funcionalidades Principais

* **Visualização em Tempo Real:** Exibe o feed original da câmera, a máscara de cor gerada e o resultado filtrado.
* **Filtragem de Cor Flexível:**
  * Seleção de espaço de cor (HSV, BGR, RGB, Lab, YCrCb).
  * Ajuste interativo dos limites mínimo e máximo para cada canal do espaço de cor selecionado usando sliders.
  * Tratamento especial para o componente Hue (Matiz) no espaço HSV para lidar com a natureza cíclica (por exemplo, para a cor vermelha).
* **Seleção Rápida de Cor:**
  * Botões pré-definidos para cores comuns (Vermelho, Verde, Azul, Amarelo, etc.).
  * Seletor de cor do sistema (`colorchooser`) para escolher uma cor visualmente e definir automaticamente uma faixa de filtro aproximada.
* **Processamento de Imagem Avançado:**
  * Suavização (Blur Gaussiano) para reduzir ruído antes da filtragem.
  * Operações morfológicas (Erosão e Dilatação) para refinar a máscara de cor.
  * Detecção e filtragem de contornos com base na área mínima.
* **Visualização de Contornos:**
  * Opção para desenhar os contornos detectados na imagem original.
  * Opção para desenhar caixas delimitadoras (bounding boxes) ao redor dos objetos detectados.
  * Opção para marcar o centro dos objetos detectados.
* **Modo Multi-Cor:**
  * Salvar configurações de filtro de cor atuais com um nome personalizado.
  * Ativar um modo para detectar *múltiplas* cores salvas simultaneamente.
  * Gerenciar a lista de cores salvas (visualizar, carregar para edição, remover, limpar tudo).
* **Interface Intuitiva:**
  * Organizada em abas (Cor Única, Avançado, Multi-Cor) para fácil navegação.
  * Sliders visuais para ajuste de parâmetros.
  * Barra de status exibindo informações úteis (contagem de objetos, FPS, modo atual).
* **Feedback Visual:**
  * Exibição da máscara binária gerada.
  * Exibição da imagem original com apenas as áreas filtradas visíveis.

## Requisitos

* **Python 3:** (Testado com Python 3.8+)
* **Bibliotecas Python:**
  * `opencv-python`: Para processamento de imagem e captura de vídeo.
  * `numpy`: Para manipulação eficiente de arrays (usado extensivamente pelo OpenCV).
  * `Pillow` (PIL Fork): Para conversão entre formatos de imagem OpenCV e Tkinter.
  * `tkinter` e `tkinter.ttk`: Para a interface gráfica (geralmente incluído na instalação padrão do Python).
* **Webcam:** Uma webcam conectada e funcional.

Você pode instalar as dependências necessárias usando pip:

```bash
pip install opencv-python numpy Pillow
```

## Guia de Uso

1. **Executando a Aplicação:**
   Salve o código como um arquivo Python (por exemplo, `color_filter_app.py`) e execute-o a partir do terminal:

   ```bash
   python color_filter_app.py
   ```

   A aplicação tentará abrir a câmera padrão (índice 0). Se a câmera não puder ser aberta, uma mensagem de erro será exibida.
2. **Interface Gráfica:**
   A janela principal é dividida em duas seções:

   * **Painel de Imagem (Esquerda):** Exibe três visualizações:
     * `Original`: O feed da câmera, possivelmente com contornos/caixas desenhados se habilitados.
     * `Máscara`: A máscara binária resultante da filtragem de cor e operações morfológicas (pixels brancos representam a cor detectada).
     * `Resultado Filtrado`: A imagem original onde apenas as áreas correspondentes à máscara são mostradas.
   * **Painel de Controle (Direita):** Contém as abas para ajustar os parâmetros.
3. **Abas do Painel de Controle:**

   * **Cor Única:**
     * **Sliders de Ajuste:** Use os sliders `Min` e `Max` para definir a faixa de valores para os três canais do espaço de cor atualmente selecionado (inicialmente HSV). Os rótulos (H, S, V ou outros) mudam de acordo com o espaço de cor selecionado na aba "Avançado".
     * **Seleção Rápida:**
       * `Selecionar Cor`: Abre um seletor de cores. Escolher uma cor definirá automaticamente uma faixa aproximada nos sliders para o espaço de cor atual.
       * `Cores pré-definidas`: Botões para carregar rapidamente faixas de filtro para cores comuns (funciona melhor no modo HSV).
     * **Salvar Cor Atual:** Dê um nome à configuração atual dos sliders e clique em `Salvar` ou `Adicionar a Multi` para adicioná-la à lista na aba "Multi-Cor".
     * `Sair`: Fecha a aplicação.
   * **Avançado:**
     * `Espaço de Cor`: Selecione o espaço de cor (HSV, BGR, RGB, Lab, YCrCb) a ser usado para a filtragem. Os sliders e seus rótulos na aba "Cor Única" serão atualizados.
     * `Erosão`/`Dilatação`: Ajuste o tamanho do kernel para as operações morfológicas (0 desativa). Erosão remove pequenos ruídos brancos; Dilatação pode aumentar as áreas detectadas e preencher buracos.
     * `Suavização`: Ajuste o tamanho do kernel para o Blur Gaussiano (0 desativa). Ajuda a reduzir o ruído da imagem antes da filtragem.
     * `Área Mínima`: Define a área mínima (em pixels) que um contorno deve ter para ser considerado um objeto detectado.
     * `Opções de Visualização`: Marque as caixas para mostrar/ocultar contornos, caixas delimitadoras e o centro dos objetos na visualização "Original".
   * **Multi-Cor:**
     * `Ativar Modo Multi-Cor`: Marque esta caixa para detectar *todas* as cores salvas na lista abaixo, em vez de apenas a cor definida pelos sliders principais.
     * `Cores Salvas`: Exibe a lista de cores que você salvou. Cada item mostra:
       * Um pequeno quadrado com uma cor representativa.
       * O nome que você deu e o espaço de cor em que foi salva.
       * Os ranges (Ch1, Ch2, Ch3) salvos.
       * Botão `Usar`: Carrega esta cor salva nos sliders principais (desativa o modo Multi-Cor).
       * Botão `X`: Remove esta cor da lista.
     * `Adicionar Cor Atual`: Adiciona a configuração atual dos sliders (da aba "Cor Única") à lista.
     * `Limpar Todas`: Remove todas as cores salvas da lista.
4. **Barra de Status:**
   Localizada na parte inferior, exibe mensagens sobre o estado da aplicação, número de objetos detectados, modo atual e a taxa de quadros por segundo (FPS) aproximada. Erros também podem ser exibidos aqui.

## Funcionalidade Principal Explicada

* **Loop `update`:** O coração da aplicação. A cada ~15ms:

  1. Lê um quadro da câmera.
  2. Converte o quadro para o espaço de cor selecionado.
  3. Aplica blur (se habilitado).
  4. Gera a máscara de cor:
     * **Modo Único:** Usa os valores dos sliders `ch1_min/max`, `ch2_min/max`, `ch3_min/max`. Lida com o "wrap-around" do Hue em HSV se `min > max`.
     * **Modo Multi:** Itera sobre `self.color_presets`. Para cada cor salva que corresponde ao espaço de cor *atual*, gera uma máscara e a combina com a máscara final usando `cv2.bitwise_or`.
  5. Aplica operações morfológicas (erosão/dilatação) na máscara (se habilitado).
  6. Encontra contornos na máscara final.
  7. Filtra contornos pela área mínima.
  8. Desenha visualizações (contornos, caixas, centros) em uma cópia do quadro original (se habilitado).
  9. Cria a imagem "Resultado Filtrado" aplicando a máscara final ao quadro original (`cv2.bitwise_and`).
  10. Converte as imagens (Original com desenhos, Máscara, Resultado Filtrado) para o formato RGB.
  11. Redimensiona as imagens para um tamanho de exibição fixo (`self.display_width`).
  12. Converte as imagens redimensionadas para o formato PIL e depois para `ImageTk.PhotoImage`.
  13. **Atualiza os `Label`s da GUI com as novas imagens, mantendo referências (`label.image = img_tk`) para evitar que sejam coletadas pelo garbage collector.**
  14. Atualiza a barra de status e o FPS.
  15. Agenda a próxima chamada `update`.
* **Gerenciamento de Cores:** As cores salvas são armazenadas na lista `self.color_presets` como dicionários contendo nome, espaço de cor e os seis valores de limite (min/max para os 3 canais).

## Estrutura do Código

O código está encapsulado na classe `ColorFilterApp`:

* **`__init__(self, root)`:** Inicializa a janela principal, a câmera, as variáveis Tkinter, configura a GUI chamando `setup_gui`, e inicia o loop principal chamando `update`.
* **`setup_gui(self)`:** Cria e organiza todos os widgets da interface gráfica (frames, labels, botões, sliders, notebook, etc.).
* **`create_slider_set(...)`**, **`create_preset_buttons(...)`:** Métodos auxiliares para criar conjuntos de widgets na GUI.
* **`get_color_presets(self)`:** Retorna dicionários com as faixas HSV pré-definidas.
* **`set_preset(self, color_key)`:** Define os valores dos sliders com base em uma cor pré-definida.
* **`choose_color(self)`:** Abre o seletor de cores e tenta definir os sliders.
* **`save_current_color(self)`**, **`add_current_color_to_multi(self)`:** Salva a configuração atual dos sliders na lista `color_presets`.
* **`clear_all_colors(self)`:** Limpa a lista `color_presets`.
* **`update_color_list(self)`:** Atualiza a exibição da lista de cores salvas na aba "Multi-Cor".
* **`get_approx_hex_color(self, color_data)`:** Tenta gerar uma cor hexadecimal representativa para a miniatura na lista multi-cor.
* **`load_color(self, color_data)`:** Carrega uma cor salva nos sliders principais.
* **`remove_color(self, index)`:** Remove uma cor da lista multi-cor.
* **`toggle_multi_color_mode(self)`:** Atualiza o status quando o modo multi-cor é ativado/desativado.
* **`change_color_space(self, *args)`:** Atualiza os rótulos dos sliders e redefine os valores padrão quando o espaço de cor é alterado.
* **`update(self)`:** O loop principal de processamento e atualização da GUI.
* **`update_status(self, message, error=False)`:** Atualiza o texto na barra de status.
* **`quit(self)`:** Libera a câmera e fecha a aplicação corretamente.

## Como Sair

Clique no botão "Sair" na aba "Cor Única" ou feche a janela da aplicação. A câmera será liberada automaticamente.

```

```
