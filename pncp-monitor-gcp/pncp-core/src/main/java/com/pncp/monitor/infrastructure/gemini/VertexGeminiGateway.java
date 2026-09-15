package com.pncp.monitor.infrastructure.gemini;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.cloud.vertexai.VertexAI;
import com.google.cloud.vertexai.api.GenerateContentResponse;
import com.google.cloud.vertexai.api.GenerationConfig;
import com.google.cloud.vertexai.generativeai.GenerativeModel;
import com.pncp.monitor.domain.model.EditalLeve;
import com.pncp.monitor.domain.model.PalavraChave;
import com.pncp.monitor.domain.model.VeredictoGemini;
import com.pncp.monitor.domain.port.GeminiGateway;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Component
public class VertexGeminiGateway implements GeminiGateway {

    private static final Logger logger = LoggerFactory.getLogger(VertexGeminiGateway.class);

    private static final String SYSTEM_PROMPT = """
        Você é um analista especializado em licitações públicas brasileiras. Sua ÚNICA função é avaliar se o texto de um edital de licitação é SEMANTICAMENTE ADERENTE ao contexto de negócio descrito por uma palavra-chave fornecida pelo usuário.

        ## REGRAS ABSOLUTAS

        1. **Análise Semântica Pura:** Você deve avaliar a INTENÇÃO e o CONTEXTO do edital, não a presença literal de palavras. Exemplo: Se a keyword for "segurança da informação" e o edital mencionar "serviços de vigilância patrimonial", o veredicto DEVE ser "NAO_ADERENTE", pois o contexto é segurança física, não cibernética.

        2. **Zero Alucinação:** Baseie sua avaliação EXCLUSIVAMENTE no texto do edital fornecido. Não invente informações, não assuma contextos implícitos, não extrapole além do que está escrito.

        3. **Tolerância Zero a Falsos Positivos:** Na dúvida, classifique como "NAO_ADERENTE". É preferível perder um edital relevante a aprovar um irrelevante.

        4. **Ignore Jargão Burocrático:** Ignore trechos como dotações orçamentárias, números de processo, referências legais e CNPJ. Concentre-se APENAS no objeto da compra e informações complementares.

        ## FORMATO DE ENTRADA

        Você receberá um JSON com:
        - "keyword": objeto contendo "termo" (a palavra-chave) e "contexto" (descrição do segmento de negócio desejado)
        - "editais": array de objetos, cada um com "id", "objeto" e "infoComplementar"

        ## FORMATO DE SAÍDA (OBRIGATÓRIO)

        Retorne EXCLUSIVAMENTE um JSON válido, sem markdown, sem explicações fora do JSON:
        {"resultados": [{"id": "<id do edital>", "veredicto": "ADERENTE" ou "NAO_ADERENTE", "confianca": <float 0.0 a 1.0>, "justificativa": "<1 frase curta>"}]}
        """;

    private final String projectId;
    private final String location;
    private final String modelName;
    private final int batchSize;
    private final ObjectMapper objectMapper = new ObjectMapper();

    public VertexGeminiGateway(
            @Value("${gcp.project-id}") String projectId,
            @Value("${gcp.location}") String location,
            @Value("${gemini.model:gemini-2.0-flash}") String modelName,
            @Value("${gemini.batch-size:10}") int batchSize) {
        this.projectId = projectId;
        this.location = location;
        this.modelName = modelName;
        this.batchSize = batchSize;
    }

    @Override
    public List<VeredictoGemini> filtrarEditais(List<EditalLeve> editais, List<PalavraChave> keywords) {
        List<VeredictoGemini> resultadosFinais = new ArrayList<>();

        try (VertexAI vertexAI = new VertexAI(projectId, location)) {
            GenerationConfig config = GenerationConfig.newBuilder()
                    .setTemperature(0.0f)
                    .setResponseMimeType("application/json")
                    .build();

            GenerativeModel model = new GenerativeModel(modelName, config, vertexAI);
            model.setSystemInstruction(SYSTEM_PROMPT);

            for (PalavraChave keyword : keywords) {
                // Processa em lotes
                for (int i = 0; i < editais.size(); i += batchSize) {
                    int end = Math.min(i + batchSize, editais.size());
                    List<EditalLeve> lote = editais.subList(i, end);

                    try {
                        String payload = montarPayloadJson(keyword, lote);
                        GenerateContentResponse response = model.generateContent(payload);
                        String jsonRetorno = response.getCandidates(0).getContent().getParts(0).getText();

                        List<VeredictoGemini> veredictos = extrairVeredictos(jsonRetorno);
                        resultadosFinais.addAll(veredictos);

                        Thread.sleep(200); // 200ms delay
                    } catch (Exception e) {
                        logger.error("Erro ao chamar Gemini para o lote", e);
                    }
                }
            }
        } catch (IOException e) {
            logger.error("Erro ao inicializar Vertex AI", e);
        }

        return resultadosFinais;
    }

    private String montarPayloadJson(PalavraChave keyword, List<EditalLeve> lote) throws Exception {
        Map<String, Object> root = new HashMap<>();
        Map<String, String> kwMap = new HashMap<>();
        kwMap.put("termo", keyword.termo());
        kwMap.put("contexto", keyword.contexto());
        root.put("keyword", kwMap);

        List<Map<String, String>> editaisList = new ArrayList<>();
        for (EditalLeve e : lote) {
            Map<String, String> editalMap = new HashMap<>();
            editalMap.put("id", e.id());
            editalMap.put("objeto", e.objeto());
            editalMap.put("infoComplementar", e.infoComplementar());
            editaisList.add(editalMap);
        }
        root.put("editais", editaisList);

        return objectMapper.writeValueAsString(root);
    }

    private List<VeredictoGemini> extrairVeredictos(String json) throws Exception {
        List<VeredictoGemini> lista = new ArrayList<>();
        JsonNode rootNode = objectMapper.readTree(json);
        JsonNode resultadosNode = rootNode.path("resultados");

        if (resultadosNode.isArray()) {
            for (JsonNode node : resultadosNode) {
                String id = node.path("id").asText();
                String veredicto = node.path("veredicto").asText();
                double confianca = node.path("confianca").asDouble();
                String justificativa = node.path("justificativa").asText();

                boolean aderente = "ADERENTE".equalsIgnoreCase(veredicto);
                lista.add(new VeredictoGemini(id, aderente, justificativa, confianca));
            }
        }
        return lista;
    }
}
