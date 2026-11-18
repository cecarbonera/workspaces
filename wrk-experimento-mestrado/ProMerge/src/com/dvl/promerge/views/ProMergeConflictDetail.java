package com.dvl.promerge.views;

import java.awt.BorderLayout;
import java.awt.Component;
import java.awt.Cursor;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.GridLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.text.ParseException;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextArea;
import javax.swing.border.EmptyBorder;
import javax.swing.border.EtchedBorder;
import com.dvl.core.dao.DaoGenerico;
import java.awt.event.KeyEvent;

@SuppressWarnings("serial")
public class ProMergeConflictDetail extends JFrame {
	// Definir os botoes
	JButton btnDefaults = new JButton("Clear");
	JButton btnComparison = new JButton("Conflict Diff");
	JButton btnAnalisys = new JButton("Conflict Analisys");
	JButton btnFechar = new JButton("Close");
	JTextArea taPrompt = new JTextArea();
	JTextArea taResolution = new JTextArea();

	// Actions Listeners
	ActionListener alBtnDefaults, alBtnComparison, alBtnAnalisys, alBtnFechar;

	// Construtor da classe
	public ProMergeConflictDetail(final String nomeArquivo) throws ParseException {
		super("Conflict Evaluation");
		setDefaultCloseOperation(DISPOSE_ON_CLOSE);
		final int _width = 850, _height = 850;

		// Adicionar os componentes
		add(criarTela(_width, _height), BorderLayout.CENTER);
		add(criarRodape(), BorderLayout.SOUTH);

		// Setar os defaults
		setarDefaults();

		// Pesquisar dados conforme os parâmetros
		alBtnDefaults = new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				setarDefaults();
			}
		};
		btnDefaults.setMnemonic(KeyEvent.VK_D);
		btnDefaults.setToolTipText("Clear (alt + D)");

		alBtnComparison = new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				// Se o diretório não existe, cria o diretório
				File diretorio = new File("C:\\Temp");
				if (!diretorio.exists())
					diretorio.mkdirs();

				// Define the paths to the two local files you want to compare.
				File file1 = new File(diretorio + "\\1_" + nomeArquivo);
				File file2 = new File(diretorio + "\\2_" + nomeArquivo);

				// Define the path to TortoiseMerge.exe (adjust as necessary for
				// your installation path)
				String tortoiseMergePath = "C:\\Program Files\\TortoiseSVN\\bin\\TortoiseMerge.exe";

				try {
					// Consultar os Arquivos
					List<String> lista = DaoGenerico.getInstance().comparaTextoConflitos(nomeArquivo);

					// Gravar 1o Arquivo
					String texto1 = lista.get(0);
					BufferedWriter writer1 = new BufferedWriter(new FileWriter(file1, true));
					writer1.write(texto1);
					writer1.close();

					// Gravar 2o Arquivo
					String texto2 = lista.get(1);
					BufferedWriter writer2 = new BufferedWriter(new FileWriter(file2, true));
					writer2.write(texto2);
					writer2.close();

					// Liberar os objetos
					writer1 = null;
					writer2 = null;

					ProcessBuilder processBuilder = new ProcessBuilder(tortoiseMergePath, "/base:" + file1.getAbsolutePath(), "/mine:" + file2.getAbsolutePath());

					System.out.println("Launching TortoiseMerge for file comparison...");
					Process process = processBuilder.start();

					int exitCode = process.waitFor();
					System.out.println("TortoiseMerge process exited with code: " + exitCode);

				} catch (Exception ex2) {
					ex2.printStackTrace();
				}

				// Delete files
				if (file1.exists())
					file1.delete();

				if (file2.exists())
					file2.delete();
			}
		};
		btnComparison.setMnemonic(KeyEvent.VK_C);
		btnComparison.setToolTipText("Source-code conflict comparison (alt + C)");

		alBtnAnalisys = new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				try {
					// Modificar o cursor
					setCursor(Cursor.getPredefinedCursor(Cursor.WAIT_CURSOR)); // ampulheta

					// Definir a URL de consulta
					URL url = new URL("http://127.0.0.1:8000/promerge_api");
					HttpURLConnection connection = (HttpURLConnection) url.openConnection();

					// Configuração dos parâmetros da requisição
					connection.setRequestMethod("POST");
					connection.setRequestProperty("Content-Type", "application/json");
					connection.setRequestProperty("Accept", "application/json");
					connection.setDoOutput(true);

					String promptCompleto = taPrompt.getText();
					List<String> lista = null;
					try {
						lista = DaoGenerico.getInstance().comparaTextoConflitos(nomeArquivo);
					} catch (Exception e1) {
						e1.printStackTrace();
					}

					// Complementar o prompt
					promptCompleto = (promptCompleto +
						"### EXECUTION RULES \n\n"+
						"1. **Focus on Difference:** Identify the exact divergences between Fragment A and Fragment B (ex: variation in data types, method specifications, visibility or calculation of rules) and look for information that clarifies these divergences. \n"+
						"2. **Loyalty to the Dice Bank:** List only information that is expressly registered in the dice bank provided. **Do not invent or deduce rules that are not documented.** \n"+
						"3. **Standard Format:** Strictly follow the response model specified below.\n\n" +
						" ### ENTRANCE \n\n *** Fragment A: \n\n" + lista.get(0) + 
						" \n\n *** Fragment B: \n\n" + lista.get(1) + 
						"\n\n ### MANDATORY RESPONSE FORMAT \n\n"+
						"*** Code Fragment A \n\n"+
						"[Display the source code of Fragment A exactly as provided] \n\n"+
						"*** Information about Fragment A \n"+
						"- [Database information related to Fragment A] \n"+
						"- [Database information related to Fragment A] \n"+
						"- ... \n\n"+
						"* Note: If there is no related information, inform: \n"+
						"- No related information \n\n"+
						"*** Code Fragment  B \n"+
						"[Display the source code of Fragment B exactly as provided] \n\n"+
						"*** Information about Fragment B \n"+
						"- [Database information related to Fragment B] \n"+
						"- [Database information related to Fragment B] \n"+ 
						"... \n\n"+
						"* Note: If there is no related information, inform: \n"+ 
						"- No related information")
						.replace("\n", "\\n")
						.replace("\r", "")
						.replace("\t", "\\t")
						.replace("\"", "\\\"");
					
					// Corpo da requisição (JSON)
					String jsonInput = "{\"query\": \"" + promptCompleto + "\"}";

					// Chamada EndPont
					try (OutputStream os = connection.getOutputStream()) {
						byte[] input = jsonInput.getBytes(StandardCharsets.UTF_8);
						os.write(input, 0, input.length);
					}

					// Status de Processamento
					BufferedReader result;
					int status = connection.getResponseCode();
					System.out.println("Status HTTP: " + status);

					// Se o processamento foi OK
					result = new BufferedReader(new InputStreamReader((status >= 200 && status < 300) ? connection.getInputStream() : connection.getErrorStream(), StandardCharsets.UTF_8));

					// Atribuir o resultado para o componente taResolution
					taResolution.setText(result.lines().collect(Collectors.joining(System.lineSeparator())).replace("\\n", "\n"));

					// Finalizar os objetos
					connection.disconnect();
					result.close();
					url = null;
					connection = null;
					result = null;

				} catch (Exception ex) {
					ex.printStackTrace();
				} finally {
					setCursor(Cursor.getPredefinedCursor(Cursor.DEFAULT_CURSOR));
				}
			}
		};
		btnAnalisys.setMnemonic(KeyEvent.VK_A);
		btnAnalisys.setToolTipText("Source code confict analisys using context sensitive information (alt + A)");

		alBtnFechar = new ActionListener() {
			public void actionPerformed(ActionEvent e) {
				setDefaultCloseOperation(DISPOSE_ON_CLOSE);
				setVisible(false);
			}
		};
		btnFechar.setMnemonic(KeyEvent.VK_F);
		btnFechar.setToolTipText("Close (alt + F)");

		// Adicionar o Evento de pesquisar
		btnDefaults.addActionListener(alBtnDefaults);
		btnComparison.addActionListener(alBtnComparison);
		btnAnalisys.addActionListener(alBtnAnalisys);
		btnFechar.addActionListener(alBtnFechar);

		// Setar o tamanho e visível
		setSize(_width, _height);
		setVisible(true);
		setResizable(true);
	}

	private Component criarTela(int width, int height) {
		setTitle("Source-code conflict analysis");
		setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		setLocationRelativeTo(null);

		// Painel principal
		JPanel painelPrincipal = new JPanel();
		painelPrincipal.setLayout(new GridLayout(2, 1, 10, 10));

		// 1o Panel
		JPanel pnlSuperior = new JPanel();
		pnlSuperior.setLayout(new BorderLayout());
		pnlSuperior.setBorder(new EmptyBorder(5, 6, 5, 6));
		taPrompt.setLineWrap(true);
		taPrompt.setWrapStyleWord(true);
		taPrompt.setFont(new Font("Arial", Font.PLAIN, 14));

		JScrollPane scroll1 = new JScrollPane(taPrompt);
		pnlSuperior.add(new JLabel("Prompt evaluation:"), BorderLayout.NORTH);
		pnlSuperior.add(scroll1, BorderLayout.CENTER);

		// 2o Panel
		JPanel pnInferior = new JPanel();
		pnInferior.setLayout(new BorderLayout());
		pnInferior.setBorder(new EmptyBorder(5, 6, 5, 6));
		taResolution.setLineWrap(true);
		taResolution.setWrapStyleWord(true);
		taResolution.setFont(new Font("Arial", Font.PLAIN, 14));

		JScrollPane scroll2 = new JScrollPane(taResolution);
		pnInferior.add(new JLabel("Analysis result:"), BorderLayout.NORTH);
		pnInferior.add(scroll2, BorderLayout.CENTER);

		// Fazer o split dos paineis
		JSplitPane splitPane = new JSplitPane(JSplitPane.VERTICAL_SPLIT, pnlSuperior, pnInferior);

		splitPane.setResizeWeight(0.3);
		splitPane.setDividerLocation(0.3);

		// return Componente
		return splitPane;
	}

	private Component criarRodape() {
		// Painel dos filtros
		JPanel pnlRodape = new JPanel(new FlowLayout(FlowLayout.RIGHT));
		pnlRodape.setBorder(new EtchedBorder(EtchedBorder.LOWERED));

		// Adicionar os botões
		pnlRodape.add(btnDefaults);
		pnlRodape.add(btnComparison);
		pnlRodape.add(btnAnalisys);
		pnlRodape.add(btnFechar);

		return pnlRodape;
	}

	private void setarDefaults() {
		taResolution.setText("");
		taPrompt.setText("");
		FormatarTexto();
	}

	/**
	 * 
	 * @param contexto_rag
	 * @param codigo_a
	 * @param codigo_b
	 */
	private void FormatarTexto(){
		String textoPromptPOrtugues =		
			"Você é um assistente especializado em engenharia de software, revisão de código e linguagem Java. \n " +
			"Seu objetivo é analisar dois fragmentos distintos de código-fonte Java que apresentam um conflito direto de implementação e sugerir a melhor alternativa de resolução. \n " +  
			"O sistema pode fornecer um CONTEXTO recuperado por um mecanismo de RAG (Retrieval Augmented Generation). Esse contexto pode conter informações como: \n " +  
			"* documentação técnica do sistema \n " +  
			"* regras de negócio \n " +  
			"* padrões arquiteturais  \n " + 
			"* exemplos de código do projeto \n " +  
			"* decisões de arquitetura (ADR) \n " +  
			"* padrões de codificação \n " +  
			"* contratos de API ou requisitos do sistema \n\n " +  
			"### Regras de Análise \n\n " +  
			"1. Analise cuidadosamente os dois fragmentos de código Java fornecidos. \n " +  
			"2. Identifique claramente o tipo de conflito existente entre eles. Exemplos: \n " +  
			"   * diferença de lógica ou comportamento \n " +  
			"   * alteração de assinatura de método \n " +  
			"   * alteração de fluxo de execução \n " +  
			"   * mudança de estrutura de dados \n " +  
			"   * alteração de tratamento de exceções \n " +  
			"   * divergência de padrão arquitetural \n " +  
			"3. Utilize **prioritariamente as informações do CONTEXTO** para orientar a decisão sobre qual implementação deve ser utilizada. \n " +  
			"4. Se o contexto contiver evidências relevantes: \n " +  
			"   * cite explicitamente quais partes do contexto suportam sua decisão. \n " +  
			"5. Caso o contexto esteja incompleto ou não contenha informações suficientes: \n " +  
			"   * informe claramente que o contexto não é suficiente \n " +  
			"   * utilize boas práticas de engenharia de software e da linguagem Java para propor a melhor solução. \n " +  
			"6. Avalie cada fragmento considerando: \n " +  
			"   * legibilidade \n " +  
			"   * manutenibilidade \n " +  
			"   * aderência ao contexto do projeto \n " +  
			"   * desempenho \n " +  
			"   * segurança \n " +  
			"   * robustez \n " +  
			"7. Caso necessário, proponha uma **terceira alternativa de implementação** que resolva o conflito de forma superior às duas versões apresentadas. \n " +  
			"8. Não invente informações que não estejam no contexto. \n\n " +  
			"### Estrutura da Resposta \n\n " +    
			"1. **Descrição do Conflito** \n " +    
			"   Explique qual é o conflito entre os dois fragmentos de código. \n " +      
			"2. **Análise do Fragmento A** \n " +      
			"   Descreva o comportamento, pontos positivos e possíveis problemas. \n " +      
			"3. **Análise do Fragmento B** \n " +      
			"   Descreva o comportamento, pontos positivos e possíveis problemas. \n " +      
			"4. **Uso do Contexto** \n " +      
			"   Explique como as informações do contexto influenciam a decisão. \n " +      
			"   Se não houver contexto relevante, informe explicitamente. \n " +      
			"5. **Recomendação de Resolução** \n " +      
			"   Indique qual abordagem deve ser utilizada ou proponha uma alternativa melhor. \n " +      
			"6. **Código Java Sugerido** \n " +      
			"   Apresente a implementação final recomendada. \n " +      
			"7. **Justificativa Técnica** \n " +      
			"   Explique por que a solução proposta é a mais adequada considerando o contexto e boas práticas de desenvolvimento Java.";

		String textoPrompt = 
			"You are a highly specialized software engineering assistant in code analysis, resolution of font-code conflicts and recovery of contextual information. \n\n"+
			"### OBJECTIVES\n"+
			"Its function is to analyze the conflicting source code fragments (Fragment A and Fragment B) and extract from the document database information related to both fragments.\n\n"+
			"### SOURCES OF CONTEXT TO CONSIDER\n\n"+
			"Filter any type of information that may contain some type of relationship with the source-code conflicts detected (for example: alteration of data type, size, name, etc.) \n"+
			"Your search must be exclusively in the database: \n"+
			"- Technical documentation \n"+
			"- Requirement specifications \n"+
			"- Business rules \n"+
			"- Contents or other appointments related to the source code conflicts \n"+
			"- Technical definitions  \n"+
			"- Architectural Decision Records (ADRs) \n"+
			"- Architectural patterns \n"+
			"- Project coding patterns \n"+
			"- Existing code examples \n\n";
		
		//Corrigir o problema da acentuação
		byte[] bytes = textoPrompt.getBytes();
		taPrompt.setText(new String(bytes, StandardCharsets.UTF_8));		
	}
}