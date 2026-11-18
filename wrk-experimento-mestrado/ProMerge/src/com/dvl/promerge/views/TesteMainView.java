package com.dvl.promerge.views;

public class TesteMainView {

	/**
	 * @param args
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {
		/*
		 * //MainView _mainview = new MainView();
		 * //_mainview.dispararSocketServerHierarquia(); ProMergeComplexity obj;
		 * //ProMergeCommits obj = new ProMergeCommits(); try { obj = new
		 * ProMergeComplexity(); obj.setLocationRelativeTo(null);
		 * obj.setVisible(true);
		 * 
		 * } catch (Exception e) { // TODO Auto-generated catch block
		 * e.printStackTrace(); }
		 */

		/*
		 * String nomeArquivo = "Employees.java"; List<String> lista =
		 * DaoGenerico.getInstance().comparaTextoConflitos(nomeArquivo);
		 * 
		 * // Define the paths to the two local files you want to compare. File
		 * file1 = new File("C:\\Temp\\1_" + nomeArquivo); File file2 = new
		 * File("C:\\Temp\\2_" + nomeArquivo);
		 * 
		 * // Define the path to TortoiseMerge.exe (adjust as necessary for your
		 * installation path) String tortoiseMergePath =
		 * "C:\\Program Files\\TortoiseSVN\\bin\\TortoiseMerge.exe";
		 * 
		 * try { //Gravar 1o Arquivo String texto1 = lista.get(0);
		 * BufferedWriter writer1 = new BufferedWriter(new FileWriter(file1,
		 * true)); writer1.write(texto1); writer1.close();
		 * 
		 * //Gravar 2o Arquivo String texto2 = lista.get(1); BufferedWriter
		 * writer2 = new BufferedWriter(new FileWriter(file2, true));
		 * writer2.write(texto2); writer2.close();
		 * 
		 * //Liberar os objetos writer1 = null; writer2 = null;
		 * 
		 * ProcessBuilder processBuilder = new ProcessBuilder(tortoiseMergePath,
		 * "/base:" + file1.getAbsolutePath(), "/mine:" +
		 * file2.getAbsolutePath());
		 * 
		 * System.out.println("Launching TortoiseMerge for file comparison...");
		 * Process process = processBuilder.start();
		 * 
		 * int exitCode = process.waitFor();
		 * System.out.println("TortoiseMerge process exited with code: " +
		 * exitCode);
		 * 
		 * } catch (Exception e) { e.printStackTrace(); }
		 * 
		 * //Delete files if (file1.exists()) file1.delete();
		 * 
		 * if (file2.exists()) file2.delete();
		 */

		/*
		try {
			//Definir a URL de consulta
			URL url = new URL("http://127.0.0.1:8000/promerge_api");
			HttpURLConnection connection = (HttpURLConnection) url.openConnection();

			//Configuração dos parâmetros da requisição
			connection.setRequestMethod("POST");
			connection.setRequestProperty("Content-Type", "application/json");
			connection.setRequestProperty("Accept", "application/json");
			connection.setDoOutput(true);

			//Corpo da requisição (JSON)
			String jsonInput = "{\"query\": \"Apresente o código-fonte em python para calcular o fatorial de um número inteiro utilizando a linguagem python.\"}";

			//Chamada EndPont
			try (OutputStream os = connection.getOutputStream()) {
				byte[] input = jsonInput.getBytes(StandardCharsets.UTF_8);
				os.write(input, 0, input.length);
			}

			//Status de Processamento
			BufferedReader result;
			int status = connection.getResponseCode();
			System.out.println("Status HTTP: " + status);

			//Se o processamento foi OK
			result = new BufferedReader(new InputStreamReader(
					(status >= 200 && status < 300) ? 
							connection.getInputStream() : connection.getErrorStream(), StandardCharsets.UTF_8));
			
			String mensagemRetorno = result.lines().collect(Collectors.joining(System.lineSeparator()));

			//Liberar variáveis da memória e fechar conexões 
			connection.disconnect();
			result.close();
			url = null;
			connection = null;
			result = null;
            
		} catch (Exception e) {
			e.printStackTrace();
		}
		*/
      }
}