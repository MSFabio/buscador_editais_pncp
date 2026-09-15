package com.pncp.monitor.domain.service;

import com.pncp.monitor.domain.model.EditalAprovado;
import com.pncp.monitor.domain.model.EditalLeve;
import com.pncp.monitor.domain.model.PalavraChave;
import com.pncp.monitor.domain.model.VeredictoGemini;
import com.pncp.monitor.domain.port.EditalRepository;
import com.pncp.monitor.domain.port.GeminiGateway;
import com.pncp.monitor.domain.port.PalavraChaveRepository;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

@Service
public class FiltragemService {

    private static final Logger logger = LoggerFactory.getLogger(FiltragemService.class);

    private final PalavraChaveRepository palavraChaveRepository;
    private final EditalRepository editalRepository;
    private final GeminiGateway geminiGateway;

    public FiltragemService(PalavraChaveRepository palavraChaveRepository,
                            EditalRepository editalRepository,
                            GeminiGateway geminiGateway) {
        this.palavraChaveRepository = palavraChaveRepository;
        this.editalRepository = editalRepository;
        this.geminiGateway = geminiGateway;
    }

    /**
     * Processa uma lista de editais e aprova os aderentes ao negócio.
     */
    public List<EditalAprovado> processarEditais(List<EditalLeve> editais) {
        logger.info("Iniciando processamento de {} editais", editais.size());

        List<EditalLeve> editaisNaoProcessados = editais.stream()
                .filter(e -> !editalRepository.existeById(e.id()))
                .collect(Collectors.toList());

        logger.info("Editais não processados ainda: {}", editaisNaoProcessados.size());

        if (editaisNaoProcessados.isEmpty()) {
            return new ArrayList<>();
        }

        List<PalavraChave> keywordsAtivas = palavraChaveRepository.listarAtivas();
        if (keywordsAtivas.isEmpty()) {
            logger.warn("Nenhuma palavra-chave ativa encontrada. Pulando análise.");
            return new ArrayList<>();
        }

        List<VeredictoGemini> veredictos = geminiGateway.filtrarEditais(editaisNaoProcessados, keywordsAtivas);
        List<EditalAprovado> aprovados = new ArrayList<>();

        for (VeredictoGemini veredicto : veredictos) {
            if (veredicto.aderente()) {
                EditalLeve editalOrigem = editaisNaoProcessados.stream()
                        .filter(e -> e.id().equals(veredicto.editalId()))
                        .findFirst()
                        .orElse(null);

                if (editalOrigem != null) {
                    EditalAprovado aprovado = EditalAprovado.fromEditalLeve(
                            editalOrigem, veredicto, "Desconhecido", Instant.now()
                    );
                    editalRepository.salvar(aprovado);
                    aprovados.add(aprovado);
                    logger.info("Edital {} aprovado e salvo com sucesso.", aprovado.id());
                }
            }
        }

        logger.info("Processamento concluído. Editais aprovados: {}", aprovados.size());
        return aprovados;
    }
}
